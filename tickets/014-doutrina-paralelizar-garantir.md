# 014 — `doutrina`: as fichas `paralelizar` e `garantir`

## Problema

Duas perguntas que um agente faz ao desenhar um sistema e hoje só se responde lendo
sete e seis páginas respectivamente:

**"Como distribuo este trabalho?"** — subagente, agent view, agent teams, workflow,
worktree, `/batch` e cross-session messaging são sete mecanismos que parecem
alternativas e não são. A doc tem a tabela, mas espalha o critério.

**"Como faço esta regra valer sempre?"** — a `onde-colocar` já diz *que* existe uma
camada de garantia; falta o detalhe de como usá-la sem construir um portão inerte.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Escolher paralelismo exige ler 7 páginas | Quatro perguntas em cascata resolvem |
| A camada de garantia é citada, não detalhada | Há ficha própria, com os modos de falha |

## Critérios de aceitação

### `paralelizar`
- [ ] Abre pela pergunta que elimina mais casos: **isolamento de contexto não é
      paralelismo** — se o problema é "isto vai poluir minha conversa", a resposta é um
      subagente e acabou
- [ ] Usa **"quem segura o plano"** como eixo de classificação, e diz onde vivem os
      resultados intermediários em cada opção — é a razão física da escolha
- [ ] Trata **isolamento de arquivo como ortogonal** à coordenação, e registra a
      assimetria: agent view isola sozinho, subagente isola se pedido, **agent teams
      não isolam**
- [ ] Nomeia os **não-mecanismos**: comando bash em background, fork, routine e
      `/batch` não são estilos de coordenação
- [ ] Diz o que exige plano pago, o que é experimental e o que exige git

### `garantir`
- [ ] Distingue os três níveis de autoridade **na prática**, não só na definição:
      quando hook basta e quando só `permissions` serve
- [ ] Cobre os modos de falha do hook que produzem portão inerte: exit code que não
      bloqueia, pasta não confiada, timeout, e stdout que o modelo nunca vê
- [ ] Diz onde declarar hook em cada situação, incluindo o caso de plugin
- [ ] **Negativo:** não repete o que `armadilhas.md` já cobre. Referencia

### Ambas
- [ ] Corpo abaixo de 500 linhas; detalhe em referência sob demanda
- [ ] Zero números de versão
- [ ] Registradas em `fontes.json`, ligadas às páginas de origem
- [ ] **Negativo:** nenhuma ficha nova órfã — a suíte reprova se houver

## Fora de escopo

- Schemas e tabelas de campos — é o ticket 016
- Um roteador entre as skills: as `description` já são o roteamento, e um roteador
  faria toda sessão pagar contexto para apontar

## Verificação

A suíte estrutural cobre integridade e ligação. O conteúdo se verifica por duas
perguntas respondidas só com arquivos locais: *"como paralelizo uma mudança em 40
arquivos?"* e *"escrevi um hook e ele não bloqueia, por quê?"*.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
