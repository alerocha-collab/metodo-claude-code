# 027 — O portão barra quem nunca adotou, e isso inverte a ordem do onboarding

## Problema

Medido ao apontar o `metodo` para um projeto real pela primeira vez:

| Situação | Portão |
|---|---|
| Sem `.claude/metodo.json`, árvore limpa | libera |
| Sem `.claude/metodo.json`, árvore **suja** | **bloqueia** |
| Sem git nenhum | **bloqueia sempre** (`sessao_mudou_codigo` falha fechada) |

A consequência prática: instalar o `metodo` em escopo `user` faz **todo projeto da
máquina** com mudança não commitada travar no fim do turno, exigindo um arquivo que a
pessoa nunca escolheu criar.

E há uma inversão pior, específica da reengenharia: **para rodar
`/metodo:onboarding-entender`, que existe para decidir se vale adotar, é preciso já ter
adotado.** A skill que avalia a adoção fica atrás do portão que a adoção liga.

## A tensão real, que não é bug de digitação

Duas regras do próprio método colidem aqui:

- **"Ausência de verificação conta como falha"** — sólida, e é o que impede um portão de
  aprovar o que não consegue verificar.
- **Ticket 018: o plugin não age em repositório que não aderiu** — `proteger_testes.py`
  já respeita isso (`comum.aderiu()` e sai 0). `verificar_suite.py` **não usa** essa
  guarda.

A primeira regra foi escrita pensando num repositório que **adotou** e depois perdeu a
verificação. Aplicada a um que nunca adotou, ela deixa de ser fail-closed e vira
coerção — o plugin exigindo adesão de quem só o instalou.

## Critérios de aceitação

- [ ] Decisão registrada sobre qual regra vence quando as duas colidem, com a
      alternativa descartada
- [ ] Se a decisão for tratar ausência de `metodo.json` como "não aderiu": o `Stop`
      passa a usar `comum.aderiu()` como primeira guarda, igual ao `PreToolUse`
- [ ] **A força do portão não pode cair onde a adesão existe.** Com `metodo.json`
      presente e comando ausente, quebrado ou vermelho, continua bloqueando
- [ ] Conjunto balanceado, e o caso que hoje falta: projeto **sem git** e sem config
      não pode travar toda sessão
- [ ] **Negativo:** não basta "não bloquear se não há git". Repositório versionado que
      adotou e apagou o git ainda deve ser tratado como suspeito

## Fora de escopo

- Mudar o comportamento onde a adesão existe. O portão do repositório que adotou é o
  que ele é hoje, e foi verificado seis vezes

## Verificação

Reproduzir a tabela do início com o caso novo, e conferir que o exit muda **só** nas
linhas em que não há adesão.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
