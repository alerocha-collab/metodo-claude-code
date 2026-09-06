# Referência 01 — Arquitetura de sistemas agênticos

Fonte: *Building effective agents*, *How we built our multi-agent research system*, *Harness design for long-running application development*, *Effective harnesses for long-running agents*, *Building a C compiler with a team of parallel Claudes*.

---

## 1. Workflow vs. agente

- **Workflow** — caminhos de código predefinidos. Previsibilidade e consistência para tarefas bem definidas.
- **Agente** — decisão dirigida pelo modelo. Melhor quando flexibilidade é necessária em escala.
- **Antes dos dois** — para muitas aplicações, otimizar uma única chamada com retrieval e exemplos basta. Não construa sistema agêntico.

O bloco básico é o **LLM aumentado**: modelo + retrieval + ferramentas + memória. Foque em adaptar essas capacidades ao caso de uso e prover interfaces claras.

**Três princípios centrais:** simplicidade; transparência (exiba os passos de planejamento); **ACI forte** — *"invista em interfaces agente-computador o mesmo esforço que se investe em interfaces humano-computador."*

## 2. Os cinco padrões de workflow

| Padrão | Mecânica | Use quando | Exemplo |
|---|---|---|---|
| **Prompt chaining** | Passos sequenciais com checkpoints programáticos | Troca latência por acurácia; tarefa decomponível | Gerar copy, depois traduzir |
| **Routing** | Classifica a entrada e direciona a handlers especializados | Categorias distintas se beneficiam de otimização separada | Rotear suporte por tipo; mandar query simples a modelo menor |
| **Parallelization** | *Sectioning* (subtarefas independentes) e *voting* (mesma tarefa N vezes) | Guardrails; confiança por consenso | Revisão de vulnerabilidades em múltiplas passagens |
| **Orchestrator-workers** | LLM central decompõe dinamicamente e delega | Subtarefas imprevisíveis | Mudança de código em muitos arquivos |
| **Evaluator-optimizer** | Um gera, outro critica, em loop | Critério de qualidade claro mas difícil de acertar de primeira | Tradução literária; busca complexa |

## 3. Orquestrador-worker: números e regras

Da arquitetura em produção (agente líder + subagentes especializados em paralelo):

- **+90,2%** sobre agente único (líder Opus 4, subagentes Sonnet 4).
- **Três fatores explicaram 95% da variância**; uso de tokens sozinho, ~80%.
- **~15× mais tokens** que chat. É o número a declarar ao propor multiagente.
- Duas formas de paralelização (3–5 subagentes simultâneos + 3 ou mais ferramentas simultâneas) **cortaram tempo em até 90%**.
- **Contrato do subagente: resumo condensado de 1.000–2.000 tokens.** É o que preserva a janela do líder.

**Os sete princípios de prompt para multiagente:**

1. **Desenvolva intuição** — simule com prompts e ferramentas reais, observe passo a passo, catalogue modos de falha.
2. **Ensine a delegar** — o líder deve especificar objetivo, formato de saída, orientação de ferramentas e **fronteiras da tarefa**. Instrução vaga causa duplicação e lacuna.
3. **Escale o esforço explicitamente** — query simples: 1 agente, 3–10 chamadas. Pesquisa complexa: 10+ subagentes. Embuta a regra no prompt.
4. **Interface de ferramenta é tão crítica quanto interface humana.**
5. **Permita auto-aperfeiçoamento** — o modelo diagnostica falhas do próprio prompt. Um agente de teste de ferramentas cortou **40%** do tempo de conclusão só otimizando descrições.
6. **Busca do amplo para o estreito** — comece amplo, avalie, depois estreite. Não comece hiperespecífico.
7. **Guie o pensamento** — extended/interleaved thinking como scratchpad para planejar e avaliar no meio da execução.

**Gargalo conhecido:** execução síncrona — o líder espera todos os subagentes. Simplifica a coordenação mas bloqueia o sistema inteiro no subagente mais lento.

## 4. Harness design

> *"Todo componente de um harness codifica uma suposição sobre o que o modelo não consegue fazer sozinho."*

### Gerador–avaliador

Inspirado em GANs. O gerador produz; o avaliador julga independentemente contra critérios concretos; o feedback retorna.

**Por que separar:** agentes *"respondem elogiando confiantemente o trabalho — mesmo quando a qualidade é obviamente medíocre."* É muito mais tratável calibrar um avaliador cético do que fazer um gerador autocrítico.

**Custo de calibração:** avaliadores iniciais *"identificavam problemas legítimos e depois se convenciam de que não eram importantes."* Foram necessárias várias rodadas de leitura de logs e ajuste de prompt.

### Três agentes, full-stack

1. **Planner** — expande um prompt de 1–4 frases em spec de produto com decisões técnicas. Previne cascata de garbage-in-garbage-out.
2. **Generator** — implementa iterativamente, com auto-avaliação antes do handoff.
3. **Evaluator** — usa Playwright MCP para operar a aplicação rodando como um usuário; testa, encontra bugs com localização no código, e atribui nota.

### Sprint contracts

Antes de cada bloco de trabalho, gerador e avaliador negociam: o que exatamente será construído, como o sucesso será verificado, quais os critérios de aceitação testáveis. **Força o acordo sobre "pronto" antes da implementação.**

### Comunicação por arquivos

Agentes se comunicam por artefatos em disco — spec, sprint contract, achados de QA — não por contexto compartilhado. Previne poluição de contexto e força clareza sobre o que atravessa a fronteira.

### Qualidade subjetiva mensurável

Para front-end: **design, originalidade, craft, funcionalidade**. Design e originalidade receberam peso maior porque o modelo já ia bem em craft e funcionalidade por padrão. Avaliador calibrado com exemplos few-shot do padrão de nota desejado.

### Custo real medido

| Abordagem | Tempo | Custo | Resultado |
|---|---|---|---|
| Agente solo | 20 min | US$ 9 | Funcionalidade central quebrada |
| Harness completo | 6 h | US$ 200 | Aplicação multi-feature funcionando |

**20× o custo.** O avaliador só agrega valor quando a tarefa está além do que o modelo faz sozinho com confiabilidade.

### Obsolescência

| Opus 4.5 | Opus 4.6 |
|---|---|
| Exigia decomposição em sprints | Rodou 2+ horas coerente sem decomposição |
| Exigia context resets (limpar a janela, não compactar) por "ansiedade de contexto" | Desnecessário |
| Avaliador envolvido a cada sprint | Avaliador virou revisão única no fim |

**A lição de projeto:** ao chegar um modelo novo, remova componentes e meça. Não presuma que a arquitetura de ontem é ótima hoje.

## 5. Agentes de longa duração (múltiplas janelas de contexto)

O problema: **cada sessão começa sem memória do que veio antes.** Sem estrutura, o agente tenta fazer tudo de uma vez (e acaba o contexto no meio) ou declara pronto prematuramente.

### Agente inicializador (só a primeira sessão)

- **Lista de features em JSON**, cada uma marcada como falhando. O formato é deliberado: *"o modelo tem menos chance de alterar ou sobrescrever inapropriadamente arquivos JSON do que arquivos Markdown."*
- `claude-progress.txt` para rastrear atividade.
- Repositório git com commit de baseline.
- `init.sh` que sobe o ambiente automaticamente.

```json
{ "category": "functional",
  "description": "New chat button creates conversation",
  "steps": ["Navigate", "Click", "Verify..."],
  "passes": false }
```

### Agente de execução (todas as demais)

Sequência de onboarding fixa: `pwd` → ler git log e progresso → escolher **uma** feature incompleta → rodar `init.sh` e testes e2e básicos → implementar → commitar e atualizar o progresso.

### Regras

- **Prompt diferente para a primeira janela** e para as seguintes. Descrito como crítico.
- Estado limpo: o código deve ficar mergeável — sem bugs graves, ordenado, documentado.
- Teste explícito com automação de browser. Sem instrução explícita, *"o Claude tendia a marcar features como completas sem testar adequadamente."*
- *"É inaceitável remover ou editar testes, porque isso pode levar a funcionalidade faltante ou com bug."*

### Matriz de falha → mitigação

| Falha | No inicializador | No executor |
|---|---|---|
| Declarar vitória cedo | Lista de features impede esquecer trabalho | Ler a lista; trabalhar em um item |
| Progresso bugado e não documentado | Git + notas de progresso | Começar verificando; terminar commitando |
| Marcar feature incompleta como pronta | Estrutura da lista | Auto-verificar antes de marcar |
| Confusão de runtime | Criar `init.sh` | Ler e executar o script primeiro |

## 6. Paralelismo em escala

Caso: 16 instâncias construindo um compilador C de ~100 mil linhas em Rust — ~2 bilhões de tokens de entrada, 2.000 sessões, ~US$ 20.000.

**Coordenação:**
- Loop infinito em container: escolhe tarefa, completa, escolhe a próxima, sem humano.
- **Task locking por arquivo** — agentes reivindicam trabalho criando arquivos em `current_tasks/`; a detecção de conflito do git previne duplicação.
- Cada agente clona em `/workspace` e dá push do próprio container, resolvendo merges.

**O pré-requisito absoluto:** *"o verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o problema errado."* Suítes de teste fortes (GCC torture tests), CI impedindo regressão, estatísticas pré-computadas para não poluir contexto, amostragem determinística de 1–10% por agente em subconjuntos diferentes.

**Lições:**
- **Logging estruturado para parsing automático** — formato consistente (`ERROR: [motivo]`) para ser passível de grep.
- **Modelos não têm noção de tempo** — o harness ofereceu um modo `--fast` para feedback rápido.
- **Especialização vence generalização** — um agente para deduplicação, outro para performance, outro para crítica de design. Times homogêneos renderam menos.
- **Quando o trabalho não é decomponível**, crie o oráculo que o torna. No gargalo do kernel (todos batiam no mesmo bug), a solução foi **teste diferencial**: compilar a maior parte com GCC e só o resto com o compilador do Claude, liberando paralelismo por arquivo.

**O que generaliza:** verificação clara de tarefas; decomposição natural; feedback estruturado que permita orientação autônoma; documentação bem mantida.

**O que não generalizou no caso:** o compilador não implementou codegen x86 de 16 bits e chamou GCC como fallback; o código gerado tem desempenho bem abaixo do GCC; features novas frequentemente quebravam as existentes — sintoma de estar no limite da capacidade.
