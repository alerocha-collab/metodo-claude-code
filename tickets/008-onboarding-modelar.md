# 008 — `onboarding-modelar`: o glossário extraído do código

## Problema

Num projeto novo, o modelo de domínio nasce da conversa. Num projeto que já existe,
ele já está no código — em nomes de tipo, de tabela, de função — e quase sempre
**inconsistente** com o que as pessoas dizem em voz alta. Essa divergência é fonte
silenciosa de retrabalho: o agente implementa o conceito que leu, e o humano queria
o que fala.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Nenhum glossário; cada sessão infere os termos de novo | Existe `/metodo:onboarding-modelar`, que extrai e confronta |
| Divergência entre o termo do código e o do negócio passa despercebida | É levantada explicitamente, para o humano decidir |

## Critérios de aceitação

- [ ] Consome o mapa produzido pelo ticket 007 em vez de reler o repositório do zero
- [ ] Produz um glossário em disco que é **glossário e nada mais** — sem detalhe de
      implementação, sem decisão de arquitetura
- [ ] Cada termo tem a definição **em uso no projeto**, não a definição ideal
- [ ] Quando o mesmo conceito tem dois nomes, ou o mesmo nome tem dois conceitos, isso
      é **reportado como conflito** e não resolvido por conta própria
- [ ] A skill confronta o que o humano diz contra o que o código faz, e nomeia a
      divergência quando encontra
- [ ] **Negativo:** a skill não renomeia nada no código. Ela descreve o que existe
- [ ] **Negativo:** termo que aparece uma vez só não entra — glossário inflado não é
      lido

## Fora de escopo

- Registrar decisões de arquitetura (ADR): barra mais alta, e outro artefato
- Refatorar nomes para ficarem consistentes — vira ticket, se o humano quiser
- Modelagem de domínio para projeto novo, que nasce da conversa

## Verificação

A suíte cobre o que for script. O glossário se verifica pelo confronto: um termo do
glossário que o código contradiz é falha da skill.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
