---
name: fluxo
description: Diz onde o projeto está e qual é o próximo passo, lendo o estado em disco — fila de tickets, git e artefatos. Use quando não souber o que fazer a seguir, ao retomar um projeto parado, ou para conferir se algo ficou pendente.
allowed-tools: Bash, Read
---

# Onde estamos, e o que vem agora

```bash
python3 plugins/metodo/scripts/estado.py
```

Rode isso primeiro. Ele lê a fila, o git e a configuração de verificação, e imprime o
cenário com o passo recomendado.

**Você roteia. Não executa.** Reporte o que o script disse, acrescente o julgamento
que ele não tem, e pare. Não pegue o ticket, não commite, não rode a verificação — a
pessoa decide, e as outras skills fazem.

## Por que um script, e não um procedimento escrito aqui

Porque assim a recomendação é **testável**. `tests/testar_estado.py` monta cada cenário
num diretório temporário e confere qual saiu. Uma skill que só descrevesse a lógica
não teria como errar em público — e erraria em silêncio.

Também é o que mantém este corpo curto. O que fica em contexto é isto que você está
lendo; a lógica vive no script e só o resultado dela entra na sessão.

## O julgamento que o script não tem

Ele lê disco. Não sabe o tamanho do que você quer fazer. Duas coisas cabem a você:

**Mande pular o rito quando ele não se paga.** Se o trabalho cabe numa frase — e a
maior parte cabe —, ticket, brief e critérios custam mais do que a mudança. Diga isso
com todas as letras: *"escreva a frase, rode o comando de verificação, implemente"*.
Uma metodologia que não sabe se dispensar vira burocracia, e é abandonada inteira
quando cansa.

O gatilho para o rito completo é **autonomia**, não tamanho: quanto mais tempo o
agente vai rodar sem alguém olhando, mais a especificação se paga. Mudança grande
acompanhada ao vivo precisa de pouca spec; mudança pequena despachada para uma fila
precisa de spec completa.

**Diga quando o estado está estranho, não só o que ele é.** Fila com quinze tickets
prontos e nenhum em andamento é sinal de fatiamento parado, não de fartura. Ticket em
andamento há muitos commits é sinal de fatia grande demais. O script relata; você
interpreta.

## Uma coisa que este comando não faz

**Ele relata verde ou vermelho. Não garante nada.**

Se ele diz que a verificação está declarada, isso significa que existe um comando no
`.claude/metodo.json` — não que ele passa, e não que alguém vai rodá-lo. A garantia é
o hook `Stop`, que barra o fim do turno de verdade.

Confundir relatório com garantia é o modo de falha clássico de um painel: ele fica
verde, todo mundo relaxa, e o que ele mede não era o que importava.

## Se a fila estiver inválida

O script reporta isso **antes** de recomendar qualquer passo, e você deve fazer o
mesmo. Um grafo de bloqueio errado — um ciclo, uma aresta pendurada — faz o próximo
passo ser o errado, e isso não aparece na leitura. Conserte antes de seguir.
