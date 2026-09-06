# 016 — `doutrina`: os quatro schemas voláteis, carimbados

## Problema

O que um agente mais erra de memória é **nome de campo e valor exato** — e não erra
por preguiça: erra porque a informação é arbitrária e muda. Nesta própria sessão, dois
relatórios de subagente vieram errados exatamente aí, um deles se contradizendo dentro
do mesmo relatório.

Mas copiar schema é copiar o que mais envelhece. A Fase D do plano previa oito ou mais
tabelas; **este ticket corta para quatro** — aqueles em que errar é caro e a consulta é
frequente. O resto continua sendo ponteiro para a fonte.

Justificativa do corte: a superfície copiada é a superfície que apodrece, e o detector
avisa que a página mudou sem dizer **o que** mudou. Menos tabelas, menos releituras
obrigatórias a cada drift.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O agente escreve frontmatter de memória e erra campo | Tem a tabela em disco, carimbada |
| Nada distingue schema fresco de schema morto | Cada ficha traz URL e data, e o detector mede |

## Critérios de aceitação

- [ ] Exatamente **quatro** fichas em `referencias/volatil/`:
      frontmatter de skill · eventos e exit codes de hook · `plugin.json` ·
      sintaxe de regra de permissão
- [ ] Cada ficha traz **URL de origem e data de verificação** no topo — a suíte já
      reprova quem não trouxer
- [ ] Cada uma abre dizendo **que é volátil** e o que fazer antes de confiar nela
- [ ] As tabelas são **transcrição fiel**, não paráfrase. Onde houver dúvida sobre a
      formulação original, a ficha diz que é reconstrução
- [ ] Os campos que a doc marca como exigindo versão mínima ficam **anotados como
      tal**, sem o número — o número vive na fonte
- [ ] `fontes.json` liga cada ficha à página, e as páginas estão carimbadas com o hash
      do dia em que a ficha foi escrita
- [ ] **Negativo:** nenhuma tabela além das quatro. Se aparecer necessidade de uma
      quinta, ela vira ticket com justificativa, não acréscimo silencioso
- [ ] **Negativo:** as fichas voláteis não repetem critério de escolha. Isso é durável
      e mora em outro lugar

## Fora de escopo

- Frontmatter de subagente, `.mcp.json`, `.lsp.json`, monitors, channels, `userConfig`,
  superfície de CLI, tabela de 44 tools — ponteiro, não cópia
- Manter as fichas atualizadas automaticamente

## Verificação

A suíte estrutural já exige carimbo em tudo que está em `volatil/`. Acrescentar um
caso que reprove uma ficha volátil sem data — o conjunto balanceado exige que exista
também o caso que **aprova** a que tem.

Mais uma pergunta respondida localmente: *"quais campos o frontmatter de uma skill
aceita?"*.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
