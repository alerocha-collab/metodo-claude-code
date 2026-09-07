---
name: escrever-skill
description: Escreve uma skill que dispara quando deve e continua influenciando o trabalho — concisão do corpo, progressive disclosure, e como formular a description. Use ao criar ou revisar uma skill, ou quando uma skill não estiver disparando.
---

# Escrever uma skill

## Quando é skill, e quando não é

**O gatilho:** você colou a mesma instrução, checklist ou procedimento no chat pela
terceira vez — ou uma seção do `CLAUDE.md` deixou de ser um fato e virou um
procedimento.

A diferença econômica que sustenta isso: o corpo da skill **só carrega quando é usado**.
Material de referência longo custa quase nada até alguém precisar dele. A mesma coisa
no `CLAUDE.md` custa em **todo request, para sempre**.

Não é skill quando: a regra precisa valer sempre mesmo que o modelo discorde — isso é
hook ou `permissions`, e a skill `garantir` cobre. E não é skill o que o Claude deriva
lendo o código.

## A regra que mais gente ignora: o corpo é custo recorrente

Uma vez invocada, **a skill fica em contexto pelos turnos seguintes**. O Claude Code não
relê o arquivo a cada turno — o conteúdo entra como uma mensagem e permanece.

Duas consequências:

**Cada linha é custo que se repete.** Escreva **o que fazer**, não o porquê nem a
narrativa de como se chegou nele. Aplique a mesma pergunta que se aplica ao `CLAUDE.md`:
*remover esta linha faria o Claude errar?* Se não, corte.

**Escreva instrução permanente, não passo único.** O que deve valer durante toda a
tarefa precisa estar redigido como regra que continua valendo, não como "agora faça X" —
porque o texto vai continuar ali quando o "agora" já tiver passado.

## Progressive disclosure

Mantenha o `SKILL.md` curto e mova o detalhe para arquivos ao lado. O corpo é
**panorama e navegação**; a referência é o que se carrega quando o passo exige.

```
minha-skill/
├── SKILL.md        obrigatório — panorama e navegação
├── referencia.md   detalhe, carregado quando preciso
├── exemplos.md     idem
└── scripts/        executados, não carregados
```

**A parte que costuma faltar: aponte explicitamente.** Uma seção "Recursos adicionais"
dizendo o que cada arquivo contém **e quando carregá-lo**. Sem o ponteiro, o mecanismo
não funciona — o Claude não sabe que o arquivo existe nem por que abriria.

E há uma razão física para pôr o que importa no topo: quando o contexto é comprimido, a
skill volta **truncada pelo começo**. Instrução crítica no fim de uma skill longa é a
primeira a desaparecer.

## A `description` é o que faz a skill disparar

O Claude escolhe lendo nome e descrição — o corpo só entra depois de escolhida. Então a
descrição não é resumo, é **critério de acionamento**.

- **Comece pelo caso de uso principal.** Quando há muitas skills, as descrições são
  encurtadas para caber num orçamento, e o que sobra é o começo. Palavra-chave no fim
  é palavra-chave que some.
- **Use as palavras que a pessoa diria.** "ao escrever ou modificar testes" acerta mais
  que "utilitário de qualidade de suíte".
- **Dispara demais?** Torne a descrição mais específica. Se ainda assim, use
  `disable-model-invocation: true` e invoque à mão.

## Conteúdo de referência ou de tarefa

Duas naturezas, e a distinção decide um campo do frontmatter.

**Referência** — convenções, padrões, conhecimento de domínio. Roda junto com a
conversa, para o Claude aplicar ao que já está fazendo. Deixe o modelo poder invocá-la.

**Tarefa** — passos para uma ação concreta: deploy, commit, publicação. Costuma ser algo
que **você** quer disparar, não algo que o modelo decide fazer. Se tem efeito colateral,
`disable-model-invocation: true`, e ela some do contexto até você digitar `/nome`.

## Quando a skill para de influenciar

Sintoma comum: funciona na primeira resposta e depois parece esquecida.

Quase sempre **o conteúdo continua lá** — o modelo é que passou a preferir outro
caminho. Duas saídas: reforçar a descrição e as instruções para ele continuar
preferindo, ou aceitar que **instrução é pedido** e mover a parte inegociável para hook.

Se a suspeita é que ela nunca disparou, o diagnóstico é outro: confira se ela aparece na
lista de skills disponíveis, e se o frontmatter está bem formado — YAML malformado faz o
corpo carregar **sem metadados**, então `/nome` funciona e a escolha automática não.

## Detalhes que envelhecem

Os campos exatos do frontmatter, com o que cada um aceita, ficam em
[referencias/volatil/](${CLAUDE_PLUGIN_ROOT}/referencias/volatil/) quando existirem — são o tipo de
coisa que muda entre versões. Aqui ficou só o que não muda.

---

*Síntese autoral a partir de `skills`, `features-overview`, `context-window`,
`best-practices` e `claude-directory`.*
