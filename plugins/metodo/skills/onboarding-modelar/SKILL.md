---
name: onboarding-modelar
description: Extrai o vocabulário de domínio de um repositório que já existe — dos nomes de tipo, tabela, função e rota — e confronta com o que as pessoas dizem, registrando divergências e conflitos sem resolvê-los sozinho. Use depois do mapa, antes de fatiar.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Task, Write, Edit
---

# O vocabulário que já está no código

Segunda das três skills de reengenharia. Num projeto novo o glossário nasce da
conversa; aqui ele **já existe**, espalhado em nomes de tipo, de tabela, de função,
de rota — e quase sempre inconsistente com o que as pessoas falam.

Essa inconsistência é a fonte silenciosa de retrabalho que esta skill existe para
tornar visível: o agente implementa o conceito que **leu**, e o humano queria o que
**fala**.

## Comece pelo mapa, não pelo repositório

`docs/mapa-do-projeto.md`, produzido por `/metodo:onboarding-entender`, já diz o que
o sistema faz, quais são as capacidades e onde estão as fronteiras. **Leia-o
primeiro.** Reler o repositório do zero desperdiça o trabalho anterior e enche a
janela com o que já foi destilado.

Se o mapa tiver outro nome, use-o assim mesmo — procure em `docs/` antes de concluir
que não existe. O que importa é não recomeçar do zero, não o nome do arquivo.

Se o mapa não existe, pare e rode `/metodo:onboarding-entender`. Extrair vocabulário
sem saber o que o sistema faz produz lista de palavras, não glossário.

A seção **"o que não entendi"** do mapa é o seu roteiro: ela diz onde procurar.

## Onde o vocabulário se esconde

Nomes que o domínio escolheu, não que o framework impôs:

- tipos, classes, enums e seus valores;
- tabelas, colunas e nomes de migração;
- rotas, comandos, eventos e mensagens de erro voltadas ao usuário;
- nomes de arquivo de teste — costumam nomear cenários de negócio com precisão.

Ignore vocabulário de infraestrutura. `Repository`, `Handler`, `Service`, `DTO`
descrevem a arquitetura, não o domínio. Se o termo faria sentido para alguém que
nunca viu o código, é candidato; se só faz sentido para quem programa, não é.

Para varredura ampla, despache subagentes. Você quer a conclusão, não os arquivos.

## Escreva a definição em uso, não a ideal

Esta é a regra que separa esta skill da modelagem de projeto novo.

Se o código chama de "cancelamento" algo que só marca uma flag e não estorna nada,
o glossário diz **isso**. Não diz o que cancelamento deveria ser.

Escrever a definição ideal produz um documento que descreve um sistema que não
existe — e ele será lido como se descrevesse o que existe. É o pior artefato
possível: parece certo, é preciso, e está errado.

A distância entre o que é e o que deveria ser não se apaga aqui. Ela vira linha na
seção de divergências, e depois vira ticket na skill seguinte.

## Conflito se registra, não se resolve

Dois casos, e nenhum é seu para decidir:

**Um conceito, dois nomes.** O código usa "cliente" num lugar e "usuário" noutro
para a mesma coisa. Registre os dois, com onde cada um aparece. Escolher o "certo"
por conta própria é apagar a evidência de que havia dois — e a evidência é o que
convence alguém a padronizar.

**Um nome, dois conceitos.** "Conta" é a entidade de cobrança num módulo e o login
noutro. Este é o mais perigoso, porque não gera erro: gera conversa em que duas
pessoas concordam falando de coisas diferentes.

Os dois vão para a seção **Conflitos em aberto**, marcados como não decididos.

## Confronte o que se diz contra o que o código faz

Quando o humano afirmar como algo funciona, **verifique**. Contradição é achado, e
vale dizê-la na hora:

> *"O código cancela o Pedido inteiro, mas você acabou de dizer que cancelamento
> parcial existe. Qual dos dois?"*

Cada uma dessas vai para a tabela de **divergências**, com o encaminhamento: virou
ticket, virou decisão registrada, ou ficou em aberto.

## O que não entra

- **Termo que aparece uma vez só.** Glossário inflado não é lido, e não ser lido é a
  única forma de falhar que importa.
- **Vocabulário de framework.** Ver acima.
- **Como as coisas funcionam.** Isso é código.
- **Decisão de arquitetura.** Isso é `DECISIONS.md` ou ADR.

## O que você não faz

**Não renomeia nada.** Nem o nome obviamente errado, nem o inconsistente. Você
descreve o que existe; renomear é mudança de comportamento observável, precisa de
ticket, e a decisão de padronizar é do humano.

**Não corrige o código para bater com o glossário.** A divergência é o produto.

## Depois

`/metodo:onboarding-lacunas` usa o mapa e este glossário para medir a distância até
o alvo e transformá-la em fila — que é onde as divergências registradas aqui viram
trabalho.
