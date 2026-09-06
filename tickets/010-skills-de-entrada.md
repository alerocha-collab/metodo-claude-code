# 010 — As skills de entrada: adaptar, depender ou dispensar

## Problema

O pipeline da metodologia é *entrevistar → nomear o domínio → especificar → fatiar →
implementar → revisar*. O plugin cobre **da metade em diante**. As duas primeiras
etapas — a entrevista que fecha decisões em aberto, e a modelagem de domínio para
projeto novo — só existem como skills instaladas em `~/.claude/skills/`, de terceiro,
sob licença MIT.

Consequência prática: **o plugin não é autossuficiente.** Instalado noutra máquina, a
trilha de projeto novo começa no meio. É o oposto do motivo de empacotá-lo.

Há uma decisão real aqui, e ela não é técnica.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| A trilha de projeto novo começa em `fatiar` | A entrada está resolvida, de um dos três jeitos, por escrito |
| A dependência de skills de terceiro é tácita | Está declarada, ou eliminada |

## Critérios de aceitação

- [ ] A escolha entre os três caminhos está tomada e **registrada no `DECISIONS.md`**
      com a alternativa descartada e o custo dela:
      **(a) adaptar** as skills para dentro do plugin, com atribuição e licença
      preservadas; **(b) declarar dependência** delas, documentando a instalação;
      **(c) escrever as nossas**, mais estreitas, cobrindo só o que a metodologia usa
- [ ] Se a escolha for (a), o `LICENSE` e a atribuição de origem existem no
      repositório, e o commit de origem fica registrado
- [ ] Se for (b), o README diz o que instalar e o `/fluxo` reporta a ausência em vez de
      recomendar um passo impossível
- [ ] Se for (c), o escopo do que **não** se cobre está escrito — a alternativa mais
      barata só é honesta se disser o que perde
- [ ] Em qualquer caso, uma instalação limpa noutra máquina consegue percorrer a
      trilha de projeto novo do início, ou saber exatamente o que falta
- [ ] **Negativo:** nada de copiar conteúdo de terceiro sem atribuição, nem "inspirado
      em" que na prática é cópia

## Fora de escopo

- Reescrever `fatiar`, `implementar`, `revisar` ou `fluxo`
- A trilha de reengenharia, que é dos tickets 007 a 009
- Publicar no marketplace

## Verificação

`claude plugin validate --strict`, mais a leitura do `DECISIONS.md`: a decisão está
registrada com alternativa descartada, ou o ticket não está pronto.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
