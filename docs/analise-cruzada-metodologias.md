# Análise cruzada — XP, engenharia clássica, as skills do Matt Pocock e a doutrina Anthropic

> Cruzamento de quatro corpos de doutrina sobre como se constrói software.
> Fontes: `guia-aplicacao-xp (1).md` (Kent Beck, *Extreme Programming Explained*) · `guia-engenharia-software.md` (Sommerville 10ª ed., Pressman 8ª ed.) · as skills instaladas em `~/.claude/skills/` (origem `github.com/mattpocock/skills`, commit `6654f6b`, MIT) · `melhores-praticas-anthropic-claude-code.md` (doutrina publicada pela Anthropic).
> Onde o texto for interpretação minha e não afirmação de uma das fontes, está marcado como **[interpretação]**.
> Compilado em 5 de setembro de 2026.

---

## Sumário

1. [As quatro camadas](#1-as-quatro-camadas)
2. [Convergências profundas](#2-convergências-profundas)
3. [Divergências e inversões](#3-divergências-e-inversões)
4. [O achado estrutural sobre o set do Matt Pocock](#4-o-achado-estrutural-sobre-o-set-do-matt-pocock)
5. [O pipeline, lado a lado](#5-o-pipeline-lado-a-lado)
6. [Lacunas — o que falta em cada corpo](#6-lacunas--o-que-falta-em-cada-corpo)
7. [Vantagens — quando cada método se paga](#7-vantagens--quando-cada-método-se-paga)
8. [Contradições que continuam abertas](#8-contradições-que-continuam-abertas)
9. [Fontes](#9-fontes)

---

## 1. As quatro camadas

A tese que organiza este documento: **os quatro corpos não competem entre si — eles respondem perguntas de camadas diferentes.** Lê-los como candidatos ao mesmo cargo é o erro que leva alguém a adotar um e descartar os outros três sem necessidade.

| Corpo | Pergunta que responde | Camada | Recurso escasso que protege |
|---|---|---|---|
| **Sommerville / Pressman** | Como não deixar um projeto fracassar? | Organização e projeto | Retrabalho — mudança tardia é cara |
| **XP (Kent Beck)** | Como um time escreve software quando os requisitos mudam? | Time e prática | Tempo e moral do programador; comunicação |
| **Matt Pocock** | O que eu digito na terça-feira de manhã? | Sessão e fluxo | A janela de contexto e a clareza do pedido |
| **Anthropic** | Como construir a máquina que roda o agente? | Harness e mecanismo | Contexto, e a atenção humana gasta verificando |

### 1.1 Engenharia clássica — reduzir a incerteza antes de gastar

Sommerville e Pressman partem de uma premissa econômica explícita: **o custo de mudança cresce ao longo do ciclo**. Consertar um requisito mal entendido na fase de requisitos é barato; consertá-lo em produção é caro. Toda a estrutura decorre disso — estudo de viabilidade (organizacional, técnica, econômica) antes de comprometer recursos, elicitação separando requisitos funcionais de não funcionais, modelagem em UML, estimativa em pessoas-mês, rede de tarefas com caminho crítico, e um **registro de riscos** dividido em riscos de projeto, de produto e de negócio.

O design é uma fase própria, onde "a qualidade técnica é injetada no sistema": arquitetura, banco, interface e componentes, guiados pelos dois pilares de **alta coesão** e **baixo acoplamento**. A validação é escalonada: sistema → aceitação pelo cliente (UAT) → beta com usuários reais. E o ciclo não termina no lançamento: manutenção corretiva, adaptativa e evolutiva.

**Não caricaturar isto.** O guia fornecido já incorpora TDD, integração contínua, histórias de usuário e MVP dentro do arcabouço clássico — não é o cascata de 1970. O que permanece distintivamente clássico é a **ordem** (entender antes de construir), o **artefato como entregável** e a **gestão formal de risco**.

### 1.2 XP — achatar a curva de custo da mudança

Beck ataca exatamente aquela premissa. Se o custo de mudança pode ser **achatado** — por testes automatizados, design simples e refatoração contínua —, antecipar decisões deixa de ser prudência e vira desperdício. Daí a pergunta central, *"qual é a coisa mais simples que poderia funcionar hoje?"*, e a aposta explícita de que é mais barato fazer algo simples agora e pagar para mudá-lo amanhã do que investir em complexidades que podem nunca ser úteis.

A estrutura são cinco valores (comunicação, simplicidade, feedback, coragem, respeito), quatro variáveis de controle, quatro atividades básicas (codificar, testar, escutar, desenhar) e as doze práticas — que "criam uma sinergia robusta porque os pontos fortes de uma cobrem as fraquezas das outras".

Dois pontos que importam para o cruzamento:

- **A maior parte das falhas de projeto vem de problemas de comunicação.** As práticas de XP são, em boa medida, dispositivos que *forçam* o diálogo: cliente no local, programação em par, propriedade coletiva.
- **Escopo é a variável de controle mais importante**, porque "requisitos de software nunca são claros no início e mudam conforme o cliente experimenta o sistema".

### 1.3 As skills do Matt Pocock — operacionalizar o trabalho com um agente

Corpo de natureza diferente: não é um livro, é **um conjunto executável**. Dez skills que compõem um pipeline — `grilling` (entrevista até entendimento compartilhado) → `domain-modeling` (`CONTEXT.md` + ADRs) → `to-spec` (a conversa vira spec publicada no issue tracker) → `to-tickets` (a spec vira tracer bullets com arestas de bloqueio) → `implement` (constrói, acionando `/tdd` em seams pré-acordados) → `mp-code-review` (dois eixos, subagentes paralelos) → commit. Com `triage` governando a fila de entrada por uma máquina de estados, e `setup-matt-pocock-skills` materializando a configuração do repositório em `docs/agents/*.md`.

A premissa econômica é nova: **o agente é rápido e barato, mas não adivinha o que você quis dizer.** A alavanca humana está na especificação e na verificação, e a unidade de trabalho é dimensionada pela janela de contexto.

### 1.4 A doutrina Anthropic — projetar a máquina

Uma camada abaixo do fluxo: como o harness que roda o agente deve ser construído. Contexto como orçamento de atenção finito, com *context rot*; a escada de complexidade (prompt único → workflow → agente → multiagente → frota paralela) que só sobe com justificativa; o loop de verificação como aquilo que permite sair da mesa; alocação de mecanismos por custo de contexto × autoridade; evals; contenção ambiental. E a advertência recursiva de que **todo componente do harness codifica uma suposição sobre o que o modelo não faz sozinho** — e envelhece.

---

## 2. Convergências profundas

Onde os quatro concordam. O interessante não é a concordância; é que **concordam por razões diferentes** — e a razão determina o que fazer quando a regra é violada.

### 2.1 Verificação automatizada é inegociável — e mudou de função

| Corpo | O que diz | Para que serve o teste |
|---|---|---|
| **XP** | "Recursos sem testes automatizados que os comprovem simplesmente não existem" | **Coragem.** Rede que permite a um humano presente mudar o código sem medo — é o que viabiliza propriedade coletiva e refatoração contínua |
| **Clássico** | V&V escalonada: unidade → integração → sistema → aceitação → beta; regressão no CI | **Evidência de conformidade.** Prova, para o cliente e para o contrato, que o requisito foi atendido |
| **Matt Pocock** | TDD em seams pré-acordados; *"No test is written at an unconfirmed seam"* | **Contrato de fronteira.** O seam define onde o agente mexe livremente e onde não mexe |
| **Anthropic** | "Dê ao Claude uma verificação que ele possa executar... é a diferença entre uma sessão que você assiste e uma da qual você pode se afastar" | **Condição de parada.** É o que faz o loop fechar sem humano no circuito |

**A reclassificação é o achado.** Em XP o teste é rede de proteção para alguém presente. Na doutrina de agentes o teste é a **condição de parada de uma máquina ausente** — porque, literalmente, *"o Claude para quando o trabalho parece pronto"*, e sem verificação executável "parece pronto" é o único sinal disponível.

Isso reordena a criticidade. Teste fraco em XP te atrasa: você descobre o bug depois. **Verificador** fraco num agente faz algo pior — ele otimiza contra o alvo errado, em escala e sem supervisão. É a lição do compilador C: *"o verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o problema errado."* O teste deixou de ser rede de segurança e virou **sistema de controle**. **[interpretação]**

Consequência prática: as disciplinas de qualidade de teste que XP e o clássico já pregavam — testar comportamento e não implementação, não acoplar a detalhes internos, cobrir os ramos — deixam de ser higiene e passam a ser requisito de segurança operacional. O skill `tdd` do Matt formaliza isso em anti-padrões nomeados: **implementation-coupled** (o tell: o teste quebra ao refatorar sem que o comportamento mude) e **tautological** (a asserção recomputa o esperado do mesmo jeito que o código, então passa por construção e nunca pode discordar).

### 2.2 Simplicidade e YAGNI — mesma regra, ameaça nova

Convergência de quatro fontes, quase palavra por palavra:

- **XP:** não projete flexibilidade para cenários que podem nunca ocorrer. As quatro regras de design simples, em ordem: passa nos testes → sem lógica duplicada (*once and only once*) → expressa a intenção → menor número possível de classes e métodos.
- **Clássico:** alta coesão e baixo acoplamento; cada módulo faz uma coisa bem.
- **Matt Pocock:** o baseline de smells do `mp-code-review` inclui **Speculative Generality** — *"abstraction, parameters, or hooks added for needs the spec doesn't have → delete it; inline back until a real need shows"* — mais Duplicated Code, Middle Man, Divergent Change, Refused Bequest.
- **Anthropic:** *"faça a coisa mais simples que funciona"*; a escada de complexidade; e o alerta explícito de que um revisor solto produz superengenharia — *"camadas extras de abstração, código defensivo, e testes para casos que não podem acontecer"*.

**A inversão da ameaça.** YAGNI nasceu contra ansiedade e ego humanos — o programador que abstrai porque "um dia vai precisar". Hoje o antagonista é outro: **geração ficou quase gratuita, manutenção não.** Um agente produz uma camada de abstração especulativa em segundos, com prosa convincente justificando-a. Por isso tanto a Anthropic quanto o Matt Pocock construíram guarda-corpos explícitos contra superengenharia *produzida pela máquina* — algo que nem Beck nem Sommerville precisavam prever. Mesma regra, vetor novo. **[interpretação]**

### 2.3 Fatia vertical sobre fatia horizontal

- **XP:** histórias de usuário atravessam camadas; versões pequenas colocam um esqueleto funcional em produção em 2 a 6 meses e entregam valor em ciclos curtos.
- **`to-tickets`:** *"Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer"*; cada fatia completa é demonstrável sozinha.
- **`tdd`:** *"horizontal slicing"* é anti-padrão nomeado — escrever todos os testes primeiro e depois toda a implementação faz os testes verificarem *comportamento imaginado*, "você testa a forma das coisas em vez do comportamento visível ao usuário".
- **Anthropic:** uma feature por vez na lista de features; commit por fatia; o alerta contra "o problema do one-shot".

**Aqui há contradição direta com o modelo de fases clássico**, que é horizontal por construção: todos os requisitos → todo o design → toda a construção → toda a validação. Os três corpos ágeis/agênticos convergem contra ele neste ponto, e é a divergência mais nítida do documento.

### 2.4 Escopo continua sendo a alavanca — mas a restrição mudou de lugar

A regra de ouro de Beck — o cliente escolhe três das quatro variáveis, a equipe calcula a quarta — sobrevive intacta. O que mudou é **qual variável morde**.

Custo e tempo de codificação despencaram, com ressalvas honestas: o harness completo documentado pela Anthropic custou US$ 200 e 6 horas contra US$ 9 e 20 minutos do agente solo, e multiagente consome ~15× mais tokens que chat. Qualidade continua não-negociável nos quatro corpos. Escopo continua sendo o que se corta.

Mas o gargalo migrou do **tempo de desenvolvedor** para a **capacidade de verificação e de contexto**. O compilador C demonstra: 16 agentes, 2 bilhões de tokens, US$ 20 mil — e o que limitava não era mão de obra, era o verificador. **Não se paraleliza além da qualidade do oráculo.** **[interpretação]**

---

## 3. Divergências e inversões

O núcleo analítico. Aqui os corpos não apenas diferem em ênfase — em vários pontos a doutrina de agentes **inverte a premissa** de uma prática do XP, mantendo o objetivo dela.

### 3.1 A revisão se inverteu

**XP:** programação em par. Piloto no teclado, copiloto pensando estrategicamente, **na mesma estação, na mesma tela**, trocando papéis duas ou três vezes por dia. O valor está no *entendimento compartilhado em tempo real*.

**Doutrina de agentes:** o revisor precisa estar em **contexto separado — precisamente para não compartilhar o entendimento.** A documentação da Anthropic é explícita: um contexto novo melhora a revisão porque "o Claude não fica enviesado a favor do código que ele mesmo acabou de escrever", e o revisor em subagente "vê apenas o diff e os critérios, não o raciocínio que produziu a mudança". O harness gerador-avaliador existe porque agentes "respondem elogiando confiantemente o trabalho — mesmo quando a qualidade é obviamente medíocre".

O `mp-code-review` materializa isso com rigor: dois subagentes **paralelos** em eixos deliberadamente separados — **Standards** (o código segue os padrões documentados do repo?) e **Spec** (o código implementa fielmente o que a issue pediu?) — *"so they don't pollute each other's context"*. E a instrução de agregação proíbe mesclar ou reranquear entre eixos, porque "um código pode passar num eixo e falhar no outro": segue todo padrão mas implementa a coisa errada, ou faz exatamente o que a issue pediu e quebra as convenções.

**A inversão:** em XP, o copiloto ver a mesma tela é a fonte do valor. Na doutrina de agentes, ver a mesma tela é o **modo de falha**. A "segunda dupla de olhos" sobreviveu; a premissa dela se inverteu. **[interpretação]**

### 3.2 O documento voltou — por um motivo que Sommerville não previu

XP tratava documentação como desperdício: não escreva, converse com o cliente que está sentado ao lado. Sommerville queria o documento porque mudança é cara e o contrato precisa de base.

O fluxo de agente quer o documento por uma terceira razão: **o agente não pode perguntar.** Em modo AFK — *away from keyboard*, na taxonomia do set do Matt, oposta a HITL, *human in the loop* — não há ninguém para consultar. A conversa precisa ser **materializada como artefato**.

Daí a característica mais distintiva do `AGENT-BRIEF.md`: **durabilidade acima de precisão**.

> "The issue may sit in `ready-for-agent` for days or weeks. The codebase will change in the meantime. Write the brief so it stays useful even as files are renamed, moved, or refactored."
>
> **Do** describe interfaces, types, and behavioral contracts. **Don't** reference file paths: they go stale. **Don't** reference line numbers.

E: **comportamental, não procedimental.** *"Good: 'The `SkillConfig` type should accept an optional `schedule` field of type `CronExpression`'. Bad: 'Open src/types/skill.ts and add a schedule field on line 42'."*

O `to-spec` repete a regra: *"Do NOT include specific file paths or code snippets. They may end up being outdated very quickly."* E a Anthropic converge: as specs mais úteis "nomeiam os arquivos e interfaces envolvidos, declaram o que está fora de escopo, e terminam com um passo de verificação end-to-end".

**A leitura:** `to-spec` + agent brief são **o cliente no local, serializado**. E por isso são o *oposto* de uma especificação de design clássica — que é procedimental por natureza, dizendo como construir. A economia da documentação se inverteu: ela deixou de ser desperdício porque ganhou **leitor garantido a cada sessão**. XP estava certo de que documento que ninguém lê é lixo; o que mudou foi que agora há um leitor obrigatório. **[interpretação]**

### 3.3 A unidade de estimativa mudou de natureza

| Corpo | Unidade | Natureza |
|---|---|---|
| Clássico | Pessoas-mês; rede de tarefas; caminho crítico | Contábil e contratual |
| XP | Tempo de Engenharia Ideal, corrigido pela **velocidade** medida do time | Empírica e social — específica daquele time |
| Matt Pocock | *"Each slice is sized to fit in a single fresh context window"* | **Física** — um limite do sistema, não do time |
| Anthropic | Uma feature por sessão; retorno de subagente de 1.000–2.000 tokens; CLAUDE.md sob 200 linhas | Física, com números explícitos |

A velocidade em XP é descoberta medindo o time ao longo de iterações. A janela de contexto é um número dado pela ferramenta. **Estimativa deixou de ser negociação com a realidade do time e virou aritmética de orçamento.** É mais previsível — e também mais rígida: não se aumenta a janela treinando o time. **[interpretação]**

### 3.4 A refatoração saiu do loop — desvio deliberado de Beck

**XP:** refatoração é contínua e faz parte do dia a dia. "Não adie a limpeza técnica: se puder fazer um design limpo em 10 minutos em vez de um remendo rápido em 1 minuto, gaste os 10 minutos." O ciclo TDD canônico é red → green → **refactor**.

**O skill `tdd` do Matt Pocock:** *"Refactoring is not part of the loop. It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle."*

Isso é desvio explícito da ortodoxia de Beck, dentro de um skill que em tudo o mais é fiel a ele. A razão provável: o passo "refactor" de um agente tende a alastrar — sem limite social, ele reescreve muito mais do que a fatia atual, e o diff deixa de ser revisável. Empurrar a refatoração para uma etapa com portão preserva a revisibilidade do incremento. **[interpretação]**

Note que a Anthropic empurra na direção oposta em um ponto vizinho, ao alertar que um revisor instruído a achar lacunas vai propor abstração demais. **As duas doutrinas concordam no diagnóstico — o agente exagera na limpeza — e discordam sobre onde colocar a contenção.**

### 3.5 Propriedade coletiva virou protocolo mecânico

**XP:** qualquer par pode modificar qualquer arquivo, a qualquer momento; a segurança vem da suíte de testes. É um **protocolo social**, viável porque o time é pequeno e conversa.

**Agentes em paralelo:** o protocolo social não escala para 16 processos que não conversam. Surgem primitivas explícitas:

- **Task locking por arquivo** — agentes reivindicam trabalho criando arquivos em `current_tasks/`; a detecção de conflito do git previne duplicação (caso do compilador C).
- **Worktrees isolados** — `/batch` distribui entre 5 e 30 subagentes, cada um no próprio worktree, abrindo um PR.
- **Arestas de bloqueio** — o `to-tickets` faz cada ticket declarar quais tickets o bloqueiam, e manda "trabalhar a fronteira: qualquer ticket cujos bloqueadores estejam prontos".

A intenção de Beck (ninguém é dono de nada; o trabalho flui para quem está livre) sobreviveu. O mecanismo passou de acordo tácito para grafo de dependências explícito. **[interpretação]**

### 3.6 Semana de 40 horas → exaustão de contexto

Não traduz literalmente, mas o análogo é real e a mitigação tem a mesma forma.

Beck: desenvolvedores cansados cometem mais erros de lógica e arquitetura; nunca faça hora extra duas semanas seguidas; se falta tempo, reajuste o escopo.

Doutrina de agentes: o desempenho degrada conforme a janela enche (*context rot*); modelos exibem "ansiedade de contexto", encerrando o trabalho prematuramente ao se aproximarem do limite percebido; e a regra das duas correções — se você corrigiu o agente mais de duas vezes sobre o mesmo assunto, o contexto está poluído, então `/clear` e recomece.

Nos dois casos, a receita é **parar e resetar em vez de forçar**, e ajustar o escopo em vez do esforço. **[interpretação]**

### 3.7 Uma contradição aparente que não é contradição

`to-spec` diz, em maiúsculas: *"Do NOT interview the user; just synthesize what you already know."* A documentação da Anthropic recomenda o oposto: "para features maiores, tenha o Claude te entrevistando primeiro... usando a ferramenta AskUserQuestion... então escreva uma spec completa em SPEC.md".

**Não se contradizem — a entrevista está fatorada em outro skill.** O `grilling` faz exatamente esse trabalho, e com um método mais sofisticado que o prompt sugerido pela Anthropic: mapeia as decisões como uma **árvore de design**, trabalha em **rodadas**, e define a **fronteira** como "toda decisão cujos pré-requisitos já estão resolvidos — as perguntas que você pode fazer *agora* sem adivinhar respostas que ainda não ouviu". Cada rodada numera as perguntas e **oferece a resposta recomendada**. A sessão acaba quando a fronteira esvazia.

Há ainda uma regra ali que merece destaque, porque é doutrina Anthropic aplicada com precisão: *"Finding facts is your job, never the user's. When a frontier question needs a fact from the environment, dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself."*

Ou seja: o pipeline é `grilling` → `to-spec`. A ordem bate com a da Anthropic; o que o Matt fez foi separar as duas responsabilidades em skills distintas. **Registre isso para não ler conflito onde há composição.**

---

## 4. O achado estrutural sobre o set do Matt Pocock

**O repositório é XP implementado sobre as primitivas da Anthropic.** É a ponte entre as duas pontas do espectro — e vê-lo assim explica tanto suas escolhas quanto sua lacuna.

### 4.1 As práticas vêm de Beck e Fowler

| Prática XP / clássica | Onde aparece no set |
|---|---|
| Testes automatizados como pré-condição | `tdd`, acionado por `implement` |
| TDD red → green | `tdd`, "Rules of the loop" |
| Fatias verticais / histórias que atravessam camadas | `to-tickets`, regra explícita de tracer bullet |
| Design simples / YAGNI | Smell **Speculative Generality** no baseline de revisão |
| Refatoração disciplinada | Os 12 smells de Fowler (*Refactoring*, cap. 3) como baseline fixo |
| Padrões de codificação | Eixo **Standards** da revisão, com a regra "o repo sobrepõe o baseline" |
| Integração contínua | `implement`: typecheck e testes ao longo, suíte completa ao final, commit |
| Metáfora / linguagem comum | `domain-modeling`: `CONTEXT.md` como glossário, e nada além disso |
| Escutar o cliente | `grilling` e a máquina de estados de `triage` |

O `domain-modeling` inclusive endurece a Metáfora de Beck em algo mais operacional: desafiar termos contra o glossário na hora (*"Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"*), cruzar com o código (*"Your code cancels entire Orders, but you just said partial cancellation is possible"*), e a regra de que `CONTEXT.md` "should be totally devoid of implementation details. It is a glossary and nothing else". ADRs só quando três condições valem: difícil de reverter, surpreendente sem contexto, e resultado de um trade-off real.

### 4.2 Os mecanismos vêm da Anthropic — e estão aplicados corretamente

| Mecanismo prescrito pela Anthropic | Como o set usa |
|---|---|
| **Progressive disclosure** — corpo enxuto, referências sob demanda | `tdd/tests.md` e `tdd/mocking.md`; `triage/AGENT-BRIEF.md` e `OUT-OF-SCOPE.md`; `domain-modeling/CONTEXT-FORMAT.md` e `ADR-FORMAT.md`; os três templates de issue-tracker do `setup` |
| **`disable-model-invocation: true` para workflows com efeito colateral** | Em **todas**: `implement`, `to-spec`, `to-tickets`, `triage`, `setup-matt-pocock-skills`. As de conhecimento (`tdd`, `domain-modeling`, `grilling`, `mp-code-review`) ficam disponíveis ao modelo |
| **Subagentes para isolar contexto** | `mp-code-review` dispara dois em paralelo, com o briefing completo passado no prompt (o subagente "has no other access to it") e limite de 400 palavras por relatório |
| **Subagente para buscar fatos em vez de perguntar** | `grilling`, com a regra de não bloquear: só as perguntas a jusante esperam o subagente |
| **Configuração do repo materializada em arquivo lido pelas skills** | `setup-matt-pocock-skills` escreve `docs/agents/issue-tracker.md`, `domain.md`, `triage-labels.md` e insere um bloco `## Agent skills` no `CLAUDE.md`/`AGENTS.md` existente — nunca criando o outro |
| **Contrato de retorno condensado do subagente** | "Under 400 words" em ambos os briefings de revisão |

O detalhe do `setup` merece nota: ele respeita a regra da Anthropic sobre `AGENTS.md` — *"Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there"* — e atualiza o bloco in-place em vez de duplicar.

### 4.3 A lacuna é uniforme: nenhum hook

**Todo o set é advisório.** Não há uma única camada de garantia. Pela própria doutrina Anthropic — "instrução em CLAUDE.md ou skill é pedido; hook é garantia; se uma regra precisa valer sempre, faça dela um hook" — várias regras do set são candidatas naturais:

- `implement` manda rodar a suíte completa ao final → candidato a **`Stop` hook**, que bloqueia o fim do turno até passar.
- `triage` exige que todo comentário publicado comece com o disclaimer *"This was generated by AI during triage"* → candidato a **`PreToolUse`** sobre a chamada que publica.
- `to-spec` e `to-tickets` proíbem caminhos de arquivo no texto → candidato a validação automática.
- O commit ao final de `implement` → candidato a portão de verificação.

Isso não é defeito de concepção: é o limite do que um repositório de skills distribuível pode fazer, já que hooks vivem em `settings.json` e são configuração da máquina, não conteúdo de skill. Mas **é a lacuna mais acionável do set**, e a que a doutrina Anthropic preenche diretamente. **[interpretação]**

---

## 5. O pipeline, lado a lado

| Fase | Clássico (Sommerville/Pressman) | XP | Matt Pocock | Anthropic |
|---|---|---|---|---|
| **Decidir se vale fazer** | Estudo de viabilidade (organizacional, técnica, econômica) | Implícito no Jogo do Planejamento | `triage`: máquina de estados, checagem de redundância, `.out-of-scope/` para rejeições anteriores | — |
| **Entender o problema** | Elicitação com stakeholders; funcionais × não funcionais | Cliente no local; escutar | `grilling`: árvore de design, rodadas, fronteira | "Deixe o Claude te entrevistar"; `AskUserQuestion` |
| **Linguagem comum** | UML, casos de uso, dicionário de dados | Metáfora | `domain-modeling`: `CONTEXT.md` + ADRs | `CLAUDE.md` para convenções |
| **Especificar** | Especificação de requisitos; MVP | Histórias de usuário em cartões | `to-spec`: problema, solução, user stories, decisões de implementação e de teste, out of scope | `SPEC.md` autocontido, terminando em verificação e2e |
| **Planejar e fatiar** | Rede de tarefas; caminho crítico; pessoas-mês | Jogo do Planejamento; velocidade; iterações de 1–4 semanas | `to-tickets`: tracer bullets + arestas de bloqueio; expand–contract para refactors amplos | Plan mode; lista de features em JSON |
| **Projetar** | Fase própria: arquitetura, banco, UI, componentes | Design simples; as 4 regras; sem antecipação | Seams acordados antes de testar | Escada de complexidade; alocação de mecanismos |
| **Construir** | Codificação + testes unitários | Par, propriedade coletiva, refatoração contínua, CI | `implement` → `/tdd`; typecheck e testes ao longo | Explore → Plan → Code → Commit |
| **Revisar** | Revisões técnicas formais | Programação em par (contínua) | `mp-code-review`: dois eixos, subagentes paralelos | Revisor adversarial em contexto novo; `/code-review` |
| **Validar** | Sistema → UAT → beta | Testes funcionais escritos pelo cliente | Critérios de aceitação no ticket | `/goal`, Stop hook, evidência em vez de afirmação |
| **Medir o processo** | Métricas de projeto; caminho crítico | Velocidade do time | — | **Evals**: 20–50 tarefas, graders, `pass@k` / `pass^k` |
| **Operar com segurança** | — | — | Disclaimer de conteúdo gerado por IA | Sandbox (filesystem + rede), auto mode, `permissions.deny` |
| **Evoluir** | Manutenção corretiva / adaptativa / evolutiva | Refatoração contínua; releases pequenas | `triage` como fila permanente | "Suposições e quando revisar"; simplificar a cada modelo novo |

Lendo a tabela por coluna, fica evidente onde cada corpo é forte e onde tem célula vazia — o que alimenta a próxima seção.

---

## 6. Lacunas — o que falta em cada corpo

Seção deliberadamente crítica, porque é a que orienta o próximo passo.

| Corpo | O que lhe falta | Quem preenche |
|---|---|---|
| **Anthropic** | A camada humana e organizacional inteira: elicitação, negociação com stakeholder, viabilidade, registro de riscos, requisitos não funcionais. A doutrina **assume que alguém já sabe o que construir** | Sommerville/Pressman e XP |
| **Matt Pocock** | **Evals** — não há como medir o desempenho do próprio fluxo (graders, `pass@k`/`pass^k`, suíte de regressão do workflow). **Segurança e permissões** — nenhum modelo de sandbox ou contenção. **Hooks** — nenhuma camada de garantia | Anthropic |
| **XP** | O agente como participante; coordenação de trabalho paralelo além do time humano; qualquer noção de orçamento de contexto | Anthropic e Matt Pocock |
| **Clássico** | Loop de feedback rápido o bastante para velocidade de agente; unidade de trabalho compatível com janela de contexto; o custo de mudança que ele pressupõe já não é o custo real | XP e Matt Pocock |
| **Os três ágeis/agênticos, juntos** | **Gestão formal de risco** e **requisitos não funcionais sistemáticos** (desempenho, portabilidade, confiabilidade, usabilidade). Ninguém na literatura de agentes mantém registro de riscos; a seção "Suposições e quando revisar" é o parente mais próximo e é bem mais fraca | **Só o clássico** |

A última linha é a mais importante e a menos óbvia. A doutrina de agentes trata segurança como **contenção** (sandbox, classificador, permissões) — o que é excelente e é uma contribuição genuinamente nova. Mas contenção não é o mesmo que **requisito não funcional**: nada nos três corpos ágeis/agênticos diz como especificar "o endpoint responde em menos de 200 ms sob 1.000 requisições concorrentes" e verificar isso. E nada neles substitui um registro de riscos com probabilidade, impacto e contingência. **[interpretação]**

---

## 7. Vantagens — quando cada método se paga

Resposta direta: em que situação concreta cada corpo rende mais.

### 7.1 Engenharia clássica ganha quando

- **Há contrato ou regulação.** Alguém precisa provar conformidade a um terceiro. Rastreabilidade requisito → design → teste → aceite é a moeda.
- **O sistema é crítico** — saúde, financeiro, industrial. O custo de uma falha em produção é assimétrico e justifica gastar muito para reduzir incerteza antes.
- **Requisitos não funcionais são duros e mensuráveis.** Desempenho, disponibilidade, portabilidade. É o único corpo que os trata sistematicamente.
- **A integração é com terceiros.** Fornecedor, órgão público, sistema legado externo — onde não há como iterar rápido com quem está do outro lado.
- **O risco precisa ser gerido explicitamente.** Perda de pessoa-chave, dependência de componente terceirizado, concorrente lançar primeiro.

**No seu contexto:** o `guia-engenharia-software.md` é a base certa para a etapa em que você decide *se* e *o que* construir, e para tudo que envolva requisito não funcional ou obrigação externa.

### 7.2 XP ganha quando

- **Os requisitos são genuinamente instáveis** e só vão clarear quando o cliente usar o sistema.
- **Existe um cliente acessível** — a prática de cliente no local só funciona se houver um usuário real disponível.
- **O time é pequeno e co-localizado** (físico ou não). Boa parte das doze práticas pressupõe conversa de baixo atrito.
- **O sistema vai viver muito tempo e mudar muito.** É onde design simples + refatoração + suíte de testes compõem juros.
- **Você herdou legado sem testes.** O capítulo de *retrofitting* é a coisa mais prática dos três guias: testes sob demanda (ao corrigir bug, ao adicionar feature, ao refatorar), refatoração incremental com metas grandes visíveis mordidas aos poucos.

**O valor duradouro do XP** não são as doze práticas, é o **sistema de valores** e a análise das quatro variáveis. Isso continua verdadeiro com agentes e não é dito por nenhum dos outros corpos.

### 7.3 O set do Matt Pocock ganha quando

- **Você já sabe o que quer e precisa executar com agente.** É a camada de fluxo, não de descoberta de produto.
- **O trabalho é decomponível em fatias verticais** e você quer despachar agentes sem supervisão contínua (AFK).
- **Existe issue tracker.** O set é construído em volta dele; sem ele você cai no modo local markdown, que funciona mas perde a máquina de estados do `triage`.
- **Você quer disciplina de teste sem ter que negociá-la toda vez.** Seams acordados uma vez, anti-padrões nomeados, revisão em dois eixos.

**A joia menos óbvia do set é o `grilling`** — a mecânica de árvore de design com fronteira e rodadas, com resposta recomendada em cada pergunta, é aplicável muito além de código.

### 7.4 A doutrina Anthropic ganha quando

- **Você está construindo o sistema que roda os agentes**, não usando um.
- **A operação é autônoma ou de longa duração** — é o único corpo que trata contenção, permissões e degradação de contexto.
- **Você precisa decidir onde colocar uma instrução** — CLAUDE.md, rule, skill, hook, subagente. A tabela custo × autoridade não tem equivalente nos outros três.
- **Você precisa medir o agente**, não o código. Evals, `pass^k`, graders, calibração de juiz.
- **Você suspeita que seu setup está inflado.** A escada de complexidade e a regra da obsolescência do harness são ferramentas de *remoção*, e os outros corpos não têm nada equivalente.

---

## 8. Contradições que continuam abertas

Estas **não** têm resposta única. São as escolhas que você terá de fazer se for destilar isto num método próprio.

**1. Refatoração dentro ou fora do loop?**
Beck diz dentro, contínua. O `tdd` do Matt diz fora, na etapa de revisão. Os dois têm razão sobre riscos diferentes: dentro do loop, o design não apodrece; fora do loop, o diff continua revisável. A escolha provavelmente depende de quanto você revisa cada incremento.

**2. Quanto de especificação antes de codificar?**
XP diz o mínimo — a spec é a conversa, e o cartão é um lembrete dela. `to-spec` pede uma spec extensa, com "a LONG, numbered list of user stories" cobrindo todos os aspectos. A Anthropic fica no meio e é explícita sobre o custo: "se você consegue descrever o diff em uma frase, pule o plano". Não há regra; há um ponto ótimo que depende do tamanho da fatia e de quanto o agente vai rodar sem você.

**3. Entrevista antes da spec, ou spec por síntese?**
Resolvido em composição (`grilling` → `to-spec`), mas resta decidir *quando* a entrevista se paga. Entrevistar antes de uma correção de uma linha é desperdício; não entrevistar antes de uma feature de duas semanas é garantia de retrabalho.

**4. Onde entra o hook num set advisório?**
Se você adotar o set do Matt, terá que decidir quais das regras dele viram garantia na sua máquina. Isso não vem no pacote e é configuração sua.

**5. Quem escreve os testes de aceitação?**
XP diz: o cliente, com apoio técnico. O set do Matt coloca critérios de aceitação no ticket, escritos pelo agente durante o `to-tickets`, aprovados por você. É uma transferência real de autoria — e vale decidir conscientemente se você quer isso.

**6. Gestão de risco: adotar do clássico, ou aceitar não ter?**
Nenhum corpo ágil/agêntico oferece substituto. Ou você importa o registro de riscos de Sommerville/Pressman, ou trabalha sem ele sabendo que trabalha sem ele.

---

## 9. Fontes

### Documentos fornecidos

- `C:\Users\alero\Downloads\guia-aplicacao-xp (1).md` — baseado em Kent Beck, *Extreme Programming Explained: Embracing Change and Managing Risk*
- `C:\Users\alero\Downloads\guia-engenharia-software.md` — baseado em Ian Sommerville, *Engenharia de Software* (10ª ed.) e Roger Pressman, *Engenharia de Software: Uma Abordagem Profissional* (8ª ed.)

### Skills lidas na íntegra (instaladas localmente)

`~/.claude/skills/` — `implement/SKILL.md` · `to-spec/SKILL.md` · `to-tickets/SKILL.md` · `tdd/SKILL.md` · `mp-code-review/SKILL.md` · `triage/SKILL.md` · `triage/AGENT-BRIEF.md` · `domain-modeling/SKILL.md` · `grilling/SKILL.md` · `setup-matt-pocock-skills/SKILL.md`

Procedência conforme `~/.claude/skills/.mattpocock-provenance.txt`: origem [github.com/mattpocock/skills](https://github.com/mattpocock/skills), licença MIT, commit fixado `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, instalado em 01/09/2026, com duas modificações locais registradas (renomeação de `code-review` para `mp-code-review` e o ajuste da referência dentro de `implement`).

**Não lidos, disponíveis para aprofundamento:** `tdd/tests.md`, `tdd/mocking.md`, `domain-modeling/CONTEXT-FORMAT.md`, `domain-modeling/ADR-FORMAT.md`, `triage/OUT-OF-SCOPE.md`, `grill-me/SKILL.md`, e os três templates de issue-tracker do `setup`.

### Doutrina Anthropic

Consolidada em `melhores-praticas-anthropic-claude-code.md` (sessão anterior) e nas referências da skill `~/.claude/skills/arquiteto-claude-code/`. As fontes primárias estão listadas lá; as mais citadas aqui: *Building effective agents*, *Effective context engineering for AI agents*, *Harness design for long-running application development*, *Building a C compiler with a team of parallel Claudes*, *Demystifying evals for AI agents*, e a documentação `code.claude.com/docs/en/best-practices`.

### Consultas web feitas para este documento

- [mattpocock/skills](https://github.com/mattpocock/skills) e o [README de `skills/engineering`](https://github.com/mattpocock/skills/blob/main/skills/engineering/README.md) — filosofia declarada do set, composição do fluxo, distinção entre skills invocadas por usuário e por modelo
- [TDD, AI agents and coding with Kent Beck](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent) — Beck sobre agentes como "gênio imprevisível" que atende desejos de formas inesperadas, e sobre TDD permanecer relevante: *"tests are a conversation with the future. AI doesn't change that"*
- [Augmented Coding with Kent Beck (O11ycast)](https://www.heavybit.com/library/podcasts/o11ycast/ep-80-augmented-coding-with-kent-beck)
- [Spec-Driven Development in 2026](https://dev.to/krlz/spec-driven-development-in-2026-what-it-is-the-tooling-and-how-teams-actually-use-it-2fk2) e [Spec-driven development com IA (Pluralsight)](https://www.pluralsight.com/resources/blog/software-development/spec-driven-development-with-AI-SDD) — o debate sobre especificação antecipada com agentes, e a distinção entre spec lida por humano e spec que executa como portão de validação
- [The /to-tickets Skill (AI Hero)](https://www.aihero.dev/skills-to-tickets) e [5 Agent Skills I Use Every Day](https://www.aihero.dev/5-agent-skills-i-use-every-day) — a taxonomia HITL × AFK e a lógica dos tracer bullets

---

## Nota sobre o que este documento deliberadamente não faz

O pedido foi **cruzar**, não sintetizar. Este documento não propõe um método unificado, não decide as seis contradições da §8 e não altera nada no seu setup. Essas são decisões suas, e são o assunto natural do segundo momento.
