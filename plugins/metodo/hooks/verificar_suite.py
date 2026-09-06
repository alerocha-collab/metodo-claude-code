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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comum  # noqa: E402

CONFIG = comum.CONFIG
LIMITE_SAIDA = 60  # linhas da cauda que entram na mensagem de bloqueio



# O Claude Code manda UTF-8 no stdin, mas o Python do Windows decodifica com a
# codificacao do console (cp1252). Qualquer caractere fora dela — as tabelas e
# setas que um agente imprime estao cheias deles — derruba `sys.stdin.read()`.
# Ler bytes e decodificar explicitamente elimina a dependencia do locale.
def ler_stdin():
    try:
        return sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except (AttributeError, ValueError):
        return sys.stdin.read()


# Pelo mesmo motivo, escrever a mensagem de bloqueio em stderr falha quando ela
# tem caractere fora do cp1252. Sem isto, o hook cai ao tentar explicar por que
# bloqueou.
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

def bloquear(mensagem):
    """Impede o fim do turno. A mensagem vira feedback para o modelo."""
    print(mensagem, file=sys.stderr)
    sys.exit(2)


def liberar():
    sys.exit(0)


def diagnosticar(evento):
    """Registra o que o hook recebeu, quando METODO_DIAGNOSTICO=1.

    A doc nao diz quais campos chegam numa sessao `--agent` de plugin, e a
    clausula de guarda abaixo foi desenhada justamente para nao depender disso.
    Este dump existe para responder a pergunta empiricamente, sem custar outra
    rodada de teste manual: rode o roteiro com a variavel ligada e olhe o
    arquivo. Fica desligado por padrao para nao criar arquivo de surpresa no
    repositorio de ninguem.
    """
    if os.environ.get("METODO_DIAGNOSTICO") != "1":
        return
    try:
        destino = os.path.join(".claude", "metodo-diagnostico.json")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "campos_recebidos": sorted(evento.keys()),
                    "evento": evento,
                    "variaveis_claude": {
                        k: v for k, v in os.environ.items()
                        if k.startswith("CLAUDE_")
                    },
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
    except OSError:
        pass  # diagnostico nunca deve atrapalhar o portao


def sessao_mudou_codigo(raiz):
    """A arvore de trabalho tem mudanca nao commitada?

    **Esta e a clausula de guarda**, e ela nao pergunta "qual e o meu papel" —
    pergunta "ha algo a verificar". A troca e deliberada:

    Hooks de plugin disparam em toda sessao, em todo papel. Barrar uma sessao do
    papel `operador` porque a suite esta vermelha seria regra de construcao
    barrando operacao — o inverso exato do sintoma que motivou separar papeis. E
    descobrir o papel pelo stdin nao e possivel: a doc nao cobre quais campos
    chegam.

    Mas o papel nunca foi a pergunta certa. O portao existe para impedir que uma
    MUDANCA quebrada seja dada por pronta. Arvore limpa significa que esta sessao
    nao produziu mudanca nenhuma — nao ha o que verificar, e verificar assim
    mesmo so faria o operador pagar por vermelho que nao foi ele quem criou.

    "Verifique o que voce mudou" e regra melhor que "verifique por causa de quem
    voce e": nao depende de campo indocumentado, e vale igual para papeis que
    ainda nao existem.

    Na duvida — git ausente, comando falhando, repositorio nao versionado —
    devolve True. Fail-closed: nao conseguir olhar nao e licenca para liberar.
    """
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=raiz,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return True
    if proc.returncode != 0:
        return True
    return bool((proc.stdout or "").strip())


def main():
    bruto = ler_stdin()
    try:
        evento = json.loads(bruto) if bruto.strip() else {}
    except json.JSONDecodeError:
        evento = {}

    # O Claude Code sobrescreve um Stop hook depois de oito bloqueios seguidos
    # sem progresso. Sair cedo quando já bloqueamos evita gastar esse teto e
    # devolve a decisão ao humano, que é o lugar certo dela.
    if evento.get("stop_hook_active") is True:
        liberar()

    diagnosticar(evento)

    raiz = evento.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

    # Clausula de guarda: nada mudou, nada a verificar. Ver docstring.
    if not sessao_mudou_codigo(raiz):
        liberar()

    # Sobe ate a raiz do repositorio. Configuracao de projeto nao e herdada de
    # diretorio pai, e a doc recomenda iniciar a sessao DENTRO do pacote num
    # monorepo — entao olhar so o `cwd` bloqueia todo turno la, dizendo que nao ha
    # verificacao declarada. Medido em arvore de teste antes de existir esta busca.
    caminho = comum.achar_config(raiz)

    if not caminho:
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

    # O comando declarado e relativo a ONDE A CONFIG MORA, nao a onde a sessao
    # comecou. Num monorepo, `python3 tests/testar_tudo.py` escrito na raiz nao
    # resolve a partir de `packages/api/`.
    raiz_config = os.path.dirname(os.path.dirname(caminho))

    try:
        proc = subprocess.run(
            comando,
            shell=True,
            cwd=raiz_config,
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
