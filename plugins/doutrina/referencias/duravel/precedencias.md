# Precedência: quem vence quando o mesmo nome existe em dois lugares

> **O aviso que a documentação não dá: as precedências não são uniformes.** Cada
> família de mecanismo resolve conflito de um jeito, e duas delas se **invertem** entre
> si. Supor que "projeto sempre ganha de usuário" é a suposição errada mais provável.

## As seis regras

**`CLAUDE.md` — aditivo, não substitutivo.** Todos os níveis carregam ao mesmo tempo e
o conteúdo se soma. Não há um vencedor: há um texto maior. Quando as instruções se
contradizem, o modelo reconcilia usando julgamento, e a mais específica tende a
prevalecer. Em conflito declarado entre usuário e projeto, **o projeto tem prioridade**.

**Rules — `project` ganha de `user`.** As de usuário carregam antes; as de projeto
depois, e por isso prevalecem.

**Skills — `managed` > `user` > `project`.** ⚠️ **Aqui inverte.** Para *instruções* o
projeto ganha do usuário; para *skills* o usuário ganha do projeto. Não há aviso disso
em página nenhuma. Skills de plugin são namespaced (`plugin:nome`) e por isso não
colidem — a de plugin e a local coexistem.

**Subagentes — `managed` > flag de CLI > `project` > `user` > `plugin`.** Cinco níveis,
e o de plugin é o mais fraco de todos: uma definição local com o mesmo nome
**substitui** a do plugin, e o plugin só passa a valer quando a local sai.

**MCP — `local` > `project` > `user`.** A entrada do escopo mais forte vence **inteira**;
não há mescla campo a campo.

**Settings — `managed` > CLI > `local` > `project` > `user`.** E com uma regra que muda
o resultado: **arrays se mesclam, escalares se sobrepõem**. Uma lista de permissões
definida em dois escopos vira a união das duas, não a do escopo mais forte.

**Hooks — não há precedência.** Todos os registrados disparam, venham de onde vierem:
managed, usuário, projeto, local, plugin, frontmatter de skill, frontmatter de agente.
**Eles se fundem, nunca se sobrescrevem.**

## A consequência do caso dos hooks

Não existe "desligar um hook de projeto colocando outro no local". Se você precisa que
uma regra valha só para parte das sessões, o escopo tem que estar **dentro do script** —
uma cláusula de guarda que lê o evento e sai sem objetar quando não se aplica.

É remendo, e é o único caminho quando o hook vem de um plugin: `hooks:` no frontmatter
de agente **é ignorado para agentes de plugin**. Ver `armadilhas.md`.

## Tabela de bolso

| Família | Vencedor | Observação |
|---|---|---|
| `CLAUDE.md` | ninguém — soma | projeto prevalece em conflito |
| Rules | **project** > user | |
| Skills | managed > **user** > project | ⚠️ inverte em relação a rules |
| Subagentes | managed > CLI > project > user > **plugin por último** | local substitui a de plugin |
| MCP | local > project > user | entrada inteira, sem mescla |
| Settings | managed > CLI > local > project > user | arrays mesclam, escalares sobrepõem |
| Hooks | **nenhum** | todos disparam |

## Como conferir em vez de supor

Quando o comportamento não bate com esta tabela, o problema costuma ser **carregamento**,
não precedência: o arquivo não está no escopo que você pensa, ou não foi carregado
ainda. `/doctor` e `--debug` respondem isso; deduzir da tabela, não.

---

*Fontes: `features-overview` (§ Understand how features layer), `claude-directory`,
`memory`, `sub-agents`, `mcp`, `settings`. A inversão skills × rules é achado nosso —
as duas regras estão documentadas em páginas diferentes e nenhuma menciona a outra.*
