#!/usr/bin/env python3
"""Lê o estado do projeto e diz qual é o próximo passo.

O problema que isto resolve não é de memória, é de **estado**. Qual passo vem a
seguir é determinado por onde o projeto está — a fila, o git, os artefatos em
disco —, e isso já existe. Decorar a sequência é a forma errada de responder uma
pergunta que o disco responde melhor.

Ser um script, e não prosa numa skill, é deliberado: a recomendação passa a ser
**testável**. Os cenários que importam se montam em diretório temporário, e a
saída de cada um se compara com o esperado. Uma skill que só descrevesse a lógica
não teria como errar em público.

SÓ LÊ. Não escreve, não marca ticket, não commita, não executa o passo que
recomenda. Relata verde ou vermelho; **não garante** nada — garantia é hook.

Uso:
  python3 estado.py [--raiz .]
Saída: relatório em texto. Exit 0 sempre que conseguir ler; 1 se não conseguir.
"""

import argparse
import json
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

# Mesma lição do bug de codificação dos hooks (decisão 011): o console do
# Windows é cp1252, e escrever caractere fora dele derruba o script. Aqui a
# queda seria menos grave — este script só relata —, mas relatório que não
# imprime não relata. Reconfigurar é uma linha; lembrar de evitar acento em
# toda string nova, não é.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

import validar_fila  # noqa: E402

FECHADOS = {"concluido", "descartado"}


def git(raiz, *args):
    try:
        proc = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip()


def ler_fila(raiz):
    caminho = os.path.join(raiz, "tickets", "fila.json")
    if not os.path.isfile(caminho):
        return None, None, caminho
    try:
        fila = validar_fila.carregar(caminho)
    except (OSError, json.JSONDecodeError) as erro:
        return None, [f"fila ilegivel: {erro}"], caminho
    return fila, validar_fila.validar(fila, raiz), caminho


def proximo_liberado(fila):
    """O primeiro ticket pronto cujos bloqueadores todos fecharam.

    Trabalha-se a fronteira: qualquer ticket cujos bloqueadores estejam prontos.
    A ordem do grafo manda, nao a numerica — 005 pode vir antes de 004.
    """
    tickets = fila.get("tickets") or []
    por_id = {t.get("id"): t for t in tickets}
    for t in tickets:
        if t.get("estado") != "pronto":
            continue
        abertos = [
            b for b in t.get("bloqueado_por") or []
            if por_id.get(b, {}).get("estado") not in FECHADOS
        ]
        if not abertos:
            return t
    return None


def bloqueados(fila):
    tickets = fila.get("tickets") or []
    por_id = {t.get("id"): t for t in tickets}
    saida = []
    for t in tickets:
        if t.get("estado") != "pronto":
            continue
        abertos = [
            b for b in t.get("bloqueado_por") or []
            if por_id.get(b, {}).get("estado") not in FECHADOS
        ]
        if abertos:
            saida.append((t, abertos))
    return saida


def verificacao_declarada(raiz):
    caminho = os.path.join(raiz, ".claude", "metodo.json")
    if not os.path.isfile(caminho):
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    comando = ((config.get("verificacao") or {}).get("comando") or "").strip()
    return comando or None


def montar(raiz):
    """Devolve (linhas do relatorio, passo recomendado, rotulo do cenario).

    O rotulo existe para os testes: ele nomeia o cenario detectado, sem
    depender de casar texto de prosa.
    """
    linhas = []
    fila, problemas, caminho_fila = ler_fila(raiz)

    branch = git(raiz, "rev-parse", "--abbrev-ref", "HEAD")
    sujo = git(raiz, "status", "--porcelain", "--untracked-files=no")
    ultimo = git(raiz, "log", "-1", "--format=%h %s")

    linhas.append(f"GIT         {branch or '(sem git)'}"
                  + (f" · {'arvore suja' if sujo else 'arvore limpa'}" if sujo is not None else ""))
    if ultimo:
        linhas.append(f"ULTIMO      {ultimo}")

    comando = verificacao_declarada(raiz)
    linhas.append(f"VERIFICACAO {comando or 'NAO DECLARADA (.claude/metodo.json ausente)'}")

    # --- cenario: sem fila ---
    if fila is None and problemas is None:
        linhas.append(f"FILA        ausente ({caminho_fila})")
        return linhas, (
            "Nao ha fila de tickets. Se o trabalho cabe numa frase, PULE o rito: "
            "escreva a frase, o comando de verificacao, e implemente.\n"
            "Se nao cabe, fatie:  /metodo:fatiar"
        ), "sem-fila"

    # --- cenario: fila invalida (reportar ANTES de recomendar passo) ---
    if problemas:
        linhas.append(f"FILA        INVALIDA — {len(problemas)} problema(s)")
        for p in problemas:
            linhas.append(f"            - {p}")
        return linhas, (
            "Conserte a fila antes de qualquer outra coisa. Um grafo de bloqueio "
            "errado faz o proximo passo ser o errado, e isso nao aparece na leitura.\n"
            f"  python3 plugins/metodo/scripts/validar_fila.py {os.path.join('tickets', 'fila.json')}"
        ), "fila-invalida"

    tickets = fila.get("tickets") or []
    por_estado = {}
    for t in tickets:
        por_estado.setdefault(t.get("estado"), []).append(t)
    resumo = " · ".join(
        f"{len(v)} {k}" for k, v in sorted(por_estado.items())
    ) or "vazia"
    linhas.append(f"FILA        {len(tickets)} ticket(s) — {resumo}")

    andando = por_estado.get("em-andamento") or []

    # --- cenario: ticket em andamento ---
    if andando:
        t = andando[0]
        linhas.append(f"EM CURSO    {t['id']} — {t.get('titulo', '')}")
        return linhas, (
            f"Continue o ticket {t['id']}. O brief esta em {t.get('brief', '(sem brief)')}.\n"
            "Confira cada criterio de aceitacao com evidencia — a saida do comando, "
            "nao a impressao.\n"
            f"Ao fechar:  python3 plugins/metodo/scripts/marcar_ticket.py {t['id']} concluido"
        ), "em-andamento"

    # --- cenario: mudanca pendente sem ticket ---
    if sujo:
        return linhas, (
            "Ha mudanca nao commitada e nenhum ticket em andamento. Revise antes de "
            "commitar:  /metodo:revisar\n"
            "Se a mudanca nao pertence a ticket nenhum, ou ela e pequena o bastante "
            "para dispensar o rito, ou faltou fatiar."
        ), "diff-pendente"

    # --- cenario: proximo ticket ---
    proximo = proximo_liberado(fila)
    presos = bloqueados(fila)
    if presos:
        linhas.append("BLOQUEADOS  " + " · ".join(
            f"{t['id']} por {', '.join(b)}" for t, b in presos))

    if proximo:
        return linhas, (
            f"Pegue o ticket {proximo['id']} — {proximo.get('titulo', '')}\n"
            f"  python3 plugins/metodo/scripts/marcar_ticket.py {proximo['id']} em-andamento\n"
            f"Depois:  /metodo:implementar   (brief: {proximo.get('brief', '(sem brief)')})"
        ), "proximo-ticket"

    if presos:
        return linhas, (
            "Nenhum ticket liberado: todos os prontos estao bloqueados. Isso e um "
            "grafo que se fechou — conclua ou descarte um bloqueador, ou fatie o que "
            "destrava."
        ), "tudo-bloqueado"

    return linhas, (
        "Fila sem trabalho pendente. Se ha mais a fazer, fatie:  /metodo:fatiar\n"
        "Se nao ha, este e um bom momento para escrever o documento de arquitetura "
        "da fase e carimba-lo com o SHA atual."
    ), "fila-vazia"


def main(argv=None):
    p = argparse.ArgumentParser(description="Estado do projeto e proximo passo.")
    p.add_argument("--raiz", default=".")
    p.add_argument("--rotulo", action="store_true",
                   help="imprime so o rotulo do cenario (para testes)")
    args = p.parse_args(argv)

    raiz = os.path.abspath(args.raiz)
    if not os.path.isdir(raiz):
        print(f"diretorio nao encontrado: {raiz}", file=sys.stderr)
        return 1

    linhas, passo, rotulo = montar(raiz)

    if args.rotulo:
        print(rotulo)
        return 0

    print("\n".join(linhas))
    print()
    print("PROXIMO PASSO")
    for linha in passo.splitlines():
        print(f"  {linha}")
    print()
    print("Isto e um relato, nao uma garantia. Garantia e hook.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
