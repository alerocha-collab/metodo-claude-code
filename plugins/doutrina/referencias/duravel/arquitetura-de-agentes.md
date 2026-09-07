# Arquitetura de sistemas agênticos — os números e os padrões

> Fontes: *Building effective agents* · *How we built our multi-agent research system* ·
> *Harness design for long-running application development* · *Effective harnesses for
> long-running agents* · *Building a C compiler with a team of parallel Claudes*.
> Indexadas em `fontes.json` sob `secao: engenharia`, com hash.

**Por que é durável.** São medições publicadas e padrões de desenho, não schemas de
plataforma. O artigo não muda quando o Claude Code atualiza — e se mudar,
`verificar_fontes.py --drift` acusa. Os números trazem o modelo em que foram medidos,
porque é isso que os data.

---

## 1. Orquestrador-worker: o que foi medido

Sistema em produção, agente líder com subagentes especializados em paralelo:

| Medida | Valor |
|---|---|
| Ganho sobre agente único | **+90,2%** (líder Opus 4, subagentes Sonnet 4) |
| Custo em tokens | **~15× um chat** |
| Variância explicada | Três fatores explicaram **95%**; uso de tokens sozinho, ~80% |
| Ganho de tempo | Até **90%**, com 3–5 subagentes simultâneos + 3 ou mais ferramentas simultâneas |
| Contrato de retorno do subagente | **1.000–2.000 tokens** de resumo condensado |

O contrato de retorno é a peça que preserva a janela do líder. Sem ele, multiagente
troca um contexto cheio por vários.

**Gargalo conhecido:** execução síncrona — o líder espera todos. Simplifica a
coordenação e bloqueia o sistema inteiro no subagente mais lento.

## 2. Os sete princípios de prompt para multiagente

1. **Desenvolva intuição** — simule com prompts e ferramentas reais, observe passo a
   passo, catalogue modos de falha.
2. **Ensine a delegar** — objetivo, formato de saída, orientação de ferramentas e
   **fronteiras da tarefa**. Instrução vaga causa duplicação e lacuna ao mesmo tempo.
3. **Escale o esforço explicitamente** — query simples: 1 agente, 3–10 chamadas.
   Pesquisa complexa: 10+ subagentes. Embuta a regra no prompt.
4. **Interface de ferramenta é tão crítica quanto interface humana.**
5. **Permita auto-aperfeiçoamento** — o modelo diagnostica falhas do próprio prompt. Um
   agente que testava ferramentas cortou **40%** do tempo só otimizando descrições.
6. **Busca do amplo para o estreito** — comece amplo, avalie, depois estreite.
7. **Guie o pensamento** — thinking estendido como scratchpad para planejar e avaliar no
   meio da execução.

## 3. Desenho de harness

> *"Todo componente de um harness codifica uma suposição sobre o que o modelo não
> consegue fazer sozinho."*

### Gerador–avaliador

O gerador produz; o avaliador julga **independentemente**, contra critérios concretos; o
feedback retorna.

**Por que separar:** agentes elogiam confiantemente trabalho medíocre próprio. É muito
mais tratável calibrar um avaliador cético.

**Custo de calibração, medido:** os primeiros avaliadores *"identificavam problemas
legítimos e depois se convenciam de que não eram importantes."* Foram necessárias várias
rodadas de leitura de logs e ajuste de prompt.

### Três agentes, full-stack

| Papel | Faz |
|---|---|
| **Planner** | Expande um prompt de 1–4 frases em spec com decisões técnicas. Previne cascata de garbage-in-garbage-out |
| **Generator** | Implementa iterativamente, com auto-avaliação antes do handoff |
| **Evaluator** | Opera a aplicação rodando como um usuário, acha bugs com localização no código, atribui nota |

### Sprint contracts

Antes de cada bloco, gerador e avaliador negociam: **o que será construído, como o
sucesso será verificado, quais os critérios testáveis.** Força o acordo sobre "pronto"
antes da implementação — e é a mesma ideia que um ticket com critérios de aceitação.

### Qualidade subjetiva mensurável

Para front-end: **design, originalidade, craft, funcionalidade.** Design e originalidade
receberam peso maior porque o modelo já ia bem nos outros dois. Avaliador calibrado com
exemplos few-shot do padrão de nota desejado.

### O custo real, medido

| Abordagem | Tempo | Custo | Resultado |
|---|---|---|---|
| Agente solo | 20 min | US$ 9 | Funcionalidade central quebrada |
| Harness completo | 6 h | US$ 200 | Aplicação multi-feature funcionando |

**20× o custo.** O avaliador só se paga quando a tarefa está além do que o modelo faz
sozinho com confiabilidade.

### Obsolescência — a parte que envelhece de propósito

| Opus 4.5 exigia | Opus 4.6 |
|---|---|
| Decomposição em sprints | Rodou 2+ horas coerente sem decomposição |
| Context resets por "ansiedade de contexto" | Desnecessário |
| Avaliador a cada sprint | Virou revisão única no fim |

**A lição:** ao chegar modelo novo, **remova componentes e meça**. Não presuma que a
arquitetura de ontem é ótima hoje. Um harness é uma lista de desconfianças, e algumas
expiram.

## 4. Agentes de longa duração — múltiplas janelas

O problema: **cada sessão começa sem memória.** Sem estrutura, o agente tenta fazer tudo
de uma vez e acaba o contexto no meio, ou declara pronto cedo demais.

**Agente inicializador** (só a primeira sessão) cria:

- **Lista de features em JSON**, cada uma marcada como falhando. O formato é deliberado:
  *"o modelo tem menos chance de alterar ou sobrescrever inapropriadamente arquivos JSON
  do que arquivos Markdown."*
- Arquivo de progresso · repositório git com baseline · `init.sh` que sobe o ambiente.

**Agente de execução** (todas as demais): `pwd` → ler git log e progresso → escolher
**uma** feature incompleta → rodar `init.sh` e os testes → implementar → commitar e
atualizar o progresso.

**Regras que o caso publicado destaca:**

- **Prompt diferente para a primeira janela e para as seguintes.** Descrito como crítico.
- Estado sempre mergeável ao fim da sessão.
- Teste explícito com automação. Sem instrução explícita, *"o Claude tendia a marcar
  features como completas sem testar adequadamente."*
- *"É inaceitável remover ou editar testes, porque isso pode levar a funcionalidade
  faltante ou com bug."*

| Falha | Mitigação no inicializador | No executor |
|---|---|---|
| Declarar vitória cedo | A lista impede esquecer trabalho | Ler a lista; um item por vez |
| Progresso bugado e não documentado | Git + notas | Começar verificando, terminar commitando |
| Marcar incompleto como pronto | Estrutura da lista | Auto-verificar antes de marcar |
| Confusão de runtime | Criar `init.sh` | Ler e executar o script primeiro |

## 5. Paralelismo em escala

Caso: 16 instâncias construindo um compilador C de ~100 mil linhas em Rust — ~2 bilhões
de tokens de entrada, 2.000 sessões, ~US$ 20.000.

**Coordenação:** loop infinito em container, sem humano. **Task locking por arquivo** —
agentes reivindicam trabalho criando arquivos numa pasta, e a detecção de conflito do git
previne duplicação. Cada agente clona, trabalha e dá push do próprio container.

**O pré-requisito absoluto:**

> *"O verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o
> problema errado."*

**Lições que generalizam:**

- **Logging estruturado para parsing automático** — formato consistente (`ERROR: [motivo]`).
- **Modelos não têm noção de tempo** — o harness ofereceu um modo rápido para feedback.
- **Especialização vence generalização** — um agente para deduplicação, outro para
  performance, outro para crítica de design. Times homogêneos renderam menos.
- **Quando o trabalho não é decomponível, crie o oráculo que o decompõe.** No gargalo em
  que todos batiam no mesmo bug, a saída foi **teste diferencial**: compilar a maior
  parte com a ferramenta de referência e só o resto com a nova, liberando paralelismo.

**O que não generalizou, e vale registrar:** o compilador não implementou parte da
geração de código e chamou a ferramenta de referência como fallback; o código gerado tem
desempenho bem abaixo; features novas frequentemente quebravam as existentes — sintoma
de estar no limite da capacidade, e sinal de que a escala não substitui capacidade.
