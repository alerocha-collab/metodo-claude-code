# Referência 03 — Mecanismos de extensão

Fonte: docs `features-overview`, `skills`, `sub-agents`, `hooks-guide`, `hooks`, `mcp`; *Steering Claude Code*; *Equipping agents for the real world with Agent Skills*; *Writing effective tools for agents*; *Code execution with MCP*.

---

## 1. O eixo de decisão

**Custo de contexto × autoridade da instrução.** Métodos baratos (skills, subagents, hooks) carregam seletivamente ou rodam fora do contexto; métodos caros (CLAUDE.md, output styles) sempre ocupam a janela mas carregam peso maior de aderência.

Corolário de projeto: **mantenha o contexto enxuto carregando sob demanda, e use ferramental determinístico para restrições duras** em vez de depender de aderência a prompt.

## 2. Skills

### Progressive disclosure em três níveis

1. `name` + `description` — pré-carregados no system prompt no startup.
2. Corpo do `SKILL.md` — carrega quando invocada ou quando o Claude julga relevante.
3. Arquivos auxiliares — só quando necessários.

**O corpo permanece em contexto entre turnos** depois de carregado. Cada linha é custo recorrente. Declare o que fazer; não narre como nem por quê.

### Frontmatter — campos de decisão arquitetural

| Campo | Decisão que ele resolve |
|---|---|
| `description` | **O gatilho.** Caso de uso principal primeiro. `description` + `when_to_use` truncam em **1.536 caracteres** na listagem |
| `when_to_use` | Frases-gatilho e exemplos de pedido. Conta para os 1.536 |
| `disable-model-invocation: true` | Workflow com **efeito colateral** que só o humano deve disparar. Também impede pré-carregamento em subagentes |
| `user-invocable: false` | Conhecimento de fundo que o humano não deve invocar |
| `allowed-tools` | Pré-aprova ferramentas durante o turno da invocação; expira na próxima mensagem do usuário |
| `disallowed-tools` | Remove ferramentas do pool enquanto ativa (ex.: tirar `AskUserQuestion` de um loop autônomo) |
| `context: fork` + `agent` + `background` | Roda a skill em subagente; `background: false` espera o resultado no mesmo turno |
| `paths` | Ativação automática limitada a globs de arquivo |
| `model` / `effort` | Modelo e esforço enquanto ativa; não persistem nas settings |
| `hooks` | Registra hooks na invocação, mantidos pelo resto da sessão |
| `arguments` / `argument-hint` | Substituição posicional `$nome` e autocomplete |

### Portabilidade — restrição importante

Fora do Claude Code (upload em claude.ai, Skills API, `package_skill.py`), **só valem** `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Qualquer outro campo faz o empacotamento **falhar com erro duro**, não ser ignorado.

**Decisão de projeto:** se a skill precisa ser portátil, projete-a sem `context: fork`, `paths`, `model`, `hooks`, `disable-model-invocation`.

### Código executável dentro da skill

Vantagens sobre gerar o equivalente em tokens: **eficiência** (rodar um algoritmo custa menos que gerá-lo), **confiabilidade** (determinístico e repetível), **preservação de contexto** (o script roda sem ser carregado). Deixe explícito na skill se o código deve ser **executado** ou **lido como referência**.

### Autoria

- **Comece pela avaliação**: rode o agente em tarefas representativas e observe onde ele trava ou pede contexto. Projete a skill contra a lacuna medida.
- **Divida quando crescer.** Mantenha separados os contextos "mutuamente exclusivos ou raramente usados".
- **Nome e descrição são o que dispara** — dê atenção desproporcional a eles.
- **Itere junto com o modelo**, capturando abordagens bem-sucedidas e erros comuns em contexto e código reutilizáveis.

### Segurança

Instale apenas de fontes confiáveis. Para fontes menos confiáveis, audite os arquivos empacotados — código, dependências, recursos — com atenção especial a instruções que mandem o Claude se conectar a fontes de rede externas.

## 3. Subagents

### Por que existem

Isolamento de contexto. O subagente lê muitos arquivos e devolve só o resumo. Benefícios adicionais: impor restrição de ferramenta e permissão; reutilizar configuração; **rotear tarefa para modelo mais barato** (Haiku); paralelismo.

### Frontmatter

| Campo | Decisão |
|---|---|
| `description` (obrigatório) | **Quando delegar.** Descrições combinadas > 15.000 tokens disparam aviso |
| `tools` / `disallowedTools` | Allowlist / denylist. `disallowedTools` é aplicada antes. `tools: Agent(worker, researcher)` restringe **quais subagentes** ele pode disparar |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, ID completo, ou `inherit` |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `skills` | Skills **pré-carregadas integralmente** no startup do subagente |
| `memory` | `user` / `project` / `local` — memória persistente própria, com `MEMORY.md` (200 primeiras linhas no system prompt) |
| `isolation: worktree` | Worktree git isolado |
| `maxTurns`, `effort`, `hooks`, `mcpServers`, `background` | Limites, esforço, hooks de ciclo de vida, MCP escopado |

### O que carrega — e o que não carrega

**Carrega:** system prompt próprio (o corpo markdown, **não** o do Claude Code) + ambiente; a mensagem de delegação; CLAUDE.md da hierarquia; snapshot do git status; skills do campo `skills`; lista de agentes irmãos para `SendMessage`.

**Não carrega:** histórico da conversa, output style da sessão principal, auto memory da sessão principal, skills já invocadas, arquivos já lidos. Os embutidos **Explore** e **Plan** pulam também CLAUDE.md e git status.

**Consequência de projeto:** o prompt de delegação é o único canal. Ele precisa carregar objetivo, formato de saída, orientação de ferramentas e fronteiras — nada é herdado.

### Precedência

managed > flag `--agents` > `.claude/agents/` > `~/.claude/agents/` > `agents/` de plugin.

### Subagent vs. fork vs. dynamic workflow

| | Contexto | Retorno | Use para |
|---|---|---|---|
| **Subagent** | Novo e isolado | Resumo (1.000–2.000 tokens) | Pesquisa, verificação, revisão |
| **Fork** (`/subtask`) | Herda **toda** a conversa, system prompt, ferramentas e modelo | Só o resultado final; one-shot, não retomável | Tarefa lateral que precisa do contexto completo |
| **Dynamic workflow** | Script que roda muitos subagentes | Um resultado | Trabalho que ultrapassa um punhado de subagentes; achados que precisam ser cross-checados |

Com subagentes, **o Claude** decide turno a turno o que roda; num workflow, **o script** decide.

### Quando *não* usar

Idas e vindas frequentes; trabalho multifásico que compartilha contexto (planejar → implementar → testar); mudança rápida e pontual; latência importa; trabalho que exige o histórico.

## 4. Hooks

> Instrução em CLAUDE.md ou skill é **pedido**. Hook é **garantia**. *"Se uma regra precisa valer sempre, faça dela um hook, não uma instrução de prompt."*

**Custo de contexto: zero**, salvo se retornar output.

### Eventos

| Categoria | Eventos |
|---|---|
| Sessão | `SessionStart`, `Setup`, `SessionEnd` |
| Prompt | `UserPromptSubmit`, `UserPromptExpansion` |
| Ferramentas | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` |
| Permissões | `PermissionRequest`, `PermissionDenied` |
| Subagentes e tarefas | `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle` |
| Fim de turno | `Stop`, `StopFailure` |
| Contexto | `PreCompact`, `PostCompact`, `InstructionsLoaded` |
| Ambiente | `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged` |
| Worktrees | `WorktreeCreate`, `WorktreeRemove` |
| Modelo | `PreModelSwitch`, `PostModelSwitch` |
| MCP | `Elicitation`, `ElicitationResult` |
| Interface | `Notification`, `MessageDisplay` |

### Tipos

`command` (shell, o padrão) · `http` (POST do evento) · `mcp_tool` (chama ferramenta em servidor já conectado) · `prompt` (avaliação LLM de um turno — para decisão que exige julgamento) · `agent` (verificação multi-turno com ferramentas; **experimental**).

### Combinação

Todos os hooks que casam com o evento **rodam até o fim** antes de os resultados serem combinados. Um `deny` **não** impede os irmãos de executarem — não confie nisso para suprimir efeito colateral. Em `PreToolUse`, a resposta mais restritiva vence: `deny` > `defer` > `ask` > `allow`. `additionalContext` de todos é preservado.

### Padrões canônicos

Format/lint pós-edição · bloqueio de paths protegidos · **reinjeção de contexto após compaction** · auditoria de mudança de configuração · recarga de ambiente em `CwdChanged` · auto-aprovação de permissões específicas · **`Stop` hook como portão de verificação** (o Claude Code encerra após 8 bloqueios consecutivos).

## 5. MCP e design de ferramentas

### Os cinco princípios

1. **Escolha as ferramentas certas.** Mais ferramentas não melhoram o resultado. Consolide por workflow, não por endpoint: um `schedule_event` em vez de `list_users` + `list_events` + `create_event`.
2. **Namespacing** por prefixo comum (`asana_search`, `jira_search`). Prefixo vs. sufixo tem "efeitos não triviais" — teste.
3. **Retorne contexto significativo.** **Identificadores semânticos, não UUIDs.** Considere um enum `response_format` (`concise` / `detailed`).
4. **Eficiência de tokens.** Paginação, filtragem, truncamento com defaults sensatos. Quando a resposta estourar, **oriente** o agente a uma busca mais focada. Erros devem comunicar melhorias acionáveis, não códigos.
5. **Prompt engineering das descrições.** Um dos métodos mais impactantes. Explicite contexto implícito, formatos de query, terminologia, relações entre recursos. `user_id`, não `user`. Refinamentos pequenos rendem melhorias dramáticas.

### Processo orientado a avaliação

Protótipo local → tarefas de avaliação ancoradas em workflows reais (múltiplas chamadas, casos de uso verdadeiros) → execução com métricas (acurácia, tempo, tokens, número de chamadas, erros) → análise, lembrando que *"o que os agentes omitem frequentemente importa mais do que o que incluem"* → **entregue os transcripts ao Claude Code e deixe-o refinar as implementações**. Ferramentas otimizadas pelo modelo superaram as escritas por humanos em conjuntos retidos.

### Code execution com MCP

**O problema em escala:** carregar todas as definições antecipadamente consome tokens massivos antes do pedido; resultados intermediários atravessam o contexto várias vezes.

**A solução:** servidores como árvore de arquivos (`servers/google-drive/getDocument.ts`), descobertos por navegação. No exemplo publicado, **150.000 → 2.000 tokens (−98,7%)**.

Ganhos: progressive disclosure; filtragem **no ambiente de execução** antes de retornar; controle de fluxo em código nativo (loops, condicionais, retry) em vez de encadear chamadas; **privacidade por padrão** (resultados intermediários não passam pelo modelo, e o cliente pode tokenizar PII); persistência de estado e acúmulo de funções reutilizáveis.

**Tradeoff a declarar:** exige ambiente de execução seguro com sandbox, limites de recurso e monitoramento. É custo de tokens e latência **contra** complexidade e superfície de segurança.

### Prefira CLI quando existir

*"Ferramentas CLI são a forma mais eficiente em contexto de interagir com serviços externos."* Instale `gh`; sem ele, requests não autenticados batem em rate limit. O modelo aprende CLIs desconhecidas: *"use `foo --help` para aprender a ferramenta, depois resolva A, B, C."*

Custo de MCP: tool search ligado por padrão — nomes carregam, schemas ficam adiados. `/context all` mostra tokens por ferramenta carregada.

## 6. Camadas e precedência

- **CLAUDE.md** é **aditivo** — todos os níveis contribuem. Em conflito, o modelo julga; o mais específico tende a prevalecer.
- **Skills e subagents** sobrescrevem **por nome**: managed > user > project (skills); managed > CLI > project > user > plugin (subagents). Skills de plugin são namespaced.
- **MCP** sobrescreve por nome: local > project > user.
- **Hooks** se **fundem** — todos disparam, qualquer que seja a origem.

## 7. Combinações produtivas

| Padrão | Mecânica |
|---|---|
| **Skill + MCP** | MCP dá a conexão; a skill ensina a usá-la (schema, padrões de query) |
| **Skill + Subagent** | Skill `/audit` dispara subagentes de segurança, performance e estilo em contexto isolado |
| **CLAUDE.md + Skill** | CLAUDE.md diz "siga nossas convenções de API"; a skill traz o style guide completo |
| **Hook + MCP** | Hook pós-edição notifica no Slack via MCP quando arquivo crítico muda |
| **Subagent + skills preloaded** | Subagente especialista com `skills:` carregando o corpo de conhecimento no startup |

## 8. Output styles — cuidado

Injetam no system prompt, nunca são compactados, carregam o **maior peso de aderência**. Mas **substituir o estilo padrão remove instruções críticas** sobre escopo, comentários, segurança e verificação de teste. Os embutidos (Proactive, Explanatory, Learning) cobrem a maioria dos casos. Use apenas para mudança significativa de papel.

`--append-system-prompt` é aditivo e por invocação — adequado a scripts, com retorno decrescente conforme se acumulam instruções.
