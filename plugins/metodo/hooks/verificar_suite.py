#!/usr/bin/env python3
"""Portão de verificação do papel `construtor` — hook Stop, fail-closed.

Bloqueia o fim do turno enquanto a verificação declarada pelo projeto não passar.

FAIL-CLOSED é o ponto inteiro deste arquivo, e ele tem duas metades:

  1. Verificação ausente conta como FALHA, nunca como "nada a verificar". Sem
     isso, um projeto sem `.claude/metodo.json` teria um portão que aprova tudo
     — o buraco do "passou porque não rodou".

  2. Qualquer erro inesperado deste script conta como FALHA. Isso não é
     paranoia: a doc é explícita que exit code 1 NÃO bloqueia — Claude Code o
     trata como erro não bloqueante e prossegue com a ação. Um traceback não
     tratado aqui abriria o portão em silêncio. Por isso tudo está sob
     try/except e todo caminho de erro sai com 2.

Contrato de saída, conforme a doc: "use exit 2 to block with a stderr message,
or exit 0 with JSON for structured control. Choose one approach per hook."
Este hook usa exit 2 + stderr, que é o mais simples de acertar.
"""

import json
import os
import subprocess
import sys

CONFIG = os.path.join(".claude", "metodo.json")
LIMITE_SAIDA = 60  # linhas da cauda que entram na mensagem de bloqueio


def bloquear(mensagem):
    """Impede o fim do turno. A mensagem vira feedback para o modelo."""
    print(mensagem, file=sys.stderr)
    sys.exit(2)


def liberar():
    sys.exit(0)


def main():
    bruto = sys.stdin.read()
    try:
        evento = json.loads(bruto) if bruto.strip() else {}
    except json.JSONDecodeError:
        evento = {}

    # O Claude Code sobrescreve um Stop hook depois de oito bloqueios seguidos
    # sem progresso. Sair cedo quando já bloqueamos evita gastar esse teto e
    # devolve a decisão ao humano, que é o lugar certo dela.
    if evento.get("stop_hook_active") is True:
        liberar()

    raiz = evento.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    caminho = os.path.join(raiz, CONFIG)

    if not os.path.isfile(caminho):
        bloquear(
            "PORTAO DE VERIFICACAO: nao ha verificacao declarada neste projeto.\n"
            f"Esperava {CONFIG} na raiz do repositorio.\n\n"
            "Ausencia de verificacao conta como falha, nao como aprovacao. Um\n"
            "portao que aprova o que nao consegue verificar nao e um portao.\n\n"
            "Copie o template do plugin (templates/metodo.json), declare o comando\n"
            "que decide verde/vermelho, e prove-o contra um caso negativo: quebre\n"
            "algo de proposito e confirme que o comando sai com codigo != 0. Um\n"
            "verificador nunca testado contra o vermelho e uma esperanca, nao um\n"
            "verificador."
        )

    try:
        with open(caminho, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError) as erro:
        bloquear(
            f"PORTAO DE VERIFICACAO: {CONFIG} nao pode ser lido: {erro}\n"
            "Config ilegivel conta como falha. Corrija o arquivo."
        )

    verificacao = config.get("verificacao") or {}
    comando = (verificacao.get("comando") or "").strip()

    if not comando or comando == "SUBSTITUA-ME":
        bloquear(
            f"PORTAO DE VERIFICACAO: {CONFIG} existe mas nao declara um comando.\n"
            "Preencha verificacao.comando com o comando que decide verde/vermelho\n"
            "e cujo exit code seja confiavel."
        )

    timeout = verificacao.get("timeout_segundos", 600)
    descricao = verificacao.get("descricao") or comando

    try:
        proc = subprocess.run(
            comando,
            shell=True,
            cwd=raiz,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        bloquear(
            f"PORTAO DE VERIFICACAO: '{descricao}' estourou {timeout}s e foi morta.\n"
            "Suite que nao termina nao e suite que passa. Ou o comando travou, ou\n"
            "o timeout em verificacao.timeout_segundos esta baixo demais."
        )
    except OSError as erro:
        bloquear(
            f"PORTAO DE VERIFICACAO: nao consegui executar '{comando}': {erro}"
        )

    if proc.returncode == 0:
        liberar()

    saida = ((proc.stdout or "") + (proc.stderr or "")).rstrip().splitlines()
    cauda = "\n".join(saida[-LIMITE_SAIDA:]) if saida else "(sem saida)"

    bloquear(
        f"PORTAO DE VERIFICACAO: '{descricao}' falhou (exit {proc.returncode}).\n"
        f"Comando: {comando}\n\n"
        f"Ultimas {LIMITE_SAIDA} linhas:\n{cauda}\n\n"
        "Conserte o codigo. NAO edite nem apague testes para ficar verde — um\n"
        "teste apagado e funcionalidade perdida em silencio. Se o teste e que\n"
        "esta errado, isso e conversa com o humano, nao edicao sua."
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as erro:  # noqa: BLE001 — fail-closed é o requisito
        # Sem este bloco, um erro inesperado sairia com 1 — que NAO bloqueia —
        # e o portao aprovaria por acidente. Ver docstring.
        print(
            f"PORTAO DE VERIFICACAO: erro inesperado no proprio hook: {erro!r}\n"
            "Bloqueando por precaucao: um portao que falha aberto nao e portao.",
            file=sys.stderr,
        )
        sys.exit(2)
