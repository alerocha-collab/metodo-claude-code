---
name: onde-colocar
description: Decide onde uma instrução, um conhecimento ou uma automação deve morar — CLAUDE.md, rule, skill, subagente, hook, permission ou MCP — e com que autoridade ela vale. Use ao desenhar a configuração de um projeto, ou quando o Claude estiver ignorando uma regra.
---

# Onde colocar uma instrução

A pergunta tem **quatro eixos**, e a documentação oficial tabela três deles em páginas
diferentes. O quarto — **autoridade** — não é tabelado em lugar nenhum: aparece como
prosa solta em quatro páginas, e numa delas com outro nome (`Determinism`), dentro de
uma comparação entre dois mecanismos apenas.

Este arquivo existe por causa desse quarto eixo.

| Eixo | A pergunta |
|---|---|
| **Onde** | Em que arquivo isto vive? |
| **Quando** | Carrega sempre, sob demanda, ou por caminho? |
| **Quanto** | O que custa em contexto? |
| **Autoridade** | É pedido, ou é garantia? |

## A árvore, e por que ela começa pela autoridade

A primeira pergunta é a que elimina mais casos, e **não é sobre formato**.

**1. Isto precisa valer sempre, mesmo que o modelo discorde ou não leia?**
→ **Sim:** `permissions.deny` (garantia dura) ou hook (garantia condicional). **Pare
aqui.** Escrever no `CLAUDE.md` uma regra que precisa valer sempre não é uma escolha
mais leve — é a escolha errada, e ela falha em silêncio.

> *"An instruction like 'never edit `.env`' in CLAUDE.md or a skill is a request, not
> a guarantee. A `PreToolUse` hook that blocks the edit is enforcement."*

**2. Existe um script que decide "violou / não violou" com exit code?**
→ **Não:** volte à etapa 1 e assuma que é pedido, ou construa o verificador primeiro.
Rebaixar uma garantia a pedido e chamar de solução é o erro caro. Sem predicado
executável você não tem regra, tem intenção.

**3. É conhecimento que o Claude deriva lendo o código?**
→ **Não escreva.** É a linha que mais engorda `CLAUDE.md` sem mudar comportamento.

**4. Vale em toda sessão deste repositório?** → `CLAUDE.md` do projeto.

**5. Vale só para certos arquivos?** → `.claude/rules/` com `paths:`. Custa contexto
só quando um arquivo correspondente entra em cena.

**6. É procedimento de vários passos, ou material de referência?** → skill.
Se tiver efeito colateral — deploy, commit, publicação —, `disable-model-invocation: true`.

**7. Precisa de dado ou ação de fora?** → MCP, e uma skill que ensina a usá-lo bem.

**8. Vai inundar o contexto principal?** → subagente. Se for além de um punhado de
agentes, workflow.

## Os três níveis de autoridade

A doc trata isto como binário — advisory versus enforced. **São três**, e confundir os
dois últimos é o que produz o portão que parece existir e não existe.

| Nível | Mecanismos | O que pode falhar |
|---|---|---|
| **Pedido** | `CLAUDE.md`, `.claude/rules/`, skills, output styles | O modelo lê e decide. Pode ignorar, e a chance cresce conforme o contexto enche |
| **Garantia condicional** | hooks | Dispara sempre no evento — mas pode dar timeout, sair com código que não bloqueia, ou **não rodar em pasta não confiada**. O filtro `if` é declaradamente best-effort |
| **Garantia dura** | `permissions` (`deny` → `ask` → `allow`, primeira regra vence), sandbox de SO | Aplicado pelo cliente antes de o modelo agir. Independe de o hook rodar |

**A consequência prática:** para "isto nunca pode acontecer", `permissions.deny` é a
resposta, não hook. Hook é para "isto tem que acontecer" e para lógica que uma regra
de permissão não expressa.

## Onde está o resto

Este corpo fica curto de propósito — ele entra em contexto e não sai. O detalhe está
em arquivos que carregam sob demanda:

- **A matriz completa**, uma linha por mecanismo com os quatro eixos:
  [referencias/duravel/matriz.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/matriz.md)
- **Precedência quando o mesmo nome existe em dois escopos** — e elas **não são
  uniformes**: [referencias/duravel/precedencias.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/precedencias.md)
- **O que sobrevive ao `/compact`**, e o que a tabela oficial omite:
  [referencias/duravel/compaction.md](${CLAUDE_PLUGIN_ROOT}/referencias/duravel/compaction.md)
- **As armadilhas** — onde a documentação se contradiz, e onde o comportamento
  surpreende: [referencias/armadilhas.md](${CLAUDE_PLUGIN_ROOT}/referencias/armadilhas.md)

## Quando o Claude ignora uma regra

Diagnóstico em ordem de probabilidade, não de sofisticação:

1. **O arquivo é grande demais.** *"Bloated CLAUDE.md files cause Claude to ignore
   your actual instructions."* Pode a regra estar se perdendo no ruído.
2. **A regra é um pedido e devia ser garantia.** Volte à etapa 1 da árvore.
3. **Ela não está carregada.** Rule com `paths:` só carrega quando um arquivo
   correspondente entra; nested `CLAUDE.md` idem — e **nenhum dos dois é reinjetado
   após compaction**.
4. **Há conflito de escopo**, e a precedência não é a que você supôs. Veja
   `precedencias.md` antes de concluir que é bug.
5. **Você enfatizou muitas linhas.** *"If you emphasize many lines, none of them
   stands out."*

---

*Síntese autoral a partir de `features-overview`, `claude-directory`, `context-window`,
`memory`, `best-practices`, `hooks` e `permissions`. O eixo de autoridade em três
níveis e a ordem da árvore são construção nossa — a doc tem as propriedades, não a
síntese.*
