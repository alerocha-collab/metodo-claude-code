---
name: contexto
description: Gerencia a janela de contexto — o que a enche, em que ordem cortar, quando delegar a um subagente e quando recomeçar do zero. Use quando a sessão estiver longa, quando o desempenho cair, ou ao decidir onde uma instrução deve morar para não custar contexto sempre.
---

# A janela de contexto

> *"A maior parte das boas práticas se apoia numa restrição só: a janela de contexto
> enche rápido, e o desempenho degrada conforme ela enche."*

É a restrição fundadora. Quase toda decisão de configuração é, no fundo, uma escolha
sobre o que ocupa espaço e quando.

## O que enche, em ordem de peso

**Antes de você digitar** já há conteúdo: o system prompt, o `CLAUDE.md` de cada nível,
a memória automática, as descrições de todas as skills disponíveis, e os nomes das
ferramentas de MCP conectados.

**Durante o trabalho**, o que pesa de verdade não são as suas mensagens:

1. **Conteúdo de arquivo lido** — o maior item isolado, quase sempre.
2. **Saída de comando** — uma suíte de testes verbosa ou um log de build passa
   qualquer arquivo.
3. **Retorno de subagente** — pequeno por design, mas muitos subagentes devolvendo
   relatório detalhado somam.
4. **Suas mensagens e as respostas** — a menor parte, e a que as pessoas tentam cortar
   primeiro.

Daí a assimetria que orienta tudo: **a economia grande está em não deixar entrar**, não
em resumir depois.

## As quatro saídas, da mais barata à mais cara

**1. Não deixe entrar.** Redirecione saída volumosa para arquivo e leia a cauda; use
busca em vez de ler arquivo inteiro. Um comando que despeja vinte mil linhas custa mais
que qualquer configuração que você vá ajustar.

**2. Delegue a um subagente.** Ele lê muito e devolve pouco — o trabalho acontece na
janela dele. É a ferramenta certa para exploração: "descubra como X funciona" produz
dezenas de leituras que você nunca mais vai consultar.

**3. Corte deliberadamente.** Comprimir a conversa com foco declarado preserva o que
importa melhor do que deixar a compressão automática escolher.

**4. Recomece.** Sessão nova, contexto zero.

## Quando recomeçar em vez de insistir

O critério é comportamental, não numérico:

> **Se você corrigiu o Claude mais de duas vezes sobre o mesmo assunto na mesma sessão,
> o contexto está poluído com abordagens que falharam.**

A saída é recomeçar com um prompt melhor, que incorpore o que você aprendeu — não
insistir. **Sessão limpa com prompt melhor quase sempre supera sessão longa com
correções acumuladas**, e a razão é que as tentativas erradas continuam no contexto
disputando atenção com a certa.

O mesmo vale entre tarefas não relacionadas: recomeçar é mais barato que carregar.

## Onde a instrução mora muda o custo

Esta é a decisão de contexto que se toma uma vez e vale para sempre.

| Onde | Custo |
|---|---|
| `CLAUDE.md` | **todo request, para sempre** |
| Rule com `paths:` | só quando um arquivo daquele tipo aparece |
| Skill | a descrição sempre; o corpo quando usada |
| Skill com `disable-model-invocation` | **zero** até você invocar |
| Hook | **zero**, salvo o que ele devolver |
| Subagente | isolado — só o resumo volta |

E a heurística de poda que a doc dá para o `CLAUDE.md`, e que vale para skill também:

> *"Para cada linha, pergunte: remover isto faria o Claude errar? Se não, corte.
> Arquivos inchados fazem o Claude ignorar suas instruções de verdade."*

Instrução ignorada raramente é falta de ênfase. Costuma ser excesso de vizinhança.

## O que acontece quando enche mesmo assim

Saídas de ferramenta são limpas primeiro; depois a conversa é sumarizada. O que volta
do disco, o que não volta, e as três regras de projeto que saem disso estão em
[referencias/duravel/compaction.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/compaction.md).

A que mais importa: **regra que precisa durar não usa `paths:`.** A mais econômica em
contexto é a mais frágil em sessão longa.

---

*Síntese autoral a partir de `context-window`, `best-practices`, `how-claude-code-works`,
`features-overview` e `memory`.*
