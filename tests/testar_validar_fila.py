#!/usr/bin/env python3
"""Suite do validador de fila de tickets.

Balanceada, como a dos hooks: casos que DEVEM reprovar e casos que NAO devem.
Um validador so testado contra filas quebradas passa reprovando tudo.

Rode: python3 tests/testar_validar_fila.py
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plugins", "metodo", "scripts"))

import validar_fila  # noqa: E402


def t(tid, estado="pronto", bloqueado_por=None, titulo="titulo"):
    return {
        "id": tid,
        "titulo": titulo,
        "estado": estado,
        "bloqueado_por": bloqueado_por or [],
    }


# (nome, fila, deve_reprovar, trecho esperado na mensagem ou None)
CASOS = [
    # --- DEVE reprovar ---
    ("id repetido",
     {"tickets": [t("001"), t("001")]}, True, "id repetido"),
    ("bloqueador inexistente",
     {"tickets": [t("001", bloqueado_por=["999"])]}, True, "inexistente"),
    ("ticket bloqueado por si mesmo",
     {"tickets": [t("001", bloqueado_por=["001"])]}, True, "por si mesmo"),
    ("ciclo de dois",
     {"tickets": [t("001", bloqueado_por=["002"]), t("002", bloqueado_por=["001"])]},
     True, "ciclo"),
    ("ciclo de tres",
     {"tickets": [t("001", bloqueado_por=["002"]), t("002", bloqueado_por=["003"]),
                  t("003", bloqueado_por=["001"])]}, True, "ciclo"),
    ("estado invalido",
     {"tickets": [t("001", estado="quase")]}, True, "invalido"),
    ("sem titulo",
     {"tickets": [{"id": "001", "estado": "pronto"}]}, True, "titulo"),
    ("concluido com bloqueador aberto",
     {"tickets": [t("001", estado="concluido", bloqueado_por=["002"]),
                  t("002", estado="pronto")]}, True, "bloqueador"),
    ("dois em andamento",
     {"tickets": [t("001", estado="em-andamento"), t("002", estado="em-andamento")]},
     True, "um ticket por sessao"),
    ("brief inexistente",
     {"tickets": [dict(t("001"), brief="tickets/nao-existe.md")]}, True, "brief"),
    ("fila sem lista tickets",
     {"outra_coisa": []}, True, "lista"),
    # --- NAO deve reprovar ---
    ("fila vazia",
     {"tickets": []}, False, None),
    ("cadeia linear valida",
     {"tickets": [t("001", estado="concluido"),
                  t("002", estado="em-andamento", bloqueado_por=["001"]),
                  t("003", bloqueado_por=["002"])]}, False, None),
    ("um so em andamento",
     {"tickets": [t("001", estado="em-andamento"), t("002"), t("003")]}, False, None),
    ("losango sem ciclo",
     {"tickets": [t("001"), t("002", bloqueado_por=["001"]),
                  t("003", bloqueado_por=["001"]),
                  t("004", bloqueado_por=["002", "003"])]}, False, None),
    ("concluido apos bloqueador descartado",
     {"tickets": [t("001", estado="descartado"),
                  t("002", estado="concluido", bloqueado_por=["001"])]}, False, None),
]


def main():
    falhas = []
    for nome, fila, deve_reprovar, trecho in CASOS:
        problemas = validar_fila.validar(fila, RAIZ)
        reprovou = bool(problemas)
        ok = reprovou == deve_reprovar
        if ok and trecho:
            ok = any(trecho in p for p in problemas)
        print(f"  {'ok  ' if ok else 'FALHA'} {nome}"
              f" ({len(problemas)} problema(s))")
        if not ok:
            esperado = "reprovar" if deve_reprovar else "aprovar"
            falhas.append(f"{nome}: esperava {esperado}, veio {problemas}")

    print()
    if falhas:
        print(f"{len(falhas)} de {len(CASOS)} FALHARAM:")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print(f"{len(CASOS)} casos, todos passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
