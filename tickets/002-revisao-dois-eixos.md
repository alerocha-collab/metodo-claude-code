# 002 — Escrever a revisão em dois eixos, Standards e Spec

## Problema

Não há revisão. O portão diz que a suíte passa; não diz se o código segue as
convenções do projeto, nem se implementa o que o ticket pediu. São perguntas
diferentes, e um mesmo diff pode passar numa e falhar na outra: seguir todo padrão e
implementar a coisa errada, ou fazer exatamente o que o ticket pediu quebrando as
convenções.

E quem escreveu o código é o pior revisor dele — não por incompetência, mas porque
não ficar enviesado a favor do que se acabou de escrever é impossível tendo em
contexto o raciocínio que o produziu.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Nenhuma revisão além da suíte verde | Dois revisores em **contexto separado**, um por eixo |
| Achado de revisão não tem destino | Achado aceito vira ticket, bloqueando a próxima fatia do mesmo módulo |

## Critérios de aceitação

- [ ] Os dois eixos rodam em contextos isolados e **não veem o raciocínio** que
      produziu a mudança — só o diff e os critérios do ticket
- [ ] O eixo Spec recebe os critérios de aceitação e responde, por critério, se o diff
      o atende
- [ ] O eixo Standards recebe as convenções documentadas do projeto e o baseline de
      smells, com a regra de que o repositório sobrepõe o baseline
- [ ] Os resultados aparecem **lado a lado, sem mesclar nem reordenar entre eixos** —
      achatar isso perde justamente a informação de que um passou e o outro não
- [ ] Todo achado aceito vira ticket na fila, com `modulo` preenchido
- [ ] Cada relatório tem teto de tamanho declarado, para não inundar a sessão
- [ ] **Negativo:** a revisão não edita código. Reporta e enfileira

## Fora de escopo

- Postar comentário em PR de plataforma externa
- Eixos de segurança ou desempenho — dois por ora
- Decidir se isto é skill ou workflow de plugin fica **dentro** desta fatia: a Fase 0
  registrou workflow como candidato natural por isolar contexto de verdade. Registrar
  a escolha no `DECISIONS.md`

## Verificação

A suíte cobre, mais `claude plugin validate --strict`. Se a escolha for workflow,
acrescentar `workflows/` ao que o CI valida.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
