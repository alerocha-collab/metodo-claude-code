---
name: decidir
description: Fecha as decisões que ainda estão em aberto antes de construir — entrevistando em rodadas, uma fronteira por vez, com resposta recomendada em cada pergunta. Use quando houver mais de um caminho razoável, quando o critério de pronto não couber numa frase, ou quando o trabalho for para uma fila sem supervisão.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Task, AskUserQuestion
---

# Fechar o que está em aberto

Você entrevista até chegar a entendimento compartilhado. Não implementa, não fatia,
não escreve spec — fecha decisões, e para.

## Primeiro: isto precisa de entrevista?

**Entrevistar não é regra, é gatilho.** Três rodadas de perguntas para algo que cabia
em duas frases é atrito puro, e atrito ensina a pular a etapa da próxima vez.

Entreviste se **qualquer um** for verdadeiro:

1. o critério de pronto não cabe numa frase;
2. há mais de um caminho razoável e o humano não declarou qual quer;
3. o trabalho vai para uma fila, e alguém vai executá-lo sem você por perto.

Nenhum verdadeiro? **Sintetize o que já foi dito e siga.** Diga que está pulando e por
quê — pular em silêncio parece descuido.

O gatilho é **quantas decisões seguem em aberto**, não o tamanho da feature. Você está
escolhendo quem paga o custo da ambiguidade: entrevistar paga agora em atenção,
sintetizar paga depois em retrabalho — mas só se houver ambiguidade.

## A árvore, a fronteira, as rodadas

Decisões pendem de decisões. Mapeie isso como **árvore**: cada escolha ramifica nas
escolhas que dependem dela.

A **fronteira** é toda decisão cujos pré-requisitos já estão resolvidos — as perguntas
que dá para fazer **agora**, sem adivinhar resposta que você ainda não ouviu.

Trabalhe em rodadas: pergunte a fronteira inteira de uma vez, espere, recompute.
Cada resposta empurra a fronteira para fora e destrava o que dependia dela.

**Pergunta cuja resposta depende de outra ainda aberta pertence à rodada seguinte.**
Furar isso é o erro que faz a entrevista parecer longa: você pergunta algo que o
humano não tem como responder ainda, ele responde por educação, e a resposta vira
suposição disfarçada de decisão.

Acaba quando a fronteira esvazia. Aí, e só aí, confirme o entendimento compartilhado.

## Use `AskUserQuestion`

É a ferramenta certa: apresenta as opções lado a lado e devolve a escolha
estruturada, em vez de prosa que você tem que interpretar.

**Toda pergunta vai com a sua resposta recomendada e o motivo.** Não é conveniência —
é o que transforma a entrevista de interrogatório em revisão. Sem recomendação você
transfere ao humano o trabalho que era seu; com ela, ele revisa e discorda, que é
muito mais barato do que produzir do zero.

E **nomeie o custo de cada opção**, não só o benefício. Opção sem desvantagem
declarada é opção que você já escolheu e está apresentando como pergunta.

## Achar fato é seu trabalho, nunca do humano

Quando uma pergunta da fronteira precisa de um fato do ambiente — o que existe no
repositório, qual versão está instalada, como o sistema se comporta hoje — **vá
buscar**. Despache um subagente. Não pergunte o que você consegue ler.

**Não bloqueie por isso.** Uma busca em andamento é um pré-requisito não resolvido:
só as perguntas a jusante dela esperam. Pergunte o resto da fronteira agora.

A divisão é limpa: **os fatos são seus, as decisões são dele.**

## O que fazer com o que foi decidido

Aqui a metodologia diverge do que uma entrevista normalmente faz. Decisão fechada não
volta para o ar: ela vira registro.

Ao fim, para cada decisão que se fechou, escreva uma entrada no `DECISIONS.md` do
projeto, no formato do `templates/DECISIONS.md`, com a **alternativa descartada** e o
custo de tê-la escolhido. A linha da alternativa é obrigatória: decisão sem
alternativa registrada não era decisão, era o caminho default.

**A barra aqui é baixa de propósito.** ADR é para decisão difícil de reverter,
surpreendente sem contexto e resultado de trade-off real. O `DECISIONS.md` fica
abaixo disso, e é onde mora a maior parte do que alguém perguntaria "por que está
assim?" daqui a três meses. Um projeto com barra só de ADR perde quase tudo.

Só ofereça um ADR quando as três condições valerem juntas. Se faltar uma, é entrada
no `DECISIONS.md`.

## Não aja sobre isso

Terminada a entrevista, **pare**. Não fatie, não implemente, não escreva spec.
O passo seguinte é do humano, e normalmente é `/metodo:fatiar`.

Agir sobre um entendimento que você acabou de construir, sem ele confirmar, é
transformar a entrevista em cerimônia — o resultado já estava decidido, as perguntas
só o adiaram.
