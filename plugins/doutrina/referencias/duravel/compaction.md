# O que sobrevive à compaction

Quando o contexto enche, o Claude Code limpa **saídas de ferramenta primeiro** e só
depois sumariza a conversa. O que acontece com cada mecanismo depois disso decide onde
uma regra deve morar para continuar valendo numa sessão longa.

## A tabela

| Mecanismo | Depois da compaction |
|---|---|
| System prompt e output style | Intactos — não são histórico |
| `CLAUDE.md` da **raiz** e rules **sem** `paths:` | Reinjetados do disco |
| Auto memory | Reinjetada do disco |
| O plano escrito em plan mode | Reinjetado do disco |
| Rules **com** `paths:` | **Só recarregam** quando um arquivo correspondente é lido de novo |
| `CLAUDE.md` **aninhado** | Idem — só se o Claude voltar àquela pasta |
| Arquivos lidos ou editados | Um punhado dos mais recentes é relido; os grandes voltam como **referência de caminho**, sem conteúdo |
| Corpos de skill invocados | Reinjetados, com teto por skill e teto total; os mais antigos caem primeiro |
| Contexto que hooks adicionaram | Sumarizado com o resto |
| Hooks `SessionStart` do tipo `compact` | Rodam de novo e o que imprimem entra no contexto novo |

## A linha que falta na tabela oficial

**O índice de descrições de skills não é reinjetado.** A tabela publicada omite isso; o
simulador da mesma página marca a linha como não sobrevivente, e o texto ao lado dele
confirma: só as skills que você **de fato invocou** são preservadas.

A consequência é concreta: depois de um `/compact`, o Claude deixa de ver a lista do que
está disponível. Skills que ele escolheria por conta própria param de ser escolhidas, e
não há erro — só ausência. Se algo precisa continuar disponível numa sessão longa,
invoque explicitamente pelo menos uma vez, ou não dependa de invocação automática.

## As três regras de projeto que saem daqui

**1. Regra que precisa durar não usa `paths:`.** Rule com escopo de caminho é a mais
econômica em contexto e a mais frágil em sessão longa. Se ela precisa valer sempre,
tire o `paths:` ou mova para o `CLAUDE.md` da raiz — e pague o custo consciente.

**2. O que importa vai no topo do `SKILL.md`.** A truncagem preserva o começo do
arquivo. Instrução crítica no fim de uma skill longa é instrução que desaparece
primeiro.

**3. Sessão longa erode o específico antes do geral.** Raiz e rules sem escopo voltam;
aninhado e escopado não. Um monorepo cujas convenções vivem todas em `CLAUDE.md` por
pacote perde exatamente as convenções do pacote em que se está trabalhando.

## O antídoto que não é técnico

*"Se você corrigiu o Claude mais de duas vezes sobre o mesmo assunto numa sessão, o
contexto está poluído com abordagens que falharam."* A recomendação é `/clear` e um
prompt melhor — não insistir. **Sessão limpa com prompt melhor quase sempre supera
sessão longa com correções acumuladas.**

Compaction é o mecanismo que adia esse momento, não o que o substitui.

---

*Fontes: `context-window` (§ What survives compaction), `how-claude-code-works`,
`memory`, `skills`, `best-practices`. A omissão do índice de skills na tabela oficial
está registrada em `armadilhas.md`.*
