---
name: avaliar
description: Projeta a verificação de um agente — que portão usar, se o verificador é bom, e como montar evals que não se enganam. Use ao decidir como saber que o trabalho está certo, ou quando o agente declara pronto o que não está.
---

# Como saber que está certo

**O Claude para quando o trabalho *parece* pronto.** Sem verificação executável,
"parece" é o único sinal, e o humano vira o loop de verificação — todo erro espera
alguém notar.

> **Dê ao Claude uma verificação que ele possa executar: testes, um build, um screenshot
> para comparar. É a diferença entre uma sessão que você assiste e uma da qual você pode
> se afastar.**

## A escada de dureza do portão

| Nível | Mecanismo | Troca |
|---|---|---|
| **No prompt** | "rode os testes e itere até passarem", na mesma mensagem | Zero setup |
| **Na sessão** | Condição de objetivo; avaliador rechecando a cada turno | Baixo setup |
| **Determinístico** | `Stop` hook roda o check e bloqueia o fim do turno | Médio setup; **garantia real** |
| **Segunda opinião** | Revisor em contexto novo — quem faz não dá a nota | Pega erro de julgamento, não só de execução |

**Cada degrau troca setup por atenção humana.** Como montar o hook: ficha `garantir`.

## O verificador é o gargalo, não o agente

> *"O verificador da tarefa precisa ser quase perfeito, senão o Claude vai resolver o
> problema errado."*

Verificador fraco não é neutro — é **ativamente perigoso**, porque o agente otimiza
contra ele em escala.

- **Cobertura** — ele falha quando o comportamento errado acontece? **Monte casos
  negativos, não só positivos.** Suíte só com casos positivos aprova uma trava que
  bloqueia tudo.
- **Regressão** — passa só se o novo funciona **e** o antigo continua funcionando.
- **Custo de contexto** — pré-compute estatísticas em vez de despejar saída bruta.
- **Parsabilidade** — formato de erro consistente, passível de grep.

## Quem dá a nota

Agentes **elogiam confiantemente o próprio trabalho medíocre**. Separar gerador de
avaliador é *"muito mais tratável"* do que fazer o gerador autocrítico. O revisor em
contexto novo vê **apenas o diff e os critérios** — não o raciocínio que produziu a
mudança.

### O contra-alerta obrigatório

> Um revisor instruído a encontrar lacunas **vai** reportar lacunas, mesmo quando o
> trabalho está sólido. Perseguir todo achado leva a superengenharia: abstração extra,
> código defensivo, testes para casos impossíveis.

**Instrua o revisor a sinalizar apenas o que afeta corretude ou requisito declarado.**
O resto é opcional. Sem esta linha, a ficha ensinaria a piorar o código.

## Evidência, não afirmação

Peça a saída do teste, o comando e o que ele retornou. Revisar evidência é mais rápido
que refazer a verificação — e é o que torna revisável uma sessão que ninguém assistiu.

## `pass@k` ou `pass^k`

- **`pass@k`** — ao menos uma solução correta em `k` tentativas. Use quando uma solução
  funcional basta.
- **`pass^k`** — **todos** os `k` passam. Fica mais difícil conforme `k` cresce. **Use
  para sistema voltado ao usuário, que precisa acertar toda vez.**

As duas divergem muito: com `k=10`, `pass@k` pode se aproximar de 100% enquanto `pass^k`
despenca. Relatar a primeira e prometer a segunda é o erro caro.

## Onde está o resto

- **Vocabulário, os três graders, o roteiro do zero e as armadilhas:**
  [referencias/duravel/evals.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/evals.md)
- **Transformar o portão em garantia:** ficha `garantir`
- **Decidir se o sistema devia ser agente:** ficha `arquitetar`
