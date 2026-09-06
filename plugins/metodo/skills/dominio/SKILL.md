---
name: dominio
description: Constrói e afia o vocabulário do projeto — desafia termos ambíguos, confronta o que se diz contra o que o código faz, e mantém o glossário em disco. Use ao discutir terminologia, ao escrever ou editar o glossário, ou quando o mesmo conceito aparecer com dois nomes.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
---

# O vocabulário do projeto

Você mantém o **glossário** — os termos do domínio, com a definição em uso.

Esta skill é para quando o modelo **muda**: um termo novo se firma, dois nomes se
revelam o mesmo conceito, uma ambiguidade aparece. Apenas *ler* o glossário para
escrever com o vocabulário certo não é isto — é hábito de uma linha que qualquer
skill faz.

## O artefato

`CONTEXT.md` na raiz, ou junto do módulo quando o projeto tiver fronteiras internas
de verdade.

**É glossário e nada mais.** Sem detalhe de implementação, sem decisão de
arquitetura, sem rascunho, sem spec. A regra é dura porque a erosão é previsível: um
`CONTEXT.md` que aceita "como funciona" vira documentação paralela ao código, e
documentação paralela ao código mente em três meses.

Crie o arquivo quando houver o primeiro termo resolvido. Não antes — glossário vazio
é convite a preenchê-lo com ruído.

## O que você faz durante a conversa

**Desafie o termo contra o glossário, na hora.** Se o humano usa uma palavra que o
glossário já define de outro jeito, aponte: *"o glossário define 'cancelamento' como
X, mas você parece querer dizer Y. Qual dos dois?"* Deixar passar é aceitar duas
definições e descobrir a divergência num bug.

**Afie linguagem frouxa.** Termo vago ou sobrecarregado ganha um nome canônico
proposto: *"você disse 'conta' — é o Cliente ou o Usuário? São coisas diferentes."*

**Invente cenários de fronteira.** Relação de domínio se testa com caso concreto:
*"e se o pedido tem três itens e o cliente cancela um?"* É onde a definição frouxa
quebra, e é mais barato quebrar aqui.

**Confronte com o código.** Quando o humano afirma como algo funciona, verifique.
Contradição é achado: *"o código cancela o Pedido inteiro, mas você acabou de dizer
que cancelamento parcial existe. Qual dos dois?"*

**Escreva na hora.** Termo resolvido entra no `CONTEXT.md` naquele momento, não no
fim. Lote acumulado é lote perdido.

## O que **não** entra

- Termo que aparece uma vez só. Glossário inflado não é lido, e não ser lido é a
  única forma de falhar que importa.
- Sinônimo que ninguém usa.
- Como as coisas funcionam. Isso é código.
- Decisão de arquitetura. Isso é `DECISIONS.md` ou ADR — ver abaixo.

## Onde as decisões vão

Duas camadas, e a diferença entre elas é a barra:

**`DECISIONS.md`** — append-only, formato em `templates/DECISIONS.md`. É onde entra a
maior parte: tudo que alguém perguntaria "por que está assim?" daqui a três meses.
Entrada nova vai no fim; decisão errada se revoga com outra que a cite, nunca por
edição. A linha da **alternativa descartada** é obrigatória — sem ela não era decisão,
era o caminho default.

**ADR** — só quando as **três** condições valem juntas:

1. difícil de reverter — mudar de ideia depois custa de verdade;
2. surpreendente sem contexto — um leitor futuro vai perguntar "por que assim?";
3. resultado de um trade-off real — havia alternativas genuínas.

Faltando uma, é entrada no `DECISIONS.md`. Ofereça ADR com parcimônia: um repositório
com barra só de ADR registra quase nada, porque quase nada passa nas três.

## Projeto novo e projeto que já existe

Aqui o vocabulário nasce da **conversa** — o humano sabe o domínio, você o extrai e
afia.

Num projeto que já existe ele nasce do **código**, e essa é outra skill
(`/metodo:onboarding-modelar`). A diferença importa: o glossário extraído do código
descreve o que está implementado, que quase nunca é o que as pessoas dizem em voz
alta. Quando as duas trilhas se encontram, **a divergência é o achado**, não um erro
a corrigir em silêncio.
