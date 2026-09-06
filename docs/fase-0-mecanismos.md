# Fase 0 — mecanismos existentes, e o que eles decidem

> Levantamento feito em 2026-09-05 sobre a doc oficial do Claude Code, para não
> reimplementar no plugin o que a plataforma já entrega. Registrado aqui porque a
> conversa que o produziu não sobrevive à sessão.
>
> Só entra o que **muda uma decisão de arquitetura**. Onde a doc não cobre, está
> escrito "não documentado" — lacuna é informação, e preenchê-la com plausibilidade
> foi o erro que quase cometemos com a P7.

---

## 1. Verificação e garantia

### `/goal` não serve para o `Stop` de verificação

A hipótese do plano era reusar `/goal`, descrito como *"um wrapper em torno de um
Stop hook prompt-based com escopo de sessão"*. **Confirmado** — e confirmada também
a limitação que o inviabiliza aqui: o avaliador roda a cada turno num modelo pequeno
(Haiku por padrão) e **julga apenas o transcript**. Não executa comandos, não lê
arquivos.

Para a condição "a suíte passou", isso significaria confiar no que o agente
*relatou* ter rodado — que é precisamente o "parece pronto" que o hook existe para
eliminar. A doutrina é explícita: sem verificação executável, "parece pronto" é o
único sinal disponível, e é o sinal errado.

**Consequência.** O hook universal da Fase 2 é `type: "command"`, executando a suíte.
`/goal` permanece útil para condição demonstrável pela saída do próprio turno — não
para verificação.

Condição do `/goal`: até 4.000 caracteres. Três vereditos: não atendida (continua),
atendida (limpa), impossível (falha). Se não houver progresso por vários turnos, o
loop é interrompido. Fonte: [goal](https://code.claude.com/docs/en/goal.md).

### O `Stop` hook precisa tratar a própria recursão

- Teto de **8 bloqueios consecutivos sem progresso**, após o qual o Claude Code
  **sobrescreve o hook**. Configurável por `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.
- O hook recebe `stop_hook_active` no JSON de stdin — é assim que ele detecta que já
  está em loop.
- Bloqueio por exit code 2, ou por JSON estruturado em stdout.
- `Stop` dispara ao fim de um turno do Claude; `SubagentStop`, ao fim de um subagente.
- Tipos: `command` (shell), `prompt` (avaliação LLM de um turno) e `agent`
  (multi-turno com tools, **experimental**).

**Consequência.** Um hook que ignora `stop_hook_active` se desliga sozinho no oitavo
bloqueio, em silêncio. O desenho precisa contemplar isso desde a primeira versão.

Fonte: [hooks-guide](https://code.claude.com/docs/en/hooks-guide.md).

### Checkpointing não é rede de segurança para esta metodologia

Rastreia snapshots de arquivos antes de cada prompt, restauráveis por `/rewind`.
**Não cobre:** mudanças feitas por comandos Bash (`rm`, `mv`, `cp`), edições de
subagentes em background, symlinks e hard links, e qualquer efeito remoto.

**Consequência.** Como a metodologia commita por fatia e opera por scripts, a rede é
**git**, não `/rewind`. Não desenhar nada contando com checkpoint.

Fonte: [checkpointing](https://code.claude.com/docs/en/checkpointing.md).

### `/doctor` já entrega a verificação nº 4 do plano

Audita custo de contexto de skills, MCP servers e plugins, identifica os não usados e
sinaliza hooks lentos. É literalmente o *"orçamento de contexto medido, não
estimado"* do plano — não precisa ser construído.

Não é validador estrutural; para isso, `claude plugin validate --strict`.

**Proveniência mais fraca:** parte desta descrição não veio de página da doc.
Tratar como provável até confirmar na prática.

---

## 2. Orquestração e contexto

### `context: fork` resolve a restrição de corpo enxuto do `/fluxo`

O plano impôs ao `/fluxo` a restrição *"corpo enxuto — o corpo de uma skill permanece
em contexto pelo resto da sessão; um manual de 300 linhas é custo recorrente"*.

`context: fork` no frontmatter da skill despacha um subagente isolado que **recebe só
o corpo da skill como prompt** — não o histórico, não o `CLAUDE.md`, não o git
status. A sessão principal recebe de volta apenas o resultado. Com
`background: false`, espera o retorno e usa o conjunto completo de ferramentas.

**Consequência.** O `/fluxo` pode ter corpo grande sem custo recorrente na sessão,
desde que seja autossuficiente — e ele é, porque lê estado de disco por construção
(decisão nº 3), não do histórico. É um encaixe direto, não uma adaptação.

Ressalva: mudanças feitas dentro do fork não entram nos checkpoints da sessão
principal. Consistente com o achado sobre checkpointing.

Fonte: [skills](https://code.claude.com/docs/en/skills.md).

### Workflows podem ser distribuídos por plugin

Scripts JavaScript que orquestram subagentes deterministicamente — até 1.000 por
execução, 16 simultâneos —, com os resultados intermediários vivendo em variáveis do
script, **fora da janela de contexto**. Um plugin os distribui em `workflows/` na
raiz, namespaced como `/<plugin>:<workflow>`.

**Consequência.** A revisão em dois eixos (Standards e Spec, em subagentes paralelos
que não poluem o contexto um do outro) é candidata natural a workflow em vez de
skill. Decidir na Fase 3, não agora.

Fonte: [workflows](https://code.claude.com/docs/en/workflows.md).

### `/batch` já implementa o paralelismo por worktree

Decompõe em 5–30 unidades, pede aprovação, despacha subagentes em background — cada
um em **worktree isolado**, abrindo um PR. Exige repositório git.

**Consequência.** É o mecanismo da doutrina de propriedade coletiva mecanizada
(worktrees isolados + arestas de bloqueio). Não construir equivalente.

Fonte: [commands](https://code.claude.com/docs/en/commands.md).

### Duas lacunas que fecham portas de design

- **Statusline distribuída por plugin: não documentado.** A ideia de exibir o próximo
  ticket na statusline não tem respaldo. A statusline em si roda local, sem custo de
  token, e pode exibir branch, contexto, custo e afins — mas configurá-la é trabalho
  de máquina, não de plugin. Não desenhar `/fluxo` contando com ela.
- **Scheduled tasks distribuídas por plugin: não documentado.** Escopo de sessão,
  expiram em 7 dias, rodam só com o Claude Code ativo e ocioso. Para durabilidade
  entre sessões a doc aponta Routines, Desktop tasks ou GitHub Actions.

Fontes: [statusline](https://code.claude.com/docs/en/statusline.md),
[scheduled-tasks](https://code.claude.com/docs/en/scheduled-tasks.md).

---

## O que a Fase 0 muda no plano

| Item do plano | Estado depois do levantamento |
|---|---|
| `Stop` de verificação reusando `/goal` | **Descartado.** Avaliador não executa nada. Vai ser `type: "command"` |
| `/fluxo` com corpo enxuto | **Reformulado.** `context: fork` paga o corpo fora da sessão; a restrição afrouxa |
| Verificação nº 4 (orçamento de contexto medido) | **Já existe:** `/doctor` |
| Paralelismo por worktree | **Já existe:** `/batch`. Não construir |
| Revisão em dois eixos | Candidata a **workflow** de plugin, não a skill. Decidir na Fase 3 |
| Estado do projeto na statusline | **Sem respaldo.** Não documentado para plugin |
| `/rewind` como rede de segurança | **Não serve.** Não cobre Bash nem subagente. A rede é git |
