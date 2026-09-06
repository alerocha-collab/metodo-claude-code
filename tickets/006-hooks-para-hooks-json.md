# 006 — Mover os hooks para `hooks/hooks.json`, com cláusula de guarda

## Problema

Os dois hooks do papel `construtor` estão declarados no `hooks:` do frontmatter do
agente e **nunca são executados**. A doc é explícita: *"Lifecycle hooks scoped to this
subagent. **Ignored for plugin subagents**"*. O agente vem de um plugin, então o bloco
é lido e descartado.

O ticket 003 mediu a consequência numa sessão real: turno encerrou com a suíte
vermelha, e edição em teste existente passou sem mensagem. **O portão inteiro está
inerte** — e nada nas 45 verificações detecta isso, porque elas testam os scripts, não
a fiação.

Enquanto isso não for corrigido, o `construtor` tem regras escritas e nenhuma garantia.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Hooks no frontmatter, ignorados em silêncio | Hooks em `plugins/metodo/hooks/hooks.json`, que é o local documentado |
| Se ligados, valeriam para toda sessão | Cláusula de guarda: a regra do papel só se aplica ao papel |
| A inércia não é detectável | Existe uma forma de saber que os hooks estão ligados |

## Critérios de aceitação

- [ ] Os hooks são declarados em `plugins/metodo/hooks/hooks.json`, e o bloco `hooks:`
      sai do frontmatter dos agentes — deixá-lo lá seria documentação falsa
- [ ] `${CLAUDE_PLUGIN_ROOT}` resolve nos comandos, verificado numa sessão real
- [ ] Numa sessão do papel `construtor`, com a suíte vermelha, **o turno é barrado**
- [ ] Numa sessão do papel `construtor`, editar um teste existente é **negado**
- [ ] O `verificar_suite` **não** barra uma sessão do papel `operador` por conta de
      suíte vermelha que não foi ele quem quebrou — é a regra de operação sendo
      barrada por regra de construção, o inverso exato do sintoma que motivou separar
      papéis
- [ ] A cláusula de guarda determina o papel a partir do que o hook recebe. **Descobrir
      empiricamente quais campos chegam** numa sessão `--agent` de plugin, e registrar
      os campos observados no `DECISIONS.md` — a doc não cobre
- [ ] Quando o papel **não puder** ser determinado, o comportamento é declarado por
      escrito e é fail-closed para o portão: na dúvida, verifica
- [ ] **Negativo:** o `proteger_testes` continua valendo em qualquer papel. Ninguém
      deve editar teste existente em silêncio, e restringi-lo ao construtor seria
      reduzir cobertura sem ganho

## Fora de escopo

- Reescrever os scripts. Eles foram exercitados com o evento real e respondem certo;
  o defeito é de fiação
- Um hook que verifique se os hooks estão ligados. Tentador e circular — se a fiação
  falha, ele falha junto
- macOS e Linux

## Verificação

A suíte cobre os scripts. A fiação se verifica pelo roteiro
[docs/exercitar-portao.md](../docs/exercitar-portao.md), refeito depois da mudança —
e é ele que decide esta fatia, não a suíte.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
