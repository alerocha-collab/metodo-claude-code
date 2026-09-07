---
name: garantir
description: Faz uma regra valer sempre, e não só na maior parte das vezes — escolhendo entre hook, permissions e sandbox, e evitando os modos de falha que produzem um portão que parece existir e não existe. Use ao converter uma convenção em garantia, ou quando um hook não estiver bloqueando.
---

# Fazer valer sempre

Instrução em `CLAUDE.md` ou em skill é **pedido**. Esta ficha é sobre as duas camadas
que não são.

> *"An instruction like 'never edit `.env`' in CLAUDE.md or a skill is a request, not a
> guarantee. A `PreToolUse` hook that blocks the edit is enforcement."*

## Qual das duas camadas

A pergunta que separa não é "isto é importante?" — é **o que a regra proíbe ou exige**.

**`permissions` quando a regra é sobre o que pode ser tocado.** "Nunca leia `.env`",
"nunca edite `tests/`", "só rode estes comandos". É aplicada pelo cliente antes de o
modelo agir, avaliada `deny` → `ask` → `allow` com a primeira regra vencendo, e não
depende de script nenhum rodar.

**Hook quando a regra é sobre o que tem que acontecer**, ou quando a decisão exige
lógica que uma regra de caminho não expressa. "Rode o linter depois de editar",
"não encerre o turno com a suíte vermelha", "bloqueie este comando se ele apontar para
produção".

**Sandbox quando a ameaça é o código que você executa**, não o agente. Rodar uma suíte
de testes **é** executar código arbitrário do repositório e de todas as dependências
dele, com os seus privilégios. Restringir as ferramentas do agente não restringe nada
disso: o processo de teste não herda as permissões do Claude Code. A fronteira precisa
ser do sistema operacional, e cobre **filesystem e rede**.

## Duas assimetrias de `permissions` que economizam regras

- Uma regra que permite **editar** um caminho **concede leitura** dele
  automaticamente.
- Uma regra que **nega leitura** de um caminho **também bloqueia** edição e escrita ali.

Então negar leitura é a regra mais forte disponível, e costuma ser a única necessária.

## A terceira assimetria: confiança barra o que concede

Num workspace ainda não confiado, `permissions.allow` e `additionalDirectories` do
projeto **não valem** — eles concedem. `deny` e `ask` valem desde sempre, porque só
restringem. **O que protege não espera permissão para proteger.**

Consequência que inverte a intuição: **hooks rodam antes de você confiar em qualquer
coisa** — os de settings, os de skill de projeto e os de plugin instalado. Se a
preocupação é código de terceiro executando na sua máquina, confiança **não** é a
defesa; `--bare`, `--setting-sources user` e `disableAllHooks` são.

A lista completa do que espera confiança, e as três consequências que pegam, estão em
[referencias/armadilhas.md](${CLAUDE_PLUGIN_ROOT}/referencias/armadilhas.md), item 15.

## Os cinco modos de falha que produzem portão inerte

Um hook que não funciona é pior que nenhum, porque dá sensação de cobertura. Estes
cinco produzem exatamente isso, e nenhum deles emite erro:

**1. O exit code não bloqueia.** Só o **2** bloqueia por código. Qualquer outro é
tratado como erro não bloqueante e a ação prossegue — inclusive o **1**, que é o código
convencional de falha, e o **127**, que é o que o shell devolve quando o interpretador
não existe.

Consequência dupla: um script que morre com exceção sai com 1 e **libera**; e um
interpretador ausente libera **na máquina mal configurada**, que é o pior lugar. Um
portão precisa capturar toda exceção e sair com 2, e o comando precisa converter
qualquer falha em bloqueio.

**2. A pasta não é confiada.** Hooks declarados no projeto, em frontmatter de skill e
em frontmatter de subagente **não rodam** até a pasta ser confiada. É regra mais
estrita que a de settings: confiar na pasta pai não basta.

**3. O modelo nunca vê a mensagem.** Texto puro no stdout só chega ao Claude em quatro
eventos. Nos demais vai só para o log de depuração. É a maior classe de bug de hook: o
script explica, ninguém recebe, e parece que ele não rodou.

**4. O filtro `if` deixa passar.** Ele é declaradamente best-effort — não consegue
decidir com certeza o que um comando com variável expandida vai executar. Como filtro
de desempenho serve; como fronteira, não.

**5. O bloco está no lugar errado.** `hooks:` no frontmatter de agente **é ignorado
para agentes de plugin**, em silêncio. Ver `armadilhas.md`.

## Onde declarar

| Situação | Onde |
|---|---|
| Vale para você, em todo projeto | `settings.json` do usuário |
| Vale para o time, neste repositório | `settings.json` do projeto, commitado |
| Só para você, neste repositório | `settings.local.json` |
| Imposto pela organização | managed settings — e user e project não sobrepõem |
| Distribuído por plugin | `hooks/hooks.json` na raiz do plugin |
| Só enquanto uma skill roda | frontmatter da skill |

**E a regra que muda o desenho: hooks se fundem, nunca se sobrescrevem.** Todos os
registrados disparam, venham de onde vierem. **Não existe desligar um hook colocando
outro num escopo mais forte.**

A consequência prática é que **escopo de hook vive dentro do script**, não na
configuração: uma cláusula de guarda que lê o evento e sai sem objetar quando não se
aplica. É remendo, e é o único caminho disponível.

## O portão de fim de turno

Um hook `Stop` que roda a verificação é o que converte sessão assistida em sessão da
qual se pode sair — é a diferença entre olhar o agente e ir embora.

Duas propriedades que ele precisa ter, e que não são óbvias:

**Fail-closed no que não conseguir determinar.** Verificação ausente conta como falha,
nunca como "nada a verificar". Um portão que aprova o que não consegue verificar não é
portão.

**Tratar a própria recursão.** O Claude Code **sobrescreve** um `Stop` hook depois de
um número de bloqueios seguidos sem progresso. O evento traz um campo dizendo que o
hook já bloqueou; um hook que o ignora se desliga sozinho, em silêncio, exatamente
quando está funcionando.

## Quando o portão é um classificador, e não uma regra

Há um terceiro desenho além de regra fixa e hook: **julgar cada ação antes de executar**.
É o que o auto mode faz, e as decisões dele generalizam para qualquer avaliador de ação.

A motivação é medida e desconfortável: **usuários aprovavam 93% dos prompts de permissão
de qualquer forma.** Prompt que aparece sempre não é revisão, é ritual.

**Duas decisões que valem fora do caso:**

1. **O avaliador não vê o raciocínio do agente.** Isso impede que o agente *"convença o
   classificador a tomar uma decisão ruim"* com racionalização persuasiva, e força a
   decisão sobre a **ação**, não sobre a justificativa dela.
2. **Negar e continuar**, em vez de negar e parar. O modelo recebe o feedback e procura
   um caminho mais seguro; o usuário vê um retry, não o fim da sessão. Isso torna falso
   positivo **sobrevivível** — e é o que permite apertar o portão sem tornar a
   ferramenta insuportável.

**E o número honesto:** em incidentes reais de ação excessiva, **17% de falso negativo**.
Não porque o classificador não veja o comando perigoso, mas porque não consegue
determinar se o consentimento cobria aquele raio de dano. *"Uma aprovação não é um
padrão."*

A consequência de projeto: um classificador **substitui acesso irrestrito, não revisão
humana** em infraestrutura de alto risco. Restrinja operação autônoma às tarefas onde
17% é aceitável.

## Antes de escrever o hook

Duas perguntas, nesta ordem:

1. **Existe um script que decide "violou / não violou" com exit code?** Se não, você
   não tem regra, tem intenção — e escrever no `CLAUDE.md` para "resolver" é rebaixar
   uma garantia a pedido e chamar isso de solução.
2. **Isto já se resolve com `permissions`?** Se a regra é sobre caminho ou comando,
   provavelmente sim, e uma regra de permissão é menos código e mais forte.

E o critério de quando vale a pena: **um hook se paga quando o custo de a regra falhar
uma vez é maior que o custo de mantê-la.** Teste prático — se você já corrigiu a mesma
coisa três vezes, ela devia ser hook.

Falso positivo é caro justamente porque **com hook não se negocia**. Comece com um.

---

*Síntese autoral a partir de `hooks`, `hooks-guide`, `permissions`, `permission-modes`,
`sandboxing`, `features-overview` e `sub-agents`. Os cinco modos de falha estão
documentados em páginas diferentes; reuni-los como lista é construção nossa, e dois
deles foram medidos em sessão real, não só lidos.*
