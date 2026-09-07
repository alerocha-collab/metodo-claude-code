# 025 — `doutrina`: a ficha de verificação e evals

## Problema

A palavra "eval" aparece **duas vezes** no `doutrina` inteiro, as duas de passagem. Não
há ficha.

É uma lacuna com consequência direta: a metodologia deste repositório inteiro se apoia em
**conjunto balanceado** e em **verificador de qualidade**, e a doutrina que fundamenta
isso — *"o verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver
o problema errado"* — não está no plugin de conhecimento.

## Critérios de aceitação

- [ ] Skill nova no `doutrina` cobrindo: a regra central (dê uma verificação executável),
      a **escada de dureza do portão**, qualidade do verificador, quem dá a nota
- [ ] O vocabulário de evals: task, trial, grader, transcript, outcome, harness, suite
- [ ] Os três graders e **`pass@k` × `pass^k`** — com o motivo de a segunda importar para
      sistema voltado ao usuário
- [ ] O roteiro do zero: 20–50 tasks de falhas reais, tasks inequívocas, **conjuntos
      balanceados**, ambientes isolados, avaliar resultado e não caminho
- [ ] **O contra-alerta obrigatório:** revisor instruído a achar lacuna **vai** achar
      lacuna. Sinalizar só o que afeta corretude ou requisito declarado. Sem isso a ficha
      ensina superengenharia
- [ ] Descrição dentro do teto, sem competir com `garantir`

## Fora de escopo

- Arquitetura de agentes: ticket 024
- Reescrever as suítes deste repositório à luz da ficha

## Verificação

Perguntas novas na bateria: *"como sei se meu verificador é bom?"*, *"pass@k ou pass^k?"*

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
