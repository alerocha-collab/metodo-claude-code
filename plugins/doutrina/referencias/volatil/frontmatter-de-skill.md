# Frontmatter de skill — campos aceitos

> **FICHA VOLÁTIL.** Isto é cópia de um schema, e schema muda entre versões.
>
> url: https://code.claude.com/docs/en/skills.md
> Verificado em 2026-09-06.
>
> Antes de confiar num campo que você nunca usou, rode
> `python3 plugins/doutrina/scripts/verificar_fontes.py --drift`. Se a página `skills`
> aparecer como mudada, esta tabela pode estar velha — e um campo que não existe mais
> faz a skill carregar **sem metadados**, o que não gera erro visível.

Nenhum campo é obrigatório. `name` vem do diretório quando omitido; `description` cai
no primeiro parágrafo do corpo.

## Identidade e acionamento

| Campo | O que faz |
|---|---|
| `name` | Nome exibido nas listagens. Padrão: o nome do diretório |
| `description` | O que a skill faz e quando usá-la. É por aqui que o Claude decide invocar. **Ponha o caso de uso principal primeiro**: o texto combinado com `when_to_use` é truncado na listagem |
| `when_to_use` | Contexto adicional de acionamento — frases-gatilho, exemplos de pedido. Anexado à `description` e conta no mesmo teto |
| `paths` | Globs que limitam quando a skill é ativada automaticamente. Mesmo formato das rules com escopo de caminho |
| `disable-model-invocation` | `true` impede o Claude de carregar sozinho. Use para workflow que você dispara à mão. **Também impede o pré-carregamento em subagentes** |
| `user-invocable` | `false` esconde do menu `/` e faz `/nome` não funcionar; o Claude ainda pode invocar. Para conhecimento de fundo |

## Argumentos

| Campo | O que faz |
|---|---|
| `argument-hint` | Dica mostrada no autocomplete, tipo `[numero-da-issue]` |
| `arguments` | Argumentos posicionais nomeados, para substituição por `$nome` no corpo. String separada por espaço ou lista YAML; os nomes mapeiam para as posições na ordem |

## Ferramentas e modelo

| Campo | O que faz |
|---|---|
| `allowed-tools` | Ferramentas que o Claude pode usar sem pedir permissão **no turno que invocou a skill**. A concessão **acaba na sua próxima mensagem** |
| `disallowed-tools` | Ferramentas removidas do conjunto disponível enquanto a skill está ativa. A restrição também acaba na próxima mensagem |
| `model` | Modelo a usar enquanto a skill está ativa. Vale pelo resto do turno e **não é salvo**. Aceita `inherit` |
| `effort` | Nível de esforço enquanto ativa. Sobrepõe o da sessão |

## Execução isolada

| Campo | O que faz |
|---|---|
| `context` | `fork` roda num subagente com contexto próprio |
| `agent` | Qual tipo de subagente usar, quando `context: fork` |
| `background` | Só vale com `context: fork`. `false` espera o resultado no mesmo turno em vez de rodar em segundo plano *(campo com versão mínima; confira na fonte)* |

> ⚠️ `context: fork` **só faz sentido para skill com instrução explícita**. Uma skill que
> só traz diretrizes — "use estas convenções de API" — sem uma tarefa entrega ao
> subagente as diretrizes e nenhum comando, e ele volta sem produzir nada.

## Ciclo de vida e metadados

| Campo | O que faz |
|---|---|
| `hooks` | Hooks registrados quando a skill é invocada, que seguem valendo pelo resto da sessão |
| `shell` | Shell para os comandos injetados no corpo. `bash` (padrão) ou `powershell` |
| `metadata` | Mapa livre para dados seus. O Claude Code não age sobre o conteúdo, e descarta valor que não seja mapa |
| `license` | Licença da skill. Aceito, sem efeito |
| `compatibility` | Requisitos de ambiente, como string. Aceito, sem efeito |

## Substituições no corpo

| Marcador | Vira |
|---|---|
| `$ARGUMENTS` | Todos os argumentos passados |
| `$ARGUMENTS[N]` / `$N` | O argumento na posição N, contando de zero |
| `$nome` | O argumento nomeado declarado em `arguments` |
| `${CLAUDE_SKILL_DIR}` | O diretório do `SKILL.md`. Em plugin, o subdiretório da skill — **não** a raiz do plugin |
| `${CLAUDE_PROJECT_DIR}` | A raiz do projeto |
| `${CLAUDE_PLUGIN_ROOT}` | O diretório de instalação do plugin. Só em skill de plugin |
| `${CLAUDE_PLUGIN_DATA}` | Diretório persistente do plugin, que sobrevive a atualização |
| `${CLAUDE_SESSION_ID}` | O id da sessão |
| `${CLAUDE_EFFORT}` | O nível de esforço atual |

## Armadilhas de escrita

- **O `---` de abertura tem que ser a primeira linha do arquivo.** Se não for, o
  frontmatter não é lido.
- **YAML malformado não gera erro visível**: o corpo carrega com metadados vazios,
  então `/nome` funciona e a escolha automática nunca acontece. `claude plugin validate`
  sobre o diretório de skills encontra isso.
- **Comando injetado que sai com código diferente de zero aborta a skill inteira**, não
  só aquele trecho. Anexe `|| true` ao que você espera que possa falhar.
- **`allowed-tools` vale um turno.** Para a sessão inteira, use regra de permissão.

---

*Transcrição da tabela de frontmatter e da tabela de substituições, condensadas na
coluna de descrição. Campos que a fonte marca com versão mínima estão anotados sem o
número — o número vive na fonte, porque é o que envelhece mais rápido.*
