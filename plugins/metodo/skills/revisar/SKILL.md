---
name: revisar
description: Revisa um conjunto de mudanças em dois eixos independentes — Standards (segue as convenções deste repositório?) e Spec (implementa o que o ticket pediu?) — em contextos separados e paralelos, e transforma cada achado aceito em ticket. Use para revisar uma branch, um diff pendente ou o trabalho desde um ponto fixo.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Task
---

# Revisar em dois eixos

Duas perguntas diferentes, dois revisores, dois contextos.

- **Standards** — este código segue as convenções documentadas deste repositório?
- **Spec** — este código faz o que o ticket pediu?

Um mesmo diff pode passar num eixo e falhar no outro: seguir todo padrão e implementar
a coisa errada, ou fazer exatamente o pedido quebrando todas as convenções. Por isso
os eixos não se misturam em momento nenhum.

## Por que os revisores não podem ser você

Quem escreveu o código é o pior revisor dele — não por incompetência. Tendo em
contexto o raciocínio que produziu a mudança, não ficar enviesado a favor dela é
impossível: o código *parece* certo porque você lembra por que cada escolha foi feita.

Por isso cada revisor roda em **subagente**, e o briefing dele carrega tudo o que ele
precisa. Ele **não** herda a conversa. Isso não é limitação a contornar: é o
mecanismo. Se você se pegar querendo "explicar o contexto" ao revisor, pare — é
exatamente o viés que a separação existe para remover.

## 1. Delimitar

Estabeleça o ponto de partida: um commit, uma branch, uma tag, ou o merge-base com a
principal. Se o humano não disse, pergunte — revisar o intervalo errado desperdiça as
duas revisões.

```bash
git diff <ponto>..HEAD --stat
```

Se o diff for grande demais para uma revisão útil, diga isso antes de gastar os dois
subagentes. Diff de quarenta arquivos não é revisado, é aprovado por cansaço — e o
achado real é sobre o fatiamento.

## 2. Montar os dois briefings

Cada briefing é **autossuficiente**. O subagente não tem acesso a mais nada.

**Eixo Standards** recebe:
- o diff completo;
- as convenções documentadas do repositório — `CLAUDE.md`, `AGENTS.md`, guias de
  estilo, o que houver;
- o baseline de smells: [references/smells.md](references/smells.md);
- a regra de precedência: **o repositório sobrepõe o baseline.** Se a convenção local
  contradiz o catálogo, a convenção local vence, e o revisor não a reporta como
  achado.

**Eixo Spec** recebe:
- o diff completo;
- os **critérios de aceitação** do ticket, verbatim;
- a seção fora de escopo do ticket, verbatim;
- **nada mais.** Sem o brief inteiro, sem a conversa, sem sua explicação.

E a instrução que define o eixo: responder **critério por critério** se o diff o
atende, com a evidência no próprio diff. Critério não atendido e critério atendido
por acidente são achados diferentes.

O eixo Spec também procura o inverso: o que foi feito **além** do pedido. Código que
não serve a nenhum critério e não estava no escopo é achado — é gold-plating, e a
seção fora de escopo existe para torná-lo visível.

## 3. Despachar em paralelo

Os dois ao mesmo tempo, numa só leva. Sequencial não traz benefício e dobra a espera.

**Contrato de retorno: no máximo 400 palavras por eixo.** Não é economia — é o que
impede que a revisão inunde a sessão e obrigue você a resumir, que é onde os eixos
se misturariam.

Cada achado vem com: o que está errado, onde (por descrição, não por número de
linha), e por que importa. Achado sem "por que importa" é preferência pessoal
disfarçada.

## 4. Apresentar lado a lado

**Não mescle. Não reordene entre eixos. Não deduplique entre eixos.**

Se os dois apontam a mesma linha por razões diferentes, isso é informação — achatar
para um item só a destrói. Ranquear os dois numa lista única obriga a comparar
severidades que não são comparáveis: "quebra a convenção de nomes" e "não implementa o
critério 3" não estão na mesma escala.

Apresente em duas seções, com os títulos dos eixos, cada uma na ordem que o revisor
dela devolveu.

Você **não** julga os achados. Você os transporta. O julgamento é do humano.

## 5. Achado aceito vira ticket, na hora

Esta é a parte que costuma não acontecer, e é a que faz a diferença entre revisão e
teatro de revisão.

Para cada achado que o humano aceitar, acrescente um ticket em `tickets/fila.json`
com **`modulo` preenchido** — é o campo que faz a próxima fatia que tocar aquele
módulo ficar bloqueada por este ticket. Sem ele, "refatoro depois" vira "não
refatoro", e seis fatias adiante o módulo tem seis variações da mesma lógica.

Depois:

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

Achado **rejeitado** também merece uma linha — no ticket que originou a revisão, ou
no `DECISIONS.md` se for uma escolha que vai se repetir. Achado rejeitado sem registro
volta na próxima revisão, e alguém gasta o mesmo tempo de novo.

## 6. Você não conserta

A revisão reporta e enfileira. Não edita código, nem "só esse aqui que é rápido".

Consertar durante a revisão mistura no mesmo diff o que estava sendo revisado e o que
foi corrigido, e a próxima revisão passa a ter dois autores sem saber. Se um achado é
urgente, ele é um ticket urgente.
