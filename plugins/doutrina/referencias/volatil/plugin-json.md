# `plugin.json` e a estrutura de um plugin

> **FICHA VOLÁTIL.** Campos novos aparecem a cada versão.
>
> url: https://code.claude.com/docs/en/plugins-reference.md
> Verificado em 2026-09-06.
>
> `claude plugin validate <caminho> --strict` é a verificação de verdade: ela conhece o
> schema da sua versão instalada, esta ficha conhece o da data acima.

## O único campo obrigatório

| Campo | O que faz |
|---|---|
| `name` | Identificador único, em kebab-case, sem espaço. **É o namespace das skills**: elas passam a ser `/nome-do-plugin:nome-da-skill` |

## Metadados

| Campo | O que faz |
|---|---|
| `displayName` | Nome legível no seletor de plugins. Aceita espaço e maiúscula; não é usado para namespace |
| `version` | Versão semântica. **Sem bump, quem instalou continua com a cópia em cache** |
| `description` | Aparece ao navegar ou instalar |
| `author` | Objeto com `name`, `email`, `url` |
| `homepage`, `repository`, `license`, `keywords` | Atribuição e descoberta |
| `metadata` | Mapa livre para dados seus. O Claude Code não lê |
| `defaultEnabled` | Se o plugin começa habilitado quando o usuário não escolheu. Padrão: sim |

## Caminhos de componente

Todos opcionais — só existem para apontar para lugar diferente do padrão.

| Campo | Padrão correspondente |
|---|---|
| `skills` | `skills/` — **acrescenta** à varredura padrão |
| `commands` | `commands/` — substitui |
| `agents` | `agents/` — substitui |
| `workflows` | `workflows/` — substitui |
| `hooks` | `hooks/hooks.json` |
| `mcpServers` | `.mcp.json` |
| `outputStyles` | `output-styles/` |
| `lspServers` | `.lsp.json` |
| `dependencies` | outros plugins de que este depende |
| `userConfig` | valores que o usuário preenche ao habilitar |

## Onde cada coisa mora, por padrão

| Componente | Local |
|---|---|
| Manifesto | `.claude-plugin/plugin.json` |
| Skills | `skills/<nome>/SKILL.md` |
| Agentes | `agents/` |
| Hooks | `hooks/hooks.json` |
| MCP | `.mcp.json` |
| Executáveis | `bin/` — entram no `PATH` da ferramenta Bash enquanto o plugin está ativo |
| Settings | `settings.json` — **só as chaves `agent` e `subagentStatusLine`** |

> ⚠️ **O erro que a documentação chama de comum:** dentro de `.claude-plugin/` vai
> **só** o `plugin.json`. `skills/`, `agents/`, `hooks/` e `.mcp.json` ficam na **raiz
> do plugin**.
>
> E a raiz do plugin é o diretório do próprio plugin — nunca `~/.claude/`.

## Variáveis substituídas

| Variável | Vira |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | O diretório de instalação do plugin |
| `${CLAUDE_PLUGIN_DATA}` | Diretório persistente que **sobrevive a atualização** — para dependências instaladas e cache |
| `${CLAUDE_PROJECT_DIR}` | A raiz do projeto |

Elas resolvem em conteúdo de skill e de agente, em comando de hook, e nos campos de
conexão de servidores MCP e LSP.

## Escopos de instalação

| Escopo | Arquivo | Para quê |
|---|---|---|
| `user` | settings do usuário | pessoal, em todo projeto — é o padrão |
| `project` | settings do projeto | do time, versionado |
| `local` | settings local | só neste projeto, fora do git |
| `managed` | managed settings | imposto pela organização |

## Skill solta, plugin, ou skill dentro de plugin

| O que você tem | O que é |
|---|---|
| `<dir>/foo/SKILL.md`, sem manifesto | uma skill chamada `foo` |
| `<dir>/foo/.claude-plugin/plugin.json` | um **plugin** `foo`, que pode trazer skills, agentes e hooks |
| `<plugin>/skills/bar/SKILL.md` | uma skill `bar` **dentro** de um plugin |

## Duas armadilhas de empacotamento

- **Plugin de skill única:** dá para pôr o `SKILL.md` direto na raiz. Mas **sempre
  declare `name` no frontmatter** — sem ele, o nome vem do diretório de instalação, que
  em plugin de marketplace é uma string de versão que muda a cada atualização.
- **Agente de plugin com o mesmo nome de um local:** o local vence, e o do plugin só
  passa a valer quando o local sai. Skills não têm esse problema porque são namespaced.

## Validação

`claude plugin validate <caminho>` confere campos obrigatórios, tipos, frontmatter de
agente, caminhos que escapam do diretório do plugin, e campos não reconhecidos. O modo
estrito transforma aviso em erro — é o que se usa em CI.

---

*Transcrição condensada do schema e das tabelas de localização. Limites numéricos,
superfície de CLI, `userConfig`, LSP, monitors e channels ficaram de fora: são o que
mais envelhece e o que menos se consulta ao desenhar.*
