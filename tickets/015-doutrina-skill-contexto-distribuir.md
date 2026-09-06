# 015 — `doutrina`: as fichas `escrever-skill`, `contexto` e `distribuir`

## Problema

Três perguntas frequentes que sobraram das duas fichas anteriores:

**"Como escrevo uma skill da melhor forma?"** — foi pergunta explícita do pedido
original. A doc tem as regras de autoria espalhadas entre a seção de criação e o
troubleshooting.

**"Como não estouro a janela?"** — a restrição fundadora de quase toda boa prática, e
que a `compaction.md` só cobre pela metade.

**"Como empacoto e compartilho isto?"** — plugin, marketplace, e o escopo por
diretório num monorepo, que é a lacuna que originou esta fase inteira.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| As regras de autoria de skill estão em duas seções distantes | Reunidas, com o porquê de cada uma |
| Orçamento de contexto só aparece na ficha de compaction | Tem ficha própria |
| Monorepo não existe em ficha nenhuma | Existe, com os mecanismos de escopo |

## Critérios de aceitação

### `escrever-skill`
- [ ] Traz o **gatilho de autoria**: quando criar uma skill em vez de escrever no
      `CLAUDE.md`, e o sinal de que uma seção do `CLAUDE.md` virou procedimento
- [ ] Explica por que o corpo precisa ser conciso — ele **fica em contexto entre
      turnos**, então cada linha é custo recorrente
- [ ] Cobre progressive disclosure: o que fica no `SKILL.md`, o que vai para arquivo
      de referência, e a regra de **apontar explicitamente** para cada arquivo
- [ ] Cobre como escrever a `description` para a skill disparar, e o que fazer quando
      ela dispara demais
- [ ] Diz o que fazer quando a skill **para de influenciar** depois da primeira
      resposta
- [ ] Distingue conteúdo de referência de conteúdo de tarefa, e liga isso a
      `disable-model-invocation`

### `contexto`
- [ ] Nomeia a restrição fundadora e o que ela implica
- [ ] Diz o que enche a janela, em ordem de peso
- [ ] Traz as saídas: delegar a subagente, cortar, recomeçar — e o **critério de
      quando recomeçar em vez de insistir**
- [ ] **Negativo:** não duplica `compaction.md`. Referencia

### `distribuir`
- [ ] Critério standalone × plugin, que é o mais limpo da doc
- [ ] O erro comum de estrutura de plugin, nomeado
- [ ] Escopo em monorepo: `CLAUDE.md` em camadas, rules com `paths:`, skills por
      diretório, e o fato de que **settings de projeto não são herdadas de pai**
- [ ] **Negativo:** não vira tutorial de marketplace. O que se decide, não o passo a
      passo

### Todas
- [ ] Corpo abaixo de 500 linhas cada; zero números de versão
- [ ] Registradas em `fontes.json`, ligadas às origens

## Fora de escopo

- Schemas — ticket 016
- Distribuição via claude.ai, gateways, e configuração de organização

## Verificação

Três perguntas respondidas só com arquivos locais: *"minha skill não dispara, por
quê?"* · *"o que faço quando o contexto enche?"* · *"como escopo o Claude num
monorepo?"*.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
