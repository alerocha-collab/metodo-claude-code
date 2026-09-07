#!/usr/bin/env python3
"""Detecta conteúdo de plugin que mudou sem `version` ter subido.

**Por que isto é mecanismo e não lembrete.** O `marketplace.json` aponta para
`./plugins/<nome>`, então quem instala do GitHub recebe o que está em `main`. **Não há
etapa de publicação separada: todo push para `main` é um release.**

E o cache é chaveado por versão — `~/.claude/plugins/cache/<mkt>/<plugin>/<versão>/`.
Mudar conteúdo sem mudar `version` publica um plugin diferente sob o mesmo número, e
quem já instalou continua com a cópia antiga sem nada avisar. O silêncio é o problema:
não há erro, não há aviso, só um plugin que não atualiza.

A suíte irmã (`tests/testar_marketplace.py`) pega **subir errado** — versão divergente
entre a entrada do marketplace e o `plugin.json`. Este script pega o outro lado:
**esquecer de subir**. Juntos fecham a pendência P4.

Contrato de sempre: **detecta, nunca corrige.** Subir versão é ato deliberado.

Uso:
    python3 scripts/verificar_bump.py [base]

`base` é o commit de comparação; o padrão é `HEAD~1`. Em CI, passe o commit anterior
do push ou a merge-base do PR.

Sai com 0 se está tudo certo, 1 se algum plugin mudou sem bump.
"""

import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(".claude-plugin", "plugin.json")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def plugin_de(caminho):
    """O nome do plugin a que `caminho` pertence, ou None se estiver fora deles.

    Aceita separador de Windows e de POSIX: o git devolve `/`, mas quem chamar com
    caminho da plataforma não deve ser surpreendido.
    """
    partes = caminho.replace("\\", "/").split("/")
    if len(partes) >= 3 and partes[0] == "plugins":
        return partes[1]
    return None


def faltou_bump(mudados, versao_antes, versao_depois):
    """Plugins que tiveram conteúdo alterado e continuaram na mesma `version`.

    - `mudados`: caminhos relativos à raiz, como o git os lista.
    - `versao_antes` / `versao_depois`: {plugin: versão ou None}.

    Núcleo puro, sem git e sem disco, para a suíte poder alimentá-lo com casos
    sintéticos — inclusive os que seria caro produzir com commits de verdade.
    """
    tocados = {p for p in (plugin_de(c) for c in mudados) if p}
    faltando = []
    for nome in sorted(tocados):
        antes = versao_antes.get(nome)
        depois = versao_depois.get(nome)
        if antes is None:
            continue          # plugin novo: não havia versão anterior para subir
        if depois is None:
            faltando.append((nome, antes, depois))   # manifesto sumiu ou ilegível
        elif antes == depois:
            faltando.append((nome, antes, depois))
    return faltando


def git(*args, cwd=RAIZ):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def versao_em(ref, nome):
    """A `version` do plugin `nome` como estava em `ref`. None se não dá para ler."""
    import json
    caminho = "plugins/" + nome + "/" + MANIFESTO.replace("\\", "/")
    r = git("show", ref + ":" + caminho)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout).get("version")
    except (ValueError, AttributeError):
        return None


def main(argv):
    base = argv[1] if len(argv) > 1 else "HEAD~1"

    if git("rev-parse", "--verify", base + "^{commit}").returncode != 0:
        # Sem base não há comparação possível. Não é falha: e um repositorio de um
        # commit so, ou um checkout raso. Dizer isso e melhor que reprovar por engano
        # — mas tambem melhor que passar em silencio.
        print(f"AVISO: base {base!r} nao existe neste checkout; nada a comparar.")
        print("Em CI, garanta historico suficiente (fetch-depth).")
        return 0

    r = git("diff", "--name-only", base, "HEAD")
    if r.returncode != 0:
        print(f"FALHA: git diff nao rodou: {r.stderr.strip()}")
        return 1
    mudados = [l for l in r.stdout.splitlines() if l.strip()]

    tocados = {p for p in (plugin_de(c) for c in mudados) if p}
    if not tocados:
        print(f"Nenhum plugin mudou entre {base} e HEAD. Nada a exigir.")
        return 0

    antes = {n: versao_em(base, n) for n in tocados}
    depois = {n: versao_em("HEAD", n) for n in tocados}

    print(f"== plugins tocados entre {base} e HEAD ==")
    for nome in sorted(tocados):
        seta = "->" if antes[nome] != depois[nome] else "=="
        print(f"  {nome}: {antes[nome]} {seta} {depois[nome]}")
    print()

    faltando = faltou_bump(mudados, antes, depois)
    if not faltando:
        print("ok: todo plugin alterado teve `version` alterada tambem.")
        return 0

    print(f"FALHA: {len(faltando)} plugin(s) mudaram sem subir `version`:")
    for nome, a, d in faltando:
        print(f"  - {nome}: continua em {a!r}")
    print()
    print("Todo push para `main` e um release: o marketplace aponta para ./plugins/<nome>")
    print("e o cache de quem instalou e chaveado por versao. Sem bump, essa pessoa fica")
    print("com a copia antiga e nada avisa.")
    print()
    print("Suba `version` no plugin.json E na entrada correspondente do marketplace.json")
    print("— as duas, ou `claude plugin validate . --strict` reprova a divergencia.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
