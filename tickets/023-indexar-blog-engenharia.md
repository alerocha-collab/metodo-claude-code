# 023 — Indexar o blog de engenharia: o ponto cego do `doutrina`

## Problema

`fontes.json` indexa **191 páginas**, todas de `code.claude.com/docs`. De
`anthropic.com/engineering`, **zero**.

Isso não é uma lacuna de catálogo, é uma lacuna de assunto. É no blog de engenharia que
mora a doutrina de **arquitetura de sistemas agênticos** — *Building effective agents*,
o sistema multiagente de pesquisa, design de harness para execuções longas, o compilador
C com Claudes em paralelo. Nada disso está na árvore de documentação, e por isso nada
disso está no `doutrina`.

A prova de que a lacuna é real: o `metodo` carrega uma skill (`arquiteto-claude-code`)
com 155 linhas de referência tiradas exatamente dessas fontes. O conhecimento existe no
repositório — **no plugin errado, e sem a máquina de detecção de fonte mudada**.

Este ticket é pré-requisito dos dois seguintes: a ficha do `doutrina` cita fonte
indexada com hash, e migrar conteúdo antes de indexar a fonte quebraria essa regra.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| `fontes.json` só conhece a árvore de docs | Conhece também as páginas de engenharia que fundamentam arquitetura |
| O detector de drift vigia 191 páginas | Vigia também as novas |
| A doutrina de arquitetura não tem fonte rastreável no `doutrina` | Tem, com hash e data |

## Critérios de aceitação

- [ ] As páginas de `anthropic.com/engineering` que fundamentam arquitetura de agentes
      entram em `fontes.json` com `url`, `titulo`, `secao`, `prioridade`, `hash` e
      `verificada_em`
- [ ] O hash é **obtido da fonte**, não inventado — se uma página não puder ser buscada,
      ela entra marcada como indeterminada, e isso aparece
- [ ] `verificar_fontes.py` continua passando, e continua separando `mudadas` de
      `indeterminadas` — a distinção existe porque não conseguir olhar não é o mesmo que
      ver mudança
- [ ] `tests/testar_doutrina.py` continua verde: toda entrada com ficha tem arquivo, todo
      arquivo tem fonte
- [ ] **Negativo:** não indexar o blog inteiro. Entram as páginas que fundamentam decisão
      de arquitetura; posts de produto e anúncios não entram, e o motivo fica escrito

## Fora de escopo

- Escrever as fichas: são os tickets 024 e 025
- Remover a `arquiteto-claude-code`: é o ticket 026, e remover antes de migrar perde
  conteúdo

## Verificação

`python3 plugins/doutrina/scripts/verificar_fontes.py` passa, e a contagem de páginas
indexadas sobe de forma declarada — o número novo entra no README, medido e não estimado.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
