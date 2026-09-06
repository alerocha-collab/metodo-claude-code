---
name: fatiar
description: Transforma um trabalho descrito em uma fila de tickets — fatias verticais dimensionadas para caber numa sessão, com critérios de aceitação escritos antes da implementação e arestas de bloqueio explícitas. Use quando houver uma spec, uma feature ou um pedaço de trabalho para decompor antes de começar a codificar.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

# Fatiar trabalho em tickets

Você transforma trabalho descrito em **fila de tickets**. Não implementa nada.

O ticket é a unidade de trabalho e é a spec: uma sessão pega um ticket, implementa,
commita, acaba. Se a fatia não couber numa sessão, o handoff cai no meio dela — e é
por isso que dimensionar é o trabalho principal aqui, não o acessório.

## Antes de tudo: isto merece tickets?

Se você consegue descrever o diff em **uma frase**, não fatie. Escreva a frase, o
comando de verificação, e mande implementar. Ticket para vinte linhas é cerimônia
que custa mais que o trabalho.

Fatie quando: o trabalho não cabe numa sessão · vai para uma fila que alguém pega
depois · atravessa mais de um módulo · ou tem ordem que importa.

## O procedimento

### 1. Leia o que já existe antes de propor

Convenções do projeto, glossário de domínio, decisões registradas, a fila atual.
Ticket que ignora o que já foi decidido gera retrabalho e discussão.

Se já houver `tickets/fila.json`, leia-a: fatias novas podem ser bloqueadas por
tickets abertos, e um smell registrado antes pode ter reservado um módulo.

### 2. Corte fatias **verticais**

Cada fatia atravessa um caminho estreito e **completo** por todas as camadas que
precisar — schema, API, interface, testes. Nunca uma camada inteira de uma vez.

A pergunta que decide: **esta fatia é demonstrável sozinha?** Se não dá para mostrar
algo funcionando ao fim dela, o corte foi horizontal e a revisão fica impossível —
você vai estar revisando a forma das coisas em vez do comportamento visível.

### 3. Dimensione pela janela, não pelo tamanho aparente

Cada fatia cabe numa sessão nova, sem contexto herdado. Sinais de que está grande:
toca muitos módulos · precisa de mais de um comando de verificação · o critério de
aceitação tem "e também".

Fatia pequena demais também tem custo: ticket, commit e revisão para vinte linhas.
Se você chegou a quarenta tickets de quinze minutos, agrupe.

### 4. Prefactoring vem antes, como ticket próprio

Se uma fatia fica mais fácil depois de uma mudança estrutural, essa mudança é **outro
ticket**, e a fatia fica bloqueada por ele. *Torne a mudança fácil, depois faça a
mudança fácil.*

Nunca embuta refatoração dentro do ticket de comportamento: o diff misturado deixa
de ser revisável, e a falha fica ambígua — quebrou pela feature ou pela limpeza?

Para refactor de raio amplo, use **expand–contract**: adicione a forma nova ao lado
da antiga, migre os chamadores em lotes dimensionados pelo raio (cada lote um
ticket), e apague a antiga só no fim. Cada passo mantém a verificação verde.

### 5. Declare as arestas de bloqueio

Cada ticket diz quais tickets o bloqueiam. Só isso — não invente ordem onde não há
dependência real. Ordem inventada serializa trabalho que poderia ser paralelo.

Preencha também `modulo`: é o que permite que um smell aceito na revisão bloqueie a
próxima fatia que tocar o mesmo lugar. Sem ele, "refatoro depois" vira "não refatoro".

### 6. Escreva os critérios de aceitação

Esta é a parte que decide se o ticket presta. Carregue
[references/criterios.md](references/criterios.md) antes de escrever o primeiro —
critério complacente é, por construção, plausível, e passa em leitura rápida.

### 7. Escreva cada brief

Use `templates/ticket.md` do plugin. Duas regras que não se negociam:

- **Durabilidade acima de precisão.** O ticket pode ficar parado por semanas enquanto
  o código muda. **Não cite caminho de arquivo. Não cite número de linha.** Descreva
  interfaces, tipos e contratos de comportamento, que sobrevivem a refatoração.
- **Comportamental, não procedimental.** Bom: *"o tipo `Config` deve aceitar um campo
  opcional `schedule`"*. Ruim: *"abra src/tipos.ts e some um campo na linha 42"*.

E a seção **fora de escopo** é obrigatória em todo ticket. É a mais barata de
escrever e a que mais economiza — é o que impede gold-plating.

### 8. Valide a fila

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

Ele pega o que falha em silêncio na leitura: ciclo de bloqueio, aresta apontando
para ticket inexistente, mais de um ticket em andamento. Não entregue fila que não
passa.

## As regras duras

**1. Os critérios entram antes da implementação e não são editados durante.**
Critério alterado no meio é o alvo se ajustando ao tiro. Se um se revelar impossível,
isso é conversa com o humano — não edição de quem está sendo medido por ele.

**2. Você propõe, o humano valida.** Você é bom em redigir critérios verificáveis, e
é exatamente por isso que não pode ser quem os aprova: quem dá a nota não pode ser
quem faz o trabalho. Entregue a fila **para revisão**, não como fato consumado.

**3. Não implemente.** Nem "só para testar". Sua saída são tickets.

## O que entregar ao humano

Um resumo curto, não a fila inteira colada:

- quantas fatias, e o critério de corte que você usou;
- a ordem de bloqueio, em uma linha (`001 → 002 → 004`, `003` paralelo);
- **as decisões que você tomou por conta própria** — onde a spec era ambígua e você
  escolheu uma leitura. É o que mais precisa de olho humano;
- o que você deixou explicitamente fora de escopo, e por quê;
- qualquer critério sobre o qual você tem dúvida de verificabilidade.

Termine perguntando o que revisar primeiro. Não peça aprovação em bloco: fila
aprovada por leitura rápida é fila não revisada.
