# Evals — vocabulário, graders, roteiro e armadilhas

> Fontes: *Demystifying evals for AI agents* · *Building a C compiler with a team of
> parallel Claudes* · *Harness design for long-running application development* · docs
> `best-practices`. Indexadas em `fontes.json`, com hash.

**Por que é durável.** Vocabulário, tipos de grader e modos de falha de eval não mudam
quando a plataforma atualiza. O que envelhece são números de benchmark, e não há nenhum
aqui.

---

## 1. Vocabulário

| Termo | Definição |
|---|---|
| **Task** | Teste único, com entradas e critério de sucesso |
| **Trial** | Uma tentativa. Vários por task cobrem a variabilidade do modelo |
| **Grader** | Lógica de pontuação. Uma task pode ter vários |
| **Transcript** | Registro completo de outputs, chamadas e raciocínio |
| **Outcome** | Estado final do ambiente — *a reserva existe mesmo no banco?* |
| **Harness** | Infraestrutura que roda tasks concorrentes, registra e agrega |
| **Suite** | Conjunto de tasks medindo uma capacidade |

Avaliação de agente é **multi-turno**: decisão autônoma ao longo de vários passos,
**onde erros compõem**. Não é avaliação de resposta única com outro nome.

## 2. Os três graders

| Tipo | Forte em | Fraco em |
|---|---|---|
| **Código** | Rápido, barato, objetivo, reproduzível | Frágil contra variação válida; sem nuance |
| **Modelo** | Flexível, escalável, captura nuance | Não determinístico, caro, precisa calibração |
| **Humano** | Padrão-ouro; calibra os graders de modelo | Caro, lento, exige especialista |

**Combine os três.** Priorize determinístico; complemente com LLM onde a flexibilidade
ajuda; use humano com parcimônia e principalmente **para calibrar os outros dois**.

## 3. Por tipo de agente

- **Código** — graders determinísticos, sobretudo testes. O padrão SWE-bench: passa só
  quando o código conserta os testes falhando **sem quebrar os existentes**.
- **Conversacional** — sucesso multidimensional: conclusão (estado), eficiência (limite
  de turnos), qualidade de interação. Frequentemente exige **simular personas**.
- **Pesquisa** — combine *groundedness* (as afirmações têm suporte nas fontes?),
  cobertura, qualidade de fonte, e rubrica para coerência da síntese.
- **Computer use** — ambiente real ou isolado, verificando **navegação de UI e mudança
  de estado no backend** — o pedido foi feito, não só exibido.

## 4. O roteiro do zero

1. **Comece pequeno agora.** 20–50 tasks vindas de **falhas reais**, não centenas de
   tasks perfeitas. No início os efeitos são grandes e amostras pequenas bastam.
2. **Converta as checagens manuais** que você já faz, mais bug tracker e fila de suporte.
3. **Tasks inequívocas, com solução de referência.** Dois especialistas independentes
   devem chegar ao mesmo veredito. A solução de referência prova que a task é solucionável
   **e que o grader funciona**. Aprovação persistente de 0% costuma indicar **especificação
   quebrada, não agente incapaz**.
4. **Conjuntos balanceados** — teste quando o comportamento **deve** e quando **não
   deve** ocorrer. Eval unilateral gera otimização unilateral.
5. **Ambientes isolados por trial.** Estado compartilhado — arquivo remanescente, cache —
   cria falha correlacionada que mascara o desempenho real.
6. **Avalie o resultado, não o caminho.** Agentes descobrem abordagens válidas que
   ninguém antecipou. Construa crédito parcial para tasks multicomponente.
7. **Leia transcripts regularmente.** Revelam se o grader avalia certo ou rejeita solução
   válida, e constroem intuição de modo de falha.
8. **Monitore saturação.** Perto de 100%, um eval de capacidade virou suíte de regressão.
   Progresso estagnado: o agente bateu no limite, ou a suíte precisa de tasks mais difíceis?
9. **Trate como teste unitário.** Pratique **eval-driven development**: defina a
   capacidade planejada via eval **antes** de o agente cumpri-la.

## 5. Armadilhas

- **Bypass e hack** — projete graders que o agente não consiga burlar por brecha não
  intencional.
- **Checagem frágil de caminho** — não exija sequência específica de chamadas.
- **Especificação ambígua** — a task precisa ser resolvível por um especialista humano.
- **Estado compartilhado entre trials.**
- **Penalizar criatividade válida** — modelos encontram soluções que superam a restrição
  estática do eval.
- **Grading rígido demais** — há relato de pontuação artificialmente suprimida por grader
  que penalizava `96.12` quando esperava `96.124991…`.

## 6. O modelo Queijo Suíço

Nenhuma camada pega tudo. Combine:

**evals automatizadas** (aceleram iteração pré-lançamento) + **monitoramento em
produção** (verdade de campo em escala) + **A/B** (lento, definitivo) + **feedback de
usuário** (esparso, autosselecionado) + **revisão manual de transcript** + **estudos
humanos sistemáticos** (padrão-ouro para subjetivo, e para calibrar juízes de modelo).

## 7. Calibrar um avaliador custa iterações

Os primeiros avaliadores *"identificavam problemas legítimos e depois se convenciam de
que não eram importantes."* Leia logs, ache as divergências do julgamento pretendido,
ajuste o prompt.

Para qualidade subjetiva, defina critérios explícitos e **pese-os deliberadamente** — o
caso publicado pesou design e originalidade acima de craft e funcionalidade, porque o
modelo já ia bem nos dois últimos. Calibre com exemplos few-shot do padrão desejado.

## 8. Antipadrões do dia a dia

| Antipadrão | Correção |
|---|---|
| **Trust-then-verify gap** — implementação plausível que não trata edge case | Sempre forneça verificação. **Se você não consegue verificar, não faça deploy** |
| **Sessão entulhada** — contexto cheio de coisa irrelevante | Limpe entre tarefas não relacionadas |
| **Correção sobre correção** | Após **duas** correções falhas, recomece com prompt novo incorporando o aprendido |
| **Exploração infinita** — "investigue X" sem escopo | Escopar, ou delegar a subagente para não consumir o contexto principal |
| **Arquivo de instruções superespecificado** | Podar; converter regra em hook |
