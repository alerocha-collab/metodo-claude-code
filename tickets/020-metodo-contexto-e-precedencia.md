# 020 — `metodo`: custo de contexto das descrições e a precedência de agente

## Problema

**Custo medido, não estimado:** os dois plugins somam ~1.242 tokens em descrições de
skill, carregados em **todo request**. A `arquiteto-claude-code` sozinha ocupa 994
caracteres — 20% do total, quatro vezes a média das outras.

Isso não é só espaço. Quando a listagem estoura o orçamento, as descrições são
**encurtadas**, e o que se perde são as palavras-chave que fazem a skill disparar. Uma
descrição gorda empurra as vizinhas para fora, e a skill que some é a que alguém
precisava.

**E uma armadilha não documentada:** agentes de plugin **perdem** para agentes locais
de mesmo nome. Um `construtor` no `.claude/agents/` do projeto sobrepõe o do plugin em
silêncio, e a pessoa vai concluir que o plugin não carregou.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Uma skill ocupa 20% do orçamento de descrição | Todas na mesma faixa |
| A precedência de agente pega quem instala de surpresa | Está no README |

## Critérios de aceitação

- [ ] A descrição de `arquiteto-claude-code` cai para a faixa das demais, **sem perder
      o gatilho**: o caso de uso principal vem primeiro, e as frases que fazem a skill
      disparar continuam lá
- [ ] A soma das descrições dos dois plugins cai de forma mensurável, e o número novo
      fica registrado — medido, não estimado
- [ ] O README do `metodo` diz que agente local de mesmo nome **sobrepõe** o do plugin,
      e o que fazer: renomear o local, ou removê-lo
- [ ] O README diz também que **skills de plugin são namespaced e coexistem** — a
      assimetria entre as duas regras é a parte que confunde
- [ ] **Negativo:** encurtar não é apagar `when_to_use`. O campo existe para as
      frases-gatilho, e é ele que faz a skill ser escolhida

## Fora de escopo

- Encurtar as demais skills: elas estão na faixa
- Reescrever o corpo de qualquer skill

## Verificação

Medir antes e depois com o mesmo script, e registrar os dois números. A suíte ganha um
caso que reprova se a soma passar de um teto declarado — assim a próxima skill que
nascer gorda é pega na hora, e não daqui a seis skills.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
