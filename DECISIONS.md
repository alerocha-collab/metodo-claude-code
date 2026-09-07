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

## 011 — O portão funciona; e o exercício encontrou um bug que os testes não pegavam

**Data:** 2026-09-06 · **SHA:** `ticket 006`

**O que foi verificado numa sessão real** (Windows 11, PowerShell,
`claude --plugin-dir ./plugins/metodo --agent metodo:construtor` — esta forma do
`--agent`, com o nome namespaced, **funciona**):

| Caso | Resultado |
|---|---|
| 1 — suíte vermelha, árvore suja | **Barrado** pelo `verificar_suite.py` |
| 2 — editar teste existente | **Negado** pelo `proteger_testes.py` em `PreToolUse:Edit` |
| 3 — criar teste novo | **Permitido** |
| 5 — a mensagem é a do portão | Confere, citando `python3 tests/testar_tudo.py` |
| 4 e 6 | **Inconclusos** — ver o bug abaixo |

`${CLAUDE_PLUGIN_ROOT}` **resolve** em `hooks/hooks.json`, confirmado pelo caminho que
apareceu no erro do hook e pela variável de ambiente:
`CLAUDE_PLUGIN_ROOT=C:/Users/alero/Downloads/Projetos/plugin/plugins/metodo`.

### O bug: codificação do stdin

O caso 4 ficou inconcluso porque o hook **caiu**, e caiu por culpa própria:

> `UnicodeDecodeError('charmap', ..., 'character maps to <undefined>')`

O Claude Code manda **UTF-8** no stdin. O Python do Windows decodifica com a
codificação do console, **cp1252**. O evento carrega `last_assistant_message`, e a
mensagem de um agente é cheia de tabela, seta e emoji — tudo fora do cp1252. Qualquer
resposta com uma tabela derrubava o portão.

**A rede de segurança segurou.** O `except BaseException` converteu a queda em exit 2,
então o portão *bloqueou* em vez de liberar — fail-open evitado. Mas virou **falso
positivo**, que é caro justamente porque com hook não se negocia.

Correção: ler `sys.stdin.buffer` e decodificar UTF-8 explicitamente, e reconfigurar
`stderr` para UTF-8 com `errors="replace"`. Três casos novos na suíte, rodando com
`PYTHONIOENCODING=cp1252` forçado — sem forçar, eles passariam em qualquer máquina
com locale UTF-8 e não provariam nada.

**O que isso diz.** As 45 verificações passavam porque o arnês de teste rodava com o
locale UTF-8 do Git Bash. O bug só existia no caminho real, com o shell real, com
conteúdo real. É a mesma lição do ticket 003, agora numa camada mais funda: **testar o
script não é testar o sistema.**

### Descoberta que muda uma decisão anterior

O diagnóstico revelou que o hook **recebe o papel**:

```
"agent_type": "metodo:construtor"
CLAUDE_CODE_AGENT=metodo:construtor
```

Ou seja, a cláusula de guarda **poderia** ter sido por papel, ao contrário do que a
decisão 010 supôs. Mantenho a guarda por árvore suja mesmo assim: *"verifique o que
você mudou"* continua sendo regra melhor que *"verifique por causa de quem você é"* —
vale para papéis que ainda não existem e não depende de campo que a doc não documenta.
Mas o campo existe, está registrado aqui, e é o caminho se a guarda atual se mostrar
grosseira demais.

**Como saber que envelheceu.** Se `agent_type` sumir do evento, nada quebra — a guarda
não o usa. Se a guarda por árvore suja liberar um caso que deveria barrar, `agent_type`
é o refinamento disponível.

---

## 012 — O portão está verificado de ponta a ponta · completa a 011

**Data:** 2026-09-06 · **SHA:** `ticket 006`

A decisão 011 registrou os casos 4 e 6 como inconclusos, porque o bug de codificação
derrubava o hook antes de ele avaliar qualquer coisa. Com a correção, a rodada nova
fechou os dois — e com eles o roteiro inteiro.

| Caso | O que prova | Resultado |
|---|---|---|
| 1 | suíte vermelha + árvore suja **barra** | ✅ |
| 2 | editar teste existente é **negado** (`PreToolUse:Edit`) | ✅ |
| 3 | criar teste novo é **permitido** | ✅ |
| 4 | some o vermelho, o turno **encerra** | ✅ |
| 5 | quem barrou foi o portão, com o comando citado | ✅ |
| 6 | **árvore limpa + suíte vermelha encerra** — a cláusula de guarda | ✅ |

O caso 6 chegou por um caminho diferente do previsto: o roteiro manda commitar para
limpar a árvore, e o que houve foi um `git checkout --` descartando a única mudança
pendente. O estado medido é o mesmo — suíte vermelha, árvore limpa — e o turno
encerrou. **É a prova de que o `operador` não será barrado por vermelho que não criou.**

### O que o exercício manual mede, e o que não mede

Observação que vale guardar, porque delimita quando repeti-lo: os casos 3 e 6 já têm
cobertura automatizada em `testar_hooks.py`. O roteiro manual não existe para provar
que a **lógica** dos hooks está certa — isso a suíte faz melhor e mais barato. Ele
existe para provar que os hooks estão **instalados e sendo chamados**.

São falhas de natureza diferente, e só a segunda é invisível para a suíte. Foi
exatamente ela que apareceu duas vezes: o `hooks:` do frontmatter sendo ignorado
(decisão 010) e a queda por codificação no caminho real (decisão 011).

**Quando repetir o roteiro:** ao mudar onde os hooks são declarados, ao atualizar o
Claude Code, e ao rodar em plataforma nova. Não a cada mudança de lógica.

**Cobertura registrada:** Windows 11, PowerShell 5.1, `claude --plugin-dir` com
`--agent metodo:construtor`. macOS e Linux seguem não verificados, e lá o shell dos
hooks é outro.

---

## 013 — As skills de entrada são escritas, não adaptadas de terceiro

**Data:** 2026-09-06 · **SHA:** `ticket 010`

**Contexto.** O plugin cobria da metade do pipeline em diante. As duas etapas de
entrada — fechar decisões em aberto, e construir o vocabulário num projeto novo — só
existiam como skills de terceiro instaladas em `~/.claude/skills/`, sob MIT. Instalado
noutra máquina, o plugin começava no meio.

**Decisão.** Escrever as duas: `decidir` e `dominio`.

**Alternativa descartada.** Adaptar as skills de referência com atribuição MIT.
Custo evitado: um repositório meio original e meio fork, com duas vozes e dois modelos
de manutenção — o arquivo de procedência daquele set já registrava duas modificações
locais cinco dias depois da instalação.

**Honestidade sobre a influência.** Este set foi estudado a fundo, e a análise cruzada
em `docs/` o cita com licença e commit. A mecânica de entrevistar em rodadas por
fronteira é convergente o bastante para que qualquer um chegue nela partindo do mesmo
problema — mas fingir origem independente seria desonesto, e registrar a influência
custa uma linha.

**O que as nossas fazem diferente, e por quê:**

| Nossa | Diferença | De onde vem |
|---|---|---|
| `decidir` | Abre decidindo **se** entrevistar, por três gatilhos | Decisão de método nº 7: gatilho, não regra |
| `decidir` | Usa `AskUserQuestion` em vez de rodadas em markdown | A ferramenta nativa devolve escolha estruturada |
| `decidir` | Exige **custo declarado** em cada opção | Opção sem desvantagem é opção já escolhida, apresentada como pergunta |
| `decidir` | Termina escrevendo no `DECISIONS.md` | Decisão de método nº 3 |
| `dominio` | Duas camadas: `DECISIONS.md` **abaixo** da barra do ADR | Este repositório tem 13 decisões e **zero** ADRs — com a barra só de ADR, teria perdido as 13 |
| `dominio` | Nomeia a divergência com a trilha de reengenharia como **achado** | O glossário do código quase nunca é o que as pessoas dizem |

**Como saber que envelheceu.** Se a `decidir` na prática só confirmar o que já se
sabia, o gatilho está frouxo demais. Se a `dominio` produzir glossário que ninguém
lê, ela está aceitando termo demais — a regra do "aparece uma vez só não entra"
existe para isso.

---

## 014 — O detector de desatualização **reporta**; não bloqueia

**Data:** 2026-09-06 · **SHA:** `ticket 011`

**Contexto.** A decisão de método nº 3 diz, sobre o documento de arquitetura
carimbado: *"o hook roda `git diff <sha>..HEAD --stat` e avisa ou bloqueia. Faça."* E
adiante: *"O hook detecta e bloqueia. Nunca atualiza."*

**Decisão.** Implementado como **script que reporta**, não como hook que bloqueia.
`verificar_documento.py` mede a distância e sai 1 quando há distância. Nada no
repositório o dispara automaticamente.

**A parte da decisão nº 3 que foi preservada é a que importa: ele nunca atualiza.** A
ênfase daquele texto está no contraste entre *detectar* e *curar sozinho* — e essa
metade está inteira, com caso de teste provando que o script não altera o documento
que lê.

**Alternativa descartada.** `Stop` hook bloqueando o fim do turno enquanto o
documento estiver atrasado. Custo, e é alto: o documento fica legitimamente atrasado
durante toda uma fase — é para isso que ele serve, descrever o fim da fase anterior.
Bloquear por isso seria bloquear semanas seguidas de trabalho correto. Falso positivo
em hook é caro porque **com hook não se negocia**, e um portão que barra todo dia
ensina a desligar portões.

**A distinção que sustenta a divergência.** Suíte vermelha e documento atrasado não
são a mesma classe de coisa. A primeira diz que **o que você acabou de fazer está
errado**; a segunda, que **um artefato descreve um estado anterior** — o que é
normal, esperado, e às vezes correto. Só a primeira justifica portão.

**Como saber que envelheceu.** Se o documento ficar meses atrasado sem ninguém
notar, o relato não bastou e a pergunta volta — provavelmente como aviso em
`SessionStart`, que é visível sem ser bloqueante, e não como `Stop`.

---

## 015 — O `doutrina` revisou o `metodo`, e o custo de contexto foi medido

**Data:** 2026-09-06 · **SHA:** `ticket 018-020`

**Contexto.** O `doutrina` foi construído para um agente decidir arquitetura. O
primeiro uso real dele foi revisar o `metodo` — e é o teste honesto: se a destilação
não muda uma decisão, ela não serve.

**Mudou quatro.** Três defeitos e uma medição, e nenhum deles eu tinha visto sozinho,
apesar de ter escrito o código dos dois hooks.

| Achado | De qual ficha veio | Fatia |
|---|---|---|
| Config não encontrada em monorepo | `distribuir` — settings não são herdadas de pai | 018 |
| Hooks agindo em repositório que não adotou | `precedencias` — hooks se fundem, não se sobrescrevem | 018 |
| Nenhuma camada de garantia dura | `onde-colocar` — três níveis de autoridade | 019 |
| Descrição ocupando 20% do orçamento | `escrever-skill` — descrição gorda empurra as vizinhas | 020 |

**Decisão sobre o orçamento de contexto.** As descrições das skills dos dois plugins
somavam **4.970 caracteres**; passaram a **4.462** depois de estreitar a da
`arquiteto-claude-code`, de 994 para 486. Medido, não estimado — é a verificação nº 4
do plano original, que até aqui só tinha sido citada.

Tetos declarados em `tests/testar_orcamento.py`: **5.000 no total** e **520 por
skill**. O segundo importa mais: o total avisa que o conjunto cresceu, o por-skill pega
a próxima que nascer gorda **na hora**, e não daqui a seis skills quando o dano já
está distribuído.

**Alternativa descartada.** Só encurtar o texto. O que se fez foi **estreitar o
escopo**: com o `doutrina` instalado, as frases-gatilho daquela skill competiam com
skills mais específicas — "hook ou CLAUDE.md?" tem resposta melhor e mais barata em
`onde-colocar`. Encurtar sem desconflitar teria mantido as duas disputando o mesmo
pedido.

**Como saber que envelheceu.** Se o teto for atingido, a resposta certa quase nunca é
subi-lo. É perguntar qual skill deixou de se pagar.

---

## 016 — A portabilidade foi provada, e quebrou onde ninguém olhava

**Data:** 2026-09-07 · **Ticket:** 021

O documento de arquitetura dizia que nenhum dos dois plugins jamais rodara fora deste
repositório, e chamava isso de *"a premissa do desenho inteiro"*. Ela agora foi
exercitada, num repositório git descartável, com `.claude-plugin/marketplace.json` na
raiz e instalação por `claude plugin install ... --scope project`.

**O que funcionou de primeira.** O marketplace validou, a instalação completou, e as
**seis** skills do `doutrina` apareceram namespaced (`doutrina:onde-colocar`, …) numa
sessão que nunca viu este repositório. `--plugin-dir`, que era o único modo usado até
aqui, não exercita nada disso: aponta para a pasta local e pula o caminho de instalação
inteiro.

**O que quebrou.** A pergunta da bateria — *qual a precedência de skills, e a de
rules?* — **não foi respondida**. A skill disparou, roteou para o arquivo certo, nomeou
o arquivo certo, e não conseguiu lê-lo. E se recusou a chutar, que é o comportamento
desejado e foi o que tornou a falha visível em vez de silenciosa.

A causa tem duas camadas, e só a primeira era nossa:

1. **Link relativo.** As skills apontavam para `](../../referencias/x.md)`. Dentro
   deste repositório isso resolve; instalado, o agente não tem base e precisa
   **adivinhar** a raiz do plugin. Corrigido para `${CLAUDE_PLUGIN_ROOT}/referencias/…`,
   que a plataforma substitui e vale nos dois modos.
2. **Fronteira de diretório de trabalho.** Mesmo com o caminho certo, os arquivos do
   plugin ficam **fora** dos diretórios da sessão — no cache, ou na pasta de origem. A
   recusa não é regra de permissão; é a fronteira, e em sessão não interativa ela não
   vira prompt: falha e pronto.

**E a condição escondida do conserto.** `permissions.additionalDirectories` no
`settings.json` do projeto é **ignorado enquanto o workspace não é confiado** — literal:
*"Ignoring 2 permissions.additionalDirectories entries … this workspace has not been
trusted."* A confiança vem do diálogo interativo, que num clone novo, numa sessão
headless ou em CI nunca aconteceu. **A configuração versionada que deveria resolver o
problema é justamente a que não vale onde o problema aparece.** Só `--add-dir` resolve
lá. Está no README e como armadilha nº 14.

**Alternativa descartada:** `allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)` no
frontmatter da skill. Foi testada e **não** derrubou a barreira — `allowed-tools`
concede ferramenta, não atravessa fronteira de diretório. Embarcar em seis skills um
mecanismo que não foi observado funcionando seria o culto de carga que o próprio
`settings.exemplo.json` condena. Revertida.

**Medido, não lido:** o validador oficial trata `version` divergente entre a entrada do
marketplace e o `plugin.json` como **aviso**, não erro — sem `--strict` o manifesto
errado passa. E no install **o `plugin.json` vence, em silêncio**. Quem sobe só a
entrada acha que publicou, e o cache continua servindo a versão antiga. Daí `--strict`
no CI, mais um passo que prova que ele morde.

**O que segue sem prova.** macOS e Linux. E o `metodo` foi instalado por ninguém ainda:
a prova é do mecanismo, que os dois compartilham, não da instalação dele.

---

## 017 — macOS e Linux saem da lista de pendências

**Data:** 2026-09-07 · **Revoga o escopo de:** 016 ("o que segue sem prova")

Decisão do dono do projeto: ele não roda nada em macOS nem em Linux. Listar as duas
plataformas como dívida é registrar uma cobrança que ninguém vai fazer — e uma lista de
pendências com item que nunca sai perde o crédito dos itens que importam.

Ao aplicar, a formulação antiga se revelou **imprecisa**, não só mal escopada. Ela dizia
*"o shell dos hooks é outro lá"*, o que sugere risco onde ele é menor:

- **Linux já tem cobertura contínua.** O job `suites` roda em `ubuntu-latest` a cada
  push: os scripts e as onze suítes — a metade Python inteira — passam lá desde sempre.
- **Nos hooks, macOS e Linux são o caso FÁCIL.** Eles rodam em `sh`, e `|| exit 2` é
  sintaxe POSIX: a rede que converte `python3` ausente em bloqueio funciona lá por
  construção.
- **O caso frágil é Windows sem Git Bash**, onde os hooks caem em PowerShell, a rede
  POSIX não vale e a ausência de `python3` volta a falhar aberta. É da própria família
  de plataformas em uso, e já estava no README como risco residual.

Ou seja: a pendência apontava para a direção errada. Removê-la não afrouxa o rigor —
corrige para onde ele aponta.

**O que fica no lugar,** em `docs/arquitetura.md`, como nota para quem instalar do
repositório público: em macOS ou Linux o não exercitado é **o portão numa sessão real**;
o resto tem CI.

**E o que virou pendência de verdade no lugar:** os hooks do `metodo` nunca dispararam a
partir de um plugin **instalado**. A prova de 021 é do mecanismo de instalação e das
skills do `doutrina`, que não têm hook. Essa é a lacuna próxima de doer, e ela é
independente de sistema operacional.

---

## 018 — O portão foi exercitado a partir de um plugin instalado

**Data:** 2026-09-07 · **Fecha:** P11

O drill rodou no mesmo repositório descartável do ticket 021, agora com o `metodo`
instalado por `claude plugin install metodo@metodo-claude-code --scope project` — não
por `--plugin-dir`. A suíte é declarada em `.claude/metodo.json` do projeto; os hooks
moram no plugin, fora dele.

| Caso | Esperado | Resultado |
|---|---|---|
| Suíte vermelha + árvore suja | **bloqueia** | bloqueou, com a mensagem do portão |
| Suíte verde + árvore suja | **solta** | soltou, turno encerrou limpo |
| Editar teste que já existe | **nega** | negou, com a mensagem do `proteger_testes` |

O conjunto é balanceado de propósito: um portão que só foi visto bloqueando é
indistinguível de um portão que bloqueia tudo.

**A combinação que nunca tinha sido exercitada** é justamente essa separação: o
`metodo.json` mora no **projeto**, os hooks moram no **plugin**, e os dois só se
encontram depois da instalação. Dentro deste repositório eles são a mesma pasta, e a
distinção não existia para ser testada.

**Erro cometido no caminho, e o que ele diz.** Escrevi o `metodo.json` com `verificacao`
como string, de memória. O schema é objeto, com `comando`, `timeout_segundos` e
`descricao`. Peguei conferindo o template antes de rodar. Vale registrar porque é o erro
que quem instalar vai cometer: **o formato não é adivinhável**, e o README não o mostra
— só o template mostra.

### Uma discrepância que este drill abriu, e não fechou

Os hooks **dispararam** num workspace que o próprio Claude Code declarou não confiado: a
mensagem *this workspace has not been trusted* apareceu em todas as execuções, e mesmo
assim o portão bloqueou e o `proteger_testes` negou.

Isso **não bate** com a linha do nosso README dizendo que hooks *não rodam em pasta não
confiada*. Ou os dois sentidos de confiança são coisas diferentes, ou a nossa formulação
está errada. Não sei qual, e escolher sem verificar seria trocar um erro por outro.

O que a falta de confiança comprovadamente desliga é `permissions.additionalDirectories`
— medido, literal, e já registrado como armadilha nº 14. A afirmação sobre hooks fica
**marcada como não verificada** em vez de repetida.

---

## 019 — A armadilha nº 14 tem conserto, e ele foi medido nos dois estados

**Data:** 2026-09-07

A decisão 016 deixou em aberto se aceitar o diálogo de confiança faria
`permissions.additionalDirectories` passar a valer. O teste foi montado como experimento
controlado, num repositório novo (`teste-metodo`) com o `doutrina` instalado por
marketplace e a regra apontando para a raiz do plugin.

**Uma variável só mudou** entre as duas execuções: `hasTrustDialogAccepted`. Mesmo
repositório, mesmo `settings.json`, mesma pergunta — a precedência de skills × rules, que
é boa justamente por ser uma **inversão**: um agente que responda de memória provavelmente
acerta, então o que conta é ele **citar o caminho**.

| Confiança | Resultado |
|---|---|
| Ausente (`hasTrustDialogAccepted` inexistente) | Roteou, nomeou `precedencias.md` — e **não conseguiu abrir**. A linha *"Ignoring 1 permissions.additionalDirectories entry"* apareceu |
| `true`, aceita no diálogo | **Leu e citou o caminho absoluto.** `managed > user > project` para skills, `project > user` para rules |

**A receita, agora com prova:** `additionalDirectories` apontando para a raiz do plugin,
**mais** o diálogo aceito uma vez. As duas são necessárias; nenhuma sozinha basta.

**O que não muda:** onde não há diálogo a aceitar — CI, headless, `-p` num clone novo —
só `--add-dir` resolve. A metade versionada da receita é justamente a que não vale lá.

**Diagnóstico de um segundo:** se a linha *"Ignoring N permissions.additionalDirectories
entries"* aparece, o problema é confiança, não a regra.

**Sobre o método.** A linha de base foi registrada **antes** de pedir a ação humana, com
o estado não confiado confirmado em `~/.claude.json`. Sem isso o resultado positivo não
provaria nada: seria indistinguível de o agente ter acertado de memória, ou de a regra
já valer o tempo todo. Um experimento com um estado só não é experimento.

---

## 020 — A confiança barra o que concede (fecha P12), e o bump virou mecanismo (fecha P4)

**Data:** 2026-09-07

### P12 — eu estava errado, e de um jeito que vale mais que o acerto

A decisão 018 registrou que os hooks dispararam num workspace não confiado, contra o que
o nosso README afirmava, e deixou a questão aberta em vez de escolher um lado. A doc
resolve, e a regra é mais estreita e mais útil do que qualquer das duas leituras:

> *"`permissions.allow` rules and `permissions.additionalDirectories` entries in a
> project's `.claude/settings.json` **grant capability**, so Claude Code applies them
> only after you accept the workspace trust dialog. `deny` and `ask` rules aren't
> affected, **since they only restrict**."*

**Confiança é um portão sobre concessão.** O que restringe vale sempre — o que protege
não espera permissão para proteger. Na tabela oficial, hooks em settings aparecem como
`Used` nas duas colunas sem confiança.

Meu erro não foi um detalhe trocado: eu tinha juntado numa lista só coisas que a
plataforma trata de formas opostas. `additionalDirectories` e hooks estavam na mesma
frase, e um espera confiança e o outro não.

**Três consequências que a correção trouxe, e que não estavam em lugar nenhum nosso:**

1. **Hooks rodam antes de qualquer confiança**, venham de settings, de skill de projeto
   ou de plugin. Se a preocupação é código de terceiro executando na máquina, confiança
   **não** é a defesa: `--bare`, `--setting-sources user` e `disableAllHooks` são.
2. **Hook de subagente é o oposto do de settings**: fica parado, e *sem diálogo
   oferecido* — não há o que aceitar.
3. **`extraKnownMarketplaces` do repositório não carrega antes da confiança.** Isso
   atinge a nossa própria instrução de instalar com `--scope project`: quem clonar não
   recebe os plugins até confiar na pasta. Está no README agora.

Registrado como armadilha nº 15, e a assimetria entrou na skill `garantir` — é dela que
alguém precisa ao decidir onde pôr uma garantia.

### P4 — de disciplina a mecanismo

O que faltava não era lembrete, era o **modelo certo do problema**: o `marketplace.json`
aponta para `./plugins/<nome>`, então **todo push para `main` é um release**. Não há
etapa de publicação separada. E o cache é chaveado por versão
(`~/.claude/plugins/cache/<mkt>/<plugin>/<versão>/`), então mudar conteúdo sem mudar
`version` publica um plugin diferente sob o mesmo número — e quem já instalou fica com a
cópia antiga **sem nada avisar**.

`scripts/verificar_bump.py` compara HEAD com a base e reprova quando conteúdo de plugin
mudou e `version` não. No CI, com `fetch-depth: 0` — com o checkout raso padrão a base
não existiria e o detector avisaria em vez de verificar, que é a falha aberta que ele
existe para impedir.

**As duas metades, agora fechadas:** `testar_marketplace.py` pega **subir errado**
(versão divergente entre marketplace e `plugin.json`); `verificar_bump.py` pega
**esquecer de subir**. Uma sozinha deixava metade do problema em pé.

**A suíte é balanceada em dois eixos, não um.** O óbvio: mudou sem bump reprova, mudou
com bump passa. O menos óbvio, e o que impede um detector histérico: mexer só em
`README.md`, em `tests/` ou no CI **não** pode exigir bump. Se exigisse, todo commit de
manutenção viraria release e a disciplina seria abandonada por ser insuportável. Também
verifica **qual** plugin foi acusado — um detector que acusa o errado passaria nos casos
positivos e mandaria subir a versão errada.

**E ele mordeu na primeira execução, num erro meu.** Rodado contra o histórico real,
acusou o commit `d34825f`: alterou `armadilhas.md` e deixou o `doutrina` em `0.1.0`.
Eu tinha acabado de escrever que o bump era disciplina — e falhei nela enquanto escrevia
o mecanismo que a substitui. `doutrina` foi para `0.2.0`, nos dois lugares.

**O que continua fora de alcance:** o detector compara commits, então ele não pode julgar
se `0.1.0 -> 0.2.0` era a *magnitude* certa. Semântica de versão segue humana.

---

## 021 — O plano vira intenção + retrospectiva, e o detector vai para onde alguém olha

**Data:** 2026-09-07 · **Ticket:** 022

`docs/plano-metodologia.md` afirmava "Fase 3 em andamento" (fechada, e três fases depois
dela também), "as duas suítes" (são doze), e que `/doctor` entregava o orçamento de
contexto (quem entregou foi `testar_orcamento.py`, com teto declarado). E não mencionava
o `doutrina`: o repositório distribui **dois** plugins e o plano descrevia um.

**A decisão de desenho veio antes da correção.** Reescrever o plano para descrever a
realidade o transformaria num **segundo documento de arquitetura** — e `arquitetura.md`
já é esse, carimbado e medido. Duas fontes sobre o mesmo assunto divergem na primeira
semana.

Um plano executado tem outro trabalho, que nenhum outro documento faz: **dizer se o
plano estava certo.** Então a doutrina fica como foi escrita — intenção não se corrige
por ter envelhecido —, as fases e a verificação ganham desfecho real, e uma seção nova
registra onde a execução divergiu.

**O que a retrospectiva encontrou, e que não estava registrado em lugar nenhum:**

- A Fase 0 foi feita **duas vezes**, e a primeira não valia: perguntas já formuladas não
  são levantamento.
- A ordem das fases estava errada por um motivo detectável antes — um leitor de estado
  não pode ser escrito antes de existir estado. Ordenar por dependência de dados, não
  por importância.
- Três verificações foram cumpridas **por mecanismo, não por consulta**. Consulta manual
  se esquece; teto reprova.
- **A verificação mais valiosa não estava no plano:** o conjunto balanceado. Ele veio dos
  mecanismos absorvidos e virou o hábito que mais achou defeito.

**O item 5 continua NÃO VERIFICADO,** e ficou escrito assim: o prefixo de reengenharia
nunca rodou contra uma base de código existente.

### O detector: em `estado.py`, deliberadamente fora do CI

**Alternativa descartada:** rodar `verificar_documento.py` no CI. Ele sai com 1 quando o
documento está atrás, e quase todo commit deixa algum documento atrás — o CI ficaria
vermelho quase sempre. **Trava que grita sempre é trava que se aprende a ignorar**, e o
detector deixaria de significar qualquer coisa exatamente por estar em toda parte.

Ele foi para `estado.py`, que é o que uma pessoa consulta ao decidir o próximo passo —
que é quando a pergunta *"este documento ainda descreve o desenho?"* importa. **Relata,
não bloqueia** (decisão de método nº 3 e decisão 014), e há um caso de teste dedicado a
essa propriedade: documento desatualizado **não** muda o cenário nem o passo recomendado.

Essa asserção foi verificada por **mutação** — transformar o relato em trava faz
exatamente esse caso reprovar, e só ele. Sem a mutação, ela poderia estar morta e os
outros quatro casos continuariam verdes.

**E o relato precisou de uma correção na primeira execução.** Os dois documentos
apareceram vermelhos de imediato, e o rótulo sozinho não distinguia estar atrás de 1
arquivo de estar atrás de 47 — que exigem decisões diferentes. Passou a mostrar a
**magnitude**. Um aviso que não distingue os casos é lido como ruído em duas semanas, e
essa era a mesma falha que motivou mantê-lo fora do CI.

### O detector de bump pegou o próprio ticket

O ticket alterou `plugins/metodo/scripts/estado.py` e não subiu a versão. O CI reprovou;
`metodo` foi para `0.2.0`. **Terceiro achado real do mecanismo, o segundo contra mim.**

A lição é de uso, não de código: `verificar_bump.py` compara estado **commitado**, então
a ordem é commitar, rodar, empurrar. Eu empurrei sem rodar.

---

## 022 — A `arquiteto-claude-code` aposentada, com inventário

**Data:** 2026-09-07 · **Tickets:** 023, 024, 025, 026

### O que motivou

Ao debater se o `metodo` deveria "chamar" o `doutrina` ao planejar, apareceu um fato que
mudava a pergunta: o `metodo` **já carregava** uma skill em forma de doutrina, com sete
arquivos de referência próprios. Não era dependência faltando — era **duplicação**.

Na primeira leitura chamei aquilo de duplicata do `doutrina`. **Estava errado**, e medir
corrigiu: os dois corpos tinham **bases de fonte diferentes**. `fontes.json` indexava 191
páginas, todas de `code.claude.com`; de `anthropic.com/engineering`, **zero**. A skill do
`metodo` vinha justamente do blog. Três das sete referências tinham par no `doutrina`;
três não tinham nenhum.

Sem essa medição, a decisão teria sido apagar a skill — e perder ~400 linhas de doutrina
sem herdeiro.

### O inventário de migração

Nada saiu por omissão. As sete referências, mais o corpo da skill:

| Origem | Destino |
|---|---|
| `01-arquitetura-agentes` | **Migrado** → skill `doutrina:arquitetar` + `referencias/duravel/arquitetura-de-agentes.md` |
| `04-verificacao-e-evals` | **Migrado** → skill `doutrina:avaliar` + `referencias/duravel/evals.md` |
| `02-contexto-e-memoria` | Coberto por `doutrina:contexto`. **Faltava a altitude do prompt** — migrada para lá |
| `03-mecanismos-extensao` | Coberto por `onde-colocar`, `escrever-skill`, `paralelizar`. MCP, output styles e precedências já estavam |
| `05-seguranca` | Coberto por `garantir`. **Faltava o padrão de classificador de ações** — migrado para lá |
| `06-fontes` | Virou dado: 19 páginas em `fontes.json`, com hash e detecção de drift. Deixa de ser lista em prosa |
| `07-template-entregavel` | **Movido para o `metodo`** → `templates/arquitetura.md`. Não é conhecimento: é a forma de um artefato, irmã do `ticket.md` |
| Corpo: regras invioláveis, viés a combater, contrato de saída | **Movidos para o template**, que é onde eles se aplicam |
| Corpo: tabela de alocação, diagnósticos rápidos | Já cobertos por `matriz.md` e `armadilhas.md` |
| Corpo: procedimento de 8 passos | **Descartado.** Era roteiro de skill; com o `doutrina` instalado, cada passo tem ficha própria e mais específica |

### A regra que a migração fixou

**A camada de processo não carrega cópia da camada de conhecimento.**

O `metodo` ficou com a *forma* do documento e o papel que o produz. O `doutrina` ficou
com o *conteúdo*. E o agente `arquiteto` foi religado: usa as fichas se elas existirem, e
**se o `doutrina` não estiver instalado, diz isso na primeira linha do documento**.

**Alternativa descartada:** declarar dependência entre os plugins. Ela reverteria a
separação da Fase 2 (cadência e propósito diferentes), custaria contexto a quem quer só o
processo, e falharia aberta no pior jeito — sem o `doutrina` instalado, o agente
improvisaria achando que cumpriu o passo. A degradação declarada é honesta; a dependência
escondida não é.

### Dois achados no caminho

**O detector não transferia para o blog.** A doc é markdown puro; o blog é página
construída — 211 KB de HTML para 20 KB de texto, `nonce` em vinte lugares, classes com
hash de build. Hashear cru faria o detector acusar a cada reconstrução do site. Daí
`normalizar_html` e o campo `formato`, com o teste que importa: ruído de build **não**
muda o hash, mudança de texto **muda** — sem o segundo, um normalizador que devolvesse
`""` passaria.

**Uma afirmação falsa no índice.** O comentário dizia que `prioridade: nucleo` significa
"destilada em ficha local". Não significa: 53 das 80 páginas núcleo não têm ficha.
`nucleo` marca o que **merece** destilação. O verificador agora imprime a diferença,
porque dívida que ninguém conta é dívida que ninguém paga.

### O saldo

Duas skills a mais no `doutrina`, uma a menos no `metodo`, e o orçamento de descrição
**caiu**: 4.462 → 4.407 caracteres. O conhecimento cresceu e o custo por request diminuiu,
porque a skill removida sozinha ocupava 486.

---

## Pendências que este repositório carrega

Registradas aqui porque bloqueiam fases seguintes e se perdem se ficarem só na conversa.

> **Higiene desta lista.** Em 2026-09-07, P2 e P3 estavam abertas e **já resolvidas há
> semanas** — a lista tinha apodrecido em silêncio. É o mesmo risco que a decisão 017
> nomeia: item que nunca sai tira o crédito dos que importam. Nada vigia esta tabela;
> ela depende de ser lida ao fechar uma fase.

**Nenhuma pendência aberta em 2026-09-07.** As riscadas ficam por registro, e vale
notar o padrão: várias foram fechadas **pelo negativo** — descobrindo que a premissa
estava errada, não que o trabalho faltava.

| # | Pendência | Bloqueia |
|---|---|---|
| ~~P1~~ | **Resolvida.** As cópias de `~/.claude/` foram movidas para `~/.claude/_backup-arquiteto/`. Achado no caminho: renomear para `.bak` **não** tira uma skill de circulação — o Claude Code carrega skill pelo **diretório**, não pelo `name:` do frontmatter, e ela reapareceu como `arquiteto-claude-code.bak`. Agente sim exige `.md`. Apagar o backup só depois da P7. | — |
| ~~P8~~ | **Resolvida por eliminação.** A questão perdeu objeto: o `hooks:` do frontmatter nem é lido para agentes de plugin (decisão 010), então a resolução da variável ali nunca importou. Ela volta a importar em `hooks/hooks.json`, onde é documentada. | — |
| ~~P9~~ | **Fechada pelo negativo.** O portão não barrou: hooks no frontmatter são ignorados para agentes de plugin. Ver decisão 010; correção no ticket 006. | — |
| ~~P2~~ | **Resolvida.** Público, em `alerocha-collab/metodo-claude-code`, sem menções ao projeto privado que serviu de exemplo. Confirmado por `gh repo view`. | — |
| ~~P3~~ | **Resolvida.** `gh` 2.100.0 no PATH e autenticado; usado para criar o repo e acompanhar o CI. | — |
| ~~P10~~ | **Descartada como causa.** O ticket 003 confirmou `python3` 3.14.2 disponível em PowerShell e cmd, fora do Git Bash. A dependência segue não declarada — isso é o ticket 004, não uma pendência solta. | — |
| ~~P12~~ | **Resolvida: o README estava errado.** A confiança barra o que **concede** (`allow`, `additionalDirectories`), não o que executa. Hooks rodam sem ela. Armadilha nº 15 e decisão 020. | — |
| ~~P4~~ | **Resolvida.** `scripts/verificar_bump.py` no CI reprova conteúdo de plugin alterado sem `version` alterada. Com `testar_marketplace.py`, as duas metades fecham: subir errado e esquecer de subir. Ver decisão 020. | — |
| ~~P11~~ | **Resolvida.** Drill de três casos a partir de um plugin instalado: bloqueia com suíte vermelha, solta com verde, nega edição de teste existente. Ver decisão 018. | — |
| ~~P5~~ | **Resolvida.** `claude plugin validate --strict` roda em CI para os dois plugins e para o marketplace, mais um passo que prova que a validação do marketplace reprova `version` divergente. | — |
| ~~P7~~ | **Resolvida com ressalva** — ver decisão 006. Nome puro funciona. Ressalva: o teste rodou num repo que contém o plugin; confirmação definitiva na Fase 5. | — |
| ~~P6~~ | **Resolvida.** Fase 0 fechada; achados e consequências em [docs/fase-0-mecanismos.md](docs/fase-0-mecanismos.md). | — |
