#!/usr/bin/env python3
"""Suite do exemplo de permissões que o `metodo` distribui.

Um exemplo de configuração de segurança é copiado sem ser lido — é essa a natureza
de exemplo. Então ele precisa ser verificável, não só bem-intencionado: uma linha
larga que passe despercebida aqui vira uma linha larga no `settings.json` de quem
copiou, e desliga a camada inteira.

Balanceada: o exemplo real precisa **passar**, e um exemplo inventado com regra larga
precisa **reprovar**. Sem a segunda metade, um validador que aprova tudo passaria.

Rode: python3 tests/testar_permissoes.py
"""

import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEMPLO = os.path.join(RAIZ, "plugins", "metodo", "templates", "settings.exemplo.json")

# `Ferramenta(especificador)` ou `Ferramenta` sozinha.
REGRA = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)(?:\((.*)\))?$")

# Ferramentas cujo uso amplo tem consequencia. Um `allow` sem especificador, ou com
# especificador que casa tudo, desliga a camada para elas.
PERIGOSAS = {"Bash", "PowerShell", "Edit", "Write", "NotebookEdit", "WebFetch",
             "Skill", "Workflow", "Artifact"}

LARGOS = {"*", "**", "./**", "./*", ":*", "**/*"}

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def problemas_de(config):
    """Devolve a lista de problemas do bloco de permissoes. Vazia = aceitavel."""
    problemas = []
    perms = config.get("permissions")
    if not isinstance(perms, dict):
        return ["nao ha bloco `permissions`"]

    for lista in ("allow", "deny", "ask"):
        regras = perms.get(lista) or []
        if not isinstance(regras, list):
            problemas.append(f"`{lista}` precisa ser lista")
            continue
        for regra in regras:
            casou = REGRA.match(regra or "")
            if not casou:
                problemas.append(f"{lista}: regra fora da sintaxe documentada: {regra!r}")
                continue
            ferramenta, spec = casou.group(1), casou.group(2)
            if lista != "allow":
                continue
            if spec is None and ferramenta in PERIGOSAS:
                problemas.append(
                    f"allow largo: {regra!r} permite a ferramenta inteira")
            elif spec is not None and spec.strip() in LARGOS:
                problemas.append(f"allow largo: {regra!r} casa qualquer coisa")

    if not perms.get("deny"):
        problemas.append("exemplo sem nenhuma regra `deny`: nao demonstra a camada")
    return problemas


def main():
    falhas, total = [], 0

    print("== o exemplo real ==")
    total += 1
    try:
        config = json.load(io.open(EXEMPLO, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erro:
        print(f"  FALHA settings.exemplo.json nao e JSON valido: {erro}")
        return 1
    print("  ok   settings.exemplo.json e JSON valido")

    total += 1
    problemas = problemas_de(config)
    print(f"  {'ok  ' if not problemas else 'FALHA'} sem regra larga nem sintaxe invalida")
    if problemas:
        falhas.extend(problemas)

    # Negar leitura ja bloqueia edicao e escrita no mesmo caminho. Um exemplo que
    # repete as tres ensina a escrever tres vezes mais regra do que o necessario.
    total += 1
    deny = config["permissions"]["deny"]
    caminhos_read = {r[5:-1] for r in deny if r.startswith("Read(")}
    redundantes = [r for r in deny
                   if (r.startswith("Edit(") or r.startswith("Write("))
                   and r[r.index("(") + 1:-1] in caminhos_read]
    print(f"  {'ok  ' if not redundantes else 'FALHA'} nao repete Edit/Write onde ja nega Read")
    if redundantes:
        falhas.append(f"regras redundantes: {redundantes}")

    # Cada bloco precisa dizer POR QUE existe. Exemplo sem razao e copiado sem
    # entendimento, e vira configuracao de carga cult.
    total += 1
    comentarios = [k for k in config.get("permissions", {}) if k.startswith("$")]
    ok = len(comentarios) >= 3
    print(f"  {'ok  ' if ok else 'FALHA'} os blocos explicam por que existem "
          f"({len(comentarios)} notas)")
    if not ok:
        falhas.append("o exemplo nao explica as razoes")

    print("== exemplos inventados que DEVEM reprovar ==")
    ruins = [
        ("allow de Bash inteiro", {"permissions": {"allow": ["Bash"], "deny": ["Read(.env)"]}}),
        ("allow com curinga", {"permissions": {"allow": ["Bash(*)"], "deny": ["Read(.env)"]}}),
        ("allow de Edit em tudo", {"permissions": {"allow": ["Edit(./**)"], "deny": ["Read(.env)"]}}),
        ("sintaxe quebrada", {"permissions": {"deny": ["Read .env"]}}),
        ("sem nenhum deny", {"permissions": {"allow": ["Bash(npm test)"]}}),
    ]
    for nome, ruim in ruins:
        total += 1
        achou = problemas_de(ruim)
        print(f"  {'ok  ' if achou else 'FALHA'} {nome}")
        if not achou:
            falhas.append(f"exemplo ruim passou: {nome}")

    print("== exemplo estreito que NAO deve reprovar ==")
    total += 1
    bom = {"permissions": {"allow": ["Bash(npm test)", "Bash(git status)"],
                           "deny": ["Read(./.env)"]}}
    achou = problemas_de(bom)
    print(f"  {'ok  ' if not achou else 'FALHA'} allow estreito com deny passa")
    if achou:
        falhas.append(f"exemplo bom reprovou: {achou}")

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
