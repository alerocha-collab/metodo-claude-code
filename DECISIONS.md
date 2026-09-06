# Decisões — repositório da metodologia

> Append-only. Entradas novas vão no fim; uma decisão se revoga com outra que a cite,
> nunca por edição. Formato em `plugins/metodo/templates/DECISIONS.md`.

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
exemplo). Descartada por ser churn sem ganho: o namespacing garante unicidade, e o
custo é estético.

**Consequência confirmada na doc.** Agentes de plugin são nomeados
`plugin-name:agent-name` no typeahead ([plugins-reference](https://code.claude.com/docs/en/plugins-reference.md)).
Este agente aparecerá como **`arquiteto:arquiteto`**. Funciona; lê mal.

**Como saber que envelheceu.** Se `arquiteto:arquiteto` no typeahead incomodar o
suficiente para justificar o rename — o momento barato de fazê-lo é antes de
qualquer outro projeto instalar o plugin.

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

## 005 — O plugin passa a se chamar `metodo` · revoga a 001

**Data:** 2026-09-05 · **SHA:** `ccf7887`

**Contexto.** A decisão 001 escolheu `arquiteto` e registrou como custo assumido a
colisão com o agente de mesmo nome. A doc então confirmou que agentes de plugin são
namespaced (`plugin:agente`), o que tornou o custo concreto e visível:
`arquiteto:arquiteto` no typeahead. Além disso, `arquiteto` nomeia **uma parte** do
plugin — o agente de arquitetura de harness — enquanto o plugin é a metodologia
inteira. O nome descrevia o componente, não o conjunto.

**Decisão.** O plugin se chama `metodo`. Skills passam a ser `/metodo:<skill>`; o
agente passa a ser `metodo:arquiteto`. Diretório renomeado para `plugins/metodo/`.

**Alternativa descartada.** Manter `arquiteto` (decisão 001) e conviver com
`arquiteto:arquiteto`. Descartada porque o custo de renomear só cresce: hoje é
`git mv` mais quatro arquivos; depois de publicar, é quebrar toda instalação
existente e todo caminho já escrito por terceiros.

**Consequências.** A colisão que motivou a decisão 003 deixa de existir — 003 fica
sem objeto, e o agente mantém o nome `arquiteto` sem custo. As decisões 001 a 004
seguem registradas com os caminhos `plugins/arquiteto/` que eram verdade quando
foram escritas; o caminho atual é `plugins/metodo/`.

**Como saber que envelheceu.** Se o plugin deixar de ser uma metodologia e virar
outra coisa. Enquanto for método, o nome descreve.

---

## Pendências que este repositório carrega

Registradas aqui porque bloqueiam fases seguintes e se perdem se ficarem só na conversa.

| # | Pendência | Bloqueia |
|---|---|---|
| P1 | **Duplicata do agente `arquiteto` e da skill `arquiteto-claude-code`** — agente e skill existem agora em `~/.claude/` **e** no plugin. Definições de usuário sobrescrevem as de plugin com mesmo nome, então a cópia de `~/.claude` é a que vale. Remover de lá só depois de confirmar o plugin carregando. | Verificação da Fase 1 |
| P2 | **Repositório GitHub: público ou privado.** Privado exige credencial git em toda máquina que instale. | Publicação |
| P3 | **`gh` não instalado** (ausente do PATH). Sem ele, requisições não autenticadas com rate limit. | Criação do repo remoto |
| P4 | **Bump de `version` a cada release.** Sem isso, quem instalou fica com a cópia em cache. Candidato a item de checklist ou hook. | Publicação |
| P5 | **CI: `claude plugin validate --strict` no GitHub Actions a cada push.** `--strict` promove avisos a erros; é a forma pensada para CI. Fecha na metodologia a lacuna de "sem CI" identificada no FirstAxiom. | Fase 2+ |
| P7 | **`skills:` no frontmatter de agente de plugin: nome puro ou namespaced?** A doc diz que skills são referenciadas pelo `name`, mas **não cobre** o caso de agente e skill no mesmo plugin. O agente `arquiteto` declara `skills: [arquiteto-claude-code]`; se o correto for `metodo:arquiteto-claude-code`, ele carrega sem a doutrina. Resolver por teste empírico ao carregar com `--plugin-dir`. | Verificação da Fase 1 |
| P6 | **Fase 0 incompleta** — falta ler: dynamic workflows, `/batch`, scheduled tasks, `context: fork` em skill, statusline, `/doctor`, checkpointing. Nenhum bloqueia a Fase 1; todos importam da Fase 2 em diante. | Fase 2 |
