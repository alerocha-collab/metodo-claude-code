#!/usr/bin/env python3
"""O que os dois hooks compartilham: achar a configuração do projeto.

Existe porque a pergunta "onde este projeto declara a metodologia?" tem uma resposta
só, e ela não é óbvia: **configuração de projeto não é herdada de diretório pai.**

Ao contrário do `CLAUDE.md`, que carrega em camadas, o `.claude/settings.json` vale
apenas a partir do diretório onde a sessão começou. E a doc recomenda iniciar a sessão
**de dentro do pacote** quando o trabalho é escopado a ele — que é o caso normal num
monorepo.

Consequência que medimos: um portão que procura a config só no `cwd` bloqueia todo
turno numa sessão iniciada dentro de um pacote, dizendo que não há verificação
declarada. Fail-closed funcionando contra o trabalho correto.

A busca sobe até a **raiz do repositório** e para lá. Não segue subindo pelo sistema
de arquivos: fora do repositório, qualquer arquivo que se ache pertence a outro
projeto.
"""

import os

CONFIG = os.path.join(".claude", "metodo.json")


def raiz_do_repositorio(inicio):
    """A pasta que contém `.git`, subindo a partir de `inicio`. None se não houver.

    `.git` pode ser diretório (checkout normal) ou arquivo (worktree vinculado), e os
    dois contam.
    """
    atual = os.path.realpath(inicio)
    while True:
        if os.path.exists(os.path.join(atual, ".git")):
            return atual
        pai = os.path.dirname(atual)
        if pai == atual:
            return None
        atual = pai


def achar_config(inicio):
    """O `.claude/metodo.json` mais próximo, subindo até a raiz do repositório.

    Devolve o caminho absoluto, ou None. Procura no proprio `inicio` primeiro — a
    config do pacote vence a da raiz, que e a precedencia que a pessoa espera.

    Quando nao ha repositorio git, olha so o diretorio de partida: sem raiz conhecida,
    subir seria adivinhar ate onde.
    """
    if not inicio:
        return None
    try:
        atual = os.path.realpath(inicio)
    except (OSError, ValueError):
        return None
    if not os.path.isdir(atual):
        atual = os.path.dirname(atual)

    raiz = raiz_do_repositorio(atual)

    while True:
        candidato = os.path.join(atual, CONFIG)
        if os.path.isfile(candidato):
            return candidato
        if raiz is None or atual == raiz:
            return None
        pai = os.path.dirname(atual)
        if pai == atual:
            return None
        atual = pai


def aderiu(inicio):
    """O projeto que contém `inicio` declarou que usa a metodologia?

    É o que distingue "instalado" de "adotado". Um plugin instalado não deve mudar o
    comportamento de repositório que não pediu por isso — a pessoa desinstala em vez de
    configurar, e aí perde também o que era útil.
    """
    return achar_config(inicio) is not None
