---
name: distribuir
description: Empacota e escopa configuração — quando converter `.claude/` em plugin, e como escopar o Claude num monorepo ou base de código grande para ele não carregar instrução de subsistema que a tarefa não toca. Use ao compartilhar configuração entre projetos, ou ao configurar um repositório grande.
---

# Empacotar e escopar

Duas perguntas diferentes que a mesma ficha responde: **como levo isto para outro
lugar** e **como impeço que tudo carregue de uma vez**.

## Standalone ou plugin

O critério mais limpo de toda a documentação:

| | `.claude/` standalone | Plugin |
|---|---|---|
| Skill se chama | `/nome` | `/plugin:nome` |
| Serve para | workflow pessoal, ajuste do projeto, experimento | compartilhar, distribuir, versionar, reusar entre projetos |

> *"Comece com configuração standalone em `.claude/` para iterar rápido, e converta
> para plugin quando estiver pronto para compartilhar."*

O gatilho de conversão é objetivo: **um segundo repositório precisa do mesmo setup.**
Antes disso, plugin é cerimônia — e cerimônia cedo é o que faz alguém abandonar a
prática inteira.

Duas consequências da conversão que surpreendem:

- Skills de plugin são **namespaced**, então a versão local e a de plugin **coexistem**;
  nenhuma sobrescreve a outra.
- Subagentes **não** coexistem: uma definição local com o mesmo nome substitui a do
  plugin, e o plugin só passa a valer quando a local sai.

## O erro de estrutura que a doc chama de comum

Dentro de `.claude-plugin/` vai **só** o `plugin.json`. Todo o resto — `skills/`,
`agents/`, `hooks/`, `.mcp.json` — fica na **raiz do plugin**.

E a raiz do plugin é o diretório do próprio plugin, nunca `~/.claude/`.

Hooks também mudam de lugar na conversão: em standalone eles vivem no `settings.json`;
num plugin, em `hooks/hooks.json`.

## Escopar um repositório grande

O problema: um `CLAUDE.md` único na raiz cresce até cobrir as convenções de todo
subsistema, e aí custa contexto em instrução que a tarefa atual não toca — ou fica
genérico demais para servir.

Cinco mecanismos, do mais simples ao mais estrutural:

**1. Onde você inicia a sessão.** Iniciar de dentro do pacote já carrega o `CLAUDE.md`
de lá e o da raiz, e **não** o dos pacotes irmãos. É a alavanca mais barata, e não exige
configuração nenhuma.

**2. `CLAUDE.md` em camadas.** Raiz para o que vale em todo lugar; um por
pacote ou subsistema para as convenções daquela área. O de subdiretório carrega sob
demanda, quando o Claude lê um arquivo ali.

**3. Rules com `paths:`.** Quando a convenção segue o *tipo* de arquivo e não a pasta —
migrações espalhadas, testes em qualquer lugar. Custa contexto só quando um arquivo
correspondente entra.

**4. Skills por diretório.** Procedimentos daquela área, carregados só quando relevante.
É onde um procedimento de operação específico de um pacote deve morar.

**5. Bloquear leitura do que é gerado.** Regras de `deny` sobre `dist/`, `build/`,
código gerado e dependências versionadas. Custo zero e evita que uma busca traga lixo.

### A armadilha que quebra configuração em monorepo

> **`settings.json` de projeto carrega apenas do diretório de onde você iniciou, e
> não é herdado de diretórios pai** — ao contrário do `CLAUDE.md`, que é.

Ou seja: um `.claude/settings.json` na raiz **não vale** quando você inicia a sessão de
dentro de um pacote. Permissões, hooks e configuração precisam existir onde a sessão
começa, ou vir de um escopo que não dependa disso.

É a diferença de comportamento entre dois arquivos vizinhos, e ela não é sinalizada
onde dói.

### Trabalho que atravessa pacotes

Iniciar dentro de um pacote restringe o acesso a ele. Para alcançar um irmão, é preciso
conceder explicitamente — e há duas formas, com um detalhe que decide qual usar:
uma delas concede **só acesso a arquivo**, sem carregar `CLAUDE.md`, rules nem skills
daquele diretório; a outra carrega as skills.

E o conselho de processo que vale mais que a configuração: **entregue a mudança inteira
numa sessão só**. Editar o tipo compartilhado e depois os chamadores em sessões
separadas faz cada uma redecidir o que a anterior já tinha decidido.

## Quando as camadas param de escalar

Sinal: as convenções derivam, os arquivos ficam velhos, e ninguém é dono da raiz.

A saída é mover conteúdo de referência para fora do que carrega sempre — para skills, e
depois para um plugin que uma equipe versiona num lugar só. É a mesma progressão de
antes, agora por governança em vez de por reuso.

---

*Síntese autoral a partir de `plugins`, `plugins-reference`, `large-codebases`,
`plugin-marketplaces`, `memory` e `claude-directory`. A armadilha do `settings.json`
não herdado foi medida em sessão real, não só lida.*
