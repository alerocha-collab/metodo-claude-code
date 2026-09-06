# Referência 04 — Verificação e evals

Fonte: docs `best-practices`; *Demystifying evals for AI agents*; *Building a C compiler with a team of parallel Claudes*; *Harness design for long-running application development*.

---

## 1. A regra central

> **Dê ao Claude uma verificação que ele possa executar: testes, um build, um screenshot para comparar. É a diferença entre uma sessão que você assiste e uma da qual você pode se afastar.**

**O Claude para quando o trabalho *parece* pronto.** Sem verificação executável, "parece pronto" é o único sinal, e o humano vira o loop de verificação — todo erro espera alguém notar.

A verificação é qualquer coisa que devolva sinal legível na conversa: suíte de testes, exit code de build, linter, script que compara com fixture, screenshot comparado a um design.

## 2. Escada de dureza do portão

| Nível | Mecanismo | Troca |
|---|---|---|
| **No prompt** | "rode os testes e itere até passarem", na mesma mensagem | Zero setup; funciona hoje |
| **Na sessão** | Condição de `/goal`; um avaliador separado rechecha a cada turno; o Claude Code encerra se travar | Baixo setup |
| **Determinístico** | `Stop` hook roda o check como script e bloqueia o fim do turno até passar. Encerra após **8 bloqueios consecutivos** | Médio setup; garantia real |
| **Segunda opinião** | Subagente revisor ou workflow em contexto novo — quem faz não dá a nota | Médio setup; pega erro de julgamento, não só de execução |

**Cada degrau troca setup por atenção humana.** Os níveis de `/goal` e Stop hook são o que permite uma execução não supervisionada terminar corretamente.

## 3. Qualidade do verificador

> *"O verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o problema errado."*

Verificador fraco não é neutro — é ativamente perigoso, porque o agente otimiza contra ele em escala. Checklist:

- **Cobertura** — o verificador falha quando o comportamento errado acontece? Monte casos negativos, não só positivos.
- **Regressão** — passa apenas se o novo comportamento funciona **e** o antigo continua funcionando.
- **Custo de contexto** — pré-compute estatísticas de resumo em vez de despejar saída bruta. Amostragem determinística (ex.: 1–10% por agente, subconjuntos diferentes) quando a suíte é grande demais.
- **Parsabilidade** — formato de erro consistente (`ERROR: [motivo]`) para ser passível de grep pelo agente.
- **Não decomponível?** Crie o oráculo que decompõe. Teste diferencial (compilar a maior parte com a ferramenta de referência, só o resto com a nova) transformou um gargalo serial em trabalho paralelo.

## 4. Quem dá a nota

Agentes **elogiam confiantemente o próprio trabalho medíocre**. Separar gerador de avaliador é *"muito mais tratável"* do que fazer o gerador autocrítico.

- O revisor em contexto novo vê **apenas o diff e os critérios** — não o raciocínio que produziu a mudança. Avalia o resultado nos próprios termos.
- Calibrar o avaliador custa iterações reais: os primeiros *"identificavam problemas legítimos e depois se convenciam de que não eram importantes."* Leia logs, ache as divergências do julgamento pretendido, ajuste o prompt.
- Para qualidade subjetiva, defina critérios explícitos e **pese-os deliberadamente** — o caso publicado pesou design e originalidade acima de craft e funcionalidade, porque o modelo já ia bem nos dois últimos. Calibre com exemplos few-shot do padrão de nota desejado.

### O contra-alerta obrigatório

> Um revisor instruído a encontrar lacunas **vai** reportar lacunas, mesmo quando o trabalho está sólido. Perseguir todo achado leva a superengenharia: abstração extra, código defensivo, testes para casos impossíveis.

**Instrua o revisor a sinalizar apenas o que afeta corretude ou os requisitos declarados.** Trate o resto como opcional.

## 5. Evidência, não afirmação

Peça a saída do teste, o comando executado e o que retornou, ou o screenshot. Revisar evidência é mais rápido que refazer a verificação — e funciona para sessões que ninguém assistiu.

## 6. Evals — vocabulário

| Termo | Definição |
|---|---|
| **Task** | Teste único, com entradas e critério de sucesso |
| **Trial** | Uma tentativa (vários por task cobrem a variabilidade do modelo) |
| **Grader** | Lógica de pontuação; uma task pode ter vários |
| **Transcript** | Registro completo de outputs, chamadas, raciocínio |
| **Outcome** | Estado final do ambiente (a reserva existe mesmo no banco?) |
| **Harness** | Infraestrutura que roda tasks concorrentes, registra e agrega |
| **Suite** | Conjunto de tasks medindo uma capacidade |

Avaliação de agente é **multi-turno**: decisão autônoma ao longo de vários passos, **onde erros compõem**.

## 7. Os três graders

| Tipo | Forte em | Fraco em | Métodos |
|---|---|---|---|
| **Código** | Rápido, barato, objetivo, reproduzível | Frágil contra variação válida; sem nuance | String matching, teste binário, análise estática, verificação de outcome, análise de transcript |
| **Modelo** | Flexível, escalável, captura nuance, saída aberta | Não determinístico, caro, precisa calibração | Rubricas, asserções em linguagem natural, consenso de múltiplos juízes |
| **Humano** | Padrão-ouro; calibra os graders de modelo | Caro, lento, exige especialista | — |

**Combine os três.** Priorize determinístico; complemente com LLM onde flexibilidade ajuda; use humano com parcimônia e para calibrar.

## 8. Por tipo de agente

- **Código** — graders determinísticos, especialmente testes unitários. O padrão SWE-bench: passa apenas quando o código conserta os testes falhando **sem quebrar os existentes**. Complemente com grading de transcript para qualidade.
- **Conversacional** — sucesso multidimensional: conclusão (estado), eficiência (limite de turnos), qualidade de interação (tom, empatia). Frequentemente exige **simular personas de usuário** com chamadas LLM adicionais.
- **Pesquisa** — combine *groundedness* (as afirmações têm suporte nas fontes?), cobertura (os fatos obrigatórios apareceram?), qualidade de fonte, e rubrica LLM para coerência da síntese. Calibre com frequência contra especialista humano.
- **Computer use** — ambiente real ou sandboxed, verificando **navegação de UI e mudança de estado no backend** (o pedido foi feito, não só exibido).

## 9. Métricas

- **`pass@k`** — probabilidade de ao menos uma solução correta em `k` tentativas. Use quando uma solução funcional basta.
- **`pass^k`** — probabilidade de **todos** os `k` trials passarem. Fica mais difícil conforme `k` cresce. **Use para sistemas voltados ao usuário que precisam acertar toda vez.**

As duas divergem muito: com `k=10`, `pass@k` pode se aproximar de 100% enquanto `pass^k` despenca.

## 10. Roteiro do zero

1. **Comece pequeno agora.** 20–50 tasks vindas de **falhas reais de usuário**, não centenas de tasks perfeitas. No início, os efeitos são grandes e amostras pequenas bastam.
2. **Converta checagens manuais** que você já faz, mais bug tracker e fila de suporte.
3. **Tasks inequívocas com solução de referência.** Dois especialistas independentes devem chegar ao mesmo veredito. A solução de referência prova que a task é solucionável e que o grader funciona. **Aprovação persistente de 0% geralmente indica especificação quebrada, não agente incapaz.**
4. **Conjuntos balanceados** — teste quando o comportamento **deve** e quando **não deve** ocorrer. Eval unilateral gera otimização unilateral.
5. **Ambientes isolados por trial.** Estado compartilhado (arquivo remanescente, cache) cria falha correlacionada que mascara o desempenho real.
6. **Avalie o resultado, não o caminho.** Agentes descobrem abordagens válidas que ninguém antecipou. Construa crédito parcial para tasks multicomponente.
7. **Leia transcripts regularmente** — revelam se o grader avalia certo ou rejeita solução válida; constroem intuição de modo de falha.
8. **Monitore saturação.** Perto de 100%, evals de capacidade viram suíte de regressão. Progresso estagnado: o agente bateu no limite ou a suíte precisa de tasks mais difíceis?
9. **Propriedade e manutenção.** Trate como teste unitário. Pratique **eval-driven development**: defina a capacidade planejada via eval antes de o agente cumpri-la.

## 11. Armadilhas

- **Bypass e hack** — projete graders que o agente não consiga burlar por brecha não intencional.
- **Checagem frágil de caminho** — não exija sequência específica de chamadas.
- **Especificação ambígua** — a task precisa ser resolvível por um especialista humano.
- **Estado compartilhado entre trials.**
- **Penalizar criatividade válida** — modelos de fronteira encontram soluções que superam a restrição estática do eval.
- **Grading rígido demais** — a Anthropic relata pontuações artificialmente suprimidas por graders que penalizavam `96.12` quando esperavam `96.124991…`.

## 12. O modelo Queijo Suíço

Nenhuma camada pega tudo. Combine: **evals automatizadas** (aceleram iteração pré-lançamento) + **monitoramento em produção** (verdade de campo em escala) + **A/B** (lento, definitivo) + **feedback de usuário** (esparso, autosselecionado) + **revisão manual de transcript** + **estudos humanos sistemáticos** (padrão-ouro para subjetivo e para calibrar juízes LLM).

## 13. Antipadrões de verificação no dia a dia

| Antipadrão | Correção |
|---|---|
| **Trust-then-verify gap** — implementação plausível que não trata edge case | Sempre forneça verificação. **Se você não consegue verificar, não faça deploy** |
| **Kitchen sink session** — contexto cheio de coisa irrelevante | `/clear` entre tarefas não relacionadas |
| **Correção sobre correção** | Após **duas** correções falhas, `/clear` e prompt novo incorporando o aprendido |
| **Exploração infinita** — "investigue X" sem escopo | Escopar, ou usar subagente para não consumir o contexto principal |
| **CLAUDE.md superespecificado** | Podar; converter regra em hook |
