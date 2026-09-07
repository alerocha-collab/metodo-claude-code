#!/usr/bin/env python3
"""Suite do detector de bump esquecido.

`tests/testar_marketplace.py` pega **subir errado** — versão divergente entre a entrada
do marketplace e o `plugin.json`. Esta pega o outro lado: **esquecer de subir**. Uma
sozinha deixa metade do problema em pé.

Balanceada em dois eixos, não um. O óbvio: mudou sem bump **reprova**, mudou com bump
**passa**. O menos óbvio, e o que impede um detector histérico: mexer só em `README.md`,
em `tests/` ou no CI **não** pode exigir bump — se exigisse, todo commit de manutenção
viraria um release, e a disciplina seria abandonada por ser insuportável.

O núcleo é puro de propósito, e é por isso que dá para testar casos que seriam caros de
montar com commits de verdade: plugin novo sem versão anterior, manifesto que sumiu,
dois plugins onde só um mudou.

Rode: python3 tests/testar_bump.py
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))

from verificar_bump import faltou_bump, plugin_de   # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

V1 = {"metodo": "0.1.0", "doutrina": "0.1.0"}


def main():
    falhas, total = [], 0

    print("== a que plugin cada caminho pertence ==")
    casos_caminho = [
        ("plugins/metodo/skills/fatiar/SKILL.md", "metodo"),
        ("plugins/doutrina/referencias/armadilhas.md", "doutrina"),
        ("plugins\\metodo\\hooks\\hooks.json", "metodo"),   # separador do Windows
        ("README.md", None),
        ("tests/testar_bump.py", None),
        (".github/workflows/verificar.yml", None),
        ("plugins", None),                                  # a pasta, sem plugin dentro
        ("docs/plugins/algo.md", None),                     # `plugins` fora da raiz
    ]
    for caminho, esperado in casos_caminho:
        total += 1
        obtido = plugin_de(caminho)
        ok = obtido == esperado
        print(f"  {'ok  ' if ok else 'FALHA'} {caminho!r} -> {obtido!r}")
        if not ok:
            falhas.append(f"{caminho!r} deu {obtido!r}, esperava {esperado!r}")

    print("== casos que DEVEM exigir bump ==")
    exigem = [
        ("uma skill mudou e a versao ficou",
         ["plugins/metodo/skills/fatiar/SKILL.md"], V1, V1),
        ("os dois mudaram e nenhum subiu",
         ["plugins/metodo/x.md", "plugins/doutrina/y.md"], V1, V1),
        ("so um dos dois subiu",
         ["plugins/metodo/x.md", "plugins/doutrina/y.md"], V1,
         {"metodo": "0.2.0", "doutrina": "0.1.0"}),
        ("o manifesto sumiu ou ficou ilegivel",
         ["plugins/metodo/x.md"], V1, {"metodo": None}),
    ]
    for nome, mudados, antes, depois in exigem:
        total += 1
        achou = faltou_bump(mudados, antes, depois)
        print(f"  {'ok  ' if achou else 'FALHA'} {nome}")
        if not achou:
            falhas.append(f"deixou passar sem bump: {nome}")

    # Verifica QUAL plugin foi acusado, nao so que houve acusacao. Um detector que
    # acusa o plugin errado passaria nos testes acima e mandaria a pessoa subir a
    # versao errada.
    total += 1
    achou = faltou_bump(["plugins/metodo/x.md", "plugins/doutrina/y.md"], V1,
                        {"metodo": "0.2.0", "doutrina": "0.1.0"})
    nomes = [n for n, _, _ in achou]
    ok = nomes == ["doutrina"]
    print(f"  {'ok  ' if ok else 'FALHA'} acusa o plugin certo, e so ele ({nomes})")
    if not ok:
        falhas.append(f"acusou {nomes}, esperava ['doutrina']")

    print("== casos que NAO devem exigir bump ==")
    nao_exigem = [
        ("mudou e subiu",
         ["plugins/metodo/skills/fatiar/SKILL.md"], V1, {"metodo": "0.2.0"}),
        ("so o README da raiz",
         ["README.md"], V1, V1),
        ("so as suites e o CI",
         ["tests/testar_bump.py", ".github/workflows/verificar.yml"], V1, V1),
        ("so os tickets e as decisoes",
         ["tickets/fila.json", "DECISIONS.md"], V1, V1),
        ("nada mudou",
         [], V1, V1),
        ("plugin NOVO, sem versao anterior",
         ["plugins/terceiro/skills/z/SKILL.md"], {}, {"terceiro": "0.1.0"}),
        ("o outro plugin mudou; este ficou parado e nao e cobrado",
         ["plugins/doutrina/y.md"], V1, {"doutrina": "0.2.0", "metodo": "0.1.0"}),
    ]
    for nome, mudados, antes, depois in nao_exigem:
        total += 1
        achou = faltou_bump(mudados, antes, depois)
        print(f"  {'ok  ' if not achou else 'FALHA'} {nome}")
        if achou:
            falhas.append(f"exigiu bump sem precisar: {nome} -> {achou}")

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
