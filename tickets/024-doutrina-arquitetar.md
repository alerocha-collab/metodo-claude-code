# 024 — `doutrina`: a ficha de arquitetura de sistemas agênticos

## Problema

O `doutrina` responde *onde colocar uma instrução*, *como paralelizar*, *como garantir*,
*como escrever uma skill*, *como distribuir*. Não responde a pergunta que vem **antes de
todas**: **isto deve ser um agente?**

Workflow × agente, os cinco padrões de workflow, os números do orquestrador-worker
(+90,2%, ~15× tokens, 3–5 subagentes), o desenho de harness, agentes de longa duração e
paralelismo em escala — nada disso está no `doutrina`, porque nada disso está na árvore
de documentação. Está no blog de engenharia, e hoje só existe em
`plugins/metodo/skills/arquiteto-claude-code/references/01`.

## Critérios de aceitação

- [ ] Skill nova no `doutrina`, com corpo enxuto e detalhe em `referencias/`
- [ ] Responde, em ordem: **não construa agente** → workflow → agente → multiagente, com
      o custo declarado em cada degrau
- [ ] Traz os números medidos, não adjetivos: ~15× tokens, +90,2%, 1.000–2.000 tokens de
      contrato de subagente, 20min/US$9 × 6h/US$200
- [ ] Traz a **obsolescência do harness**: modelo novo, remova componentes e meça
- [ ] A `description` respeita o teto de `tests/testar_orcamento.py` e **não compete**
      com `paralelizar` — a fronteira entre as duas fica explícita nas duas
- [ ] Toda afirmação normativa aponta para fonte indexada no ticket 023

## Fora de escopo

- Evals: ficam no ticket 025
- Remover a skill velha: ticket 026

## Verificação

`tests/testar_bateria.py` ganha perguntas que só esta ficha responde — *"isto deve ser
agente ou workflow?"*, *"quanto custa multiagente?"* — e elas passam **sem rede**.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
