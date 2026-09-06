#!/usr/bin/env python3
"""Valida a fila de tickets — `tickets/fila.json`.

Por que validar em vez de confiar na redacao: o valor da fila esta no **grafo de
bloqueio**, e um grafo errado falha em silencio. Um ciclo faz o `/fluxo` nunca
achar proximo ticket; uma aresta apontando para id inexistente faz um ticket
parecer liberado quando nao esta. Nenhum dos dois aparece na leitura.

Este script DETECTA. Nunca corrige. Fila desatualizada e sinal para decisao
humana, nao coisa a curar sozinha.

Rode: python3 plugins/metodo/scripts/validar_fila.py [caminho da fila]
Saida: exit 0 se valida, 1 com a lista de problemas se nao.
"""

import json
import os
import sys

ESTADOS = {"pronto", "em-andamento", "concluido", "descartado"}
PADRAO = os.path.join("tickets", "fila.json")


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def validar(fila, raiz):
    """Devolve a lista de problemas. Vazia significa fila valida."""
    problemas = []
    tickets = fila.get("tickets")

    if not isinstance(tickets, list):
        return ["a fila precisa de uma lista `tickets`"]

    ids = [t.get("id") for t in tickets]
    vistos = set()
    duplicados = set()
    for i in ids:
        if i in vistos:
            duplicados.add(i)
        vistos.add(i)
    for i in sorted(d for d in duplicados if d is not None):
        problemas.append(f"id repetido: {i}")

    por_id = {t.get("id"): t for t in tickets}

    for t in tickets:
        tid = t.get("id")
        if not tid:
            problemas.append("ticket sem `id`")
            continue
        if not t.get("titulo"):
            problemas.append(f"{tid}: sem `titulo`")

        estado = t.get("estado")
        if estado not in ESTADOS:
            problemas.append(
                f"{tid}: estado {estado!r} invalido (use um de {sorted(ESTADOS)})"
            )

        brief = t.get("brief")
        if brief and not os.path.isfile(os.path.join(raiz, brief)):
            problemas.append(f"{tid}: brief nao encontrado: {brief}")

        bloqueadores = t.get("bloqueado_por") or []
        if not isinstance(bloqueadores, list):
            problemas.append(f"{tid}: `bloqueado_por` precisa ser lista")
            continue
        for b in bloqueadores:
            if b == tid:
                problemas.append(f"{tid}: bloqueado por si mesmo")
            elif b not in por_id:
                problemas.append(f"{tid}: bloqueado por id inexistente: {b}")

    # Um ticket concluido cujo bloqueador nao esta concluido significa que a ordem
    # foi furada. E o erro mais caro da fila, porque ja aconteceu.
    for t in tickets:
        if t.get("estado") != "concluido":
            continue
        for b in t.get("bloqueado_por") or []:
            bloqueador = por_id.get(b)
            if bloqueador and bloqueador.get("estado") not in {"concluido", "descartado"}:
                problemas.append(
                    f"{t['id']}: concluido, mas o bloqueador {b} esta "
                    f"{bloqueador.get('estado')!r}"
                )

    # Decisao no 1: sessao = um ticket. Dois em andamento significa que a fatia
    # deixou de ser a unidade de trabalho.
    andando = [t.get("id") for t in tickets if t.get("estado") == "em-andamento"]
    if len(andando) > 1:
        problemas.append(
            f"{len(andando)} tickets em andamento ({', '.join(map(str, andando))}); "
            "a unidade de trabalho e um ticket por sessao"
        )

    problemas.extend(ciclos(por_id))
    return problemas


def ciclos(por_id):
    """Detecta ciclos no grafo de bloqueio por busca em profundidade."""
    ENTRANDO, PRONTO = 1, 2
    marca = {}
    achados = []

    def visitar(no, caminho):
        marca[no] = ENTRANDO
        for prox in por_id.get(no, {}).get("bloqueado_por") or []:
            if prox not in por_id:
                continue  # aresta pendurada; ja reportada em outro lugar
            if marca.get(prox) == ENTRANDO:
                inicio = caminho.index(prox)
                achados.append(" -> ".join(map(str, caminho[inicio:] + [prox])))
            elif prox not in marca:
                visitar(prox, caminho + [prox])
        marca[no] = PRONTO

    for no in por_id:
        if no not in marca:
            visitar(no, [no])

    return [f"ciclo de bloqueio: {c}" for c in sorted(set(achados))]


def main(argv):
    caminho = argv[1] if len(argv) > 1 else PADRAO
    if not os.path.isfile(caminho):
        print(f"fila nao encontrada: {caminho}", file=sys.stderr)
        return 1

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(caminho)))
    try:
        fila = carregar(caminho)
    except json.JSONDecodeError as erro:
        print(f"{caminho} nao e JSON valido: {erro}", file=sys.stderr)
        return 1

    problemas = validar(fila, raiz)
    if problemas:
        print(f"{len(problemas)} problema(s) em {caminho}:", file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
        return 1

    total = len(fila.get("tickets", []))
    print(f"fila valida: {total} ticket(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
