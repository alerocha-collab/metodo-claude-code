# 009 — `onboarding-lacunas`: a distância até o alvo, como fila

## Problema

Depois de entender o que existe e nomear o domínio, falta a pergunta que decide o
trabalho: **o que este projeto ainda não tem que a metodologia pressupõe?** Fila de
tickets, verificação declarada, decisões registradas, testes onde importa.

Sem esta etapa, a reengenharia vira ou um relatório que ninguém executa, ou uma
tentativa de conformidade total numa passada — que é a forma conhecida de parar o
desenvolvimento e nunca terminar.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| A trilha de reengenharia termina no entendimento | Termina numa **fila executável** |
| Sem critério de quanto fazer agora | O caminho crítico vira ticket; o resto tem regra de quando entra |

## Critérios de aceitação

- [ ] A saída é **fila de tickets**, não relatório. Rodá-la produz entradas em
      `tickets/fila.json` e briefs pelo template
- [ ] Os tickets gerados têm critérios de aceitação escritos **antes**, como qualquer
      outro — a origem automática não dispensa a regra
- [ ] A fila resultante passa em `validar_fila.py`
- [ ] Enfileira **só o caminho crítico**. O resto entra na forma de uma regra escrita:
      *o que estiver fora entra quando a área for tocada*, e essa regra fica registrada
      num artefato, não só na conversa
- [ ] O critério de "caminho crítico" é declarado e defensável, não implícito
- [ ] Cada lacuna vira ticket com `modulo` preenchido, para bloquear a próxima fatia
      que tocar o mesmo lugar
- [ ] **Negativo:** não enfileira "adicionar testes ao módulo X" para todo módulo sem
      teste. Cobertura total numa passada é o modo de falha desta skill
- [ ] **Negativo:** não sobrescreve mecanismo que o projeto já tem. Se o projeto
      resolve algo de outro jeito, isso é registrado como **decisão a tomar**, com a
      alternativa descartada — nunca substituído em silêncio

## Fora de escopo

- Implementar qualquer um dos tickets gerados
- Auditar qualidade de código: conformidade primeiro, porque é ela que constrói o
  receptáculo onde achado de código aterrissa
- Migrar o projeto para os artefatos da metodologia sem decisão humana

## Verificação

A suíte cobre o que for script, inclusive um caso que prove que a saída é fila válida
e não texto. O comportamento se verifica rodando num repositório real e conferindo
que a fila resultante é trabalhável — tickets em ordem de bloqueio, com critérios.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
