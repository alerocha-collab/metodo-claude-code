# 001 — Escrever a skill `implementar`, o loop que o construtor segue

## Problema

O papel `construtor` sabe **o que não fazer** — não editar testes, não refatorar
durante, não alterar critérios. Não há nada que descreva **o que fazer**: como pegar
um ticket, em que ordem verificar, quando acionar TDD, o que fazer quando a
verificação fica vermelha, e como fechar a fatia.

Sem isso, cada sessão de construção reinventa o procedimento, e a aderência às
decisões de método depende de o construtor lembrar delas.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O construtor tem regras, não procedimento | Existe `/metodo:implementar`, que conduz uma fatia do início ao commit |
| A escolha de fazer TDD ou não é ad hoc | O ponto em que se escreve teste primeiro é acordado antes, não decidido no meio |
| Verificação vermelha não tem protocolo | Há um caminho definido para vermelho, incluindo quando parar e devolver ao humano |

## Critérios de aceitação

- [ ] A skill lê o ticket da fila, marca `em-andamento` e recusa começar se já houver
      outro ticket em andamento — a fila permite um por vez
- [ ] A skill recusa começar se o ticket não tiver critérios de aceitação escritos
- [ ] O procedimento diz explicitamente que critério impossível interrompe o trabalho
      e devolve a decisão ao humano, em vez de ser reescrito
- [ ] O procedimento inclui verificação ao longo, não só ao fim
- [ ] O procedimento termina em commit, e o texto diz o que a mensagem deve conter
- [ ] Um smell encontrado durante a implementação vira ticket novo com `bloqueado_por`
      apontando para o ticket atual e `modulo` preenchido — nunca conserto de passagem
- [ ] A skill não é auto-invocável pelo modelo (`disable-model-invocation: true`),
      porque marca estado e commita
- [ ] **Negativo:** a skill não duplica o conteúdo do agente `construtor`; onde a
      regra já existe lá, ela referencia em vez de repetir

## Fora de escopo

- A revisão do diff — é o ticket 002
- Ensinar TDD do zero: a skill aciona a disciplina, não a explica
- Integração com issue tracker externo; a fila em disco basta por ora

## Verificação

A suíte cobre (`python3 tests/testar_tudo.py`), mais `claude plugin validate
--strict`. Nenhum comportamento existente pode mudar.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
