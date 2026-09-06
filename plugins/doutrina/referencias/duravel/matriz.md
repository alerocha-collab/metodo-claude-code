# A matriz: um mecanismo por linha, quatro eixos

Referência da skill `onde-colocar`. Carregue quando a árvore de decisão não bastar —
tipicamente quando o caso está entre dois mecanismos.

**Autoridade** é a coluna que a documentação oficial não tem. `P` = pedido (o modelo
decide se obedece) · `GC` = garantia condicional (dispara sempre, mas pode falhar) ·
`GD` = garantia dura (aplicada pelo cliente, independe do modelo).

## Instruções e conhecimento

| Mecanismo | Onde vive | Quando carrega | Custo | Autoridade | Sobrevive a `/compact` |
|---|---|---|---|---|---|
| `CLAUDE.md` do projeto | raiz do repo | início de sessão | **todo request** | P | **sim**, relido do disco |
| `CLAUDE.md` do usuário | `~/.claude/` | início de sessão | todo request | P | sim |
| `CLAUDE.md` aninhado | subdiretório | quando o Claude lê arquivo ali | quando carrega | P | **não** — só se um arquivo daquela pasta for lido de novo |
| `CLAUDE.local.md` | raiz, gitignored | com o `CLAUDE.md` | todo request | P | sim |
| Rule sem `paths:` | `.claude/rules/` | início de sessão | todo request | P | sim |
| Rule com `paths:` | `.claude/rules/` | quando um arquivo casa o glob | só então | P | **não** — recarrega se o arquivo voltar |
| Skill (auto) | `skills/<n>/SKILL.md` | descrição no início; corpo ao usar | descrição sempre | P | corpo sim, **índice de descrições não** |
| Skill com `disable-model-invocation` | idem | só quando você digita `/nome` | **zero** até invocar | P | corpo sim |
| Output style | `output-styles/` | início de sessão | system prompt | P | sim (não é histórico) |
| Auto memory | `~/.claude/projects/` | início de sessão | primeiras linhas do índice | P | sim, relida do disco |

**A distinção de camada que mais se confunde:** output style altera **o system prompt
em si**; `CLAUDE.md` é entregue como mensagem de usuário depois do system prompt. Por
isso um substitui instruções nativas e o outro se soma a elas.

## Execução e isolamento

| Mecanismo | Onde vive | Quando roda | Custo no contexto principal | Autoridade |
|---|---|---|---|---|
| Subagente | `agents/*.md` | quando invocado | **isolado** — só o resumo volta | P (dentro dele) |
| Skill com `context: fork` | frontmatter | quando invocada | isolado | P |
| Dynamic workflow | `workflows/*.js` | quando invocado | isolado — intermediários em variáveis | — |
| Sessão em background | agent view | você despacha | zero (outra sessão) | — |
| Teammate | agent teams | o lead cria | zero (outra sessão) | — |

**Onde vivem os resultados intermediários** é o que decide entre estes. Contexto do
Claude (subagente) · lista de tarefas compartilhada (teams) · variáveis de script
(workflow). É a razão física por trás da escolha, não preferência.

## Garantia

| Mecanismo | Onde vive | Quando dispara | Custo | Autoridade |
|---|---|---|---|---|
| Hook | `settings.json`, `hooks/hooks.json` de plugin, frontmatter de skill | no evento | **zero**, salvo o que ele devolver | **GC** |
| `permissions.allow/ask/deny` | `settings.json` | antes de toda chamada de ferramenta | zero | **GD** |
| Sandbox de SO | `settings.json` | envolve o processo | zero | **GD** |
| Managed settings | política da organização | sempre | zero | **GD**, e não sobreponível |

**Hook não é garantia dura**, e a diferença aparece exatamente quando importa: ele não
roda em pasta não confiada, pode dar timeout, e um exit code que não seja o de bloqueio
deixa a ação passar. Para "nunca, em hipótese alguma", a resposta é `permissions.deny`.

## Ferramentas externas

| Mecanismo | Onde vive | Quando carrega | Custo | Autoridade |
|---|---|---|---|---|
| MCP server | `.mcp.json`, ou plugin | conecta no início | nomes das tools; schemas sob demanda | — |
| Plugin | marketplace ou `--plugin-dir` | quando habilitado | o que ele contiver | herda de cada peça |

**MCP é para o que está fora.** Arquivo do próprio repositório já é alcançável — expor
o filesystem como MCP é acrescentar uma camada que não compra nada.

## Como escolher entre os dois que mais se confundem

**Skill ou subagente?** A skill roda **no seu contexto** e se soma a ele; o subagente
roda **em contexto separado** e devolve só o resumo. Se você quer que o conhecimento
influencie a conversa atual, skill. Se quer que o trabalho aconteça longe dela, subagente.

**Skill ou hook?** A skill é interpretada e o resultado varia; o hook dispara sempre no
evento dele. Se a frase que descreve a regra tem "sempre" ou "nunca", é hook — ou
`permissions`, se for "nunca".

**Rule ou CLAUDE.md?** Se vale para o repositório inteiro, `CLAUDE.md`. Se vale para
uma linguagem, uma pasta ou um tipo de arquivo, rule com `paths:` — e ela só custa
contexto quando aquele tipo de arquivo aparece. Em repositório grande essa diferença
é a maior economia disponível.

**Skill ou plugin?** Não é a mesma pergunta: plugin é **empacotamento**. Comece em
`.claude/` e converta quando um segundo repositório precisar do mesmo.

---

*Fontes: `features-overview`, `claude-directory`, `context-window`, `memory`, `skills`,
`hooks`, `permissions`, `mcp`, `plugins`, `sub-agents`, `workflows`. A coluna de
autoridade e a classificação em três níveis são síntese autoral.*
