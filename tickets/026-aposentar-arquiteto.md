# 026 — Aposentar a `arquiteto-claude-code`, sem perder nada

## Problema

Com 023, 024 e 025 feitos, a skill vira duplicata de verdade — mas só **depois** deles.
Aposentá-la exige provar que nada morreu no caminho.

Ela tem sete referências e ~50 seções. Três já tinham par no `doutrina` (`contexto`,
`onde-colocar`, `garantir`), duas migram nos tickets anteriores, uma é lista de fontes
que vira `fontes.json`, e uma — o **template do entregável** — não é conhecimento: é a
forma de um artefato, irmã do `ticket.md` e do `DECISIONS.md`. Essa fica no `metodo`.

## Critérios de aceitação

- [ ] `07-template-entregavel` vira `plugins/metodo/templates/arquitetura.md`, e o
      `metodo` passa a distribuí-lo como distribui os outros artefatos
- [ ] **Inventário de migração escrito**: toda seção das sete referências mapeada para
      destino — migrada para onde, já coberta por qual ficha, ou **descartada com
      motivo**. Nada sai por omissão
- [ ] `plugins/metodo/skills/arquiteto-claude-code/` removida
- [ ] `tests/testar_orcamento.py` mede o novo total, e o número entra no README —
      medido, não estimado
- [ ] README dos dois plugins atualizado: o `metodo` deixa de anunciar a skill, o
      `doutrina` anuncia as duas novas
- [ ] `version` sobe nos **dois** plugins, nos dois lugares cada
- [ ] **Negativo:** a suíte continua verde sem a skill. Se algum teste dependia dela,
      isso aparece agora

## Fora de escopo

- Fazer o `metodo` chamar o `doutrina`. O debate concluiu o contrário: a camada de
  processo não carrega cópia da de conhecimento, e quem instala só o `metodo` fica sem
  doutrina **por escolha declarada**, não por dependência escondida

## Verificação

Instalar o `doutrina` num repositório limpo e fazer as perguntas de arquitetura que antes
só a skill do `metodo` respondia. Se não responder, a migração não terminou.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
