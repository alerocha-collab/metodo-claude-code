# metodo — metodologia de engenharia com agentes, como plugin

Repositório que carrega a metodologia entre projetos. O que vive aqui são as skills,
os agentes e os hooks que codificam nove decisões de método já fechadas — não código
de aplicação.

**Estado:** Fase 1 (esqueleto). Só o agente `arquiteto` e a skill
`arquiteto-claude-code` estão migrados. `/fluxo`, os agentes de papel e o core
adaptado entram nas fases seguintes.

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
| [docs/decisoes-metodologia.md](docs/decisoes-metodologia.md) | As nove decisões de método, com alternativas e modos de falha |
| [docs/analise-cruzada-metodologias.md](docs/analise-cruzada-metodologias.md) | XP × engenharia clássica × set do Matt Pocock × doutrina Anthropic |
| [docs/melhores-praticas-anthropic-claude-code.md](docs/melhores-praticas-anthropic-claude-code.md) | Doutrina Anthropic consolidada |
| [DECISIONS.md](DECISIONS.md) | Decisões sobre **este** repositório, append-only |
