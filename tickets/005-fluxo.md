# 005 — Escrever o `/fluxo`

## Problema

Saber qual passo vem a seguir depende de onde o projeto está, e esse estado já existe
em disco: a fila de tickets, o histórico de commits, a presença ou ausência de
artefatos. Hoje ninguém lê isso — a sequência tem que ser lembrada, e lembrar é
exatamente o que falha quando o contexto enche.

O problema nunca foi de memória. É de estado.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O próximo passo é lembrado | O próximo passo é **lido** do estado |
| Nenhum atalho para trabalho pequeno | Sabe recomendar **pular o rito** quando o trabalho não o justifica |

## Critérios de aceitação

- [ ] Em repositório sem fila, recomenda fatiar — e não outra coisa
- [ ] Com fila e nenhum ticket em andamento, nomeia o **próximo ticket não bloqueado**,
      respeitando o grafo e não a ordem numérica
- [ ] Com um ticket em andamento, nomeia esse ticket e o que falta nele
- [ ] Com diff não commitado, nomeia a revisão como próximo passo
- [ ] Para trabalho descritível em uma frase, **recomenda pular** o rito, e diz por quê
- [ ] Roteia; **não executa** o passo que recomenda, e não reimplementa o que as outras
      skills fazem
- [ ] Relata verde/vermelho e diz explicitamente que **não garante** nada — garantia é
      hook
- [ ] Se a fila não passa no validador, reporta isso **antes** de recomendar qualquer
      passo
- [ ] **Negativo:** não escreve nem altera a fila, e não marca estado de ticket

## Fora de escopo

- Exibir estado na statusline — a Fase 0 registrou que não é documentado para plugin
- Executar o passo recomendado
- Ler issue tracker externo

## Verificação

A suíte cobre. Acrescentar uma suíte que monte os quatro cenários de estado em
diretório temporário e verifique a recomendação de cada um — é a verificação nº 2 do
plano, e ela **pode** ser automatizada porque só depende de leitura de disco.

## Prefactoring

Necessário? ( ) não · (x) **avaliar ao começar** — o `/fluxo` precisa ler a fila, e a
leitura hoje vive dentro de `validar_fila.py`. Se a duplicação aparecer, extrair a
leitura para função reutilizável em ticket próprio, **antes** desta fatia.
