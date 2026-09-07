# 022 — Reconciliar o plano com a realidade, e fazer alguém vigiar

## Problema

`docs/plano-metodologia.md` afirma coisas falsas sobre o próprio repositório:

- **"Fase 3 — Core adaptado. Em andamento."** Está concluída, e as Fases `/fluxo` e 4
  também — todas depois dela.
- **"as duas suítes são conjuntos balanceados."** São doze.
- **"Orçamento de contexto medido — `/doctor` já entrega isto."** Foi medido, mas por
  `tests/testar_orcamento.py`, com tetos declarados. O plano previa consulta manual;
  a realidade construiu mecanismo.
- **O `doutrina` não existe neste documento.** O repositório distribui **dois** plugins,
  e o plano descreve um.

E, ao contrário de `docs/arquitetura.md`, ele **não tem carimbo e nada o vigia**. Foi
por isso que apodreceu sem ninguém notar: o detector existe desde o ticket 012 e nunca
foi apontado para ele.

## A pergunta de desenho, antes da correção

Reescrever o plano para descrever a realidade o transforma num **segundo documento de
arquitetura** — e o `arquitetura.md` já é esse, carimbado e medido. Duplicar seria
criar duas fontes que divergem na primeira semana.

Um plano executado tem outro trabalho, que nenhum outro documento faz: **dizer se o
plano estava certo.** Onde a execução divergiu da intenção, e se a divergência foi
correção ou falha. Isso é retrospectiva, e é o retorno sobre o ato de planejar.

Então a reconciliação **não é** "atualizar o plano para o presente". É separar o que era
intenção do que virou resultado, e nomear a distância entre os dois.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O plano afirma fases em andamento que fecharam | Cada fase carrega o desfecho real |
| A verificação lista seis itens sem status | Cada item diz verificado, verificado de outro jeito, ou **não verificado** |
| Nada vigia o documento | Carimbo, e `estado.py` reporta a distância |
| O detector só é lembrado por quem já sabe dele | Aparece onde alguém já olha ao decidir o próximo passo |

## Critérios de aceitação

- [ ] As fases carregam desfecho real, incluindo a 5, que **segue sem alvo**
- [ ] Os seis itens de verificação recebem status honesto. Pelo menos um continua
      **não verificado** — o prefixo de reengenharia nunca rodou contra código existente
- [ ] Uma seção nova registra **onde a execução divergiu do plano**, com o motivo — é a
      parte que só um plano executado pode entregar
- [ ] O `doutrina` aparece, e o documento diz que ele veio de **outro** plano
- [ ] O documento é carimbado com o SHA
- [ ] `estado.py` reporta a distância dos documentos carimbados — **detecta, não
      bloqueia**, como a decisão 014 fixou
- [ ] **Negativo:** o detector **não** entra no CI como trava. Ele ficaria vermelho em
      quase todo commit, e trava que grita sempre é trava que se aprende a ignorar
- [ ] **Negativo:** o plano não vira relatório de estado. Onde o assunto é o desenho em
      vigor, ele aponta para `arquitetura.md` em vez de repetir

## Fora de escopo

- Reescrever a doutrina do plano — as nove decisões, o desenho do `/fluxo`, o prefixo de
  reengenharia. Aquilo é intenção, e intenção não se corrige por ter envelhecido
- Fase 5: continua sem alvo, e escolher um é decisão do dono, não desta fatia

## Verificação

Rodar `estado.py` num repositório com documento carimbado desatualizado e confirmar que
ele **reporta e não impede**. Conjunto balanceado: também num repositório sem documento
nenhum, onde ele não pode inventar cobrança.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
