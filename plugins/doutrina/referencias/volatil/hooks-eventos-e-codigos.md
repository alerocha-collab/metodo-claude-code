# Hooks — eventos, códigos de saída e saída estruturada

> **FICHA VOLÁTIL.** A lista de eventos cresce a cada versão, e os timeouts mudam.
>
> url: https://code.claude.com/docs/en/hooks.md
> Verificado em 2026-09-06.
>
> A semântica dos códigos de saída é a parte mais estável desta ficha; a lista de
> eventos é a mais volátil. Rode `verificar_fontes.py --drift` antes de confiar num
> evento que você nunca usou.

## Os códigos de saída — a parte que decide tudo

| Código | Significa | Bloqueia? |
|---|---|---|
| **0** | Sucesso | Não. É o código correto quando você imprime JSON para controle estruturado |
| **2** | Erro bloqueante | **Sim**, nos eventos que podem bloquear — e bloqueia mesmo que o JSON diga o contrário |
| qualquer outro | Não padronizado | **Não**, na maioria dos eventos |

> ⚠️ **Exit 1 não bloqueia.** É tratado como erro não bloqueante e a ação prossegue,
> apesar de 1 ser o código convencional de falha no Unix. Um script que morre com
> exceção **libera**.
>
> ⚠️ **Exit 127 também não bloqueia.** É o que o shell devolve quando o interpretador
> não existe — então um hook falha aberto exatamente na máquina mal configurada.

**Escolha um dos dois caminhos por hook**, não misture: exit 2 com a razão em stderr,
**ou** exit 0 com JSON estruturado no stdout.

## Onde a mensagem de bloqueio vem

Na ordem: o campo de razão do JSON → senão, o stderr → senão, uma mensagem genérica.

## Quando o Claude vê o que o hook escreveu

**Texto puro no stdout só chega ao modelo em quatro eventos**: `UserPromptSubmit`,
`UserPromptExpansion`, `SessionStart` e `PostModelSwitch`. Nos demais vai **só para o
log de depuração**.

É a maior classe de bug de hook. Para falar com o modelo nos outros eventos, use os
campos estruturados.

## Campos de saída estruturada

| Campo | Faz |
|---|---|
| `permissionDecision` | `allow` prossegue, `deny` bloqueia, `skip` ignora a decisão do hook |
| `permissionDecisionReason` | A mensagem de bloqueio |
| `additionalContext` | Acrescentado ao contexto do Claude como mensagem de sistema |
| `updatedInput` | Só em `PreToolUse`. Modifica o input da ferramenta antes de executar — é **merge profundo**, não substituição |
| `systemMessage` | Mensagem na interface. Nunca entra no transcript |
| `blockReason` | Alternativa ao campo de razão, nos eventos que bloqueiam |

**Regra de parsing:** o stdout é lido como JSON quando começa com `{` e termina com
`}`. Se o parse falhar, é tratado como texto puro — e cai na regra dos quatro eventos.

## Os eventos

Sessão e configuração: `SessionStart` · `Setup` · `SessionEnd` · `ConfigChange` ·
`CwdChanged` · `DirectoryAdded` · `FileChanged` · `InstructionsLoaded`

Prompt: `UserPromptSubmit` · `UserPromptExpansion` · `MessageDisplay`

Ferramentas: `PreToolUse` · `PostToolUse` · `PostToolUseFailure` · `PostToolBatch` ·
`PermissionRequest` · `PermissionDenied`

Fim de turno: `Stop` · `StopFailure`

Subagentes e tarefas: `SubagentStart` · `SubagentStop` · `TaskCreated` ·
`TaskCompleted` · `TeammateIdle`

Contexto e modelo: `PreCompact` · `PostCompact` · `PreModelSwitch` · `PostModelSwitch`

Worktree: `WorktreeCreate` · `WorktreeRemove`

Outros: `Notification` · `Elicitation` · `ElicitationResult`

**Nem todos aceitam matcher.** Entre os que **não** aceitam: `UserPromptSubmit`,
`Stop`, `PostToolBatch`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`,
`WorktreeCreate`, `WorktreeRemove`, `MessageDisplay`, `CwdChanged`.

## Quais bloqueiam com exit 2

Bloqueiam: `PreToolUse` · `UserPromptSubmit` (e **apaga** o prompt) ·
`UserPromptExpansion` · `Stop` (a conversa continua) · `SubagentStop` ·
`PostToolBatch` · `TeammateIdle` · `TaskCreated` (desfaz a criação) · `TaskCompleted` ·
`ConfigChange` · `CwdChanged` · `WorktreeCreate` · `PreModelSwitch`

**Não** bloqueiam: `PermissionRequest` e `PermissionDenied` (usam campos próprios) ·
`PostToolUse` e `PostToolUseFailure` (a ferramenta já rodou; o stderr aparece) ·
`Notification` · `MessageDisplay` · `SessionEnd` · `StopFailure` · `SubagentStart` ·
`Elicitation` · `ElicitationResult`

## Matchers

| Valor | É lido como |
|---|---|
| `*`, vazio, ou omitido | casa tudo |
| letras, dígitos, `_`, `-`, espaço, `,`, `\|` | string exata ou lista de exatas |
| qualquer outro caractere | **expressão regular, sem âncoras** |

Regex sem âncora casa em qualquer posição — envolva em `^...$` para casar a string
inteira. Ferramentas de MCP seguem `mcp__<servidor>__<ferramenta>`, e para casar todas
as de um servidor o `.*` é obrigatório.

## O `Stop` hook e o teto de bloqueios

O Claude Code **sobrescreve** um `Stop` hook depois de um número de bloqueios seguidos
sem progresso. O evento traz um campo indicando que o hook já bloqueou; um hook que o
ignora se desliga sozinho, em silêncio.

*(O número e a variável de ambiente que o ajusta estão na fonte — são o tipo de valor
que muda.)*

## Onde declarar

`settings.json` de usuário, de projeto ou local · managed settings · `hooks/hooks.json`
de plugin · frontmatter de skill · frontmatter de subagente.

⚠️ **Frontmatter de subagente é ignorado para agentes de plugin.** Ver `armadilhas.md`.

⚠️ **Hooks de projeto, de frontmatter de skill e de frontmatter de subagente não rodam
em pasta não confiada** — e confiar na pasta pai não basta.

---

*Transcrição condensada das tabelas de eventos, códigos de saída, matchers e campos de
saída. Timeouts e o teto de bloqueios foram deixados de fora de propósito: são valores
numéricos, envelhecem primeiro, e vivem na fonte.*
