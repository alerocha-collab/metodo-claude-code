# 013 — `doutrina`: a matriz "onde colocar" e as armadilhas da doc

## Problema

A pergunta que um agente mais faz ao desenhar um sistema — *"tenho uma instrução, onde
ela vai, e com que autoridade?"* — **não é respondida pela documentação oficial**.

O reconhecimento mediu: o eixo de **autoridade** (pedido × garantia) não é tabelado em
página nenhuma. Aparece como prosa solta em quatro páginas diferentes, e uma delas o
chama de `Determinism`, dentro de uma comparação entre dois mecanismos apenas.

E a doc se contradiz em pontos caros, sem sinalizar:
- precedência de **skills** é `user > project`; a de **rules** é `project > user`;
- a tabela "o que sobrevive à compaction" **omite** que o índice de skills não sobrevive
  — o widget da mesma página diz o contrário;
- o limite do `CLAUDE.md` é declarado de três formas em três páginas.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| A decisão exige ler 6 páginas e sintetizar | Uma matriz responde em uma tela |
| O eixo de autoridade não existe tabelado | Existe, como coluna |
| As contradições da doc pegam quem confia nela | Estão nomeadas, com as duas versões |

## Critérios de aceitação

- [ ] A matriz tem uma linha por mecanismo e, no mínimo, as colunas: **onde vive** ·
      **quando carrega** · **custo de contexto** · **autoridade** · **sobrevive à
      compaction** · **precedência quando duplicado**
- [ ] Cobre pelo menos: `CLAUDE.md` (e seus escopos), `.claude/rules/` (com e sem
      `paths:`), skills (auto e `disable-model-invocation`), subagentes, hooks,
      `permissions`, sandbox, MCP, auto memory, plugins, output styles
- [ ] A coluna **autoridade** distingue três níveis, não dois: pedido (o modelo pode
      ignorar) · garantia condicional (hook, best-effort) · garantia dura
      (`permissions`, sandbox)
- [ ] Há uma **árvore de decisão** que começa pela pergunta que elimina mais casos, e
      a primeira pergunta é sobre autoridade, não sobre formato
- [ ] As precedências estão numa seção própria com **aviso explícito de que não são
      uniformes** entre mecanismos
- [ ] `armadilhas.md` nomeia cada contradição com **as duas versões e onde cada uma
      aparece**, para quem for conferir não achar que a ficha está errada
- [ ] O que é síntese autoral está **marcado como tal**, separado do que é transcrição
- [ ] O corpo da skill fica **abaixo de 500 linhas**; o que passar disso vai para
      referência carregada sob demanda
- [ ] **Negativo:** nenhum número de versão (`v2.1.x`) no núcleo durável. Número de
      versão é sinal de conteúdo volátil e ele não mora aqui
- [ ] **Negativo:** a ficha não repete a doc. Onde a doc já responde bem e sem
      contradição, ela **aponta** em vez de copiar

## Fora de escopo

- Schemas de frontmatter e tabelas de campos — são a Fase D, e são voláteis
- As demais fichas por pergunta — Fase C
- Corrigir a documentação da Anthropic ou reportar as contradições a eles

## Verificação

A bateria de perguntas da Fase E ainda não existe, então esta fatia se verifica por
duas perguntas respondidas **só com o arquivo local**, sem rede:
*"isto deve ser hook ou CLAUDE.md?"* e *"qual precedência vale quando uma skill e uma
rule conflitam?"*. A segunda é a que a doc erra.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
