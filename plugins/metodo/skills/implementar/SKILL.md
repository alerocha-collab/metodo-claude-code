---
name: implementar
description: Conduz uma fatia do início ao commit — pega um ticket da fila, acorda onde os testes entram, implementa, verifica ao longo e fecha em commit. Use quando houver um ticket pronto para implementar.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

# Implementar uma fatia

Uma sessão, um ticket, um commit.

As **regras** do papel estão no agente `construtor` e valem aqui inteiras — não as
repito. Este arquivo é o **procedimento**: a ordem das coisas, e o que fazer quando
algo sai do previsto.

## 1. Pegar o ticket

```bash
python3 plugins/metodo/scripts/marcar_ticket.py <id> em-andamento
```

O script recusa se outro ticket já estiver em andamento, ou se um bloqueador ainda
estiver aberto. Se ele recusar, **a recusa está certa** — resolva o que ele apontou
em vez de contornar editando o JSON.

Leia o brief inteiro antes de abrir qualquer arquivo, inclusive **fora de escopo**,
que é a seção que mais economiza trabalho.

### Duas recusas suas, antes de começar

**Sem critérios de aceitação, não comece.** Um ticket sem critério não é uma spec, é
um desejo, e você vai acabar escrevendo os critérios que já sabe satisfazer. Devolva
ao humano para fatiar direito.

**Se o brief exige prefactoring que ainda não foi feito**, esse prefactoring é outro
ticket e vem antes. Não faça os dois na mesma fatia: o diff misturado deixa de ser
revisável e a falha fica ambígua.

## 2. Acordar onde os testes entram

Antes de escrever o primeiro teste, decida **em quais fronteiras** ele vai existir, e
diga isso em voz alta. Teste escrito numa fronteira que ninguém acordou tende a
cristalizar uma decisão de implementação que ainda ia mudar.

Fronteira boa é onde há contrato observável — uma função pública, um endpoint, um
arquivo de saída. Fronteira ruim é o meio de uma implementação que a próxima fatia
vai reescrever.

## 3. O ciclo

Vermelho → verde. **O terceiro tempo não é aqui** — a razão está no agente
`construtor`.

- Escreva o teste que falha, e **veja-o falhar**. Teste que nunca foi vermelho não
  prova nada: pode estar passando por construção.
- Faça-o passar da forma mais simples que funcione.
- Rode a verificação da área a cada passo que faça sentido. Não espere o fim: a
  quebra descoberta no portão é a mais cara de diagnosticar, porque acumulou causas.

**Se a verificação fica vermelha e você não entende por quê**, pare de tentar
consertar e leia. Duas correções sobre o mesmo assunto significam contexto poluído —
a saída é recomeçar limpo, não insistir.

## 4. O que fazer com o que você encontra pelo caminho

Você vai encontrar coisa errada ao lado do caminho. **A resposta quase nunca é
consertar agora.**

Achou um smell, código duplicado, um nome ruim, uma abstração especulativa? Vira
ticket, na hora:

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

Acrescente o ticket com `modulo` preenchido — é o campo que faz a próxima fatia que
tocar aquele módulo ficar bloqueada por ele. Sem isso, "refatoro depois" vira "não
refatoro", e seis fatias adiante o módulo tem seis variações da mesma lógica.

A exceção é estreita: se a coisa errada **impede** a fatia atual, ela vira ticket de
prefactoring, você para, e devolve ao humano a decisão de fazer o prefactoring
primeiro. Não a engula dentro desta fatia.

## 5. Quando um critério não se sustenta

Critério impossível, ambíguo ou simplesmente errado acontece. O que **não** acontece
é você reescrevê-lo.

Pare, e devolva ao humano: qual critério, o que ele exige, por que não se sustenta, e
qual você proporia no lugar. A decisão é dele. Critério ajustado por quem está sendo
medido por ele deixa de ser contrato e vira descrição do que foi feito.

O mesmo vale para o portão: se a verificação não passa e a causa é o teste estar
errado, isso é conversa, não edição.

## 6. Fechar

Antes do commit, confira cada critério de aceitação contra o que existe — com
**evidência**, não com impressão. "Os testes passam" sem a saída do comando é uma
opinião sobre o código.

O commit é o handoff. A mensagem diz **por que**, não o quê — o diff já diz o quê.
Inclua o id do ticket e, se houver, o que ficou deliberadamente de fora e por quê.

```bash
python3 plugins/metodo/scripts/marcar_ticket.py <id> concluido
```

O portão do papel `construtor` roda a verificação ao fim do turno. Se ele bloquear,
ele está fazendo o trabalho dele.

## 7. Se a fatia não couber

Diga explicitamente, com o que já está commitado e o que falta. Fatia que não cabe
numa sessão é informação sobre o fatiamento, não fracasso seu — e é a informação que
faz a próxima ficar do tamanho certo.

Não estenda a sessão para "só terminar". É assim que o handoff volta a doer.
