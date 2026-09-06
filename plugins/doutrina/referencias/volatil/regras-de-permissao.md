# Sintaxe das regras de permissão

> **FICHA VOLÁTIL.** A lista de ferramentas cresce, e o comportamento de casamento de
> caminho já mudou entre versões.
>
> url: https://code.claude.com/docs/en/tools-reference.md
> Verificado em 2026-09-06. Complementada por
> https://code.claude.com/docs/en/permissions.md
>
> Esta é a camada de **garantia dura** — o que ela permite ou nega não depende de o
> modelo cooperar. Errar aqui é o tipo de erro que só aparece depois.

## Como uma regra é avaliada

`deny` → `ask` → `allow`, e **a primeira que casa vence**. Uma negação não é
sobreponível por permissão em escopo mais forte: ela é consultada primeiro.

## O formato, por ferramenta

| Formato | Vale para | Casa por |
|---|---|---|
| `Bash(npm run *)` | Bash, Monitor | padrão de comando |
| `PowerShell(Get-ChildItem *)` | PowerShell | padrão de comando |
| `Read(~/secrets/**)` | Read, Grep, Glob, LSP | padrão de caminho |
| `Edit(/src/**)` | Edit, Write, NotebookEdit | padrão de caminho |
| `Skill(deploy *)` | Skill | nome de skill |
| `Agent(Explore)` | Agent | tipo de subagente |
| `WebFetch(domain:exemplo.com)` | WebFetch | domínio |
| `WebSearch` | WebSearch | sem especificador — permite ou nega a ferramenta inteira |

## As duas assimetrias que economizam regras

Elas não são simétricas, e é isso que as torna úteis:

- **Permitir `Edit` num caminho concede leitura dele automaticamente.** Você não
  precisa das duas regras.
- **Negar `Read` num caminho também bloqueia edição e escrita ali.** Negar leitura é a
  regra mais forte disponível, e costuma ser a única necessária.

## Casamento de caminho

Um padrão de segmento único, como `Edit(src/**)`, casa `src` **no diretório de
trabalho**, não em qualquer profundidade. Para qualquer profundidade, use `**/src/**`.

*(Esse comportamento mudou entre versões — se o repositório é antigo e a regra parece
larga demais, é aqui que olhar.)*

## Onde as permissões são configuradas

Seis lugares, e vale conhecer todos porque a pergunta "por que isto foi permitido?"
depende de saber onde procurar:

1. `permissions.allow` / `ask` / `deny` nos arquivos de settings
2. Flags de linha de comando de ferramentas permitidas e negadas
3. Opções equivalentes no Agent SDK
4. Frontmatter de subagente — `tools` e `disallowedTools`
5. Frontmatter de skill — `allowed-tools`, que **vale só um turno**
6. A condição `if` de um hook — que é **best-effort**, não garantia

## O que exige permissão e o que não

Exigem, entre outras: `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`,
`WebSearch`, `Skill`, `Workflow`, `Artifact`, `EnterWorktree`, `Monitor`.

Não exigem, entre outras: `Read`, `Grep`, `Glob`, `Agent`, `AskUserQuestion`,
`TodoWrite`, `ToolSearch`, `SendMessage`, `TaskList`.

> Note que **`Skill` exige permissão** e **`Agent` não**. É contraintuitivo e importa ao
> desenhar uma skill que invoca outras.

## Sandbox é outra camada

Regras de permissão controlam o que **o agente** faz. Sandbox isola o que **o processo**
faz — filesystem e rede, no nível do sistema operacional.

A distinção importa quando o agente roda código de terceiros: uma suíte de testes
executa `package.json`, plugins de configuração e fixtures, e **nada disso herda as
permissões do Claude Code**. Restringir as ferramentas do agente não restringe o
processo que ele iniciou.

## Uma nota sobre fadiga

Aprovação repetida do mesmo comando é o que treina alguém a aprovar sem ler — e aí a
camada de permissão vira teatro. Uma allowlist estreita para o que se repete, e prompt
para o resto, protege mais do que negar tudo e aprovar sempre.

---

*Transcrição da tabela de formatos e da lista de permissão por ferramenta, condensadas.
A lista completa das ferramentas com descrição fica na fonte — ela cresce, e é
consultável no lugar.*
