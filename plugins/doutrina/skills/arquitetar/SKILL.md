---
name: arquitetar
description: Decide se a tarefa pede agente, workflow ou nenhum dos dois, e qual dos cinco padrões usar. Traz o custo medido de cada degrau. Use antes de montar um sistema com agentes, ou ao avaliar se multiagente se paga.
---

# Isto deve ser um agente?

A pergunta vem **antes** de escolher hook, skill ou subagente. Errar aqui faz o resto
não importar.

## A escada, e onde parar

| Degrau | O que é | Pare aqui quando |
|---|---|---|
| **0. Nenhum sistema** | Uma chamada, com retrieval e bons exemplos | A tarefa é bem definida e cabe num prompt. **É o degrau mais subestimado** |
| **1. LLM aumentado** | Modelo + retrieval + ferramentas + memória | O trabalho precisa de contexto ou ação externa, mas não de decisão em cadeia |
| **2. Workflow** | Caminhos de código predefinidos | A tarefa se decompõe em passos conhecidos. Ganha previsibilidade |
| **3. Agente** | Decisão dirigida pelo modelo | Os passos não são conhecidos de antemão |
| **4. Multiagente** | Líder decompõe e delega | O trabalho é grande e paralelizável — e você aceita **~15× os tokens** |

> *"Para muitas aplicações, otimizar uma única chamada com retrieval e exemplos basta.
> Não construa sistema agêntico."*

**Declare o degrau e por que o anterior não bastou.** Sem isso, a escolha é gosto.

## Os cinco padrões de workflow

| Padrão | Use quando |
|---|---|
| **Prompt chaining** | Troca latência por acurácia; a tarefa se decompõe em passos sequenciais |
| **Routing** | Categorias distintas se beneficiam de tratamento separado |
| **Parallelization** | Subtarefas independentes (*sectioning*) ou confiança por consenso (*voting*) |
| **Orchestrator-workers** | As subtarefas são imprevisíveis — decompostas em execução, não no desenho |
| **Evaluator-optimizer** | O critério de qualidade é claro, mas difícil de acertar de primeira |

Para **como** distribuir o trabalho entre agentes na prática — subagente, worktree,
workflow, agent teams — a ficha é `paralelizar`. Esta aqui decide **se** e **qual
forma**; aquela decide **com que mecanismo**.

## Três princípios que atravessam tudo

1. **Simplicidade.** Cada componente do harness codifica uma suposição sobre o que o
   modelo não consegue fazer sozinho. Suposição errada vira trabalho inútil.
2. **Transparência.** Exiba os passos de planejamento.
3. **ACI forte.** *"Invista em interfaces agente-computador o mesmo esforço que se
   investe em interfaces humano-computador."*

## O que quase ninguém faz, e devia

**Gerador e avaliador separados.** Agentes *"respondem elogiando confiantemente o
próprio trabalho — mesmo quando a qualidade é obviamente medíocre."* Calibrar um
avaliador cético é muito mais tratável do que fazer um gerador autocrítico. Detalhe em
`avaliar`.

**Comunicação por arquivos, não por contexto compartilhado.** Spec, contrato, achados
em disco. Previne poluição de contexto e força clareza sobre o que atravessa a
fronteira.

**Remova componentes quando chegar modelo novo, e meça.** O harness de ontem foi
desenhado contra limitações que podem não existir mais — decomposição em sprints,
resets de contexto, avaliador a cada ciclo. A arquitetura envelhece para baixo.

## Onde está o resto

- **Os números, o desenho de harness, agentes de longa duração e paralelismo em escala:**
  [referencias/duravel/arquitetura-de-agentes.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/arquitetura-de-agentes.md)
- **Como verificar o que o sistema produz:** ficha `avaliar`
- **Onde cada instrução mora, e com que autoridade:** ficha `onde-colocar`
