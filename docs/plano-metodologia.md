# Plano — a metodologia como plugin

**SHA:** `99fa983` · **Data:** 2026-09-07

> **O que este documento é, e o que ele não é.** Ele é a **intenção**, mais o registro
> de como a execução se comportou contra ela. Não é o desenho em vigor — esse é
> [arquitetura.md](arquitetura.md), que é carimbado e medido para isso. Onde os dois
> falarem do mesmo assunto, o `arquitetura.md` manda.
>
> A doutrina abaixo — as nove decisões, o desenho do `/fluxo`, o prefixo de reengenharia
> — fica **como foi escrita**. Intenção não se corrige por ter envelhecido; ela se
> confere contra o resultado. É o que a seção *Onde a execução divergiu* faz.
>
> **Nota sobre esta versão.** O plano original nasceu junto com a auditoria de um
> projeto privado, que é o primeiro caso de teste da metodologia. Esta versão contém
> a metade que é método; a auditoria daquele projeto não é pública e vive fora deste
> repositório. Onde o texto disser "o projeto de referência", é a ele que se refere.

## Objetivo

Um conjunto próprio de skills, agentes e hooks que codifique um método de trabalho
com agentes, instalável como plugin, que viaje entre projetos — e que sirva tanto
para projeto novo quanto para reconciliar um projeto já codificado com o desenho.

**A reconciliação é bidirecional.** Um projeto maduro pode ter resolvido melhor do
que o set de referência aquilo que o set prescreve. Impor a metodologia por cima
destruiria mecanismos superiores. O projeto existente é, em parte, **fonte** do
método — não só destino dele.

## As nove decisões que este plano executa

| # | Decisão fechada |
|---|---|
| 1 | Fase = spec · ticket = fatia dimensionada por janela · **sessão = um ticket + commit** |
| 2 | Separação por **papel** (não por ambiente); barreira dura em `permissions.deny` |
| 3 | Estado estruturado + git durante; documento de arquitetura carimbado com SHA no fim; hook **detecta, nunca atualiza** |
| 4 | Spec dimensionada pela autonomia; **o ticket é a spec** |
| 5 | Prefactor antes · nunca durante · achado de revisão vira **ticket automático** |
| 6 | Agente redige os critérios, o humano valida; **entram antes da implementação e não são editados durante** |
| 7 | Entrevistar por gatilho, não por regra |
| 8 | Hooks em três escopos: universal no `settings.json` · papel no agente · fluxo na skill |
| 9 | Sem registro de risco de projeto, conscientemente |

Fundamentação completa, com alternativas e modos de falha, em
[decisoes-metodologia.md](decisoes-metodologia.md).

**Restrição de ambiente registrada:** sandbox não roda em Windows nativo (só macOS,
Linux, WSL2). A barreira dura disponível é `permissions.deny`. Risco residual aceito.

## O orquestrador `/fluxo` — lê estado, não decora sequência

O problema que ele resolve ("não lembrava qual skill chamar") **não é de memória, é
de estado**. Qual skill vem a seguir é determinado por onde o projeto está, e esse
estado já existe em disco pela decisão nº 3.

`/fluxo` é um `git status` da metodologia: lê tickets, git e presença de artefatos,
reporta onde o projeto está, recomenda o próximo passo — **e sabe recomendar pular**
quando o trabalho é pequeno demais para o rito completo.

Três restrições de projeto, derivadas dos riscos identificados:

- **Roteia, não executa.** Se reimplementar o que as outras skills fazem, vira ponto
  único de doutrina e duplicação.
- **Corpo enxuto** — reformulado depois da Fase 0: `context: fork` paga o corpo fora
  da sessão, então a restrição afrouxa. Ver [fase-0-mecanismos.md](fase-0-mecanismos.md).
- **Relata verde/vermelho; não garante.** A garantia é hook.

## O prefixo de reengenharia — três skills, não um modo

As trilhas divergem apenas no início e depois **convergem por completo**:

| Etapa | Projeto novo | Reengenharia |
|---|---|---|
| Entender o que existe | — | `onboarding-entender` |
| Modelo de domínio | pela conversa | `onboarding-modelar` (extrai do código) → normal |
| Diferença vs. alvo | — | `onboarding-lacunas` |
| Daí em diante | spec → tickets → implementa → revisa | **idêntico** |

Descartadas: ramificar por modo dentro de cada skill (complexidade paga em contexto
sempre) e set paralelo (divergiria em meses).

**TDD não precisa de modo:** a diferença mora **no ticket**. Ticket de reengenharia
diz "escreva o teste de caracterização do comportamento atual, depois altere".

**Formato da saída do prefixo, com respaldo no retrofitting do XP:** não tentar
conformidade total numa passada. Beck é explícito — não pare o desenvolvimento para
testar todo o código antigo; aplique testes sob demanda (ao corrigir bug, ao
adicionar feature, ao refatorar). Logo `onboarding-lacunas` entrega **o mapa + os
tickets do caminho crítico + a regra de que o resto entra quando a área for tocada**
— nunca um relatório.

## Mecanismos absorvidos de um projeto em produção

Cinco mecanismos que o projeto de referência resolveu melhor que o set de referência,
e que subiram para a metodologia:

| Mecanismo | Por que absorver |
|---|---|
| **Regras como JSON com severidade** | Governança verificável por script, não por leitura. JSON resiste à reescrita pelo modelo |
| **Runner fail-closed** | Suíte ausente conta como falha — fecha o buraco do "passou porque não rodou" |
| **Fixtures negativas** | Conjunto balanceado: testa quando *deve* e quando *não deve* passar. É a doutrina de evals aplicada |
| **Gerador/avaliador com portão entre os dois** | Padrão validado em campo |
| **Artefato imutável endereçado por hash** | O carimbo de aprovação aponta para o hash do que foi julgado |

**Os cinco foram implementados.** `testar_tudo.py` é o runner fail-closed; as **doze**
suítes são conjuntos balanceados; `validar_fila.py` é governança por script; a revisão
em dois eixos, em contextos separados, é o gerador/avaliador com portão; e o carimbo de
SHA com `verificar_documento.py` é o artefato endereçado por hash.

O quinto rendeu mais do que o plano previa: o mesmo contrato reaparece em
`plugins/doutrina/fontes.json`, que guarda o hash de 191 páginas de documentação para
detectar quando a fonte mudou.

## Fases

| Fase | Desfecho |
|---|---|
| **0 — Exaurir a doutrina que falta** | **Concluída**, e depois refeita: a primeira passada foi confirmação de hipóteses, não levantamento. Ver *Onde a execução divergiu*. Achados em [fase-0-mecanismos.md](fase-0-mecanismos.md) |
| **1 — Esqueleto do repositório + plugin** | **Concluída** |
| **2a — Os papéis e o portão** | **Concluída.** `construtor` e `operador`, o `Stop` de verificação e o `PreToolUse` que protege os testes |
| **3 — Core adaptado** | **Concluída.** As skills de fluxo com as nove decisões aplicadas |
| **2b — `/fluxo`** | **Concluída.** Reordenada para depois da 2a e da 3: o leitor de estado só podia ser escrito depois de existir estado real. Decisões 007 e 008 |
| **4 — Prefixo de reengenharia** | **Concluída** como código: as três skills de onboarding existem. **Não exercitada:** nenhuma rodou contra uma base de código existente |
| **5 — Reconciliação do projeto de referência** | **Aberta, e sem alvo.** O dono do projeto retirou o projeto privado do escopo e ofereceu "outro projeto se for o caso". Escolher o alvo é decisão dele, não deste plano |

O plano não previa uma fase de distribuição, e ela aconteceu: `.claude-plugin/marketplace.json`,
instalação num repositório limpo, e o portão exercitado a partir de um plugin instalado.
Decisões 016 e 018.

## Verificação

| # | O que o plano exigiu | Status |
|---|---|---|
| 1 | Plugin instala e as skills aparecem, com custo de contexto baixo | ✅ **Verificado.** Instalado por marketplace num repositório limpo; as seis skills do `doutrina` apareceram namespaced. Decisão 016 |
| 2 | `/fluxo` acerta o estado em **quatro** cenários montados | ✅ **Verificado, e excedido:** `tests/testar_estado.py` cobre **doze**, incluindo os que o plano não previu — grafo de bloqueio mandando sobre ordem numérica, e ticket em andamento vencendo árvore suja |
| 3 | O `Stop` hook barra de verdade | ✅ **Verificado duas vezes.** Local (ticket 003) e a partir de um plugin **instalado** (decisão 018), com o conjunto balanceado: bloqueia com suíte vermelha, **solta** com verde |
| 4 | Orçamento de contexto medido, não estimado | ✅ **Verificado, por outro caminho.** Não por `/doctor`: `tests/testar_orcamento.py` mede com tetos declarados. O plano previa consulta manual; a execução construiu mecanismo |
| 5 | O prefixo produz fila, não relatório | ⬜ **Não verificado.** As três skills existem e nunca rodaram contra uma base de código existente. É a lacuna aberta mais antiga deste plano |
| 6 | Nada do projeto existente é sobrescrito sem decisão explícita | ⬜ **Sem objeto.** Depende da Fase 5, que não tem alvo. O `DECISIONS.md` cumpre a forma — 20 decisões com alternativa descartada — mas nunca contra um projeto existente |

## Onde a execução divergiu do plano

É o que só um plano executado pode entregar: se ele estava certo.

**A Fase 0 foi feita duas vezes, e a primeira não valia.** Ela despachou subagentes com
perguntas já formuladas e chamou aquilo de levantamento — era confirmação de hipóteses.
Monorepo nunca apareceu porque ninguém perguntou, e ninguém perguntou por não saber que
existia. O dono do projeto achou a lacuna com uma pesquisa simples. **Lição:** um
levantamento que só responde ao que você já sabe perguntar não é levantamento.

**Nasceu um segundo plugin que este plano não previu.** O `doutrina` — a documentação do
Claude Code destilada para o agente — veio de outro plano, escrito depois da Fase 0
refeita. Ele é separado de propósito: cadência de atualização diferente e propósito
diferente. Bundlar seria *Divergent Change* — corrigir uma ficha obrigaria a subir a
versão da metodologia.

**A ordem das fases estava errada, e o erro era detectável antes.** A 2b (`/fluxo`) veio
depois da 3 porque um leitor de estado não pode ser escrito antes de existir estado. O
plano original a colocava antes. **Lição:** ordenar por dependência de dados, não por
ordem de importância.

**Três verificações do plano foram cumpridas por mecanismo, não por consulta.** O
orçamento de contexto viraria `/doctor` na intenção, e virou suíte com teto declarado. A
diferença importa: consulta manual se esquece; teto reprova. O mesmo aconteceu com o
bump de `version`, que o plano nem listava e virou detector em CI.

**A verificação mais valiosa não estava no plano.** Nenhum dos seis itens pedia o
conjunto balanceado — *bloqueia quando deve* **e** *solta quando não deve*. Ele veio dos
mecanismos absorvidos, e virou o hábito que mais achou defeito: o portão, o detector de
referências e o detector de bump foram todos aprovados por um teste positivo antes de
alguém perguntar se eles sabiam **não** agir.

## Fora de escopo

- **RAG.** Capacidade de projeto, não componente de metodologia.
- **Sandbox / WSL2.** Adiado por decisão; risco residual registrado.
- **Registro de risco de projeto** (decisão nº 9).
