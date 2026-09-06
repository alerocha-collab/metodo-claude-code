# 003 — Exercitar o portão numa sessão real e registrar o resultado

## Problema

As 32 verificações provam o **contrato dos scripts**: exit 2 bloqueia, exit 0 libera.
Não provam que o Claude Code de fato recusa encerrar o turno quando o hook devolve 2,
nem que `${CLAUDE_PLUGIN_ROOT}` resolve dentro do `hooks:` do frontmatter de agente —
que a doc não cobre.

Enquanto isso não for exercitado, o portão é uma hipótese bem testada, não um
mecanismo verificado.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O portão nunca rodou dentro de uma sessão | Está registrado, com evidência, que ele barra — ou que não barra |
| Não se sabe se a variável resolve no frontmatter | Está registrado qual dos dois caminhos vale |

## Critérios de aceitação

- [ ] Uma sessão carrega o plugin e entra no papel `construtor`
- [ ] Com a suíte deliberadamente quebrada, encerrar o turno é **barrado**, e a
      mensagem do portão aparece
- [ ] Com a suíte verde, o turno encerra normalmente — o portão não bloqueia sempre
- [ ] Editar um teste existente é **negado**, com a mensagem do hook
- [ ] Criar um teste novo é **permitido**
- [ ] O resultado entra no `DECISIONS.md`: se a variável resolveu, fecha P8 e P9; se
      não, registra a migração para `hooks/hooks.json` com cláusula de guarda, e o
      motivo
- [ ] **Negativo:** se o portão não barrar, isso é registrado como falha e vira ticket
      de correção — não é arredondado para "funcionou"

## Fora de escopo

- Automatizar este teste: exigiria dirigir uma sessão interativa, e custa mais que o
  valor
- macOS e Linux; fica registrado que só o Windows foi coberto

## Verificação

A evidência é a saída da própria sessão, colada no `DECISIONS.md`. O texto do bloqueio
basta e é conferível.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
