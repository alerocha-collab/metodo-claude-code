# metodo — metodologia de engenharia com agentes, como plugin

Repositório que carrega a metodologia entre projetos. O que vive aqui são as skills,
os agentes e os hooks que codificam nove decisões de método já fechadas — não código
de aplicação.

**Estado:** o pipeline está completo — seis skills, dois papéis, e o portão de
verificação exercitado numa sessão real. Falta o prefixo de reengenharia, para partir
de um repositório que já existe.

## Verificação

```bash
python3 tests/testar_tudo.py
```

Cinco suítes, 68 casos, todas com **conjunto balanceado**: metade verifica que a trava
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
        ├── agents/              papéis: construtor, operador, arquiteto
        ├── skills/              as seis do pipeline
        ├── hooks/               hooks.json + os dois hooks do portão
        ├── scripts/             fila, estado, transição de ticket
        └── templates/           artefatos que o plugin instala em projetos
```

O plugin fica em `plugins/metodo/`, não na raiz, para que
`.claude-plugin/marketplace.json` possa ser adicionado depois com
`"source": "./plugins/metodo"` sem mover nada.

## Requisitos

**`python3` 3.8 ou mais novo, no PATH.** Os hooks e os scripts do plugin são Python.

A escolha é deliberada: a doc do Claude Code diz que hooks rodam em `sh` no
macOS/Linux, em Git Bash no Windows, ou em PowerShell quando Git Bash não está
instalado. Um script `.sh` não cobriria os três; Python cobre.

**Se `python3` faltar, o portão de verificação bloqueia** — não libera. Sem tratamento
ele falharia aberto, porque o shell sai com 127 e a doc classifica 127 como não
bloqueante; por isso o comando no `hooks/hooks.json` termina em `|| exit 2`. A
mensagem que aparece é a do shell, `python3: command not found`, que nomeia o que
falta.

**Risco residual:** `|| exit 2` é sintaxe POSIX. No caso restrito de Windows **sem**
Git Bash, onde os hooks rodam em PowerShell, a rede não vale e a ausência de `python3`
volta a poder falhar aberta. Não há contorno portátil conhecido; registrado aqui em
vez de escondido.

## Usar em desenvolvimento

Sem instalar, isolado por sessão:

```bash
claude --plugin-dir ./plugins/metodo
```

`/reload-plugins` recarrega sem reiniciar. Para validar antes de publicar:

```bash
claude plugin validate ./plugins/metodo
```

## As skills

| Skill | Para quê |
|---|---|
| `/metodo:decidir` | Fecha decisões em aberto, em rodadas, antes de construir |
| `/metodo:dominio` | Constrói e afia o vocabulário do projeto |
| `/metodo:fatiar` | Transforma trabalho descrito em fila de tickets |
| `/metodo:implementar` | Conduz uma fatia do ticket ao commit |
| `/metodo:revisar` | Revisa em dois eixos, Standards e Spec, em contextos separados |
| `/metodo:fluxo` | Diz onde o projeto está e qual é o próximo passo |

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
