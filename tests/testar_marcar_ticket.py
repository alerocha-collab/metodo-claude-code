#!/usr/bin/env python3
"""Suite do `marcar_ticket.py`.

Balanceada: casos que DEVEM ser recusados e casos que NAO devem. Um guardiao so
testado contra transicoes ilegais passa recusando tudo.

Rode: python3 tests/testar_marcar_ticket.py
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plugins", "metodo", "scripts"))

import marcar_ticket  # noqa: E402


def t(tid, estado="pronto", bloqueado_por=None):
    return {
        "id": tid,
        "titulo": f"ticket {tid}",
        "estado": estado,
        "bloqueado_por": bloqueado_por or [],
    }


# (nome, fila, id, novo estado, deve_recusar, trecho esperado)
CASOS = [
    # --- DEVE recusar ---
    ("comecar com outro em andamento",
     {"tickets": [t("001", "em-andamento"), t("002")]}, "002", "em-andamento",
     True, "um ticket por sessao"),
    ("comecar com bloqueador aberto",
     {"tickets": [t("001"), t("002", bloqueado_por=["001"])]}, "002", "em-andamento",
     True, "bloqueado por"),
    ("concluir sem ter estado em andamento",
     {"tickets": [t("001")]}, "001", "concluido",
     True, "so se conclui o que esteve em andamento"),
    ("concluir com bloqueador aberto",
     {"tickets": [t("001"), t("002", "em-andamento", ["001"])]}, "002", "concluido",
     True, "bloqueador"),
    ("ticket inexistente",
     {"tickets": [t("001")]}, "999", "em-andamento", True, "nao existe"),
    ("estado invalido",
     {"tickets": [t("001")]}, "001", "quase-la", True, "invalido"),
    # --- NAO deve recusar ---
    ("comecar o unico ticket pronto",
     {"tickets": [t("001")]}, "001", "em-andamento", False, None),
    ("comecar com bloqueador concluido",
     {"tickets": [t("001", "concluido"), t("002", bloqueado_por=["001"])]},
     "002", "em-andamento", False, None),
    ("comecar com bloqueador descartado",
     {"tickets": [t("001", "descartado"), t("002", bloqueado_por=["001"])]},
     "002", "em-andamento", False, None),
    ("concluir o que estava em andamento",
     {"tickets": [t("001", "em-andamento")]}, "001", "concluido", False, None),
    ("devolver a pronto",
     {"tickets": [t("001", "em-andamento")]}, "001", "pronto", False, None),
    ("descartar a qualquer momento",
     {"tickets": [t("001")]}, "001", "descartado", False, None),
    ("re-marcar em andamento o que ja esta",
     {"tickets": [t("001", "em-andamento")]}, "001", "em-andamento", False, None),
]


def main():
    falhas = []
    for nome, fila, tid, novo, deve_recusar, trecho in CASOS:
        motivo = marcar_ticket.transicao_ilegal(fila, tid, novo)
        recusou = motivo is not None
        ok = recusou == deve_recusar
        if ok and trecho:
            ok = trecho in (motivo or "")
        print(f"  {'ok  ' if ok else 'FALHA'} {nome}")
        if not ok:
            esperado = "recusar" if deve_recusar else "aceitar"
            falhas.append(f"{nome}: esperava {esperado}, motivo={motivo!r}")

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
