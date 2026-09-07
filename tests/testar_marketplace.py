#!/usr/bin/env python3
"""Suite do `.claude-plugin/marketplace.json` — o que torna os plugins instaláveis.

Enquanto tudo roda por `--plugin-dir`, o marketplace nunca é exercitado: aquele modo
aponta para a pasta local, não resolve fonte e não passa pelo cache. O primeiro erro
aqui só aparece na máquina de quem instalou — e lá ele aparece como "o plugin não
carregou", sem dizer por quê.

Duas coisas medidas neste repositório, com o validador oficial, e que valem mais que a
prosa da doc:

1. **`version` divergente é AVISO, não erro.** Sem `--strict`, um marketplace com
   versão errada passa. Por isso a suíte trata como falha aqui dentro.
2. **No install, o `plugin.json` VENCE.** A versão da entrada é ignorada em silêncio.
   Quem sobe só a entrada acha que publicou, e o cache continua servindo a antiga.

Balanceada: o marketplace real precisa **passar**, marketplaces inventados com defeito
precisam **reprovar**, e um marketplace inventado correto precisa **passar**. Sem esse
último caso, um validador que reprova tudo passaria na suíte.

Esta suíte não chama o `claude` — ela roda no job sem CLI. A validação oficial
(`claude plugin validate . --strict`) fica no job que instala o Claude Code.

Rode: python3 tests/testar_marketplace.py
"""

import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(RAIZ, ".claude-plugin", "marketplace.json")

OBRIGATORIOS = ("name", "owner", "plugins")

# Link markdown que sobe de diretorio: `](../algo)`. E o que quebra ao instalar.
RELATIVO = re.compile(r"\]\(\.\./")
# Referencia pela variavel que a plataforma substitui.
VARIAVEL = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^)\s]+)")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def problemas_de(manifesto, raiz):
    """Problemas do marketplace `manifesto`, com fontes resolvidas contra `raiz`.

    Lista vazia = aceitavel. Nunca corrige nada: so relata.
    """
    problemas = []

    for campo in OBRIGATORIOS:
        if not manifesto.get(campo):
            problemas.append(f"campo obrigatorio ausente ou vazio: `{campo}`")
    if problemas:
        return problemas

    if not isinstance(manifesto["plugins"], list):
        return ["`plugins` precisa ser lista"]

    vistos = set()
    for i, entrada in enumerate(manifesto["plugins"]):
        onde = f"plugins[{i}]"
        nome = entrada.get("name")
        if not nome:
            problemas.append(f"{onde}: sem `name`")
            continue
        if nome in vistos:
            problemas.append(f"{onde}: nome duplicado {nome!r}")
        vistos.add(nome)

        fonte = entrada.get("source")
        if not fonte:
            problemas.append(f"{onde}: sem `source`")
            continue
        if not isinstance(fonte, str):
            # Fonte remota (github, url, npm...) nao da para conferir em disco.
            # Este repositorio usa so caminho relativo; outra forma e sinal de
            # desenho mudado, nao de erro — mas precisa ser deliberada.
            problemas.append(f"{onde}: fonte nao e caminho relativo: {fonte!r}")
            continue

        destino = os.path.realpath(os.path.join(raiz, fonte))
        if os.path.commonpath([destino, os.path.realpath(raiz)]) != os.path.realpath(raiz):
            problemas.append(f"{onde}: `source` escapa do repositorio: {fonte!r}")
            continue

        alvo = os.path.join(destino, ".claude-plugin", "plugin.json")
        if not os.path.exists(alvo):
            problemas.append(f"{onde}: `source` {fonte!r} nao tem .claude-plugin/plugin.json")
            continue

        try:
            plugin = json.load(io.open(alvo, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            problemas.append(f"{onde}: plugin.json de {fonte!r} ilegivel: {erro}")
            continue

        # O `name` da entrada e o que se digita no install. Divergir do plugin.json
        # deixa o namespace das skills diferente do nome anunciado.
        if plugin.get("name") != nome:
            problemas.append(
                f"{onde}: entrada diz {nome!r}, plugin.json diz {plugin.get('name')!r}")

        # `version` na entrada e OPCIONAL. Mas se estiver la e divergir, o validador
        # oficial so avisa — e no install o plugin.json vence em silencio.
        v_entrada, v_plugin = entrada.get("version"), plugin.get("version")
        if v_entrada is not None and v_entrada != v_plugin:
            problemas.append(
                f"{onde}: version {v_entrada!r} != plugin.json {v_plugin!r} "
                "(no install o plugin.json vence, em silencio)")

    return problemas


def skills_de(raiz):
    return glob.glob(os.path.join(raiz, "plugins", "*", "skills", "*", "SKILL.md"))


def links_relativos(raiz):
    """[(caminho, linha)] de skills que apontam para arquivo empacotado com `../`."""
    achados = []
    for c in skills_de(raiz):
        for linha in io.open(c, encoding="utf-8"):
            if RELATIVO.search(linha):
                achados.append((os.path.relpath(c, raiz), linha.strip()))
    return achados


def alvos_quebrados(raiz):
    """[(caminho, alvo)] de referencias `${CLAUDE_PLUGIN_ROOT}/...` sem arquivo."""
    achados = []
    for c in skills_de(raiz):
        # A raiz do plugin e duas pastas acima de skills/<nome>/SKILL.md.
        base = os.path.dirname(os.path.dirname(os.path.dirname(c)))
        for alvo in VARIAVEL.findall(io.open(c, encoding="utf-8").read()):
            if not os.path.exists(os.path.join(base, alvo.rstrip("/"))):
                achados.append((os.path.relpath(c, raiz), alvo))
    return achados


def falso(tmp, nome="p", nome_plugin=None, versao="0.1.0"):
    """Cria um plugin de mentira em disco e devolve o caminho relativo dele."""
    d = os.path.join(tmp, "plugins", nome, ".claude-plugin")
    os.makedirs(d)
    io.open(os.path.join(d, "plugin.json"), "w", encoding="utf-8").write(
        json.dumps({"name": nome_plugin or nome, "version": versao}))
    return "./plugins/" + nome


def main():
    falhas, total = [], 0

    print("== o marketplace real ==")
    total += 1
    if not os.path.exists(MANIFESTO):
        print("  FALHA nao ha .claude-plugin/marketplace.json na raiz")
        print("\n1 de 1 FALHARAM")
        return 1
    print("  ok   .claude-plugin/marketplace.json existe na raiz do repositorio")

    total += 1
    try:
        real = json.load(io.open(MANIFESTO, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        print(f"  FALHA marketplace.json nao e JSON valido: {erro}")
        print("\n1 de 2 FALHARAM")
        return 1
    print("  ok   marketplace.json e JSON valido")

    total += 1
    problemas = problemas_de(real, RAIZ)
    print(f"  {'ok  ' if not problemas else 'FALHA'} fontes resolvem, nomes e versoes batem")
    if problemas:
        falhas.extend(problemas)

    # Os dois plugins do repositorio precisam estar anunciados. Um plugin que existe
    # mas nao esta no marketplace nao e instalavel, e nada mais avisa.
    total += 1
    em_disco = {n for n in os.listdir(os.path.join(RAIZ, "plugins"))
                if os.path.exists(os.path.join(RAIZ, "plugins", n,
                                               ".claude-plugin", "plugin.json"))}
    anunciados = {e.get("name") for e in real.get("plugins", [])}
    faltando = em_disco - anunciados
    print(f"  {'ok  ' if not faltando else 'FALHA'} todo plugin em disco esta anunciado "
          f"({len(em_disco)} em disco)")
    if faltando:
        falhas.append(f"plugin(s) em disco fora do marketplace: {sorted(faltando)}")

    print("== como as skills apontam para os arquivos que carregam sob demanda ==")
    # Medido ao instalar num repositorio limpo: com link relativo (`../../ref.md`) o
    # agente nao tem base para resolver e precisa ADIVINHAR o diretorio do plugin.
    # `${CLAUDE_PLUGIN_ROOT}` e substituido pela plataforma e vale nos dois modos —
    # `--plugin-dir` e instalado. Enquanto tudo roda neste repositorio, o link
    # relativo parece funcionar; ele so quebra na maquina de quem instalou.
    total += 1
    relativos = links_relativos(RAIZ)
    print(f"  {'ok  ' if not relativos else 'FALHA'} nenhuma skill aponta para arquivo "
          "empacotado por caminho relativo")
    if relativos:
        falhas.extend(f"link relativo em {c}: {l!r}" for c, l in relativos)

    # E o outro lado: caminho que usa a variavel mas aponta para arquivo que nao
    # existe. A variavel resolve, o arquivo nao — e o sintoma e o mesmo.
    total += 1
    quebrados = alvos_quebrados(RAIZ)
    print(f"  {'ok  ' if not quebrados else 'FALHA'} todo alvo de ${{CLAUDE_PLUGIN_ROOT}} existe")
    if quebrados:
        falhas.extend(f"alvo inexistente em {c}: {a}" for c, a in quebrados)

    print("== marketplaces inventados que DEVEM reprovar ==")
    tmp = tempfile.mkdtemp()
    try:
        bom = falso(tmp, "bom")
        ruins = [
            ("sem `owner`",
             {"name": "m", "plugins": [{"name": "bom", "source": bom}]}),
            ("sem `plugins`",
             {"name": "m", "owner": {"name": "x"}}),
            ("fonte que nao existe",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "fantasma", "source": "./plugins/fantasma"}]}),
            ("pasta sem plugin.json",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "oco", "source": "./plugins"}]}),
            ("nome divergindo do plugin.json",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "outro", "source": bom}]}),
            ("version divergindo do plugin.json",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "bom", "source": bom, "version": "9.9.9"}]}),
            ("fonte escapando do repositorio",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "fuga", "source": "../../etc"}]}),
            ("dois plugins com o mesmo nome",
             {"name": "m", "owner": {"name": "x"},
              "plugins": [{"name": "bom", "source": bom},
                          {"name": "bom", "source": bom}]}),
        ]
        for nome, ruim in ruins:
            total += 1
            achou = problemas_de(ruim, tmp)
            print(f"  {'ok  ' if achou else 'FALHA'} {nome}")
            if not achou:
                falhas.append(f"marketplace ruim passou: {nome}")

        # Os dois detectores de referencia precisam ACUSAR quando ha o que acusar.
        # Sem estes casos, uma regex que nunca casa passaria nos dois testes acima.
        print("== skills inventadas: o detector de referencia acusa? ==")
        d = os.path.join(tmp, "plugins", "px", "skills", "s")
        os.makedirs(d)
        io.open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(
            "---\nname: s\n---\nVeja [r](../../referencias/r.md) e "
            "[q](${CLAUDE_PLUGIN_ROOT}/referencias/nao-existe.md).\n")

        total += 1
        achou = links_relativos(tmp)
        print(f"  {'ok  ' if achou else 'FALHA'} acusa o link relativo")
        if not achou:
            falhas.append("link relativo inventado passou despercebido")

        total += 1
        achou = alvos_quebrados(tmp)
        print(f"  {'ok  ' if achou else 'FALHA'} acusa o alvo que nao existe")
        if not achou:
            falhas.append("alvo inexistente inventado passou despercebido")

        print("== marketplace inventado CORRETO que nao deve reprovar ==")
        # Sem este caso, um validador que reprova tudo passaria em todos os de cima.
        total += 1
        certo = {"name": "m", "owner": {"name": "x"},
                 "plugins": [{"name": "bom", "source": bom, "version": "0.1.0"}]}
        achou = problemas_de(certo, tmp)
        print(f"  {'ok  ' if not achou else 'FALHA'} marketplace correto passa")
        if achou:
            falhas.append(f"marketplace correto reprovou: {achou}")

        # E `version` ausente e legitimo: o campo e opcional.
        total += 1
        sem_versao = {"name": "m", "owner": {"name": "x"},
                      "plugins": [{"name": "bom", "source": bom}]}
        achou = problemas_de(sem_versao, tmp)
        print(f"  {'ok  ' if not achou else 'FALHA'} entrada sem `version` passa (campo opcional)")
        if achou:
            falhas.append(f"entrada sem version reprovou: {achou}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if falhas:
        print(f"{len(falhas)} de {total} FALHARAM:")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print(f"{total} casos, todos passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
