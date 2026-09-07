---
name: paralelizar
description: Escolhe como distribuir trabalho entre agentes — subagente, agent view, agent teams, dynamic workflow, worktree ou mensagem entre sessões. Use quando uma tarefa parecer grande demais para uma conversa, ou quando o contexto estiver enchendo de saída que não se vai reler.
---

# Como distribuir o trabalho

Sete mecanismos parecem alternativas e não são. Quatro coordenam, um isola arquivos,
um passa recados, e um é embalagem dos outros.

## Pergunta 0 — você quer paralelismo, ou só tirar lixo do contexto?

**Esta pergunta elimina a maioria dos casos, e a resposta quase nunca é paralelismo.**

Se o problema é *"isto vai inundar minha conversa com resultado de busca, log ou
conteúdo de arquivo que eu nunca mais vou olhar"* — a resposta é **um subagente**, e
acabou. Não é paralelismo, é higiene de contexto. Um subagente só já resolve.

O ganho é assimétrico e é o argumento inteiro: ele lê muito e devolve pouco.

Só continue lendo se a resposta for genuinamente "preciso de várias coisas
acontecendo".

## Pergunta 1 — quem segura o plano?

É o eixo que classifica os quatro mecanismos de coordenação, e o que decide o custo.

| Quem decide o que roda a seguir | Mecanismo | Onde vivem os resultados intermediários |
|---|---|---|
| O Claude, turno a turno, na sua conversa | **subagentes** | na janela de contexto dele |
| **Você**, despachando e voltando depois | **agent view** | em outras sessões; só o que você olhar |
| Um agente *lead*, supervisionando pares | **agent teams** | numa lista de tarefas compartilhada |
| Um **script** | **dynamic workflow** | em variáveis do script — **fora de qualquer contexto** |

A última linha é a diferença que importa em escala: quando o plano está em código, os
intermediários não passam por janela de contexto nenhuma. É por isso que workflow é o
único que vai a dezenas ou centenas de agentes.

E workflow não serve só para escala: como o roteiro é código, ele repete um **padrão de
qualidade** — fazer agentes independentes revisarem adversarialmente os achados uns dos
outros antes de reportar, por exemplo. Uma passada só não faz isso.

## Pergunta 2 — os trabalhadores precisam conversar?

- **Não, só devolver resultado** → subagentes.
- **Não, só reportar a você** → agent view.
- **Sim, e discordar entre si** → agent teams. É o único desenhado para **desacordo
  produtivo**: hipóteses concorrentes testadas em paralelo, com os pares se refutando.
  Investigação sequencial sofre de ancoragem; várias tentando derrubar umas às outras
  produzem uma teoria sobrevivente mais confiável.
- **Sim, mas entre sessões que você iniciou** → mensagem entre sessões. Ela carrega
  **texto, nunca histórico nem arquivos**. Para mover contexto, retome a sessão.

## Pergunta 3 — eles tocam nos mesmos arquivos?

**Isolamento de arquivo é ortogonal à coordenação.** Worktree não é um quinto
mecanismo; é a camada de baixo, e exige repositório git.

E a assimetria é a parte que mais surpreende:

| Mecanismo | Isola arquivos? |
|---|---|
| Agent view | **sim, sozinho** — move a sessão para um worktree antes de editar |
| Subagente | **se você pedir**, com `isolation: worktree` |
| Agent teams | **não** — você tem que particionar os arquivos à mão |

Dois teammates editando o mesmo arquivo se sobrescrevem. Não há aviso.

## Pergunta 4 — escala

Dezenas a centenas de agentes: só workflow. Um punhado de pares longos: teams. Algumas
tarefas delegadas por turno: subagentes.

E a heurística que a doc dá para teams vale para todos: **três focados costumam superar
cinco espalhados.** O overhead de coordenação cresce mais rápido que o paralelismo, e
os retornos são decrescentes.

## O que **não** é um mecanismo de coordenação

Nomear isto evita quatro perguntas erradas:

- **Comando bash em background** roda um comando sem bloquear a conversa. Não cria
  agente.
- **Fork** é um subagente que herda a conversa inteira em vez de começar do zero.
  É uma variedade de subagente, não uma superfície nova — e é a que **abre mão do
  isolamento de entrada**.
- **Routine** roda uma sessão em horário agendado, na nuvem. Não é paralelo na sua
  máquina.
- **`/batch`** é subagentes + worktrees embalados, com um PR por unidade. Uso
  empacotado, não estilo de coordenação.

## O que custa e o que exige

- **Custo é linear no número de agentes.** Dez sessões em background consomem cota
  cerca de dez vezes mais rápido que uma. Teams é o mais caro: cada teammate é uma
  instância inteira.
- **Agent teams é experimental e desligado por padrão**, e exige sessão interativa —
  em modo não interativo ele simplesmente não forma equipe.
- **Dynamic workflows exigem plano pago.**
- **Worktrees exigem git.**
- **Agent view é research preview**, e o trabalho vive na sua máquina.

## Antes de decidir, veja também

Três confusões de nome que produzem escolha errada — `/agents` não é `claude agents`,
e habilitar agent teams muda o comportamento de subagentes nomeados sem avisar — estão
em [referencias/armadilhas.md](${CLAUDE_PLUGIN_ROOT}/referencias/armadilhas.md).

Para *onde a instrução mora* em vez de *quem executa*, veja a skill `onde-colocar`.

---

*Síntese autoral a partir de `agents`, `sub-agents`, `agent-view`, `agent-teams`,
`cross-session-messaging`, `workflows` e `worktrees`. A ordem das perguntas e a
elevação da pergunta 0 são construção nossa: a doc tabela os mecanismos, não a
cascata.*
