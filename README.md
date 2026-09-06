# metodo — metodologia de engenharia com agentes, como plugin

Repositório que carrega a metodologia entre projetos. O que vive aqui são as skills,
os agentes e os hooks que codificam nove decisões de método já fechadas — não código
de aplicação.

**Estado:** Fase 2a entregue (papéis e portão) e Fase 3 iniciada (formato do ticket).
As skills de fluxo e o `/fluxo` vêm a seguir — o orquestrador é o último, porque é o
único que só lê estado, sem produzi-lo.

## Verificação

```bash
python3 tests/testar_tudo.py
```

Duas suítes, 32 casos, ambas com **conjunto balanceado**: metade verifica que a trava
age quando deve, metade que ela **não** age quando não deve. Uma suíte só com casos
positivos aprova uma trava que bloqueia tudo.

O runner é *fail-closed*: nenhuma suíte encontrada conta como **falha**. Sem isso,
apagar os testes deixaria o runner verde — e o portão passaria a aprovar um
repositório sem verificação nenhuma.

Este repositório usa o próprio portão que distribui: `.claude/metodo.json` aponta
para o runner.

## O que o plugin instala num projeto

| Artefato | Onde | Para quê |
|---|---|---|
| `metodo.json` | `.claude/` | Declara o comando que decide verde/vermelho. Sem ele, o portão bloqueia |
| `fila.json` | `tickets/` | Estado dos tickets e o grafo de bloqueio. JSON porque muda toda sessão |
| `ticket.md` | `tickets/NNN-*.md` | A spec de uma fatia. Markdown porque é prosa escrita uma vez |
| `DECISIONS.md` | raiz | Decisões append-only, abaixo da barra de um ADR |

Valide a fila com:

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

## Estrutura

```
.
├── docs/                        doutrina e decisões que fundamentam a metodologia
└── plugins/
    └── metodo/                 o plugin propriamente dito
        ├── .claude-plugin/plugin.json
        ├── agents/              papéis (construtor, operador, arquiteto)
        ├── skills/              fluxo, onboarding, core adaptado
        ├── hooks/               hooks.json + scripts (Fase 2)
        └── templates/           artefatos que o plugin instala em projetos
```

O plugin fica em `plugins/metodo/`, não na raiz, para que
`.claude-plugin/marketplace.json` possa ser adicionado depois com
`"source": "./plugins/metodo"` sem mover nada.

## Usar em desenvolvimento

Sem instalar, isolado por sessão:

```bash
claude --plugin-dir ./plugins/metodo
```

`/reload-plugins` recarrega sem reiniciar. Para validar antes de publicar:

```bash
claude plugin validate ./plugins/metodo
```

## Namespacing

Tudo que o plugin distribui carrega o prefixo `metodo:`. Skills se invocam como
`/metodo:arquiteto-claude-code`; agentes aparecem no typeahead como
`metodo:arquiteto`.

## Publicar

Ainda não há marketplace — ele só se paga ao instalar num segundo projeto.
Quando existir, **todo release exige bump de `version` no `plugin.json`**: sem isso,
quem já instalou continua com a cópia em cache.

## Documentos

| Arquivo | O que é |
|---|---|
| [docs/plano-metodologia.md](docs/plano-metodologia.md) | O plano que este repositório executa, fase a fase |
| [docs/fase-0-mecanismos.md](docs/fase-0-mecanismos.md) | O que a plataforma já entrega, e o que isso muda no plano |
| [docs/decisoes-metodologia.md](docs/decisoes-metodologia.md) | As nove decisões de método, com alternativas e modos de falha |
| [docs/analise-cruzada-metodologias.md](docs/analise-cruzada-metodologias.md) | XP × engenharia clássica × set do Matt Pocock × doutrina Anthropic |
| [docs/melhores-praticas-anthropic-claude-code.md](docs/melhores-praticas-anthropic-claude-code.md) | Doutrina Anthropic consolidada |
| [DECISIONS.md](DECISIONS.md) | Decisões sobre **este** repositório, append-only |
