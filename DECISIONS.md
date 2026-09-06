# Decisões — repositório da metodologia

> Append-only. Entradas novas vão no fim; uma decisão se revoga com outra que a cite,
> nunca por edição. Formato em `plugins/metodo/templates/DECISIONS.md`.

---

## 001 — O plugin se chama `arquiteto`

**Data:** 2026-09-05 · **SHA:** commit inicial

**Contexto.** O nome vira prefixo de toda skill (`/<nome>:<skill>`) e será digitado
para sempre. Candidatos discutidos na sessão de planejamento: `fx` (curtíssimo,
opaco), `metodo` (equilíbrio), `axiom` (amarra à marca, mas sugere uma
especificidade que a metodologia não tem).

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

## 006 — Agente de plugin referencia skill do mesmo plugin pelo **nome puro**

**Data:** 2026-09-05 · **SHA:** `0ef60e0`

**Contexto.** A doc diz que skills são referenciadas pelo `name` no campo `skills:`,
mas não cobre o caso de agente e skill virem do mesmo plugin — onde as skills
aparecem namespaced (`metodo:arquiteto-claude-code`). Se o campo exigisse o prefixo,
o agente carregaria **sem** a doutrina, e a falha seria silenciosa: uma resposta
competente e genérica em vez de uma resposta ancorada.

**Decisão.** `skills:` usa o nome puro (`arquiteto-claude-code`). É como o agente
`arquiteto` está escrito, e é como os agentes das próximas fases serão escritos.

**Evidência.** O agente foi invocado como `metodo:arquiteto` com um prompt que **não
mencionava a skill nem caminho algum** — apenas "uma regra do meu projeto deve virar
hook ou entrada no CLAUDE.md?". A resposta exibiu quatro comportamentos que só
existem naquele `SKILL.md`: abriu por uma seção "Bloqueios" de uma pergunta com o
delta por resposta (a exceção prescrita quando falta enquadramento); citou "regra 3
das invioláveis" e as seções §2/§4/§8 por número; recusou o template de 10 seções
invocando o viés antisuperengenharia; e fechou por "Suposições e quando revisar".

**Alternativa descartada.** Prefixar (`metodo:arquiteto-claude-code`) por precaução.
Descartada porque a evidência aponta para o nome puro, e prefixar "por garantia" um
campo cujo comportamento agora conhecemos seria construir sobre superstição.

**Ressalva registrada.** O teste rodou num repositório que **contém** o plugin, e o
agente tem `Read`/`Glob`/`Grep` — não dá para excluir com certeza absoluta que tenha
encontrado a doutrina em disco. A evidência é forte porque o comportamento é
estrutural e imediato, não resultado de busca. O teste definitivo é invocar o agente
de um repositório que não contenha o plugin, o que acontece naturalmente na Fase 5.

**Como saber que envelheceu.** Se um agente do plugin passar a responder de forma
competente mas genérica — sem as marcas da doutrina — em outro repositório. É o
sinal de que o campo parou de resolver, e ele é silencioso: procure ativamente.

---

## 007 — A Fase 2 se parte em duas fatias; os papéis vêm antes do `/fluxo`

**Data:** 2026-09-05 · **SHA:** `9bd23e2`

**Contexto.** O plano define a Fase 2 como `/fluxo` + `construtor` + `operador` + o
`Stop` de verificação, numa fatia só. Isso contraria a decisão de método nº 1 —
fatia dimensionada pela janela, sessão = um ticket + commit. Uma fatia que entrega
quatro artefatos independentes não cabe numa sessão, e o handoff cai no meio.

Há também uma dependência real entre eles: o `/fluxo` é um leitor de estado, e o
estado que ele lê (tickets, commits por fatia, artefatos em disco) só passa a existir
quando os papéis estiverem operando.

**Decisão.** Duas fatias.

- **2a — os papéis e o portão.** `construtor` e `operador`, o `Stop` de verificação e
  o `PreToolUse` deny sobre os testes. É o que fecha o loop de verificação e converte
  sessão assistida em sessão da qual se pode sair.
- **2b — o `/fluxo`.** O orquestrador que lê estado, escrito depois que houver estado
  real para ler.

**Alternativa descartada.** Executar a Fase 2 como o plano a define, numa fatia só.
Custo: a fatia não cabe na sessão, e o `/fluxo` seria escrito contra estado
imaginado — projetando o leitor antes de existir o que ler.

**Como saber que envelheceu.** Se a 2a terminar e o formato do estado ainda estiver
em aberto, a 2b precisa de mais uma fatia antes dela, não menos.

---

## 008 — O core (Fase 3) vem antes do `/fluxo` · estende a 007

**Data:** 2026-09-05 · **SHA:** `85c3a1f`

**Contexto.** A decisão 007 adiou o `/fluxo` porque ele é um leitor de estado e o
estado ainda não existia. O argumento vale mais longe do que eu o levei: o estado que
o `/fluxo` lê é a **fila de tickets**, e o formato do ticket é entregue pela Fase 3,
não pela 2. Colocar o `/fluxo` como 2b apenas move o mesmo erro uma casa adiante.

**Decisão.** A ordem passa a ser: 2a (papéis e portão, feita) → **3 (core, começando
pelo formato do ticket)** → **`/fluxo`** → 4 (onboarding) → 5 (projeto de referência).

O `/fluxo` é o último item de fluxo a ser escrito, porque é o único que não produz
estado — só o lê.

**Alternativa descartada.** Escrever o `/fluxo` agora contra um formato de ticket
inventado na hora e ajustá-lo depois. Custo: o formato do ticket seria decidido pelo
que é fácil de ler, e não pelo que é certo de escrever — a cauda abanando o cachorro.

**Como saber que envelheceu.** Não envelhece; é ordem de dependência. Mas se a Fase 3
inteira for entregue e o `/fluxo` ainda parecer difícil de escrever, o problema é o
formato do estado, não o orquestrador.

---

## 009 — A revisão em dois eixos é **skill com subagentes**, não workflow de plugin

**Data:** 2026-09-06 · **SHA:** `ticket 002`

**Contexto.** A Fase 0 registrou workflow de plugin como candidato natural para a
revisão em dois eixos, porque workflows orquestram subagentes deterministicamente e
mantêm os resultados intermediários **fora da janela de contexto**. A decisão ficou
para o momento de olhar o problema.

**Decisão.** Skill que despacha dois subagentes em paralelo.

**O argumento que decidiu, e não é elegância: portabilidade.** Workflows são
oferecidos em planos pagos, API, Bedrock, Vertex e Foundry. Uma metodologia
distribuída como plugin que só funciona em parte dos ambientes falha no propósito que
motivou empacotá-la — viajar entre projetos e máquinas. Skill funciona em todos.

Dois argumentos de apoio:

- **Escada de complexidade.** Dois subagentes paralelos é o degrau mais baixo que
  entrega isolamento de contexto, que é o requisito real. Workflow é o degrau de
  orquestração determinística em escala — dezenas de agentes, resultados que não cabem
  na janela. Duas revisões de um diff não são isso.
- **O que o workflow compraria já se compra mais barato.** A garantia de não mesclar
  os eixos vem do contrato de retorno com teto de 400 palavras e de um formato de
  saída fixo — não da linguagem de orquestração.

**Alternativa descartada.** Workflow em `workflows/` do plugin, namespaced como
`/metodo:revisar`. Ganho real: a não-mesclagem passa a ser estrutural, garantida pelo
script, em vez de instruída. Custo: o plugin deixa de funcionar em parte dos
ambientes, e ganha um script para manter.

**Como saber que envelheceu.** Se os relatórios começarem a chegar mesclados ou
reordenados entre eixos na prática, a instrução não bastou e o argumento de "se compra
mais barato" caiu — aí o workflow se paga, com o custo de portabilidade assumido por
escrito. Também envelhece se workflows deixarem de ser gated por plano.

---

## 010 — Hooks no frontmatter de agente **não funcionam** para agentes de plugin

**Data:** 2026-09-06 · **SHA:** `ticket 003`

**Contexto.** O ticket 003 exercitou o portão numa sessão real, no papel `construtor`
carregado por `--plugin-dir`. **Resultado negativo nos dois casos que deveriam
bloquear:** o turno encerrou normalmente com a suíte deliberadamente vermelha, e uma
edição em `tests/testar_hooks.py` passou sem qualquer mensagem de hook.

**A causa não são os scripts.** Ambos foram exercitados na mesma sessão com o evento
real e responderam certo — `proteger_testes` saiu 2 com a mensagem de bloqueio, e
`verificar_suite` saiu 2 citando o comando da suíte. `python3` está disponível fora do
Git Bash (3.14.2 em PowerShell e cmd), o que descarta a hipótese do ticket 004.

**E não é `${CLAUDE_PLUGIN_ROOT}` sem resolver.** Se fosse, `python3` receberia um
caminho inexistente e sairia com **2**, e o turno teria sido *barrado*. Não foi barrado
nem executado: os hooks nunca foram invocados.

**A causa, na doc, verbatim** ([sub-agents](https://code.claude.com/docs/en/sub-agents.md),
tabela de frontmatter):

> `hooks` | No | Lifecycle hooks scoped to this subagent. **Ignored for plugin
> subagents**

A mesma página afirma que frontmatter hooks disparam quando o agente roda como sessão
principal via `--agent` — mas a exceção da tabela é mais específica e prevalece: **o
agente vem de um plugin, então seu `hooks:` é ignorado.**

**Decisão.** Os hooks saem do frontmatter dos agentes e vão para
`plugins/metodo/hooks/hooks.json`, que é o local documentado para hooks de plugin, com
**cláusula de guarda** no script para que a regra do papel não valha para todo mundo.

É exatamente o escape que a decisão de método nº 8 previa e preferia evitar —
*"funciona, mas é remendo"*. O remendo deixou de ser opcional.

**Consequência para a decisão de método nº 8.** O escopo do meio — "por papel, no
frontmatter do agente" — **não existe para agentes distribuídos por plugin**. Os
escopos viáveis passam a ser dois: universal (`settings.json` ou `hooks/hooks.json` do
plugin) e por fluxo (frontmatter da skill). O escopo por papel volta a depender de
guarda no script, e portanto de o script conseguir descobrir o papel — que é o que o
ticket 006 precisa determinar.

**Como saber que envelheceu.** Se a doc deixar de listar "Ignored for plugin
subagents". Revisar a cada atualização relevante do Claude Code.

**O que este resultado vale.** A P9 fecha pelo negativo, que é o desfecho mais útil
possível: os scripts estavam certos, a fiação estava errada, e sem exercitar ninguém
saberia — as 45 verificações passavam, e passariam para sempre.

---

## Pendências que este repositório carrega

Registradas aqui porque bloqueiam fases seguintes e se perdem se ficarem só na conversa.

| # | Pendência | Bloqueia |
|---|---|---|
| ~~P1~~ | **Resolvida.** As cópias de `~/.claude/` foram movidas para `~/.claude/_backup-arquiteto/`. Achado no caminho: renomear para `.bak` **não** tira uma skill de circulação — o Claude Code carrega skill pelo **diretório**, não pelo `name:` do frontmatter, e ela reapareceu como `arquiteto-claude-code.bak`. Agente sim exige `.md`. Apagar o backup só depois da P7. | — |
| ~~P8~~ | **Resolvida por eliminação.** A questão perdeu objeto: o `hooks:` do frontmatter nem é lido para agentes de plugin (decisão 010), então a resolução da variável ali nunca importou. Ela volta a importar em `hooks/hooks.json`, onde é documentada. | — |
| ~~P9~~ | **Fechada pelo negativo.** O portão não barrou: hooks no frontmatter são ignorados para agentes de plugin. Ver decisão 010; correção no ticket 006. | — |
| P2 | **Repositório GitHub: público ou privado.** Privado exige credencial git em toda máquina que instale. | Publicação |
| P3 | **`gh` não instalado** (ausente do PATH). Sem ele, requisições não autenticadas com rate limit. | Criação do repo remoto |
| ~~P10~~ | **Descartada como causa.** O ticket 003 confirmou `python3` 3.14.2 disponível em PowerShell e cmd, fora do Git Bash. A dependência segue não declarada — isso é o ticket 004, não uma pendência solta. | — |
| P4 | **Bump de `version` a cada release.** Sem isso, quem instalou fica com a cópia em cache. Candidato a item de checklist ou hook. | Publicação |
| P5 | **CI: `claude plugin validate --strict` no GitHub Actions a cada push.** `--strict` promove avisos a erros; é a forma pensada para CI. Fecha na metodologia uma lacuna identificada na auditoria do projeto de referência. | Fase 2+ |
| ~~P7~~ | **Resolvida com ressalva** — ver decisão 006. Nome puro funciona. Ressalva: o teste rodou num repo que contém o plugin; confirmação definitiva na Fase 5. | — |
| ~~P6~~ | **Resolvida.** Fase 0 fechada; achados e consequências em [docs/fase-0-mecanismos.md](docs/fase-0-mecanismos.md). | — |
