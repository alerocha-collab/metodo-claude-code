#!/usr/bin/env python3
"""Impede que testes sejam editados ou apagados — hook PreToolUse.

Por que um hook e nao uma linha no CLAUDE.md: um agente medido por "suite verde"
tem um caminho trivial de trapaca, que e apagar o teste que incomoda. O incentivo
e estrutural, nao e desatencao — e instrucao em prompt nao segura incentivo. A
doutrina e explicita: "e inaceitavel remover ou editar testes, porque isso pode
levar a funcionalidade faltante ou com bug".

Este hook NAO bloqueia criar teste novo, nem editar arquivo que ainda nao existe
em disco. So barra alteracao e remocao do que ja esta la.

A regra vive na mensagem de negacao, nao no CLAUDE.md: o modelo recebe o motivo e
continua trabalhando a partir dele, entao a regra e ensinada no instante em que e
relevante, a custo de contexto zero nos turnos em que nao se aplica.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comum  # noqa: E402

# Convencoes de nome de teste dos ecossistemas mais comuns. Deliberadamente
# conservador: falso negativo aqui custa menos que falso positivo, porque falso
# positivo em hook nao se negocia.
PADROES = [
    r"(^|/)tests?/",
    r"(^|/)__tests__/",
    r"(^|/)spec/",
    r"(^|/)test_[^/]+\.py$",
    r"[^/]+_test\.(py|go|rb)$",
    r"[^/]+\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs)$",
    r"[^/]+Test\.(java|kt|cs)$",
    r"(^|/)conftest\.py$",
]

FERRAMENTAS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}



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

def e_teste(caminho):
    normalizado = caminho.replace("\\", "/")
    return any(re.search(p, normalizado) for p in PADROES)


def negar(motivo):
    print(motivo, file=sys.stderr)
    sys.exit(2)


def main():
    bruto = ler_stdin()
    try:
        evento = json.loads(bruto) if bruto.strip() else {}
    except json.JSONDecodeError:
        # Entrada ilegivel: nao ha o que julgar. Sair 0 aqui e liberar, e e o
        # certo — este hook e uma trava especifica, nao um portao geral. Travar
        # tudo por nao entender a entrada seria falso positivo garantido.
        sys.exit(0)

    if evento.get("tool_name") not in FERRAMENTAS:
        sys.exit(0)

    entrada = evento.get("tool_input") or {}
    caminho = entrada.get("file_path") or entrada.get("notebook_path") or ""
    if not caminho or not e_teste(caminho):
        sys.exit(0)

    # CLAUSULA DE ADESAO. Hooks de plugin disparam em toda sessao que carrega o
    # plugin, e se fundem em vez de se sobrescrever — nao ha como desliga-los por
    # escopo. Sem esta guarda, instalar o `metodo` impediria editar teste existente
    # em QUALQUER repositorio, tenha ele adotado a metodologia ou nao.
    #
    # Um plugin instalado nao deve mudar o comportamento de projeto que nao pediu por
    # isso: a pessoa desinstala em vez de configurar, e ai perde tambem o que era util.
    #
    # A adesao e procurada a partir do caminho DO ARQUIVO, nao do diretorio da sessao:
    # num monorepo os dois divergem, e quem manda e onde o arquivo mora.
    if not comum.aderiu(os.path.dirname(caminho)):
        sys.exit(0)

    # Escrever teste NOVO e o trabalho, e nao pode ser barrado. Mas so `Write`
    # cria arquivo — `Edit` e as variantes exigem que ele ja exista. Entao para
    # elas nem consultamos o disco: bloqueiam sempre.
    #
    # A distincao importa porque `os.path.exists` pode falhar por motivo bobo
    # (caminho num formato que este Python nao resolve, permissao) e "nao
    # consegui olhar, entao libero" e fail-open numa trava. Restringir a
    # consulta ao unico caso que precisa dela reduz essa superficie ao minimo.
    if evento.get("tool_name") == "Write" and not os.path.exists(caminho):
        sys.exit(0)

    negar(
        f"BLOQUEADO: {caminho} e um arquivo de teste que ja existe.\n\n"
        "Testes nao se editam nem se apagam para a suite ficar verde. Se o teste\n"
        "falha, ou o codigo esta errado — conserte o codigo — ou o teste esta\n"
        "errado, e isso e conversa com o humano, nao edicao sua.\n\n"
        "Se a mudanca de comportamento e legitima e o teste precisa mesmo mudar,\n"
        "diga qual teste, o que ele afirma hoje, o que deveria afirmar, e por que.\n"
        "Quem decide isso nao e quem esta sendo medido por ele."
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except BaseException as erro:  # noqa: BLE001
        # Aqui, ao contrario do portao de verificacao, erro inesperado LIBERA.
        # Este hook e uma trava estreita; um bug nele nao deve travar o trabalho
        # inteiro. O portao que protege a corretude e o outro.
        print(f"proteger_testes: erro ignorado: {erro!r}", file=sys.stderr)
        sys.exit(0)
