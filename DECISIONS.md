# Decisões — repositório da metodologia

> Append-only. Entradas novas vão no fim; uma decisão se revoga com outra que a cite,
> nunca por edição. Formato em `plugins/arquiteto/templates/DECISIONS.md`.

---

## 001 — O plugin se chama `arquiteto`

**Data:** 2026-09-05 · **SHA:** commit inicial

**Contexto.** O nome vira prefixo de toda skill (`/<nome>:<skill>`) e será digitado
para sempre. Candidatos discutidos na sessão de planejamento: `fx` (curtíssimo,
opaco), `metodo` (equilíbrio), `axiom` (amarra à marca, mas sugere especificidade ao
FirstAxiom que a metodologia não tem).

**Decisão.** `arquiteto`.

**Alternativa descartada.** `metodo` e `fx`. Custo assumido: colisão de nome com o
agente `arquiteto` que o plugin distribui — ver decisão 003.

**Como saber que envelheceu.** Se o plugin crescer para além de metodologia de
engenharia e o nome passar a descrever mal o conteúdo.

---

## 002 — O plugin mora em `plugins/arquiteto/`, não na raiz do repo

**Data:** 2026-09-05 · **SHA:** commit inicial

**Contexto.** O plano prevê que este repositório seja, no futuro, marketplace **e**
host do plugin. Um marketplace aponta seus plugins por `"source"` relativo à raiz.

**Decisão.** Plugin em `plugins/arquiteto/` desde a Fase 1. Adicionar
`.claude-plugin/marketplace.json` depois vira acrescentar um arquivo, não
reorganizar a árvore.

**Alternativa descartada.** Plugin na raiz do repo (`./.claude-plugin/plugin.json`,
`./skills/`, `./agents/`). É o layout mais simples enquanto não há marketplace, e o
custo de migrar depois é mover tudo e quebrar todo caminho já escrito.

**Como saber que envelheceu.** Se a decisão de nunca publicar via marketplace for
tomada, o nível extra de pasta vira cerimônia.

---

## 003 — O agente `arquiteto` mantém o nome dentro do plugin `arquiteto`

**Data:** 2026-09-05 · **SHA:** commit inicial

**Contexto.** O plugin se chama `arquiteto` (decisão 001) e distribui um agente
também chamado `arquiteto`, migrado de `~/.claude/agents/`. O nome do agente já está
em uso e renomeá-lo quebra a invocação por nome.

**Decisão.** Manter os dois nomes. O agente continua `arquiteto`.

**Alternativa descartada.** Renomear o agente (para `arquiteto-harness`, por
exemplo). Descartada por ser churn sem ganho enquanto não houver conflito observado.

**Como saber que envelheceu.** Se a invocação do agente ficar ambígua na prática —
namespacing do plugin colidindo com o `name:` do frontmatter. Verificar ao carregar
o plugin com `--plugin-dir` pela primeira vez.

---

## 004 — A skill `arquiteto-claude-code` migra junto com o agente

**Data:** 2026-09-05 · **SHA:** commit inicial

**Contexto.** O frontmatter do agente `arquiteto` declara
`skills: [arquiteto-claude-code]`. Migrar só o agente deixaria o plugin com uma
dependência satisfeita apenas nesta máquina — o oposto da portabilidade que motivou
empacotar como plugin.

**Decisão.** Skill migrada inteira (SKILL.md + os sete arquivos de `references/`)
para `plugins/arquiteto/skills/`.

**Alternativa descartada.** Deixar a skill em `~/.claude/skills/` e o agente
depender dela. Custo: o plugin não funciona em outra máquina.

**Como saber que envelheceu.** Não envelhece — é pré-requisito de portabilidade.
Mas as cópias em `~/.claude/` agora são duplicatas: ver "Pendências".

---

## Pendências que este repositório carrega

Registradas aqui porque bloqueiam fases seguintes e se perdem se ficarem só na conversa.

| # | Pendência | Bloqueia |
|---|---|---|
| P1 | **Duplicata do `arquiteto`** — agente e skill existem agora em `~/.claude/` **e** no plugin. Definições de usuário sobrescrevem as de plugin com mesmo nome, então a cópia de `~/.claude` é a que vale. Remover de lá só depois de confirmar o plugin carregando. | Verificação da Fase 1 |
| P2 | **Repositório GitHub: público ou privado.** Privado exige credencial git em toda máquina que instale. | Publicação |
| P3 | **`gh` não instalado** (ausente do PATH). Sem ele, requisições não autenticadas com rate limit. | Criação do repo remoto |
| P4 | **Bump de `version` a cada release.** Sem isso, quem instalou fica com a cópia em cache. Candidato a item de checklist ou hook. | Publicação |
| P5 | **CI: `claude plugin validate` no GitHub Actions a cada push.** Fecha na metodologia a lacuna de "sem CI" identificada no FirstAxiom. | Fase 2+ |
| P6 | **Fase 0 incompleta** — falta ler: dynamic workflows, `/batch`, scheduled tasks, `context: fork` em skill, statusline, `/doctor`, checkpointing. Nenhum bloqueia a Fase 1; todos importam da Fase 2 em diante. | Fase 2 |
