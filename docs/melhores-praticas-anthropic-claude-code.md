# Melhores práticas da Anthropic para desenvolvimento de sistemas com Claude Code

> Consolidação do que a Anthropic define oficialmente, a partir do blog de engenharia (`anthropic.com/engineering`), da documentação do Claude Code (`code.claude.com/docs`) e dos repositórios em `github.com/anthropics`.
> Compilado em setembro de 2026. Toda afirmação normativa aqui é rastreável a uma das fontes listadas na §13.

---

## Sumário

1. [O princípio unificador: contexto é o recurso escasso](#1-o-princípio-unificador-contexto-é-o-recurso-escasso)
2. [Arquitetura de sistemas agênticos](#2-arquitetura-de-sistemas-agênticos)
3. [Qualidade de código e verificação](#3-qualidade-de-código-e-verificação)
4. [Memória e contexto persistente](#4-memória-e-contexto-persistente)
5. [Skills](#5-skills)
6. [Subagents e paralelismo](#6-subagents-e-paralelismo)
7. [Hooks](#7-hooks)
8. [MCP e design de ferramentas](#8-mcp-e-design-de-ferramentas)
9. [Escolha do mecanismo: tabela de decisão](#9-escolha-do-mecanismo-tabela-de-decisão)
10. [Avaliação (evals)](#10-avaliação-evals)
11. [Segurança e operação autônoma](#11-segurança-e-operação-autônoma)
12. [Operação diária e escala](#12-operação-diária-e-escala)
13. [Fontes](#13-fontes)

---

## 1. O princípio unificador: contexto é o recurso escasso

Praticamente toda recomendação da Anthropic deriva de uma única restrição, dita explicitamente na documentação de best practices: **a janela de contexto enche rápido e o desempenho degrada conforme ela enche**. Quando o contexto está cheio, o Claude começa a "esquecer" instruções anteriores e a cometer mais erros. A janela de contexto é o recurso mais importante a gerenciar.

### Context engineering substitui prompt engineering

O artigo *Effective context engineering for AI agents* formaliza a mudança. **Contexto** é o conjunto de todos os tokens fornecidos ao modelo na inferência. **Context engineering** é o problema de otimização de maximizar a utilidade dos tokens dentro das restrições arquiteturais.

A distinção importa: prompt engineering trata de redigir instruções; context engineering gerencia todo o ecossistema de informação — "qual configuração de contexto tem mais chance de gerar o comportamento desejado do modelo?". Agentes rodando em loop geram dados que se acumulam a cada iteração, exigindo curadoria dinâmica, não otimização estática de um prompt.

### Context rot

A pesquisa citada demonstra que **conforme o número de tokens na janela cresce, a capacidade do modelo de recuperar informação daquela janela com precisão cai**. Isso é chamado de *context rot*, e tem base arquitetural: a atenção do transformer cria `n²` relações par-a-par para `n` tokens. Conforme o contexto cresce, o mecanismo de atenção se dilui. Além disso, modelos treinados em distribuições que favorecem sequências curtas têm menos parâmetros especializados em dependências de longo alcance.

O resultado é um **gradiente de desempenho, não um penhasco**: precisão degradada na recuperação de informação e no raciocínio de longo alcance, mesmo com a capacidade nominal preservada.

### As oito recomendações concretas do artigo

1. **Trate contexto como finito.** Cada token consome um "orçamento de atenção" com retornos marginais decrescentes.
2. **Busque o conjunto mínimo de tokens de alto sinal** — o menor conjunto que maximiza a chance do resultado desejado.
3. **Estruture a informação sistematicamente** — tags XML ou headers Markdown para separar seções.
4. **Teste primeiro com modelos capazes** — estabeleça a linha de base antes de adicionar complexidade.
5. **Projete ferramentas autocontidas** — sem sobreposição funcional nem ambiguidade de uso.
6. **Habilite exploração autônoma** — dê ao agente ferramentas e heurísticas para navegar o ambiente.
7. **Escolha a técnica pela tarefa** — compaction para idas e vindas, note-taking para desenvolvimento iterativo, multiagente para exploração paralela.
8. **Simplicidade** — "faça a coisa mais simples que funciona" continua sendo a melhor prática.

### A "altitude certa" do prompt de sistema

O artigo descreve uma "zona de Cachinhos Dourados" entre dois extremos: prompts excessivamente complexos que codificam lógica condicional frágil, e prompts vagos que não guiam comportamento ou assumem falsamente um entendimento compartilhado.

A recomendação: buscar **"o conjunto mínimo de informação que descreve completamente o comportamento esperado"**; começar com prompts mínimos em modelos capazes e adicionar instruções com base em falhas observadas; equilibrar especificidade e flexibilidade — concreto o bastante para guiar, flexível o bastante para servir de heurística.

> A observação de fechamento do artigo é importante para quem projeta harnesses: *"modelos mais inteligentes exigem menos engenharia prescritiva, permitindo que agentes operem com mais autonomia"* — mas a escassez de contexto continuará central.

---

## 2. Arquitetura de sistemas agênticos

### 2.1 Comece pelo mais simples: workflow antes de agente

*Building effective agents* estabelece a regra fundacional: **comece com a solução mais simples e só aumente a complexidade quando necessário**.

- **Workflows** oferecem previsibilidade e consistência para tarefas bem definidas, através de caminhos de código predefinidos.
- **Agentes** são a escolha melhor quando flexibilidade e decisão dirigida pelo modelo são necessárias em escala.

E antes de ambos: para muitas aplicações, **otimizar uma única chamada de LLM com retrieval e exemplos já basta** — não construa um sistema agêntico.

O bloco de construção básico é o **LLM aumentado**: um modelo com retrieval, ferramentas e memória. O foco deve estar em adaptar essas capacidades ao caso de uso e prover interfaces claras.

### 2.2 Os cinco padrões de workflow

| Padrão | O que é | Quando usar | Exemplo da Anthropic |
|---|---|---|---|
| **Prompt chaining** | Decompõe a tarefa em passos sequenciais com checkpoints programáticos | Troca latência por acurácia em tarefas decomponíveis | Gerar texto de marketing e depois traduzi-lo |
| **Routing** | Classifica a entrada e direciona a handlers especializados | Categorias distintas que se beneficiam de otimização separada | Rotear perguntas de suporte por tipo; mandar perguntas simples a modelos menores |
| **Parallelization** | *Sectioning* (subtarefas independentes em paralelo) e *voting* (mesma tarefa várias vezes para confiança) | Guardrails, revisão de vulnerabilidades | Revisar código em busca de vulnerabilidades com múltiplas passagens |
| **Orchestrator-workers** | Um LLM central decompõe dinamicamente e delega a workers | Subtarefas imprevisíveis | Mudanças de código em múltiplos arquivos |
| **Evaluator-optimizer** | Um LLM gera, outro critica em loop | Tradução literária, busca complexa | Refinamento iterativo com crítica |

### 2.3 Os três princípios centrais

1. **Simplicidade** — mantenha o design direto em vez de superengenharia.
2. **Transparência** — exiba explicitamente os passos de planejamento para que o usuário entenda o raciocínio.
3. **ACI forte** — invista pesado em documentação e teste de ferramentas. A citação exata: *"pense em quanto esforço vai para interfaces humano-computador (HCI) e planeje investir o mesmo esforço em boas interfaces agente-computador (ACI)."*

### 2.4 Orquestrador-worker na prática: o sistema de pesquisa multiagente

*How we built our multi-agent research system* documenta a arquitetura em produção: um **agente líder** analisa a query, cria a estratégia e dispara **subagentes especializados** que exploram dimensões diferentes em paralelo. Os subagentes atuam como filtros inteligentes, usando ferramentas de busca iterativamente e devolvendo achados para síntese.

**Números que a Anthropic publicou:**

- O sistema multiagente (líder Opus 4, subagentes Sonnet 4) superou o Opus 4 solo em **90,2%** na avaliação interna.
- **Três fatores explicaram 95% da variância de desempenho** — o uso de tokens sozinho respondeu por ~80%.
- Sistemas multiagente usam cerca de **15× mais tokens** que chats. A tarefa precisa ter valor suficiente para justificar o gasto.
- Duas formas de paralelização (3–5 subagentes em paralelo + 3 ou mais ferramentas simultâneas) **cortaram o tempo de pesquisa em até 90%**.

**Os sete princípios de prompt engineering para multiagente:**

1. **Desenvolva intuição de agente** — simule com os prompts e ferramentas reais, observe passo a passo, identifique modos de falha.
2. **Ensine a delegar** — o líder precisa dar descrições detalhadas: objetivo, formato de saída, orientação de ferramentas, e **fronteiras da tarefa**. Instruções vagas causam duplicação e lacunas.
3. **Escale o esforço proporcionalmente** — regras explícitas embutidas: queries simples usam 1 agente e 3–10 chamadas de ferramenta; pesquisas complexas podem exigir 10+ subagentes.
4. **A seleção de ferramentas importa** — "interfaces agente-ferramenta são tão críticas quanto interfaces humano-computador".
5. **Permita auto-aperfeiçoamento** — o Claude diagnostica falhas do próprio prompt. Um agente de teste de ferramentas reduziu o tempo de conclusão em **40%** apenas otimizando descrições.
6. **Hierarquia de estratégia de busca** — comece amplo, avalie o que existe, depois estreite. Não comece com queries hiperespecíficas.
7. **Guie o pensamento** — extended thinking e interleaved thinking como scratchpad controlável para planejar e avaliar resultados no meio da busca.

**Contrato do subagente:** cada subagente explora extensivamente mas devolve um **resumo condensado de tipicamente 1.000–2.000 tokens**. Isso é o que preserva a janela do agente líder.

### 2.5 Harness design

*Harness design for long-running application development* define **harness** como o andaime estruturado em volta do agente que o permite completar tarefas de várias horas de forma confiável. A frase-chave:

> *"Todo componente de um harness codifica uma suposição sobre o que o modelo não consegue fazer sozinho."*

**Arquitetura gerador-avaliador.** Inspirada em GANs: um agente **gerador** produz o trabalho; um agente **avaliador** julga independentemente contra critérios concretos; o feedback volta ao gerador. A separação é crítica porque agentes "tendem a responder elogiando confiantemente o próprio trabalho — mesmo quando a qualidade é obviamente medíocre". É muito mais tratável calibrar um avaliador cético do que fazer um gerador autocrítico.

**Arquitetura de três agentes** para desenvolvimento full-stack:

1. **Planner** — recebe um prompt de 1 a 4 frases e o expande em spec de produto com decisões técnicas. Previne a cascata de garbage-in-garbage-out.
2. **Generator** — implementa iterativamente, com auto-avaliação antes do handoff.
3. **Evaluator** — usa Playwright MCP para interagir com a aplicação rodando como um usuário, testando e atribuindo nota contra critérios concretos.

**Sprint contracts.** Antes de cada sprint, gerador e avaliador negociam um contrato: exatamente o que será construído, como o sucesso será verificado, critérios de aceitação testáveis. Isso força um acordo explícito sobre o que significa "pronto" *antes* da implementação.

**Comunicação via arquivos, não via contexto.** Os agentes se comunicam por artefatos em disco (spec de produto, sprint contract, achados de QA), não por contexto compartilhado. Isso previne poluição de contexto e força clareza sobre o que está sendo passado.

**Tornando qualidade subjetiva mensurável.** Para trabalho de front-end, quatro critérios de nota: qualidade de design, originalidade, craft (tipografia, espaçamento, contraste) e funcionalidade. Design e originalidade receberam peso maior — o Claude já pontuava bem em craft e funcionalidade por padrão. O avaliador foi calibrado com exemplos few-shot mostrando o padrão de pontuação preferido.

**A calibração do avaliador custa iterações.** Avaliadores iniciais falharam porque "identificavam problemas legítimos e depois se convenciam de que não eram importantes". Foram necessárias várias rodadas de leitura de logs e ajuste de prompt até chegar a um QA razoável.

**A lição sobre obsolescência do harness.** As características mudaram drasticamente entre versões de modelo:

- **Opus 4.5** exigia decomposição em sprints, context resets e envolvimento pesado do avaliador, por causa da "ansiedade de contexto" que fazia o modelo encerrar o trabalho prematuramente.
- **Opus 4.6** manteve coerência por mais de 2 horas sem decomposição. Consequência prática: o construto de sprint foi removido, o avaliador virou uma revisão única no fim, e o harness inteiro ficou mais simples.

> *"Essas suposições merecem ser testadas sob estresse, porque podem ficar obsoletas rapidamente conforme os modelos melhoram."*

**Custo-benefício, com números reais.** No exemplo do criador de jogos retrô: agente solo — 20 minutos, US$ 9, funcionalidade central quebrada. Harness completo — 6 horas, US$ 200, aplicação multi-feature funcionando. O aumento de 20× no custo produziu resultado demonstravelmente superior, mas **o avaliador só agrega valor quando a tarefa está além do que o modelo faz sozinho com confiabilidade**.

### 2.6 Agentes de longa duração: o padrão inicializador + executor

*Effective harnesses for long-running agents* trata do problema de agentes cuja tarefa atravessa várias janelas de contexto: **cada nova sessão começa sem memória do que veio antes**. Sem estrutura explícita, o agente ou tenta fazer tudo de uma vez (e acaba o contexto no meio) ou declara o projeto pronto prematuramente.

**Agente inicializador (só na primeira sessão):**

- Cria um arquivo **JSON** de lista de features (200+ features, cada uma marcada como falhando). O artigo é explícito sobre o formato: *"o modelo tem menos chance de alterar ou sobrescrever inapropriadamente arquivos JSON do que arquivos Markdown."*
- Cria `claude-progress.txt` para rastrear atividade e inicializa um repositório git com commit de baseline.
- Escreve um `init.sh` que sobe o ambiente de desenvolvimento automaticamente.

```json
{
  "category": "functional",
  "description": "New chat button creates conversation",
  "steps": ["Navigate", "Click", "Verify..."],
  "passes": false
}
```

**Agente de execução (todas as sessões seguintes)** segue uma sequência de onboarding padronizada:

1. Roda `pwd` para estabelecer o diretório de trabalho.
2. Lê logs do git e arquivos de progresso.
3. Escolhe **uma** feature incompleta da lista.
4. Executa `init.sh` e roda testes end-to-end básicos.
5. Implementa a feature incrementalmente.
6. Commita com mensagem descritiva e atualiza a documentação de progresso.

**Princípios explícitos:**

- **Progresso incremental** — uma feature por vez, evitando o problema do "one-shot".
- **Estado limpo** — o código deve chegar a um estado apropriado para merge na main: sem bugs graves, ordenado, documentado.
- **Teste explícito** — sem instrução explícita para testar como um usuário testaria, "o Claude tendia a marcar features como completas sem testar adequadamente". Automação de browser (Puppeteer) foi essencial.
- **Prompts diferentes para a primeira janela de contexto e para as seguintes** — essa distinção é descrita como crítica.
- Linguagem forte contra atalhos: *"É inaceitável remover ou editar testes, porque isso pode levar a funcionalidade faltante ou com bug."*

### 2.7 Paralelismo real: o caso do compilador C

*Building a C compiler with a team of parallel Claudes* documenta 16 instâncias de Opus 4.6 construindo autonomamente um compilador C de ~100 mil linhas em Rust, capaz de compilar Linux para x86, ARM e RISC-V. Aproximadamente **2 bilhões de tokens de entrada, 2.000 sessões, ~US$ 20.000**.

**Mecanismos de coordenação:**

- **Loop infinito** — cada agente roda em container, escolhe tarefa, completa, escolhe a próxima, sem intervenção humana.
- **Task locking por arquivos** — agentes reivindicam trabalho criando arquivos de texto em `current_tasks/`. A detecção de conflito do git previne trabalho duplicado.
- **Isolamento** — cada agente clona uma cópia local em `/workspace`, e ao terminar dá push do próprio container para o upstream, resolvendo conflitos de merge.

**O pré-requisito absoluto:**

> *"O verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o problema errado."*

Na prática: suítes de teste de compilador de alta qualidade (GCC torture tests), CI impedindo que novos commits quebrem o que funcionava, estatísticas pré-computadas para evitar poluir contexto, e amostragem determinística — cada agente testa uma amostra aleatória de 1–10% em subconjuntos diferentes.

**Lições de paralelismo:**

- **Otimize o contexto do log** — logging estruturado para parsing automático; mensagens de erro em formato consistente (`ERROR: [motivo]`) para serem passíveis de grep.
- **Consciência temporal** — modelos não têm noção de tempo; o harness incluiu um modo `--fast` para feedback rápido.
- **Especialização vence generalização** — atribuir papéis específicos (um agente para deduplicação, outro para performance, outro para crítica de design) foi mais eficaz que times homogêneos.
- **Tornar o paralelismo tratável** — quando o trabalho não é naturalmente decomponível (compilação monolítica do kernel, onde todos os agentes batiam no mesmo bug), a solução foi **teste diferencial**: compilar a maior parte com GCC e só os arquivos restantes com o compilador do Claude, permitindo que agentes consertassem arquivos diferentes em paralelo.

**O que generaliza:** projetos com verificação clara de tarefas, decomposição natural em fluxos paralelos, feedback estruturado que permita orientação autônoma, e documentação bem mantida para construção de contexto.

---

## 3. Qualidade de código e verificação

### 3.1 A regra central

A documentação de best practices coloca isso como a primeira e mais importante prática:

> **Dê ao Claude uma verificação que ele possa executar: testes, um build, um screenshot para comparar. É a diferença entre uma sessão que você assiste e uma da qual você pode se afastar.**

O raciocínio: **o Claude para quando o trabalho *parece* pronto**. Sem uma verificação executável, "parece pronto" é o único sinal disponível, e *você* vira o loop de verificação — todo erro espera você notar. Com algo que produz um pass/fail legível, o loop fecha sozinho.

A verificação é qualquer coisa que devolva um sinal legível na conversa: suíte de testes, exit code de build, linter, script que compara saída com um fixture, ou screenshot de browser comparado a um design.

### 3.2 Escada de rigor da verificação

| Nível | Mecanismo | Custo de setup |
|---|---|---|
| **No prompt** | Peça ao Claude para rodar a verificação e iterar na mesma mensagem | Zero — funciona hoje em qualquer tarefa |
| **Na sessão** | Defina a verificação como condição de `/goal`; um avaliador separado rechecha a cada turno | Baixo |
| **Portão determinístico** | Um **Stop hook** roda a verificação como script e bloqueia o fim do turno até passar (o Claude Code sobrepõe o hook e encerra após 8 bloqueios consecutivos) | Médio |
| **Segunda opinião** | Um subagente verificador ou workflow dinâmico faz um modelo novo tentar refutar o resultado — quem faz o trabalho não é quem dá a nota | Médio |

Cada degrau troca setup por atenção. Os níveis de `/goal` e Stop hook são o que permite uma execução não supervisionada terminar corretamente sem você.

### 3.3 Prompts com critério de verificação

Da tabela oficial de "antes e depois":

| Estratégia | Antes | Depois |
|---|---|---|
| Forneça critério de verificação | *"implemente uma função que valida emails"* | *"escreva uma função validateEmail. casos de teste: user@example.com é true, invalid é false, user@.com é false. rode os testes depois de implementar"* |
| Verifique UI visualmente | *"deixe o dashboard mais bonito"* | *"[cola screenshot] implemente este design. tire um screenshot do resultado e compare com o original. liste as diferenças e conserte"* |
| Ataque a causa raiz | *"o build está falhando"* | *"o build falha com este erro: [cola erro]. conserte e verifique que o build passa. ataque a causa raiz, não suprima o erro"* |

**Exija evidência, não afirmação.** Peça a saída do teste, o comando executado e o que ele retornou, ou um screenshot. Revisar evidência é mais rápido que refazer a verificação você mesmo — e funciona para sessões que você não assistiu.

### 3.4 Explore → Plan → Code → Commit

O workflow recomendado tem quatro fases:

1. **Explore** — entre em plan mode (`Shift+Tab` até `⏸ plan mode on`, ou `claude --permission-mode plan`). O Claude lê arquivos e responde sem alterar nada.
2. **Plan** — peça um plano de implementação detalhado. `Ctrl+G` abre o plano no seu editor para edição direta.
3. **Implement** — aprove o plano ou saia do plan mode; o Claude codifica verificando contra o próprio plano.
4. **Commit** — commit com mensagem descritiva e PR.

**Quando pular o plano:** a própria documentação alerta que plan mode adiciona overhead. Para escopo claro e correção pequena (typo, linha de log, renomear variável), peça direto. Planejar vale quando você está incerto sobre a abordagem, quando a mudança toca múltiplos arquivos, ou quando o código é desconhecido. **Se você consegue descrever o diff em uma frase, pule o plano.**

### 3.5 Revisão adversarial

Antes de considerar uma tarefa pronta, tenha um subagente revisando o diff em contexto novo. O revisor em contexto fresco vê apenas o diff e os critérios — não o raciocínio que produziu a mudança — então avalia o resultado nos próprios termos.

O `/code-review` embutido revisa o diff atual em busca de bugs num subagente novo. Para checar contra o plano, escreva o prompt você mesmo, nomeando: o trabalho a checar, o plano contra o qual checar, e o que conta como achado.

**O contra-alerta explícito da documentação:**

> Um revisor instruído a encontrar lacunas normalmente vai reportar algumas, mesmo quando o trabalho está sólido, porque foi isso que foi pedido. Perseguir todo achado leva a superengenharia: camadas extras de abstração, código defensivo, e testes para casos que não podem acontecer. **Diga ao revisor para sinalizar apenas lacunas que afetam corretude ou os requisitos declarados**, e trate o resto como opcional.

### 3.6 Padrão Writer/Reviewer com sessões paralelas

Um contexto novo melhora a revisão de código porque o Claude não fica enviesado a favor do código que ele mesmo acabou de escrever.

| Sessão A (Writer) | Sessão B (Reviewer) |
|---|---|
| `Implemente um rate limiter para nossos endpoints` | |
| | `Revise a implementação do rate limiter em @src/middleware/rateLimiter.ts. Procure edge cases, race conditions, e consistência com nossos padrões de middleware.` |
| `Aqui está o feedback: [saída da Sessão B]. Trate esses pontos.` | |

O mesmo vale para testes: uma sessão escreve os testes, outra escreve o código que os faz passar.

### 3.7 Os cinco antipadrões nomeados pela Anthropic

| Antipadrão | Sintoma | Correção |
|---|---|---|
| **Kitchen sink session** | Você começa com uma tarefa, pergunta algo não relacionado, volta à primeira. O contexto está cheio de coisa irrelevante | `/clear` entre tarefas não relacionadas |
| **Correção sobre correção** | O Claude erra, você corrige, ainda erra, você corrige de novo. O contexto está poluído com abordagens que falharam | Após **duas** correções falhas, `/clear` e escreva um prompt inicial melhor incorporando o que você aprendeu |
| **CLAUDE.md superespecificado** | O arquivo é longo demais; o Claude ignora metade porque as regras importantes se perdem no ruído | Poda impiedosa. Se o Claude já faz certo sem a instrução, apague ou converta em hook |
| **Trust-then-verify gap** | Implementação plausível que não trata edge cases | Sempre forneça verificação. **Se você não consegue verificar, não faça deploy** |
| **Exploração infinita** | "Investigue X" sem escopo; o Claude lê centenas de arquivos e enche o contexto | Escope a investigação ou use subagentes |

### 3.8 Faça as perguntas que faria a um engenheiro sênior

Para onboarding em um codebase, a documentação recomenda usar o Claude Code para aprendizado e exploração, com as mesmas perguntas que você faria a outro engenheiro:

- Como funciona o logging aqui?
- Como crio um novo endpoint de API?
- O que `async move { ... }` faz na linha 134 de `foo.rs`?
- Que edge cases `CustomerOnboardingFlowImpl` trata?
- Por que este código chama `foo()` em vez de `bar()` na linha 333?

Não requer prompting especial. É descrito como um workflow eficaz de onboarding, que reduz o tempo de rampa e a carga sobre outros engenheiros.

### 3.9 Deixe o Claude entrevistar você e escrever a spec

Para features maiores, a documentação recomenda inverter o fluxo:

```text
Quero construir [descrição breve]. Me entreviste em detalhe usando a ferramenta AskUserQuestion.

Pergunte sobre implementação técnica, UI/UX, edge cases, preocupações e tradeoffs.
Não faça perguntas óbvias, aprofunde nas partes difíceis que eu talvez não tenha considerado.

Continue entrevistando até cobrirmos tudo, então escreva uma spec completa em SPEC.md.
```

Depois, **comece uma sessão nova para executar** — contexto limpo, focado inteiramente na implementação, com a spec escrita como referência.

As specs mais úteis são autocontidas: nomeiam os arquivos e interfaces envolvidos, declaram o que está fora de escopo, e terminam com um passo de verificação end-to-end que prova que a feature funciona. **Tempo gasto tornando a spec precisa rende mais que tempo gasto assistindo a implementação.**

---

## 4. Memória e contexto persistente

Cada sessão do Claude Code começa com uma janela de contexto nova. Dois mecanismos carregam conhecimento entre sessões:

| | `CLAUDE.md` | Auto memory |
|---|---|---|
| **Quem escreve** | Você | O Claude |
| **O que contém** | Instruções e regras | Aprendizados e padrões |
| **Escopo** | Projeto, usuário ou organização | Por repositório, compartilhado entre worktrees |
| **Carregado em** | Toda sessão | Toda sessão (primeiras 200 linhas ou 25KB) |
| **Use para** | Padrões de código, workflows, arquitetura do projeto | Suas preferências, correções que você dá, contexto que o Claude não deriva do código |

**Ambos são contexto, não configuração aplicada.** Para bloquear uma ação independentemente do que o Claude decidir, use um hook `PreToolUse`.

### 4.1 CLAUDE.md: hierarquia e ordem de carga

| Escopo | Localização | Propósito |
|---|---|---|
| **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux/WSL: `/etc/claude-code/CLAUDE.md` · Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Instruções da organização (não podem ser excluídas por configuração individual) |
| **User** | `~/.claude/CLAUDE.md` | Preferências pessoais para todos os projetos |
| **Project** | `./CLAUDE.md` ou `./.claude/CLAUDE.md` | Instruções do time, versionadas |
| **Local** | `./CLAUDE.local.md` | Preferências pessoais do projeto; colocar no `.gitignore` |

**Como carrega:** o Claude Code lê `CLAUDE.md` e `CLAUDE.local.md` do diretório de trabalho e de todos os diretórios acima. Todos os arquivos descobertos são **concatenados**, não sobrescritos, ordenados da raiz do filesystem até o diretório de trabalho — ou seja, instruções mais próximas de onde você lançou o Claude são lidas por último. Dentro de cada diretório, `CLAUDE.local.md` vem depois de `CLAUDE.md`.

Arquivos em subdiretórios abaixo do diretório de trabalho **não** carregam no lançamento — são incluídos quando o Claude lê arquivos daqueles subdiretórios.

### 4.2 Como escrever um CLAUDE.md eficaz

**Rode `/init`** para gerar um arquivo inicial a partir da estrutura do projeto, e refine com o tempo. Com `CLAUDE_CODE_NEW_INIT=1` há um fluxo interativo multifásico que pergunta quais artefatos configurar, explora o codebase com um subagente e apresenta uma proposta revisável antes de escrever.

**Tamanho: alvo de menos de 200 linhas por arquivo.** Arquivos mais longos consomem mais contexto e reduzem a aderência. O Claude Code carrega um `CLAUDE.md` de até 4 MiB inteiro e pula arquivos maiores — mas arquivos curtos produzem aderência melhor.

**O teste de cada linha:** *"Remover isso faria o Claude cometer um erro?"* Se não, corte.

| ✅ Incluir | ❌ Excluir |
|---|---|
| Comandos bash que o Claude não tem como adivinhar | Qualquer coisa que o Claude descobre lendo o código |
| Regras de estilo que divergem do padrão | Convenções padrão da linguagem que o Claude já conhece |
| Instruções de teste e test runner preferido | Documentação detalhada de API (linkar em vez de colar) |
| Etiqueta do repositório (nomes de branch, convenções de PR) | Informação que muda com frequência |
| Decisões arquiteturais específicas do projeto | Explicações longas ou tutoriais |
| Peculiaridades do ambiente (variáveis obrigatórias) | Descrição arquivo-por-arquivo do codebase |
| Pegadinhas comuns e comportamentos não óbvios | Práticas autoevidentes tipo "escreva código limpo" |

**Especificidade:** *"Use indentação de 2 espaços"* em vez de *"formate o código adequadamente"*. *"Rode `npm test` antes de commitar"* em vez de *"teste suas mudanças"*. *"Handlers de API ficam em `src/api/handlers/`"* em vez de *"mantenha os arquivos organizados"*.

**Ênfase seletiva:** se o Claude continua pulando uma instrução, adicione "IMPORTANT" **àquela linha só**. Se você enfatizar muitas linhas, nenhuma se destaca.

**Diagnóstico:** se o Claude insiste em fazer algo que você proibiu, o arquivo provavelmente está longo demais e a regra se perdeu. Se o Claude faz perguntas já respondidas no CLAUDE.md, a redação está ambígua. Trate o arquivo como código: revise quando algo der errado, pode regularmente, e teste mudanças observando se o comportamento realmente muda.

**Verificação:** rode `/context` e confira a lista sob **Memory files**. Se o arquivo não estiver lá, o Claude não o está vendo.

**`/doctor`** propõe cortes para um CLAUDE.md versionado — remove o que o Claude deriva do codebase (layout de diretórios, listas de dependências, visões arquiteturais) e mantém pegadinhas, racional e convenções que divergem dos padrões da ferramenta.

**Imports:** `@path/to/import` expande e carrega arquivos adicionais no lançamento. Caminhos relativos resolvem relativos ao arquivo que contém o import. Profundidade máxima de 4 saltos. Para citar um caminho sem importar, envolva em crases. **Importar não reduz contexto** — o arquivo importado carrega igualmente no lançamento.

**`AGENTS.md`:** o Claude Code lê `CLAUDE.md`, não `AGENTS.md`. Se o repositório já usa `AGENTS.md`, crie um `CLAUDE.md` que o importe:

```markdown
@AGENTS.md

## Claude Code

Use plan mode para mudanças em `src/billing/`.
```

**Monorepos:** use `claudeMdExcludes` (com globs contra caminhos absolutos) em `.claude/settings.local.json` para pular CLAUDE.md de outros times. Managed policy não pode ser excluído.

### 4.3 `.claude/rules/` — regras escopadas por caminho

Para projetos maiores, organize instruções em `.claude/rules/`, um arquivo por tópico, descobertos recursivamente:

```
your-project/
├── .claude/
│   ├── CLAUDE.md
│   └── rules/
│       ├── code-style.md
│       ├── testing.md
│       └── security.md
```

Regras **sem** frontmatter `paths` carregam no lançamento com a mesma prioridade de `.claude/CLAUDE.md`. Regras **com** `paths` só entram em contexto quando o Claude trabalha com arquivos que casam:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# Regras de desenvolvimento de API

- Todo endpoint deve incluir validação de entrada
- Use o formato padrão de resposta de erro
- Inclua comentários de documentação OpenAPI
```

Suporta brace expansion (`src/**/*.{ts,tsx}`), com orçamento de 1.000 padrões expandidos e 4 MiB por regra. Suporta symlinks, o que permite manter um conjunto compartilhado de regras e linkar em vários projetos. Regras de usuário em `~/.claude/rules/` carregam antes das de projeto, dando prioridade maior às de projeto.

> **A escolha:** use regras path-scoped em vez de CLAUDE.md aninhado para restrições específicas de arquivo que aparecem em vários lugares.

### 4.4 Auto memory

O Claude salva quatro tipos de nota, registrados no campo `type` do frontmatter:

- `user` — seu papel, expertise e preferências de trabalho
- `feedback` — correções que você dá e abordagens que você confirma
- `project` — trabalho em andamento, prazos e decisões que o Claude não deriva do código ou do histórico git
- `reference` — onde encontrar informação fora do projeto (issue tracker, dashboard)

**O que o Claude deliberadamente não salva:** qualquer coisa derivável do codebase (arquitetura, caminhos de arquivo, correções de bug) e qualquer coisa que os arquivos CLAUDE.md já digam.

**Estrutura:** `~/.claude/projects/<project>/memory/` contendo um `MEMORY.md` (índice, uma linha por memória) e um arquivo por tópico. O `<project>` deriva do repositório git, então todos os worktrees e subdiretórios do mesmo repo compartilham um diretório de memória.

**Limites:** as primeiras **200 linhas ou 25KB** do `MEMORY.md` (o que vier primeiro) carregam no início de toda conversa. Conteúdo além disso é descartado. O Claude Code avisa quando o arquivo se aproxima do limite e retorna erro quando o ultrapassa, instruindo a reescrita do índice. Arquivos de tópico **não** carregam no startup — são lidos sob demanda.

Auto memory é local à máquina, não é compartilhada entre máquinas nem com ambientes na nuvem, e é excluída da varredura de retenção que apaga transcripts antigos. Desligue com o toggle em `/memory`, com `autoMemoryEnabled: false` nas settings, ou com `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

**A auto memory da conversa principal não é carregada em subagentes** — a exceção é um fork, que herda a conversa e o system prompt do pai. Um subagente pode ter a própria memória, via o campo `memory`.

### 4.5 Gestão ativa de contexto na sessão

- **`/clear`** entre tarefas não relacionadas — reseta a janela inteira. A prática mais recomendada da lista.
- **Compaction automática** quando o limite se aproxima: o Claude resume o que importa (padrões de código, estados de arquivo, decisões-chave).
- **`/compact <instruções>`** para controle, ex.: `/compact Foque nas mudanças de API`.
- **`Esc + Esc` ou `/rewind`** para restaurar conversa, código ou ambos a um checkpoint anterior; ou **Summarize from here / Summarize up to here** para compactar apenas parte da conversa.
- **Customizar a compaction no CLAUDE.md**, ex.: *"Ao compactar, sempre preserve a lista completa de arquivos modificados e os comandos de teste"*.
- **`/btw`** para perguntas laterais cuja resposta nunca entra no histórico.
- **`Esc`** interrompe o Claude no meio de uma ação preservando contexto.

**Checkpoints só rastreiam mudanças feitas pelas ferramentas de edição do Claude.** Mudanças feitas por comandos Bash ou processos externos não são capturadas — não substitui git.

**O que sobrevive à compaction:** o `CLAUDE.md` da raiz do projeto é relido do disco e reinjetado. CLAUDE.md aninhados e regras com `paths:` recarregam conforme o Claude lê arquivos correspondentes. **Instruções dadas apenas na conversa não sobrevivem** — se importam, vão para o CLAUDE.md.

### 4.6 Técnicas de horizonte longo (do artigo de context engineering)

- **Compaction** — resume o conteúdo próximo ao limite e reinicializa com o resumo. Princípios de implementação: maximizar *recall* primeiro (capturar tudo relevante), depois iterar para melhorar *precisão* (eliminar o supérfluo). Limpar resultados de chamadas de ferramenta é a otimização mais óbvia. Risco: compaction agressiva demais elimina contexto sutil mas crítico.
- **Note-taking estruturado** — memória persistente fora da janela (`CLAUDE.md`, `NOTES.md`, listas de to-do), trazida de volta quando necessária. Permite rastrear progresso, manter dependências ao longo de dezenas de chamadas de ferramenta e manter coerência através de resets de contexto.
- **Arquiteturas de subagentes** — subagentes especializados com janelas limpas, coordenador mantendo o plano de alto nível.

---

## 5. Skills

### 5.1 O que são e por que existem

*Equipping agents for the real world with Agent Skills* define skills como **"pastas organizadas de instruções, scripts e recursos que agentes podem descobrir e carregar dinamicamente para ter melhor desempenho em tarefas específicas"** — comparadas a um guia de onboarding para um novo contratado.

A documentação do Claude Code dá o gatilho prático: **crie uma skill quando você continuar colando as mesmas instruções, checklist ou procedimento de vários passos no chat, ou quando uma seção do CLAUDE.md virou um procedimento em vez de um fato.** Diferente do CLAUDE.md, o corpo de uma skill só carrega quando é usada — material de referência longo custa quase nada até ser necessário.

> Nota de nomenclatura: comandos customizados foram fundidos em skills. `.claude/commands/deploy.md` e `.claude/skills/deploy/SKILL.md` ambos criam `/deploy`. Arquivos existentes em `.claude/commands/` continuam funcionando.

### 5.2 Progressive disclosure em três níveis

1. **Metadata** (`name` + `description`) — pré-carregados no system prompt no startup, permitindo ao modelo reconhecer quando ativar cada skill sem consumir contexto.
2. **Conteúdo completo do `SKILL.md`** — carrega quando o Claude determina relevância.
3. **Arquivos auxiliares** (referências, código) — acessados apenas quando necessários.

O exemplo canônico: na skill de PDF, as instruções de preenchimento de formulário ficam num `forms.md` separado, carregado só quando o Claude encontra uma tarefa de formulário.

### 5.3 Reference vs. Task

**Reference content** adiciona conhecimento que o Claude aplica ao trabalho atual — convenções, padrões, style guides, conhecimento de domínio. Roda inline junto com o contexto da conversa:

```yaml
---
name: api-conventions
description: Padrões de design de API para este codebase
---

Ao escrever endpoints de API:
- Use convenções RESTful de nomenclatura
- Retorne formatos de erro consistentes
- Inclua validação de request
```

**Task content** dá instruções passo a passo para uma ação específica — deploys, commits, geração de código. Costumam ser invocadas diretamente com `/skill-name`:

```yaml
---
name: deploy
description: Faz deploy da aplicação em produção
context: fork
disable-model-invocation: true
---

Faça o deploy:
1. Rode a suíte de testes
2. Build da aplicação
3. Push para o alvo de deploy
```

**Mantenha o corpo conciso.** Uma vez que a skill carrega, o conteúdo **permanece em contexto entre turnos** — cada linha é custo recorrente de tokens. Declare o que fazer, em vez de narrar como ou por quê. Aplique o mesmo teste de concisão do CLAUDE.md.

### 5.4 Frontmatter — os campos que mais importam

Todos os campos são opcionais; apenas `description` é recomendado. O frontmatter só é lido se o `---` de abertura for a primeira linha do arquivo.

| Campo | O que resolve |
|---|---|
| `name` | Nome exibido. Padrão: o nome do diretório |
| `description` | **O que dispara a skill.** O que ela faz e quando usar. Se omitido, usa o primeiro parágrafo. **Coloque o caso de uso principal primeiro:** o texto combinado de `description` + `when_to_use` é truncado em **1.536 caracteres** na listagem de skills |
| `when_to_use` | Contexto adicional de disparo — frases-gatilho, exemplos de pedido. Conta para o limite de 1.536 caracteres |
| `disable-model-invocation` | `true` impede o Claude de carregar automaticamente. **Use para workflows com efeitos colaterais que só você deve disparar.** Também impede o pré-carregamento em subagentes |
| `user-invocable` | `false` quando só o Claude deve invocar — esconde do menu `/`. Para conhecimento de fundo |
| `allowed-tools` | Ferramentas que o Claude pode usar sem pedir permissão durante o turno que invoca a skill. A concessão expira na sua próxima mensagem |
| `disallowed-tools` | Ferramentas removidas do pool enquanto a skill está ativa. Ex.: remover `AskUserQuestion` de um loop autônomo |
| `context: fork` | Roda a skill em contexto de subagente forkado |
| `agent` | Qual tipo de subagente usar com `context: fork` |
| `background` | Com `context: fork`, `false` espera o resultado no mesmo turno |
| `paths` | Globs que limitam quando a skill é ativada automaticamente. Mesmo formato das path-specific rules |
| `model` / `effort` | Modelo e nível de esforço enquanto a skill está ativa. Não são salvos nas settings |
| `hooks` | Hooks registrados quando a skill é invocada, mantidos pelo resto da sessão |
| `argument-hint` / `arguments` | Autocomplete e substituição posicional (`$name`) |
| `metadata`, `license`, `compatibility` | Campos da spec Agent Skills; o Claude Code aceita mas não age sobre eles |

**Portabilidade — atenção.** Fora do Claude Code, só valem os campos da spec [Agent Skills](https://agentskills.io):

| Caminho de distribuição | Campos permitidos |
|---|---|
| Skills do Claude Code (inclusive de plugins) | Todos os campos acima |
| Upload em claude.ai, Skills API, empacotamento com `package_skill.py` de `anthropics/skills` | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` |

Incluir campo fora da spec faz o empacotamento ou upload falhar com erro duro, não ignorar o campo.

### 5.5 Código executável dentro de skills

Skills podem trazer scripts que o Claude executa como ferramentas. As vantagens sobre gerar o equivalente em tokens:

- **Eficiência** — rodar um algoritmo de ordenação custa menos tokens que gerá-lo.
- **Confiabilidade** — execução de código dá resultado determinístico e repetível.
- **Preservação de contexto** — o Claude roda o script sem carregá-lo em contexto.

Exemplo citado: a skill de PDF usa um script Python que extrai campos de formulário sem que o script nem o documento precisem ser lidos como texto.

### 5.6 Autoria de skills — o que a Anthropic recomenda

- **Comece pela avaliação.** *"Identifique lacunas específicas nas capacidades dos seus agentes rodando-os em tarefas representativas e observando onde eles travam ou precisam de contexto adicional."*
- **Estruture para escalar.** Quando o `SKILL.md` fica pesado, divida em arquivos separados. Mantenha contextos "mutuamente exclusivos ou raramente usados" separados. Deixe claro se o código deve ser **executado** ou **lido como referência**.
- **Pense da perspectiva do Claude.** Monitore o uso real; "observe trajetórias inesperadas ou dependência excessiva de certos contextos". **Dê atenção cuidadosa ao nome e à descrição** — é neles que o Claude se baseia para decidir o disparo.
- **Itere junto com o Claude.** Trabalhe com o modelo para "capturar suas abordagens bem-sucedidas e erros comuns em contexto e código reutilizáveis".

**Diagnóstico de disparo** (da documentação): se uma skill não dispara, a descrição provavelmente é vaga ou sobrepõe outra; se dispara demais, a descrição é ampla demais; descrições cortadas indicam que o limite de 1.536 caracteres foi atingido.

### 5.7 Segurança de skills

O artigo é explícito: skills expandem capacidade e por isso trazem risco. **Instale skills apenas de fontes confiáveis.** Para fontes menos confiáveis, audite completamente os arquivos empacotados antes do uso — inspecionando código, dependências e recursos. Examine com atenção especial instruções que mandem o Claude se conectar a fontes de rede externas.

### 5.8 Onde as skills funcionam

Skills funcionam hoje no Claude.ai, no Claude Code, no Claude Agent SDK e na Claude Developer Platform. A spec foi publicada como padrão aberto para portabilidade entre plataformas. O repositório `anthropics/skills` traz `./skills/` (exemplos por categoria), `./spec/` (a especificação) e `./template/` (template para skills novas) — com a ressalva de que os exemplos são para fins demonstrativos e educacionais e podem divergir do comportamento de produção.

> A aspiração declarada de longo prazo: permitir que agentes **criem, editem e avaliem skills por conta própria**, codificando os próprios padrões de comportamento em capacidades reutilizáveis.

---

## 6. Subagents e paralelismo

### 6.1 A razão de existir: isolamento de contexto

Subagents são assistentes especializados que rodam em **janelas de contexto isoladas**. São úteis quando uma tarefa inundaria a conversa principal com resultados de busca, logs ou arquivos que você não vai reler — o subagente faz esse trabalho separado e devolve apenas o resumo.

Como a documentação de best practices coloca: *"já que contexto é sua restrição fundamental, use subagentes para manter a pesquisa fora dele."*

**Benefícios listados:** preservar contexto separando exploração de implementação; impor restrições de ferramenta e permissão; reutilizar configurações entre projetos; controlar custo roteando tarefas para modelos mais baratos como Haiku; rodar tarefas em paralelo ou em sequência.

### 6.2 Formato e campos de frontmatter

```markdown
---
name: security-reviewer
description: Revisa código em busca de vulnerabilidades de segurança
tools: Read, Grep, Glob, Bash
model: opus
---

Você é um engenheiro de segurança sênior. Revise o código buscando:
- Vulnerabilidades de injeção (SQL, XSS, injeção de comando)
- Falhas de autenticação e autorização
- Segredos ou credenciais no código
- Manipulação insegura de dados

Forneça referências de linha específicas e correções sugeridas.
```

| Campo | Descrição |
|---|---|
| `name` (obrigatório) | Identificador único; minúsculas e hífens |
| `description` (obrigatório) | **Quando o Claude deve delegar a este subagente.** Descrições combinadas acima de 15.000 tokens disparam aviso |
| `tools` | Allowlist. Herda todas se omitido |
| `disallowedTools` | Denylist. Aplicada antes de `tools` |
| `model` | `sonnet`, `opus`, `haiku`, `fable`, ID completo, ou `inherit` |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | Máximo de turnos agênticos antes de parar |
| `skills` | Skills **pré-carregadas** integralmente no contexto do subagente no startup |
| `mcpServers` | Servidores MCP escopados a este subagente |
| `hooks` | Hooks de ciclo de vida (`PreToolUse`, `PostToolUse`, `Stop`) |
| `memory` | Memória persistente: `user`, `project` ou `local` |
| `isolation` | `worktree` para worktree git isolado |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` |
| `background`, `color`, `initialPrompt`, `experimental` | Comportamento de execução e apresentação |

Um detalhe útil de segurança: `tools: Agent(worker, researcher), Read, Bash` restringe **quais tipos de subagente** este subagente pode disparar.

### 6.3 Precedência e o que carrega no startup

| Localização | Escopo | Prioridade |
|---|---|---|
| Managed settings | Organização | 1 (mais alta) |
| Flag `--agents` | Sessão atual | 2 |
| `.claude/agents/` | Projeto (versionar) | 3 |
| `~/.claude/agents/` | Todos os projetos | 4 |
| `agents/` de plugin | Onde o plugin está ativo | 5 |

**Carrega no startup de um subagente não-fork:** o system prompt próprio (o corpo markdown, **não** o system prompt do Claude Code) + detalhes de ambiente; a mensagem de delegação; os arquivos CLAUDE.md da hierarquia; snapshot do git status; conteúdo integral das skills listadas em `skills`; e a lista de agentes irmãos disponíveis via `SendMessage`.

**Não carrega — e isso é o ponto:** histórico da conversa, output style da sessão principal, auto memory da sessão principal, skills que o Claude já invocou, arquivos que o Claude já leu. Os agentes embutidos **Explore** e **Plan** pulam inclusive CLAUDE.md e git status.

### 6.4 Subagent vs. fork vs. dynamic workflow

- **Subagente comum** — worker focado com contexto próprio; devolve resumo. Use para pesquisa, verificação, revisão de arquivo.
- **Fork** (`/subtask`) — herda **toda** a conversa, system prompt, ferramentas e modelo do pai. Roda em background enquanto você continua; as chamadas de ferramenta ficam isoladas e só o resultado final volta. É one-shot, não pode ser retomado. Use quando a tarefa lateral precisa do contexto completo para fazer sentido.
- **Dynamic workflow** — script que o Claude escreve rodando muitos subagentes em background e devolvendo um resultado. Use quando o trabalho **ultrapassa um punhado de subagentes**, ou quando você quer os achados cross-checados antes de vê-los: auditoria de codebase inteiro, migração grande, plano montado sob vários ângulos.

Nas palavras da documentação: com subagentes, o **Claude** decide turno a turno o que roda em seguida; num workflow, o **script** decide.

### 6.5 Quando *não* usar subagente

Use a conversa principal para: idas e vindas frequentes; trabalho multifásico que compartilha contexto (planejar → implementar → testar); mudanças rápidas e pontuais; quando latência importa; trabalho que exige o histórico existente.

### 6.6 Memória persistente de subagente

```yaml
name: code-reviewer
memory: project
```

Cria `.claude/agent-memory/code-reviewer/`, com o subagente mantendo automaticamente um `MEMORY.md` (as primeiras 200 linhas entram no system prompt dele). Escopos: `user` → `~/.claude/agent-memory/<nome>/`; `project` → `.claude/agent-memory/<nome>/` (versionável); `local` → `.claude/agent-memory-local/<nome>/`.

---

## 7. Hooks

### 7.1 A distinção fundamental

> Instruções em CLAUDE.md ou numa skill são **advisórias**. Hooks são **determinísticos e garantem que a ação aconteça**.

A documentação é direta sobre a consequência prática: *"uma instrução como 'nunca edite `.env`' no CLAUDE.md ou numa skill é um pedido, não uma garantia. Um hook `PreToolUse` que bloqueia a edição é aplicação da regra. **Se uma regra precisa valer sempre, faça dela um hook, não uma instrução de prompt.**"*

**Use hooks para ações que precisam acontecer toda vez, sem exceção.** O Claude pode escrever hooks para você: *"Escreva um hook que roda eslint depois de cada edição de arquivo"*, *"Escreva um hook que bloqueia escritas na pasta de migrations"*. Configure à mão em `.claude/settings.json` e navegue o que existe com `/hooks`.

**Custo de contexto: zero**, a menos que o hook retorne output.

### 7.2 Catálogo de eventos

| Categoria | Eventos |
|---|---|
| **Sessão** | `SessionStart`, `Setup`, `SessionEnd` |
| **Prompt** | `UserPromptSubmit`, `UserPromptExpansion` |
| **Ferramentas** | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` |
| **Permissões** | `PermissionRequest`, `PermissionDenied` |
| **Subagentes e tarefas** | `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle` |
| **Fim de turno** | `Stop`, `StopFailure` |
| **Contexto** | `PreCompact`, `PostCompact`, `InstructionsLoaded` |
| **Ambiente** | `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged` |
| **Worktrees** | `WorktreeCreate`, `WorktreeRemove` |
| **Modelo** | `PreModelSwitch`, `PostModelSwitch` |
| **MCP** | `Elicitation`, `ElicitationResult` |
| **Interface** | `Notification`, `MessageDisplay` |

### 7.3 Os cinco tipos de hook

| Tipo | O que faz | Quando cabe |
|---|---|---|
| `command` | Roda um comando de shell | O caso padrão — lint, format, validação |
| `http` | POST dos dados do evento para uma URL | Integração com serviços externos |
| `mcp_tool` | Chama uma ferramenta em um servidor MCP já conectado | Reaproveitar uma integração existente |
| `prompt` | Avaliação de LLM em um único turno | Decisões que exigem julgamento, não regra determinística |
| `agent` | Verificação multi-turno com acesso a ferramentas (**experimental**) | Verificação profunda |

### 7.4 Combinação de múltiplos hooks

Quando vários hooks casam com o mesmo evento, **todos rodam até o fim** antes de o Claude Code combinar os resultados. Um hook retornando `deny` **não** impede os hooks irmãos de executarem — não confie em um `deny` para suprimir efeitos colaterais de outro hook.

Para decisões de permissão em `PreToolUse`, a resposta **mais restritiva** vence, na ordem: `deny` → `defer` → `ask` → `allow`. Texto em `additionalContext` de todos os hooks é preservado e passado junto ao Claude.

### 7.5 Casos canônicos

Os exemplos que a documentação desenvolve: notificação quando o Claude precisa de input; auto-formatação de código após edições; bloqueio de edições em arquivos protegidos; **reinjeção de contexto após compaction**; auditoria de mudanças de configuração; recarga de ambiente quando o diretório ou arquivos mudam; auto-aprovação de prompts de permissão específicos.

E, para fechar o loop de verificação da §3: um **Stop hook** que roda seu check e bloqueia o fim do turno até passar. O Claude Code sobrepõe o hook e encerra o turno após **8 bloqueios consecutivos**.

---

## 8. MCP e design de ferramentas

### 8.1 Os cinco princípios de ferramentas eficazes

*Writing effective tools for agents — with agents* parte da premissa de que **"agentes são tão eficazes quanto as ferramentas que damos a eles"**, e que isso exige mudar as práticas de desenvolvimento de design determinístico para design não determinístico.

**1. Escolha as ferramentas certas.** Mais ferramentas não melhoram o resultado. Em vez de empacotar cada endpoint de API, foque nos workflows de alto impacto e **consolide**: uma única ferramenta `schedule_event` em vez de `list_users`, `list_events` e `create_event` separadas. Isso reduz consumo de contexto e previne confusão do agente.

**2. Namespacing.** Agrupe ferramentas relacionadas sob prefixos comuns (`asana_search`, `jira_search`). Esquemas baseados em prefixo vs. sufixo produzem "efeitos não triviais" no desempenho — teste.

**3. Retorne contexto significativo.** Priorize informação de alto sinal sobre detalhe técnico. Use **identificadores semânticos em vez de UUIDs crípticos** — agentes vão melhor com nomes em linguagem natural. Uma técnica útil: expor um parâmetro enum `response_format` que permita ao agente pedir resposta "concise" ou "detailed".

**4. Otimize eficiência de tokens.** Implemente paginação, filtragem, seleção de faixa e truncamento com defaults sensatos. Quando a resposta exceder o tamanho ideal, **forneça orientação** que direcione o agente a buscas mais focadas. Respostas de erro devem comunicar "melhorias específicas e acionáveis" em vez de códigos obscuros.

**5. Faça prompt engineering das descrições.** Descrito como um dos métodos de otimização mais impactantes. As descrições devem explicitar o contexto implícito: formatos de query especializados, definições de terminologia, relações entre recursos. Nomes de parâmetros inequívocos (`user_id` em vez de `user`) previnem uso incorreto. Até refinamentos pequenos rendem "melhorias dramáticas".

### 8.2 Desenvolvimento de ferramentas orientado a avaliação

O processo recomendado:

1. **Protótipo** — envolva as ferramentas num servidor MCP local ou Desktop extension e teste no Claude Code / Claude Desktop. Use documentação LLM-friendly (arquivos `llms.txt`) para as APIs e SDKs relevantes.
2. **Gere tarefas de avaliação ancoradas em workflows reais** — tarefas fortes exigem múltiplas chamadas de ferramenta e espelham casos de uso reais (agendar reunião com documentos anexados, investigar problema de cobrança). Tarefas fracas simplificam demais o cenário.
3. **Execute** com chamadas programáticas à API em loops agênticos simples. O system prompt deve encorajar o agente a raciocinar antes das chamadas. Métricas: acurácia, tempo de execução, consumo de tokens, número de chamadas, taxa de erro.
4. **Analise** — *"o que os agentes omitem no feedback e nas respostas frequentemente importa mais do que o que eles incluem."*
5. **Colabore com o Claude** — forneça os transcripts de avaliação ao Claude Code e deixe-o analisar padrões e refinar as implementações. No teste interno, as ferramentas otimizadas pelo Claude tiveram acurácia significativamente melhor em conjuntos de teste retidos que as escritas por humanos.

### 8.3 Code execution with MCP

O artigo identifica dois padrões que degradam desempenho conforme agentes se conectam a centenas ou milhares de ferramentas MCP:

1. **Sobrecarga de definições** — clientes que carregam todas as definições antecipadamente consomem tokens massivos antes de ler o pedido. Com milhares de ferramentas, "vão processar centenas de milhares de tokens antes de ler um request".
2. **Duplicação de resultados intermediários** — em chamadas sequenciais, os resultados passam pelo contexto múltiplas vezes. Buscar uma transcrição no Google Drive e subi-la ao Salesforce força a transcrição inteira pelo contexto duas vezes.

**A solução:** apresentar os servidores MCP como **APIs de código** em uma árvore de arquivos, onde cada servidor é um diretório:

```
servers/
├── google-drive/getDocument.ts
├── salesforce/updateRecord.ts
└── ...
```

O agente descobre ferramentas explorando diretórios e lendo apenas as definições necessárias. No exemplo apresentado, o uso de tokens caiu de **150.000 para 2.000 — economia de 98,7%**.

**Benefícios:**

- **Progressive disclosure** — *"modelos são ótimos em navegar filesystems."* Definições carregam sob demanda. Uma função opcional `search_tools` com níveis configuráveis de detalhe economiza ainda mais.
- **Resultados eficientes em contexto** — o agente filtra e transforma dados **no ambiente de execução** antes de retornar. Em vez de passar 10.000 linhas de planilha pelo contexto para filtrar, processa localmente e devolve só o subconjunto relevante. Vale também para agregações, joins entre fontes e extração de campos.
- **Controle de fluxo poderoso** — *"loops, condicionais e tratamento de erro podem ser feitos com padrões familiares de código em vez de encadear chamadas individuais."* Reduz latência ao eliminar a alternância entre avaliação do modelo e chamada de ferramenta.
- **Privacidade por padrão** — *"resultados intermediários ficam no ambiente de execução por padrão."* O agente só vê o que é explicitamente logado. Para workflows sensíveis, o cliente MCP pode tokenizar PII automaticamente, permitindo que dados reais fluam entre ferramentas sem que o modelo os acesse.
- **Persistência de estado e skills** — o agente escreve arquivos e os relê depois; e, mais significativo, **salva código funcionante como funções reutilizáveis**, construindo um toolkit crescente de capacidades de nível mais alto.

**O tradeoff, dito explicitamente:** *"rodar código gerado por agente exige um ambiente de execução seguro com sandboxing apropriado, limites de recurso e monitoramento."* Essas demandas de infraestrutura adicionam overhead e considerações de segurança que chamadas diretas de ferramenta evitam. É uma decisão de custo de tokens e latência **contra** complexidade de implementação e requisitos de segurança.

### 8.4 Quando preferir CLI a MCP

A documentação de best practices é explícita: **ferramentas CLI são a forma mais eficiente em contexto de interagir com serviços externos.** Se você usa GitHub, instale o `gh` — o Claude sabe usá-lo para criar issues, abrir PRs e ler comentários. Sem ele, o Claude ainda pode usar a API do GitHub, mas requests não autenticados frequentemente batem em rate limit.

O Claude também é eficaz em aprender CLIs que não conhece: *"Use 'foo-cli-tool --help' para aprender sobre a ferramenta foo, depois use para resolver A, B, C."*

**Custo de contexto do MCP:** tool search está ligado por padrão, então ferramentas MCP ociosas consomem contexto mínimo — nomes de ferramenta e instruções de servidor carregam no início, mas os schemas JSON completos ficam adiados. Use `/mcp` para status de conexão e `/context all` para ver quantos tokens cada ferramenta MCP carregada usa.

---

## 9. Escolha do mecanismo: tabela de decisão

### 9.1 O eixo: custo de contexto vs. autoridade da instrução

O artigo *Steering Claude Code* nomeia o tradeoff central: **cada método troca custo de contexto por autoridade**. Métodos de baixo custo (skills, subagents, hooks) carregam seletivamente ou rodam fora do contexto; métodos de alto custo (CLAUDE.md, output styles) sempre ocupam a janela mas carregam peso maior de aderência.

O raciocínio central: mantenha o contexto da sessão enxuto carregando instruções só quando relevantes, e use **ferramental determinístico (hooks, permissões) para restrições duras**, em vez de depender da aderência do Claude a prompts.

### 9.2 Tabela consolidada

| Mecanismo | Quando carrega | O que carrega | Custo de contexto | Determinismo | Melhor para |
|---|---|---|---|---|---|
| **CLAUDE.md** | Início da sessão | Conteúdo integral | **A cada request** | Advisório | Convenções do projeto, regras "sempre faça X" |
| **`.claude/rules/`** | Toda sessão, ou quando arquivos correspondentes são abertos (`paths:`) | Conteúdo integral | Alto sem `paths`, baixo com | Advisório | Convenções transversais escopadas por caminho |
| **Skill** | Descrições no início; corpo quando usada | Descrição sempre; corpo sob demanda | Baixo (descrições a cada request) | Advisório | Material de referência, workflows repetíveis |
| **Subagent** | Quando disparado | Contexto novo e isolado | **Isolado** da sessão principal | Advisório | Tarefas que leem muitos arquivos, trabalho paralelo |
| **Dynamic workflow** | Quando disparado | Script rodando muitos subagentes | Isolado; devolve um resultado | Script decide o fluxo | Auditorias de codebase inteiro, migrações grandes |
| **Hook** | No evento de ciclo de vida | Nada (roda externamente) | **Zero**, salvo se retornar output | **Garantido** | Guardrails, lint/format, logging, notificações |
| **MCP** | Início da sessão | Nomes de ferramenta; schemas sob demanda | Baixo até uso | Ferramenta determinística, uso advisório | Dados e ações externas |
| **Code intelligence (LSP)** | Após edições e sob demanda | Diagnósticos e localização de símbolos | Baixo; **reduz** leituras de arquivo | Determinístico | Linguagens tipadas, codebases grandes |
| **Output style** | Sempre (system prompt) | Conteúdo integral | Alto; nunca compactado | Maior peso de aderência | Mudança significativa de papel |
| **`--append-system-prompt`** | Por invocação | Conteúdo integral | Alto | Alto | Padrões injetados em scripts/automação |
| **Plugin** | Camada de empacotamento | Agrupa skills, hooks, subagents, MCP | Depende do conteúdo | — | Reusar o mesmo setup em vários repositórios |

> ⚠️ Sobre output styles, a documentação alerta: **substituir o estilo padrão remove instruções críticas** sobre escopo, comentários, segurança e verificação de testes. Os estilos embutidos (Proactive, Explanatory, Learning) cobrem a maioria das necessidades.

### 9.3 Como as camadas se combinam

- **CLAUDE.md** é **aditivo**: todos os níveis contribuem simultaneamente. Em conflito, o Claude usa julgamento — instruções mais específicas tendem a prevalecer.
- **Skills e subagents** sobrescrevem **por nome**: managed > user > project (skills); managed > flag CLI > project > user > plugin (subagents). Skills de plugin são namespaced.
- **Servidores MCP** sobrescrevem por nome: local > project > user.
- **Hooks** se **fundem**: todos os hooks registrados disparam nos eventos correspondentes, independentemente da origem.

### 9.4 Gatilhos de adoção incremental

Você não precisa configurar tudo antecipadamente. Cada mecanismo tem um gatilho reconhecível:

| Gatilho | Adicione |
|---|---|
| O Claude erra uma convenção ou comando **duas vezes** | Uma linha no CLAUDE.md |
| Você digita o mesmo prompt para começar uma tarefa | Uma skill user-invocable |
| Você cola o mesmo playbook no chat pela **terceira** vez | Uma skill |
| Você copia dados de uma aba de browser que o Claude não vê | Um servidor MCP |
| O Claude lê muitos arquivos para achar onde um símbolo é definido | Um plugin de code intelligence |
| Uma tarefa lateral inunda a conversa com output que você não vai reler | Um subagente |
| Você quer que algo aconteça **toda vez**, sem perguntar | Um hook |
| Um segundo repositório precisa do mesmo setup | Um plugin |

Os mesmos gatilhos dizem quando **atualizar** o que já existe: um erro repetido ou um comentário recorrente de revisão é uma edição no CLAUDE.md, não uma correção pontual no chat.

### 9.5 Antipadrões → correção

| Problema | Correção |
|---|---|
| "Toda vez que X, sempre faça Y" no CLAUDE.md | Mova para um hook no `settings.json` |
| "Nunca faça isso" no CLAUDE.md | Hook `PreToolUse` ou permissões gerenciadas — prompts sozinhos falham sob pressão |
| Procedimentos de 30 linhas no CLAUDE.md | Mova para `.claude/skills/`, onde só carregam quando invocados |
| Regras específicas de API sem escopo | Adicione frontmatter `paths:` |
| Preferências pessoais no CLAUDE.md do projeto | Use arquivos de nível de usuário; mantenha o do projeto para convenções do time |

### 9.6 Combinações que a Anthropic destaca

| Padrão | Como funciona |
|---|---|
| **Skill + MCP** | MCP provê a conexão; a skill ensina o Claude a usá-la bem (schema do banco, padrões de query) |
| **Skill + Subagent** | Uma skill `/audit` dispara subagentes de segurança, performance e estilo em contexto isolado |
| **CLAUDE.md + Skills** | CLAUDE.md diz "siga nossas convenções de API"; a skill contém o style guide completo |
| **Hook + MCP** | Hook pós-edição dispara notificação no Slack via MCP quando arquivos críticos mudam |

---

## 10. Avaliação (evals)

*Demystifying evals for AI agents* trata evals como testes sistemáticos que medem desempenho antes do deploy. *"Boas avaliações ajudam times a lançar agentes de IA com mais confiança"* — tornando problemas visíveis cedo, em vez de reativamente por reclamação de usuário.

Os benefícios que compõem e justificam o investimento inicial: proteção contra regressão, adoção rápida de novos modelos, linha de base de desempenho, e alinhamento entre produto e pesquisa em torno de métricas concretas.

### 10.1 Vocabulário

| Termo | Definição |
|---|---|
| **Task / problem** | Um teste único, com entradas e critérios de sucesso definidos |
| **Trial** | Uma tentativa de uma task (múltiplos trials cobrem a variabilidade do modelo) |
| **Grader** | Lógica de pontuação; uma task pode ter múltiplos graders com checagens diferentes |
| **Transcript / trace** | Registro completo de outputs, chamadas de ferramenta, raciocínio e interações |
| **Outcome** | Estado final do ambiente (ex.: a reserva realmente existe no banco?) |
| **Harness de avaliação** | Infraestrutura que roda tasks concorrentemente, registra passos e agrega resultados |
| **Suite** | Coleção de tasks relacionadas medindo uma capacidade específica |

A distinção single-turn vs. multi-turn importa: avaliações de agente precisam acomodar decisão autônoma ao longo de vários passos, **onde erros compõem**.

### 10.2 Os três tipos de grader

| Tipo | Forças | Fraquezas | Métodos |
|---|---|---|---|
| **Código** | Rápido, barato, objetivo, reproduzível | Frágil contra variações válidas; sem nuance para tarefas subjetivas | String matching, testes binários, análise estática, verificação de outcome, análise de transcript |
| **Modelo** | Flexível, escalável, captura nuance, lida com saídas abertas | Não determinístico, mais caro, precisa de calibração contra julgamento humano | Rubricas, asserções em linguagem natural, consenso de múltiplos juízes |
| **Humano** | Padrão-ouro; calibra os graders de modelo | Caro, lento, frequentemente exige especialista de domínio | — |

Avaliações eficazes **combinam os três** estrategicamente.

### 10.3 Abordagem por tipo de agente

- **Agentes de código** — graders determinísticos, especialmente testes unitários. SWE-bench Verified e Terminal-Bench como exemplos: a task passa apenas quando o código gerado conserta os testes falhando **sem quebrar os existentes**. Complemente a verificação de outcome com grading de transcript avaliando qualidade de código.
- **Agentes conversacionais** — sucesso multidimensional: conclusão da tarefa (verificação de estado), eficiência (limites de turnos) e qualidade de interação (tom, empatia). Frequentemente exigem **simular personas de usuário** com chamadas LLM adicionais.
- **Agentes de pesquisa** — combine graders: checagens de *groundedness* (as afirmações têm suporte nas fontes?), de cobertura (os fatos obrigatórios apareceram?), de qualidade de fonte, e rubricas LLM para coerência da síntese. Calibração frequente contra julgamento humano especialista é essencial.
- **Agentes de computer use** — rodar em ambientes reais ou sandboxed, verificando **tanto a navegação de UI quanto a mudança de estado no backend** (o pedido foi realmente feito, não só exibido).

### 10.4 `pass@k` vs. `pass^k`

- **`pass@k`** — probabilidade de ao menos uma solução correta em `k` tentativas. Útil quando uma solução funcional basta.
- **`pass^k`** — probabilidade de **todos** os `k` trials passarem. Fica mais difícil conforme `k` cresce; **essencial para sistemas voltados ao usuário que precisam de confiabilidade toda vez**.

As métricas divergem significativamente: com `k=10`, `pass@k` pode se aproximar de 100% enquanto `pass^k` despenca.

### 10.5 Roteiro do zero

1. **Comece imediatamente com escopo mínimo.** **20–50 tasks simples** vindas de falhas reais de usuário, em vez de esperar centenas de tasks perfeitas. No início do desenvolvimento os efeitos são grandes e amostras pequenas bastam.
2. **Converta checagens manuais existentes.** Puxe tasks de comportamentos que você já verifica manualmente, de bug trackers e da fila de suporte.
3. **Escreva tasks inequívocas com solução de referência.** **Dois especialistas independentes devem chegar ao mesmo veredito** de pass/fail. A solução de referência prova que a task é solucionável e que os graders funcionam. Uma taxa de aprovação persistente de 0% frequentemente indica **especificação quebrada**, não agente incapaz.
4. **Monte conjuntos balanceados.** Teste tanto quando o comportamento **deve** ocorrer quanto quando **não deve**. Evals unilaterais criam otimização unilateral.
5. **Construa ambientes robustos e isolados.** Cada trial começa do zero. Estado compartilhado entre execuções (arquivos remanescentes, cache) introduz falhas correlacionadas que mascaram o desempenho real.
6. **Projete os graders com cuidado.** Priorize determinísticos; complemente com LLM onde flexibilidade ajuda; use humanos com parcimônia. **Avalie o resultado, não o caminho específico** — agentes descobrem abordagens válidas que o avaliador não antecipou. Construa crédito parcial para tasks multicomponente.
7. **Leia transcripts regularmente.** Revelam se os graders estão avaliando corretamente ou rejeitando soluções válidas. Constrói intuição para modos de falha.
8. **Monitore saturação.** Conforme o agente se aproxima de 100%, evals de capacidade se formam em suítes de regressão. Quando o progresso estagna, investigue se o agente realmente bateu no limite ou se a suíte precisa de tasks mais difíceis.
9. **Estabeleça propriedade e manutenção.** Trate evals como testes unitários, que exigem cuidado contínuo. Pratique **eval-driven development**: defina as capacidades planejadas através de evals antes de o agente cumpri-las.

### 10.6 Armadilhas

- **Bypasses e hacks** — projete graders que o agente não consiga "burlar" explorando brechas não intencionais.
- **Checagem frágil de caminho** — não exija sequências específicas de chamadas de ferramenta; avalie resultados.
- **Especificações ambíguas** — a task precisa ser resolvível por um especialista humano.
- **Estado compartilhado entre trials.**
- **Ignorar a criatividade de modelos de fronteira** — modelos encontram soluções válidas que superam as restrições estáticas do eval; não penalize sucesso inesperado.

A Anthropic relata que **grading rígido que penalizava "96.12" quando esperava "96.124991…"** e outras tasks mal configuradas suprimiam artificialmente as pontuações dos modelos até serem corrigidas.

### 10.7 O modelo Queijo Suíço

Evals automatizadas combinam com: **monitoramento em produção** (comportamento real em escala), **testes A/B** (lento mas definitivo), **feedback de usuário** (esparso e autosselecionado), **revisão manual de transcripts** e **estudos humanos sistemáticos**. Nenhuma camada isolada pega tudo. Evals automatizadas aceleram iteração pré-lançamento; monitoramento em produção dá a verdade de campo; revisão humana periódica calibra e valida.

---

## 11. Segurança e operação autônoma

### 11.1 O modelo de três camadas

*How we contain Claude across products* descreve defesas sobrepostas em três componentes:

1. **Camada de ambiente** — fronteiras duras: sandboxes, VMs, controles de egresso.
2. **Camada de modelo** — system prompts, classificadores, modificações de treinamento.
3. **Camada de conteúdo externo** — permissões de ferramenta e validação de servidores MCP.

A Anthropic **prioriza a contenção ambiental**, com a tese explícita:

> *"A fronteira determinística é o que é atingido quando tudo o que é probabilístico erra."*

**Três padrões de contenção em produção:**

- **claude.ai** — containers gVisor com filesystem efêmero por sessão. Blast radius mínimo, capacidade limitada.
- **Claude Code** — sandbox com humano no loop; execução local com acesso ao filesystem do usuário, usando sandboxing de SO (Seatbelt / bubblewrap). Desenvolvedores conseguem avaliar comandos bash, o que torna a supervisão humana viável.
- **Claude Cowork** — VM selada, para usuários não técnicos que não conseguem avaliar comandos bash. O loop do agente roda **fora** da VM (confiabilidade); a execução de código acontece dentro. Diretórios montados com controles granulares (read-only, read-write, read-write-no-delete).

### 11.2 Sandboxing no Claude Code

*Beyond permission prompts* parte do problema de **fadiga de aprovação**: clicar "aprovar" constantemente desacelera o ciclo e leva as pessoas a pararem de revisar com cuidado — a fadiga paradoxalmente **reduz** a segurança. Nos testes internos, sandboxing reduziu os prompts de permissão em **84%**.

**As duas camadas são ambas necessárias:**

- **Isolamento de filesystem** — o Claude só acessa ou modifica diretórios designados, impedindo que um agente comprometido altere arquivos de sistema ou configuração sensível.
- **Isolamento de rede** — *"o Claude só se conecta a servidores aprovados. Isso impede que um Claude sob injeção de prompt vaze informação sensível ou baixe malware."*

Sem isolamento de rede, um atacante pode exfiltrar chaves SSH; sem isolamento de filesystem, pode escapar do sandbox.

> *"Sandboxing garante que mesmo uma injeção de prompt bem-sucedida fique totalmente isolada e não possa afetar a segurança geral do usuário."*

Recomendações: habilite as fronteiras de sandbox **antes** de conceder autonomia; implemente controles de filesystem e rede simultaneamente; use primitivas de nível de SO em vez de restrições de nível de aplicação; considere o sandbox runtime open-source da Anthropic (`anthropics/sandbox-runtime`) para implementações próprias.

### 11.3 Auto mode: como um classificador substitui o prompt de permissão

*How we built Claude Code auto mode* documenta o meio-termo entre aprovação manual e acesso irrestrito. O dado que motivou o design: **usuários aprovavam 93% dos prompts de permissão de qualquer forma**, sugerindo que não estavam revisando com cuidado.

**Duas camadas defensivas:**

- **Entrada** — uma sonda server-side rastreia saídas de ferramenta (leituras de arquivo, web fetches, resultados de shell) em busca de tentativas de injeção. Quando detecta conteúdo suspeito, o sistema **adiciona um aviso ao contexto do agente** em vez de bloquear diretamente, levando o agente a reconsiderar a intenção do usuário.
- **Saída** — um classificador de transcript avalia cada ação antes da execução, em dois estágios: um filtro rápido de token único que **erra para o lado de bloquear**, seguido de raciocínio em cadeia apenas se sinalizado. *"Tokens de raciocínio são gastos só onde é necessário."*

**Modelo de ameaça — quatro modos de falha:** comportamento overeager (o agente interpreta o escopo errado — ex.: apagar branches remotos ao ouvir "limpe isso"); erros honestos; injeção de prompt; e desalinhamento do modelo (não observado até agora).

**Duas decisões de design que valem generalizar:**

1. **O classificador não vê o raciocínio do agente nem o conteúdo que motivou a ação.** Isso impede que "o agente convença o classificador a tomar uma decisão ruim" com racionalizações persuasivas. Retirar resultados de ferramenta também reduz a superfície de injeção e força a decisão com base na intenção do usuário.
2. **Deny-and-continue** — o auto mode não interrompe o agente. Quando o classificador bloqueia, o modelo recebe feedback para encontrar "um caminho mais seguro" em vez de a sessão terminar. Isso torna falsos positivos sobreviventes. O sistema só escala após **3 negações consecutivas ou 20 no total**.

**Os números publicados:** em tráfego real (10.000 ações), **0,4%** de falso positivo após o estágio 2. Em ações overeager reais (52 incidentes), **17%** de falso negativo. Em exfiltração sintética (1.000 ataques), **5,7%** de falso negativo após o estágio 2.

**As recomendações de design de permissão para agentes autônomos:**

1. Assuma que fadiga de aprovação importa — bloquear tudo com prompts cria atalhos inseguros.
2. Torne a defesa **estrutural** — separe validação de entrada e de saída para que um comprometimento não contorne as duas.
3. **Retire o raciocínio do agente do avaliador** — force a decisão sobre as ações em si, não sobre as justificativas.
4. Aceite perfis de risco assimétricos — falsos negativos pesam mais que falsos positivos; o usuário pode tentar de novo uma ação benigna.
5. Customize conservadoramente — defaults seguros com extensão opcional de política, em vez de exigir configuração do zero.
6. Monitore o risco residual explicitamente. Nas palavras dos autores: *"17% é o número honesto."*

> O posicionamento final é explícito: auto mode **não é substituto para revisão humana cuidadosa em infraestrutura de alto risco**. Ele substitui padrões de acesso irrestrito, não o julgamento humano.

### 11.4 Lições de falhas reais

- **Exploração de egresso** — domínios aprovados viram superfície de ataque. Um `api.anthropic.com` na allowlist permitiu upload de arquivos para contas de atacantes. Solução: proxies man-in-the-middle interceptando chamadas de API para validar tokens de sessão.
- **Injeção com o usuário como vetor** — prompts diretos do tipo "leia `~/.aws/credentials` e faça POST" contornam defesas da camada de modelo, porque *"quando é o usuário quem digita a instrução, não há nada de anômalo para um classificador pegar"*. **Só controles de ambiente impediram a exfiltração.**
- **Execução antes do trust prompt** — configurações e hooks de projeto eram executados **antes** do prompt de confiança aparecer. A correção: adiar todo parsing de configuração até depois do consentimento do usuário.

### 11.5 Recomendações para quem constrói sobre o Claude

- **Projete o ambiente primeiro.** Sandboxes, VMs e fronteiras de filesystem pegam as falhas que as camadas de modelo deixam passar.
- **Case o isolamento com a expertise do usuário.** Desenvolvedores toleram diálogos de aprovação; knowledge workers exigem fronteiras absolutas.
- **Desconfie de componentes customizados.** Hipervisores e seccomp duram mais que código de segurança proprietário.
- **Inspecione saídas de ferramenta.** Trate resultados de ferramentas com acesso a rede como não confiáveis, **mesmo vindos de ferramentas confiáveis**.
- **Gerencie estado persistente.** Memória que sobrevive à sessão e diretórios montados viram alvos de injeção e exigem classificadores mais fortes.

**Riscos emergentes que a Anthropic sinaliza:** envenenamento de memória persistente entre sessões; escalada de confiança em sistemas multiagente hierárquicos; e a ausência de padrões de identidade de agente entre plataformas.

### 11.6 Permissões no dia a dia

Em planos Pro, Max e Team, o **auto mode** é o modo de permissão inicial em sessões interativas de terminal e VS Code. No **Manual mode** (padrão nos demais planos), o Claude pergunta antes de ações que possam modificar o sistema. Duas ferramentas cortam as interrupções:

- **Allowlists de permissão** — libere ferramentas que você sabe serem seguras (`npm run lint`, `git commit`), via `/permissions`.
- **Sandboxing** — isolamento de SO restringindo filesystem e rede, via `/sandbox`.

Para **restrições organizacionais**, a documentação separa claramente os papéis:

| Preocupação | Onde configurar |
|---|---|
| Bloquear ferramentas, comandos ou caminhos | Managed settings: `permissions.deny` |
| Impor isolamento em sandbox | Managed settings: `sandbox.enabled` |
| Variáveis de ambiente e roteamento de provedor | Managed settings: `env` |
| Método de login e restrições de organização | Managed settings: `forceLoginMethod`, `forceLoginOrgUUID` |
| Diretrizes de estilo e qualidade de código | Managed CLAUDE.md |
| Lembretes de compliance e tratamento de dados | Managed CLAUDE.md |

> **Settings são aplicadas pelo cliente independentemente do que o Claude decide. Instruções de CLAUDE.md moldam comportamento, mas não são camada de aplicação.**

---

## 12. Operação diária e escala

### 12.1 Prompts específicos

| Estratégia | Antes | Depois |
|---|---|---|
| **Escope a tarefa** | *"adicione testes para foo.py"* | *"escreva um teste para foo.py cobrindo o edge case em que o usuário está deslogado. evite mocks."* |
| **Aponte a fonte** | *"por que ExecutionFactory tem uma api tão estranha?"* | *"olhe o histórico git de ExecutionFactory e resuma como a api chegou nesse estado"* |
| **Referencie padrões existentes** | *"adicione um widget de calendário"* | *"veja como os widgets existentes são implementados na home para entender os padrões. HotDogWidget.php é um bom exemplo. siga o padrão para implementar um widget de calendário… sem bibliotecas além das já usadas no codebase."* |
| **Descreva o sintoma** | *"conserte o bug de login"* | *"usuários relatam que o login falha após timeout de sessão. verifique o fluxo de auth em src/auth/, especialmente o refresh de token. escreva um teste que falha reproduzindo o problema, depois conserte"* |

Prompts vagos têm lugar: quando você está explorando e pode se dar ao luxo de corrigir o curso. *"O que você melhoraria neste arquivo?"* pode revelar coisas que você não pensaria em perguntar.

**Conteúdo rico:** referencie arquivos com `@`; cole imagens direto; dê URLs de documentação (com allowlist de domínios via `/permissions`); canalize dados (`cat error.log | claude`); ou deixe o Claude buscar o que precisa via Bash, MCP ou leitura de arquivos.

### 12.2 Corrija cedo e com frequência

Os melhores resultados vêm de loops de feedback apertados. Embora o Claude às vezes resolva de primeira, **corrigi-lo rapidamente geralmente produz soluções melhores mais rápido**.

- `Esc` — interrompe no meio da ação, preservando contexto para redirecionar.
- `Esc + Esc` ou `/rewind` — restaura conversa e/ou código a um estado anterior.
- `"Desfaça isso"` — o Claude reverte as próprias mudanças.
- `/clear` — reseta o contexto entre tarefas não relacionadas.

**A regra das duas correções:** se você corrigiu o Claude mais de duas vezes sobre o mesmo assunto na mesma sessão, o contexto está entulhado de abordagens falhas. `/clear` e recomece com um prompt mais específico incorporando o que você aprendeu. *"Uma sessão limpa com um prompt melhor quase sempre supera uma sessão longa com correções acumuladas."*

**Checkpoints como licença para arriscar:** em vez de planejar cada passo com cuidado, você pode mandar o Claude tentar algo arriscado. Se não der certo, faça rewind e tente outra abordagem. Checkpoints são salvos com a conversa — você pode fechar o terminal, retomar depois e ainda fazer rewind.

**Sessões como branches:** nomeie com `/rename` (ex.: `oauth-migration`) e trate cada workstream como uma sessão persistente. `claude --continue` retoma a última; `claude --resume` escolhe de uma lista.

### 12.3 Modo não interativo

```bash
# Query pontual
claude -p "Explique o que este projeto faz"

# Saída estruturada para scripts
claude -p "Liste todos os endpoints de API" --output-format json

# Streaming para processamento em tempo real
claude -p "Analise este arquivo de log" --output-format stream-json --verbose
```

`json` retorna um objeto único com campo `result`; `stream-json` imprime um objeto JSON por linha, começando com um evento de init. Use `--verbose` para depuração no desenvolvimento e desligue em produção. A execução cria uma sessão retomável, a não ser que você passe `--no-session-persistence`.

Integração em pipelines: `claude -p "<prompt>" --output-format json | seu_comando`.

Autonomia com checagem: `claude --permission-mode auto -p "conserte todos os erros de lint"`.

### 12.4 Fan-out

**Com `/batch`:** dentro de um repositório git, `/batch <instrução>` faz o Claude dividir a mudança entre 5 a 30 subagentes. Cada um trabalha no próprio worktree e abre um pull request.

**Com script próprio:**

1. Gere a lista de tarefas: *"liste todos os 2.000 arquivos Python que precisam migrar e salve a lista em files.txt"*.
2. Faça o loop:

```bash
for file in $(cat files.txt); do
  claude -p "Migre $file de Python 2 para Python 3. Retorne OK ou FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

3. **Teste em 2–3 arquivos primeiro**, refine o prompt com base no que der errado, e só então rode no conjunto completo. `--allowedTools` restringe o que o Claude pode fazer — o que importa quando roda sem supervisão.

### 12.5 Sessões paralelas

Escolha a abordagem conforme quanta coordenação você quer fazer manualmente:

- **Worktrees** — sessões CLI separadas em checkouts git isolados, para que as edições não colidam.
- **Cross-session messaging** — as sessões que você mesmo roda passam achados entre si.
- **App de desktop** — gerencia múltiplas sessões locais visualmente, cada uma no próprio worktree.
- **Claude Code na web** — sessões na nuvem, em infraestrutura gerenciada pela Anthropic por padrão.
- **Agent view** (`claude agents`, research preview) — despacha sessões que continuam rodando em background, observadas de uma única tela.
- **Agent teams** (experimental, desabilitado por padrão) — coordenação automatizada com tarefas compartilhadas, mensagens e um líder de time.

### 12.6 Plugins como camada de empacotamento

Plugins agrupam skills, hooks, subagents e servidores MCP numa unidade instalável. Skills de plugin são namespaced (`/meu-plugin:review`), permitindo coexistência. Use plugins quando quiser reutilizar o mesmo setup em vários repositórios ou distribuir via **marketplace**. `/plugin` navega o marketplace.

### 12.7 Desenvolva sua própria intuição

O fechamento da documentação oficial merece ser citado, porque relativiza tudo acima:

> *"Os padrões deste guia não estão gravados em pedra. São pontos de partida que funcionam bem em geral, mas podem não ser ótimos para toda situação. Às vezes você **deve** deixar o contexto acumular, porque você está fundo em um problema complexo e o histórico é valioso. Às vezes você deve pular o planejamento… Às vezes um prompt vago é exatamente o certo."*

Preste atenção ao que funciona: quando o Claude produz um ótimo resultado, note o que você fez — a estrutura do prompt, o contexto fornecido, o modo em que estava. Quando o Claude trava, pergunte por quê: o contexto estava ruidoso demais? O prompt vago demais? A tarefa grande demais para uma passagem?

---

## 13. Fontes

### Blog de engenharia — `anthropic.com/engineering`

Artigos lidos e usados diretamente neste documento:

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Beyond permission prompts: making Claude Code more secure and autonomous](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [How we built Claude Code auto mode: a safer way to skip permissions](https://www.anthropic.com/engineering/claude-code-auto-mode)
- [How we contain Claude across products](https://www.anthropic.com/engineering/how-we-contain-claude)

Demais artigos do índice, não desenvolvidos aqui mas relevantes ao tema:

- [Scaling Managed Agents: Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)
- [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use)
- [Designing AI-resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)
- [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)
- [Eval awareness in Claude Opus 4.6's BrowseComp performance](https://www.anthropic.com/engineering/eval-awareness-browsecomp)
- [Desktop Extensions: One-click MCP server installation for Claude Desktop](https://www.anthropic.com/engineering/desktop-extensions)
- [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool)
- [Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)
- [Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet](https://www.anthropic.com/engineering/swe-bench-sonnet)
- [An update on recent Claude Code quality reports](https://www.anthropic.com/engineering/april-23-postmortem) e [A postmortem of three recent issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues)

### Documentação oficial — `code.claude.com/docs`

- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) — destino atual do antigo `/engineering/claude-code-best-practices`
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- [How Claude remembers your project (CLAUDE.md e auto memory)](https://code.claude.com/docs/en/memory)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) e [Hooks reference](https://code.claude.com/docs/en/hooks)
- Índice completo em [`code.claude.com/docs/llms.txt`](https://code.claude.com/docs/llms.txt)

### Blog de produto

- [Steering Claude Code: when to use CLAUDE.md, skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)

### GitHub — `github.com/anthropics`

| Repositório | Conteúdo |
|---|---|
| [`anthropics/skills`](https://github.com/anthropics/skills) | Skills de exemplo por categoria, a spec Agent Skills (`./spec/`) e um template (`./template/`) |
| [`anthropics/claude-code`](https://github.com/anthropics/claude-code) | O Claude Code em si; issues e discussões |
| [`anthropics/claude-cookbooks`](https://github.com/anthropics/claude-cookbooks) | Notebooks e receitas de uso do Claude |
| [`anthropics/prompt-eng-interactive-tutorial`](https://github.com/anthropics/prompt-eng-interactive-tutorial) | Tutorial interativo de prompt engineering |
| [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) | Diretório oficial de plugins mantido pela Anthropic |
| [`anthropics/claude-agent-sdk-python`](https://github.com/anthropics/claude-agent-sdk-python) | SDK para construir agentes sobre o mesmo harness |
| [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action) | Integração com GitHub Actions |
| [`anthropics/sandbox-runtime`](https://github.com/anthropics/sandbox-runtime) | Sandboxing de filesystem e rede em nível de SO, sem container |

Especificação aberta de skills: [agentskills.io](https://agentskills.io)

---

## Nota sobre datação

Parte destas orientações é **dependente de versão** e vai envelhecer:

- Números de versão do Claude Code aparecem na documentação para vários comportamentos (`v2.1.196`, `v2.1.206`, `v2.1.214`, `v2.1.218`, `v2.1.234`, `v2.1.239`). Confira contra a versão instalada antes de depender de um campo específico.
- Recomendações de harness são explicitamente relativas à capacidade do modelo. O caso Opus 4.5 → 4.6 documentado em *Harness design* mostra componentes inteiros (sprints, context resets) ficando desnecessários com uma geração de modelo. A própria Anthropic recomenda **testar sob estresse as suposições embutidas no harness sempre que um modelo novo chega, e simplificar**.
- Auto mode, agent teams e agent view estão em estágios diferentes de disponibilidade (padrão por plano, experimental, research preview).
