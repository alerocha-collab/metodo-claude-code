# Referência 06 — Fontes

Use para citar a URL exata ao sustentar uma recomendação. Toda afirmação normativa no documento de arquitetura deve apontar para uma destas.

---

## Blog de engenharia — `anthropic.com/engineering`

### Base doutrinária das referências 01–05

| Artigo | URL | O que sustenta |
|---|---|---|
| Building effective agents | `/engineering/building-effective-agents` | Workflow vs. agente; os 5 padrões; simplicidade/transparência/ACI |
| Effective context engineering for AI agents | `/engineering/effective-context-engineering-for-ai-agents` | Context rot; altitude do prompt; just-in-time vs. pré-recuperação; compaction, note-taking, subagentes |
| Equipping agents for the real world with Agent Skills | `/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Progressive disclosure; autoria de skills; código executável; segurança de skills |
| Writing effective tools for agents — with agents | `/engineering/writing-tools-for-agents` | Os 5 princípios de ferramenta; desenvolvimento orientado a avaliação |
| Code execution with MCP | `/engineering/code-execution-with-mcp` | 150k→2k tokens; filesystem como descoberta; privacidade por padrão; tradeoff de sandbox |
| How we built our multi-agent research system | `/engineering/multi-agent-research-system` | +90,2%; 15× tokens; 7 princípios de prompt; 1.000–2.000 tokens de retorno |
| Harness design for long-running application development | `/engineering/harness-design-long-running-apps` | Gerador/avaliador; sprint contracts; handoff por arquivo; obsolescência do harness; 20min/$9 vs 6h/$200 |
| Effective harnesses for long-running agents | `/engineering/effective-harnesses-for-long-running-agents` | Inicializador vs. executor; lista de features em JSON; `init.sh`; matriz de falha |
| Building a C compiler with a team of parallel Claudes | `/engineering/building-c-compiler` | Verificador quase perfeito; task locking; especialização; teste diferencial |
| Demystifying evals for AI agents | `/engineering/demystifying-evals-for-ai-agents` | Vocabulário; 3 graders; pass@k vs. pass^k; roteiro; Queijo Suíço |
| Beyond permission prompts | `/engineering/claude-code-sandboxing` | Fadiga de aprovação; 84%; filesystem + rede |
| How we built Claude Code auto mode | `/engineering/claude-code-auto-mode` | 93% de aprovação cega; classificador em 2 estágios; deny-and-continue; 0,4%/17%/5,7% |
| How we contain Claude across products | `/engineering/how-we-contain-claude` | Três camadas; três padrões de contenção; falhas reais |

### Demais artigos do índice

`/engineering/managed-agents` · `/engineering/advanced-tool-use` · `/engineering/AI-resistant-technical-evaluations` · `/engineering/infrastructure-noise` · `/engineering/eval-awareness-browsecomp` · `/engineering/desktop-extensions` · `/engineering/claude-think-tool` · `/engineering/contextual-retrieval` · `/engineering/swe-bench-sonnet` · `/engineering/a-postmortem-of-three-recent-issues` · `/engineering/april-23-postmortem`

## Documentação oficial — `code.claude.com/docs/en/`

| Página | Cobre |
|---|---|
| `best-practices` | Verificação, Explore→Plan→Code→Commit, CLAUDE.md, sessões, fan-out, antipadrões. É o destino atual do antigo `/engineering/claude-code-best-practices` |
| `features-overview` | Tabela de mecanismos, custo de contexto por feature, gatilhos de adoção, camadas |
| `memory` | CLAUDE.md, hierarquia, `.claude/rules/`, auto memory, managed CLAUDE.md |
| `skills` | Frontmatter completo, portabilidade, `context: fork`, evals de skill, troubleshooting |
| `sub-agents` | Frontmatter, precedência, o que carrega no startup, forks, memória persistente |
| `hooks-guide` / `hooks` | Eventos, tipos, matchers, combinação, exit codes |
| `mcp` | Escopo, tool search, reconexão |
| `permissions`, `sandboxing`, `managed-settings` | Modelo de permissão e enforcement |
| `workflows` | Dynamic workflows |
| `llms.txt` | Índice completo da documentação |

## Blog de produto

**Steering Claude Code: when to use CLAUDE.md, skills, hooks, rules, subagents and more** — `claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more`

Sustenta: o eixo custo de contexto × autoridade; os sete métodos de direcionamento; a tabela de antipadrões → correção; o alerta sobre output styles.

## GitHub — `github.com/anthropics`

| Repositório | Uso arquitetural |
|---|---|
| `anthropics/skills` | Skills de exemplo, **a spec Agent Skills** (`./spec/`), template (`./template/`), `package_skill.py` |
| `anthropics/claude-code` | O produto; issues e discussões |
| `anthropics/claude-agent-sdk-python` | Construir agentes sobre o mesmo harness |
| `anthropics/sandbox-runtime` | Sandbox de filesystem e rede em nível de SO, sem container |
| `anthropics/claude-code-action` | Integração com GitHub Actions |
| `anthropics/claude-plugins-official` | Diretório oficial de plugins |
| `anthropics/claude-cookbooks` | Receitas de uso |
| `anthropics/prompt-eng-interactive-tutorial` | Tutorial de prompt engineering |

Spec aberta de skills: **agentskills.io**

## Nota de datação

Estas orientações envelhecem em dois eixos, e o documento de arquitetura deve dizer isso:

1. **Versão do Claude Code** — a documentação cita comportamentos atrelados a versões (`v2.1.196`, `v2.1.206`, `v2.1.214`, `v2.1.218`, `v2.1.234`, `v2.1.239`). Confira contra a versão instalada antes de depender de um campo.
2. **Capacidade do modelo** — recomendações de harness são relativas. O caso Opus 4.5 → 4.6 eliminou componentes inteiros. **Ao chegar um modelo novo, remova componentes e meça.**

Auto mode, agent teams e agent view estão em estágios diferentes de disponibilidade (padrão por plano, experimental, research preview).
