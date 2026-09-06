#!/usr/bin/env python3
"""Muda o estado de um ticket na fila, recusando transicao ilegal.

Existe para que as regras da fila sejam **verificadas**, e nao pedidas. Duas
delas importam o bastante para virar codigo:

  - **Um ticket em andamento por vez.** E a decisao no 1: sessao = um ticket. Um
    agente com dois tickets abertos nao esta fatiando, esta multitarefando, e o
    handoff volta a doer.
  - **Nao se conclui ticket com bloqueador aberto.** E o erro mais caro da fila,
    porque quando aparece ja aconteceu: trabalho feito fora de ordem.

Escrever JSON pelo modelo funciona, mas pedir cuidado e mais fraco que recusar a
transicao. O script tambem revalida a fila inteira antes de gravar: se a mudanca
deixaria a fila invalida, nada e escrito.

Uso:
  python3 marcar_ticket.py <id> <estado> [--fila tickets/fila.json]
"""

import argparse
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import validar_fila  # noqa: E402

FECHADOS = {"concluido", "descartado"}


def transicao_ilegal(fila, tid, novo):
    """Devolve o motivo da recusa, ou None se a transicao e legal."""
    tickets = fila.get("tickets") or []
    por_id = {t.get("id"): t for t in tickets}

    if tid not in por_id:
        return f"ticket {tid} nao existe na fila"
    if novo not in validar_fila.ESTADOS:
        return f"estado {novo!r} invalido (use um de {sorted(validar_fila.ESTADOS)})"

    alvo = por_id[tid]
    atual = alvo.get("estado")

    if novo == "em-andamento":
        outros = [
            t["id"] for t in tickets
            if t.get("estado") == "em-andamento" and t.get("id") != tid
        ]
        if outros:
            return (
                f"{', '.join(outros)} ja esta em andamento. A unidade de trabalho e "
                "um ticket por sessao: conclua, descarte ou devolva o outro a `pronto` "
                "antes de comecar este."
            )
        abertos = [
            b for b in alvo.get("bloqueado_por") or []
            if por_id.get(b, {}).get("estado") not in FECHADOS
        ]
        if abertos:
            return (
                f"{tid} esta bloqueado por {', '.join(abertos)}, que ainda nao "
                "fecharam. Trabalhe a fronteira: pegue um ticket cujos bloqueadores "
                "estejam prontos."
            )

    if novo == "concluido":
        if atual != "em-andamento":
            return (
                f"{tid} esta {atual!r}; so se conclui o que esteve em andamento. "
                "Marcar concluido direto pula a fatia inteira."
            )
        abertos = [
            b for b in alvo.get("bloqueado_por") or []
            if por_id.get(b, {}).get("estado") not in FECHADOS
        ]
        if abertos:
            return f"{tid}: bloqueador {', '.join(abertos)} ainda aberto"

    return None


def aplicar(fila, tid, novo):
    for t in fila.get("tickets") or []:
        if t.get("id") == tid:
            t["estado"] = novo
            return


def main(argv=None):
    p = argparse.ArgumentParser(description="Muda o estado de um ticket na fila.")
    p.add_argument("id")
    p.add_argument("estado")
    p.add_argument("--fila", default=os.path.join("tickets", "fila.json"))
    args = p.parse_args(argv)

    if not os.path.isfile(args.fila):
        print(f"fila nao encontrada: {args.fila}", file=sys.stderr)
        return 1

    try:
        fila = validar_fila.carregar(args.fila)
    except json.JSONDecodeError as erro:
        print(f"{args.fila} nao e JSON valido: {erro}", file=sys.stderr)
        return 1

    motivo = transicao_ilegal(fila, args.id, args.estado)
    if motivo:
        print(f"RECUSADO: {motivo}", file=sys.stderr)
        return 1

    aplicar(fila, args.id, args.estado)

    # A fila resultante tem que continuar valida. Detectar depois de gravar seria
    # detectar tarde.
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(args.fila)))
    problemas = validar_fila.validar(fila, raiz)
    if problemas:
        print("RECUSADO: a mudanca deixaria a fila invalida:", file=sys.stderr)
        for p_ in problemas:
            print(f"  - {p_}", file=sys.stderr)
        return 1

    with io.open(args.fila, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(fila, ensure_ascii=False, indent=2) + "\n")

    print(f"{args.id} -> {args.estado}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
