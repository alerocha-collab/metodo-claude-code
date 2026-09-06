# Plano — a metodologia como plugin

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

Os três primeiros já estão implementados: `testar_tudo.py` é o runner fail-closed,
as duas suítes são conjuntos balanceados, e `validar_fila.py` é governança por script.

## Fases

**Fase 0 — Exaurir a doutrina que falta.** Concluída. Achados e consequências em
[fase-0-mecanismos.md](fase-0-mecanismos.md).

**Fase 1 — Esqueleto do repositório + plugin.** Concluída.

**Fase 2a — Os papéis e o portão.** Concluída. `construtor` e `operador`, o `Stop`
de verificação e o `PreToolUse` que protege os testes.

**Fase 3 — Core adaptado.** Em andamento. As skills de fluxo, com as nove decisões
aplicadas — sobretudo a nº 5 (achado vira ticket automático) e a nº 6 (critérios
antes, não editados durante). Começou pelo formato do ticket.

**Fase `/fluxo`** — o orquestrador, depois que houver estado real para ler. Reordenado
em relação ao plano original; ver decisão 008 no `DECISIONS.md`.

**Fase 4 — Prefixo de reengenharia.** As três skills de onboarding.

**Fase 5 — Reconciliação do projeto de referência.** O primeiro caso de teste real, e
o mais exigente.

## Verificação

1. **Plugin instala e as skills aparecem**, com `/context` mostrando custo baixo.
2. **`/fluxo` acerta o estado em quatro cenários montados**: repo vazio · spec sem
   tickets · tickets prontos · diff pendente de revisão. Em cada um, deve nomear o
   próximo passo certo e, no caso trivial, recomendar pular o rito.
3. **O `Stop` hook barra de verdade.** Quebrar um teste de propósito e confirmar que
   o turno não encerra.
4. **Orçamento de contexto medido**, não estimado — `/doctor` já entrega isto.
5. **O prefixo produz fila, não relatório** — tickets em ordem de bloqueio, com
   critérios de aceitação escritos antes.
6. **Nada do projeto existente é sobrescrito sem decisão explícita.** Toda
   substituição de mecanismo entra no `DECISIONS.md` com a alternativa descartada.

## Fora de escopo

- **RAG.** Capacidade de projeto, não componente de metodologia.
- **Sandbox / WSL2.** Adiado por decisão; risco residual registrado.
- **Registro de risco de projeto** (decisão nº 9).
