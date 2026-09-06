#!/usr/bin/env python3
"""Roda todas as suites do repositorio. FAIL-CLOSED.

Descobre `tests/testar_*.py` (menos este) e roda cada uma. A propriedade que
importa: **nenhuma suite encontrada e FALHA, nao sucesso.** Sem isso, apagar os
testes deixa o runner verde, e o portao de verificacao passa a aprovar um
repositorio sem verificacao nenhuma — o buraco do "passou porque nao rodou".

E o mesmo motivo pelo qual o hook `proteger_testes.py` existe: um agente medido
por verde tem incentivo para reduzir o que e medido.

Rode: python3 tests/testar_tudo.py
"""

import glob
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ESTE = os.path.basename(__file__)


def main():
    suites = sorted(
        s for s in glob.glob(os.path.join(AQUI, "testar_*.py"))
        if os.path.basename(s) != ESTE
    )

    if not suites:
        print(
            "FALHA: nenhuma suite encontrada em tests/testar_*.py\n"
            "Ausencia de teste conta como falha, nunca como aprovacao. Um runner\n"
            "que fica verde quando nao ha o que rodar mede a propria ausencia.",
            file=sys.stderr,
        )
        return 1

    vermelhas = []
    for suite in suites:
        nome = os.path.basename(suite)
        print(f"\n=== {nome} ===")
        proc = subprocess.run([sys.executable, suite], cwd=RAIZ)
        if proc.returncode != 0:
            vermelhas.append(nome)

    print()
    if vermelhas:
        print(f"VERMELHO: {len(vermelhas)} de {len(suites)} suite(s) falharam: "
              f"{', '.join(vermelhas)}", file=sys.stderr)
        return 1
    print(f"VERDE: {len(suites)} suite(s), todas passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
