# 017 — `doutrina`: a bateria de perguntas que verifica a destilação

## Problema

Uma destilação pode estar completa, bem escrita, carimbada, com o índice íntegro — e
**não responder as perguntas para as quais foi feita**. Nada do que existe hoje detecta
isso: a suíte estrutural verifica que os arquivos existem e estão ligados, não que
alguém consegue decidir algo a partir deles.

É a mesma distinção que custou dois tickets nesta sessão: **testar o script não é
testar o sistema**. Os 68 casos do `metodo` passavam com o portão inerte.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Sabemos que os arquivos existem | Sabemos que eles respondem |
| Uma ficha pode perder o trecho que importa sem ninguém notar | A bateria acusa |

## Critérios de aceitação

- [ ] Existe uma bateria de **perguntas de arquitetura reais**, cada uma com a ficha
      que deve contê-la e uma asserção verificável de que a resposta está lá
- [ ] Cobre, no mínimo, uma pergunta por ficha do núcleo, incluindo as seis já
      declaradas nos tickets anteriores como critério de verificação
- [ ] Inclui ao menos **duas perguntas cuja resposta a doc oficial erra ou omite** —
      a inversão de precedência e o índice de skills não sobreviver à compaction. São
      elas que provam que a destilação vale mais que um link
- [ ] A asserção é **estrutural, não literal**: verifica que o conceito está presente,
      de forma que reescrever a redação não quebre a suíte. Uma bateria que quebra por
      motivo cosmético é abandonada em semanas
- [ ] Roda offline, em segundos, e entra no `testar_tudo.py` por descoberta
- [ ] **Negativo:** a bateria **não** chama modelo nenhum. Verificação que depende de
      inferência não é determinística, custa a cada execução, e não pode rodar no CI
- [ ] **Negativo:** pergunta cuja resposta não estiver em ficha nenhuma **reprova** —
      não é motivo para relaxar a asserção. É lacuna de cobertura, e vira ticket

## Fora de escopo

- Avaliar a **qualidade** da resposta: isso exige julgamento e continua humano
- Comparar a ficha com a fonte viva — é o `verificar_fontes.py`, e ele já existe
- Medir se o agente de fato escolhe a ficha certa em sessão real: é observação de uso,
  não suíte

## Verificação

A própria bateria, mais o teste inverso: **apagar um trecho central de uma ficha faz a
bateria reprovar**. Conjunto balanceado — sem esse caso, uma bateria que sempre aprova
passaria despercebida, que é exatamente o defeito que ela existe para não ter.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
