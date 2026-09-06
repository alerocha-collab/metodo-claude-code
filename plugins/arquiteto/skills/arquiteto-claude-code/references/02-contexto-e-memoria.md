# Referência 02 — Contexto e memória

Fonte: *Effective context engineering for AI agents*; docs `memory`, `best-practices`, `features-overview`.

---

## 1. A restrição que gera todas as regras

**A janela enche rápido e o desempenho degrada conforme ela enche.** Quando cheia, o modelo "esquece" instruções anteriores e erra mais.

**Context rot** tem base arquitetural: a atenção do transformer cria `n²` relações par-a-par para `n` tokens; conforme o contexto cresce, a atenção se dilui. Modelos treinados em distribuições que favorecem sequências curtas têm menos parâmetros especializados em dependência de longo alcance. O resultado é **gradiente, não penhasco**: precisão degradada na recuperação e no raciocínio longo.

**Consequência de projeto:** trate contexto como orçamento de atenção finito, com retorno marginal decrescente. Busque **o menor conjunto de tokens de alto sinal** que maximiza a chance do resultado desejado.

## 2. Altitude do prompt de sistema

Zona entre dois extremos: prompt complexo demais codifica lógica condicional frágil; prompt vago demais não guia e assume falsamente entendimento compartilhado.

- Estruture em seções com tags XML ou headers Markdown.
- Busque *"o conjunto mínimo de informação que descreve completamente o comportamento esperado."*
- **Comece mínimo em um modelo capaz** e adicione instrução com base em falha observada — não antecipadamente.
- Concreto o bastante para guiar, flexível o bastante para servir de heurística.

## 3. Estratégias de recuperação

**Just-in-time** — o agente mantém identificadores leves (caminhos, queries, links) e carrega dados em runtime via ferramentas. Espelha a cognição humana: *"não memorizamos corpora inteiros, introduzimos sistemas externos de organização e indexação."*

Benefícios: eficiência de armazenamento; progressive disclosure; **metadados como sinal** (hierarquia de pastas, convenção de nomes, timestamps guiam comportamento); janela autogerida.

Custo: exploração em runtime é mais lenta que recuperação pré-computada e exige *"engenharia opinada e cuidadosa"* para evitar que o agente desperdice contexto usando ferramentas errado e perseguindo becos sem saída.

**Híbrido** — recuperar dados críticos antecipadamente e manter capacidade de exploração autônoma. O Claude Code é o exemplo: READMEs carregam no início, `grep`/`glob` navegam sob demanda, *"contornando problemas de índice desatualizado e árvores sintáticas complexas."* Contextos menos dinâmicos (jurídico, financeiro) toleram mais pré-recuperação.

## 4. CLAUDE.md — decisões de projeto

**Hierarquia e ordem de carga** (todos concatenados, não sobrescritos; da raiz do filesystem até o diretório de trabalho — o mais próximo é lido por último):

| Escopo | Localização |
|---|---|
| Managed policy (não excluível) | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md` · Linux/WSL `/etc/claude-code/CLAUDE.md` · Windows `C:\Program Files\ClaudeCode\CLAUDE.md` |
| User | `~/.claude/CLAUDE.md` |
| Project | `./CLAUDE.md` ou `./.claude/CLAUDE.md` |
| Local (gitignore) | `./CLAUDE.local.md` |

Arquivos em subdiretórios **abaixo** do cwd não carregam no lançamento — entram quando o Claude lê arquivos daqueles diretórios.

**Alvo: < 200 linhas.** O Claude Code carrega até 4 MiB inteiro e pula acima disso, mas arquivos curtos produzem aderência melhor.

**Teste de cada linha:** *"remover isso faria o Claude errar?"* Se não, corte.

| Incluir | Excluir |
|---|---|
| Comandos que o Claude não adivinha | O que ele descobre lendo o código |
| Estilo que diverge do padrão | Convenção padrão da linguagem |
| Instruções de teste e test runner | Documentação de API (linkar) |
| Etiqueta do repo (branches, PRs) | Informação que muda muito |
| Decisões arquiteturais do projeto | Explicação longa, tutorial |
| Peculiaridades de ambiente | Descrição arquivo-por-arquivo |
| Pegadinhas e comportamento não óbvio | "Escreva código limpo" |

**Especificidade:** "Use indentação de 2 espaços" > "formate adequadamente". "Rode `npm test` antes de commitar" > "teste suas mudanças". "Handlers ficam em `src/api/handlers/`" > "mantenha organizado".

**Ênfase seletiva:** IMPORTANT em **uma** linha só. Se muitas linhas são enfatizadas, nenhuma se destaca.

**Diagnóstico:** regra ignorada → arquivo longo demais. Pergunta cuja resposta está no arquivo → redação ambígua. Verifique a carga com `/context` (seção **Memory files**); `/doctor` propõe cortes automáticos.

**Imports `@path`:** expandem no lançamento; caminho relativo resolve relativo ao arquivo que importa; máximo 4 saltos; crases impedem a importação. **Importar não reduz contexto.**

**`AGENTS.md`:** o Claude Code lê `CLAUDE.md`. Se o repo já usa `AGENTS.md`, crie um `CLAUDE.md` com `@AGENTS.md` na primeira linha e o conteúdo específico abaixo.

**Monorepo:** `claudeMdExcludes` (globs contra caminhos absolutos) em `.claude/settings.local.json`. Managed policy não pode ser excluído.

## 5. `.claude/rules/` — o mecanismo subusado

```
.claude/
├── CLAUDE.md
└── rules/
    ├── code-style.md
    ├── testing.md
    └── frontend/components.md   # descoberta recursiva
```

Sem `paths:` carrega no lançamento com a mesma prioridade de `.claude/CLAUDE.md`. Com `paths:` só entra em contexto quando o Claude toca arquivos correspondentes:

```markdown
---
paths:
  - "src/api/**/*.{ts,tsx}"
---
```

Brace expansion com orçamento de 1.000 padrões expandidos e 4 MiB por regra. Suporta symlinks — permite manter um conjunto compartilhado e linkar em vários projetos. Regras de usuário (`~/.claude/rules/`) carregam antes das de projeto, dando prioridade maior às de projeto.

**Regra de projeto:** prefira rules com `paths:` a CLAUDE.md aninhado quando a restrição é específica de tipo de arquivo e aparece em vários diretórios.

## 6. Auto memory

Quatro tipos, no campo `type` do frontmatter: `user` (papel, expertise, preferências), `feedback` (correções e abordagens confirmadas), `project` (trabalho em andamento, prazos, decisões não deriváveis do código), `reference` (onde achar informação externa).

**Não salva** o que é derivável do codebase (arquitetura, caminhos, correções de bug) nem o que o CLAUDE.md já diz.

Estrutura: `~/.claude/projects/<project>/memory/` com `MEMORY.md` (índice, uma linha por memória) + um arquivo por tópico. `<project>` deriva do repositório git — worktrees compartilham o mesmo diretório.

**Limite:** primeiras **200 linhas ou 25KB** do `MEMORY.md`, o que vier primeiro. Além disso é descartado. Arquivos de tópico não carregam no startup — são lidos sob demanda.

Local à máquina; não sincroniza entre máquinas nem para a nuvem; excluída da varredura de retenção. Desligue com `autoMemoryEnabled: false` ou `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

**A auto memory da conversa principal não entra em subagentes** (exceto forks). Subagentes têm memória própria, via campo `memory`.

## 7. Técnicas de horizonte longo — escolha pela tarefa

| Técnica | Mecânica | Use quando |
|---|---|---|
| **Compaction** | Resume o conteúdo perto do limite e reinicializa | Idas e vindas conversacionais |
| **Context reset** | Limpa a janela inteira e recomeça com handoff estruturado | O modelo perde coerência ou entra em "ansiedade de contexto" (ver ref. 01 sobre obsolescência) |
| **Note-taking estruturado** | Memória persistente em disco (`NOTES.md`, to-dos, JSON de features) trazida de volta sob demanda | Desenvolvimento iterativo longo; dependências ao longo de dezenas de chamadas |
| **Subagentes** | Janelas limpas para exploração; coordenador mantém o plano | Exploração paralela |

**Implementação da compaction:** maximize *recall* primeiro (capture tudo relevante), depois itere para melhorar *precisão*. Limpar resultados de chamadas de ferramenta é a otimização mais óbvia. Risco: compaction agressiva demais elimina contexto sutil mas crítico.

**O que sobrevive à compaction:** o `CLAUDE.md` da raiz é relido do disco e reinjetado; CLAUDE.md aninhados e rules com `paths:` recarregam conforme arquivos correspondentes são lidos. **Instrução dada só na conversa não sobrevive.**

## 8. Controles de sessão

`/clear` entre tarefas não relacionadas · `/compact <instruções>` para compaction dirigida · `Esc` interrompe preservando contexto · `Esc+Esc` / `/rewind` restaura conversa, código ou ambos · `/btw` para pergunta lateral cuja resposta não entra no histórico · `/rename` para tratar sessões como branches.

**A regra das duas correções:** corrigiu o Claude mais de duas vezes sobre o mesmo assunto? O contexto está poluído com abordagens falhas. `/clear` e recomece com prompt melhor. *"Uma sessão limpa com um prompt melhor quase sempre supera uma sessão longa com correções acumuladas."*

**Checkpoints só rastreiam mudanças feitas pelas ferramentas de edição** — mudanças via Bash ou processo externo não são capturadas. Não substitui git.
