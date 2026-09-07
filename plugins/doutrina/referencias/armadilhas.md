# Armadilhas: onde a documentação se contradiz, e onde o comportamento surpreende

> Levantado em 2026-09-06, lendo as páginas lado a lado. Cada item traz **as duas
> versões e onde cada uma aparece**, para quem for conferir não concluir que esta ficha
> está errada.
>
> Isto não é crítica à documentação — é o custo normal de doutrina escrita por páginas,
> cada uma correta no próprio escopo. A contradição só aparece na costura, e ninguém
> lê a costura.

---

## Contradições dentro da doc

### 1. A precedência de skills inverte a de rules

- `features-overview` — skills: `managed > user > project`.
- `memory` — *"User-level rules are loaded before project rules, giving project rules
  higher priority."*
- `claude-directory`, sobre `~/.claude/CLAUDE.md` — *"When instructions conflict,
  project-level instructions take priority."*

Para **instruções** o projeto ganha do usuário. Para **skills** o usuário ganha do
projeto. As duas regras estão certas; **nenhuma das páginas menciona a outra**.

**Consequência:** uma skill pessoal com o mesmo nome de uma do projeto silenciosamente
substitui a do projeto — inclusive num repositório de equipe, onde a expectativa é a
oposta.

### 2. O índice de skills não sobrevive à compaction, e a tabela omite

A tabela "What survives compaction" de `context-window` não tem linha para o índice de
descrições. O simulador **da mesma página** marca essa linha como não sobrevivente, e o
texto ao lado confirma que só as skills invocadas são preservadas.

Quem consulta só a tabela conclui que o índice persiste. Não persiste.

### 3. O limite do `CLAUDE.md` é declarado de três formas

- `features-overview`: *"Keep CLAUDE.md under 200 lines"* — imperativo.
- `memory`: *"target under 200 lines"* — alvo, mais um teto duro em que o arquivo é
  **pulado inteiro**.
- `best-practices`: nenhum número, só *"keep it short"*.

Três autoridades para a mesma regra. A que muda comportamento é a terceira: o arquivo
grande demais não é truncado, é **ignorado**.

### 4. A tabela de custo de contexto mistura eixos

A coluna "Context cost" de `features-overview` traz `Every request` para `CLAUDE.md` e
`Low` / `Zero` / `Isolated` para o resto. "Every request" responde **frequência**, não
custo. A tabela não é comparável coluna a coluna.

### 5. Compaction: a versão simplificada induz falsa confiança

`how-claude-code-works` diz que instruções antigas podem se perder e que a solução é
pôr regras persistentes no `CLAUDE.md` — sem qualificar. As outras duas páginas
detalham que **`CLAUDE.md` aninhado e rules com `paths:` não são reinjetados**.

Quem lê só a página simplificada acredita que "põe no CLAUDE.md" resolve, e num
monorepo isso é falso justamente para o arquivo do pacote em que se está trabalhando.

---

## Comportamentos que surpreendem

### 6. `hooks:` no frontmatter é **ignorado** para agentes de plugin

A tabela de frontmatter de `sub-agents` diz, na própria linha do campo: *"Ignored for
plugin subagents."* A mesma página, num parágrafo acima, afirma que hooks de frontmatter
disparam também quando o agente roda como sessão principal. As duas coisas convivem: a
exceção da tabela é mais específica e prevalece.

**Achado nosso, medido em sessão real:** o bloco é lido e descartado **em silêncio**.
Nada avisa. O portão inteiro fica inerte enquanto os testes dos scripts passam, porque
eles testam os scripts e não a fiação.

Quem distribui hooks por plugin precisa de `hooks/hooks.json`, com o escopo por papel
virando cláusula de guarda dentro do script.

### 7. `exit 1` não bloqueia. `127` também não

Só o **exit 2** bloqueia por código. Qualquer outro é tratado como erro não bloqueante e
**a ação prossegue** — mesmo sendo 1, que é o código convencional de falha no Unix.

Duas consequências que mordem:
- Um hook em qualquer linguagem que morra com traceback sai com 1 e **libera**. Se ele
  é um portão, precisa capturar toda exceção e sair com 2.
- Interpretador ausente faz o shell sair com **127**, e o portão libera exatamente na
  máquina mal configurada. `|| exit 2` no comando fecha isso.

### 8. Texto puro de hook só chega ao Claude em quatro eventos

`UserPromptSubmit`, `UserPromptExpansion`, `SessionStart` e `PostModelSwitch`. Nos
demais, stdout em texto puro vai **só para o log de depuração** — o Claude nunca vê.

É a maior classe de bug de hook: o script imprime a explicação, ninguém recebe, e
parece que o hook não rodou. Para falar com o modelo nos outros eventos, use os campos
estruturados de saída.

### 9. `/agents` não é `claude agents`

Um é comando de sessão; o outro é a tela de sessões em background. A própria doc
sinaliza a semelhança como problema. O primeiro hoje só imprime um aviso.

### 10. Habilitar agent teams reescreve o comportamento de subagentes

Com teams ligado, **um subagente nomeado passa a ser criado como teammate**. A doc é
explícita: *"teams can form even when you didn't ask for one."* O mesmo arquivo de
agente, o mesmo prompt, comportamento diferente — e a variável de ambiente que muda
isso está a uma sessão de distância.

### 11. Skills em subagentes são pré-carregadas, não sob demanda

No contexto principal, o corpo da skill carrega quando é usada. Num subagente, as
skills listadas em `skills:` entram **inteiras no lançamento**. Uma skill grande listada
num subagente custa contexto toda vez que ele roda, mesmo que não seja usada.

### 12. O `if` de hook é declaradamente best-effort

*"Use the permission system for hard enforcement."* Ele não consegue decidir com certeza
o que um comando com variável expandida vai executar e, na dúvida, **roda o hook assim
mesmo**. Como filtro de desempenho serve; como fronteira de segurança, não.

### 13. Os agentes Explore e Plan não carregam `CLAUDE.md`

Os built-ins pulam `CLAUDE.md` e git status para ter contexto menor. Um subagente
Explore não conhece as convenções do projeto — e vai relatar como se conhecesse.

### 14. Os arquivos de referência de um plugin ficam FORA do diretório de trabalho

A progressive disclosure de uma skill de plugin depende de o agente **ler** um arquivo
empacotado. Enquanto tudo roda dentro do repositório que produziu o plugin, isso parece
funcionar. Instalado, o plugin mora em outro lugar — no cache
(`~/.claude/plugins/cache/<marketplace>/<plugin>/<versão>/`) ou, para fonte do tipo
`directory`, na pasta de origem. Nos dois casos, **fora dos diretórios de trabalho da
sessão**.

Duas consequências medidas ao instalar num repositório limpo:

- **Link relativo (`](../../referencias/x.md)`) não dá base para resolver.** O agente
  precisa adivinhar a raiz do plugin. Use `${CLAUDE_PLUGIN_ROOT}/referencias/x.md`, que
  a plataforma substitui e que vale nos dois modos, `--plugin-dir` e instalado.
- **O caminho certo ainda pode ser barrado.** A recusa não é regra de permissão, é a
  fronteira de diretório de trabalho: *"Claude Code may only list files in the allowed
  working directories for this session"*. Em sessão não interativa (`-p`) isso não vira
  prompt: falha e pronto. `allowed-tools: Read(${CLAUDE_PLUGIN_ROOT}/**)` na skill
  **não** derrubou a barreira no teste; `--add-dir` derrubou.
- **E o conserto permanente tem uma condição escondida.** `additionalDirectories` no
  `settings.json` do projeto é **ignorado enquanto o workspace não é confiado**, e a
  mensagem é literal: *"Ignoring 1 permissions.additionalDirectories entry from
  .claude/settings.json: this workspace has not been trusted."* A confiança vem do
  diálogo interativo — que num clone novo, numa sessão headless ou em CI **nunca
  aconteceu**. A configuração versionada que deveria resolver o problema é justamente a
  que não vale onde o problema aparece.

### O conserto, medido nos dois estados

Mesmo repositório, mesmo `settings.json`, mesma pergunta. A única variável trocada foi
`hasTrustDialogAccepted`:

| Confiança | O que aconteceu |
|---|---|
| **Não aceita** | A skill disparou, roteou e **nomeou o arquivo certo** — e não conseguiu abri-lo |
| **Aceita** | Leu o arquivo e citou o caminho absoluto na resposta |

Então a receita é: `permissions.additionalDirectories` apontando para a raiz do plugin,
**mais** o diálogo de confiança aceito uma vez. Onde não há como aceitar diálogo — CI,
headless, `-p` num clone novo — só `--add-dir` resolve.

O diagnóstico rápido: se a linha *"Ignoring N permissions.additionalDirectories
entries"* aparece, o problema é confiança, não a regra.

### 15. A confiança de workspace barra o que CONCEDE, não o que executa

O erro intuitivo é achar que pasta não confiada é pasta inerte. Não é. A regra real é
mais estreita e mais útil:

> *"`permissions.allow` rules and `permissions.additionalDirectories` entries in a
> project's `.claude/settings.json` **grant capability**, so Claude Code applies them
> only after you accept the workspace trust dialog. `deny` and `ask` rules aren't
> affected, **since they only restrict**."*

Ou seja: **confiança é um portão sobre concessão.** Restrição vale sempre — o que protege
não espera permissão para proteger.

O que isso implica, e contradiz a leitura rápida:

| Conteúdo do repositório | Vale sem confiança? |
|---|---|
| Hooks em settings, `env`, `apiKeyHelper` | **Sim** |
| Hooks e `allowed-tools` de skill de projeto | **Sim** — `allowed-tools` nunca é barrado por confiança, em sessão nenhuma |
| Hooks de plugin instalado | **Sim** (medido) |
| `deny` e `ask` | **Sim** |
| `permissions.allow` e `additionalDirectories` | **Não** |
| Hooks no frontmatter de **subagente** de projeto | **Não** — e nenhum diálogo é oferecido |
| `extraKnownMarketplaces` vindo do repositório | **Não** |
| `mcpServers` inline no frontmatter de subagente | **Não** |

**Três consequências que pegam:**

1. **Um `hooks.json` roda antes de você confiar em nada.** Se a preocupação for código de
   terceiro executando na sua máquina, confiança **não** é a defesa — `--bare`,
   `--setting-sources user` ou `--settings '{"disableAllHooks": true}'` são.
2. **Hook de subagente e hook de settings se comportam de formas opostas.** O de subagente
   fica parado, e *sem diálogo oferecido* — não há o que aceitar.
3. **`extraKnownMarketplaces` no `.claude/settings.json` de um repositório não carrega
   antes da confiança.** Quem clona um repositório que declara um marketplace de projeto
   não recebe o plugin até confiar na pasta.

**Onde a confiança mora:** é chaveada na **raiz do repositório git**, não na pasta onde
você abriu. Fora de repositório, na pasta de início. Na home, vale só para a sessão e não
é escrita em disco.

**`claude -p` nunca mostra o diálogo**, e confiar na pasta-pai não conta para estas
regras. Para conceder à mão: `projects["<raiz>"].hasTrustDialogAccepted: true` em
`~/.claude.json`.

O sintoma engana: a skill dispara, roteia certo, nomeia o arquivo — e não entrega. Parece
skill mal escrita, e é fronteira de diretório.

---

### 16. Você não vê o seu próprio hook falhar

> *"Stderr from a hook that exits 0 goes to the debug log only, never the transcript,
> and Claude never sees it."*

Falha **não bloqueante** — exit 1, exit 127, qualquer código que não seja 2 — mostra a
primeira linha do stderr **ao usuário**, no transcript da interface. O modelo não recebe
nada.

**Exit 2 é o único código que devolve o stderr ao modelo.** É por isso que a doc
recomenda `exit 2` quando um `PostToolUse` quer avisar o Claude de algo, mesmo com a
ferramenta já executada: sem isso, o aviso não chega em quem deveria agir.

A consequência prática, medida em sessão real: **um agente não consegue diagnosticar os
próprios hooks.** Ele pode passar uma sessão inteira com o portão desligado, ver os cinco
hooks falharem na tela do usuário, e escrever com sinceridade que o portão funciona.

Corolário para quem escreve procedimento: **"não apareceu erro" não é evidência de
nada.** Se importa saber que um hook rodou, o procedimento tem que **provar** que rodou —
executando o comando, ou observando o efeito colateral dele.

### 17. No Windows não existe caminho de hook que funcione nos dois shells

O Claude Code roda hooks em Git Bash quando ele está instalado, e em PowerShell/cmd
quando não está. **Quem decide é a máquina, não você** — e o mesmo repositório troca de
shell quando alguém instala o Git.

Medido nas quatro combinações:

| Comando declarado | Git Bash | cmd / PowerShell |
|---|---|---|
| `.claude\hooks\x.cmd` | **quebra** — o bash come as contrabarras e sobra `.claudehooksx.cmd` | funciona |
| `.claude/hooks/x.cmd` | funciona | **quebra** — `'.claude' não é reconhecido` |
| `cmd /c "...\x.cmd"` | **quebra** — o MSYS traduz `/c` em `C:\` e abre um cmd interativo | funciona |
| `cmd //c "...\x.cmd"` | funciona (`//` escapa a tradução) | **quebra** |

**Nenhuma linha funciona nas duas colunas.** E como a falha é não bloqueante (armadilha
16), ela é invisível para o agente e quase invisível para a pessoa.

**O que funciona:** invocar um interpretador que aceite barra normal como argumento —
`python3 .claude/hooks/x.py`. `python3` resolve como comando nos dois shells, e o Python
normaliza o caminho no Windows. É o mesmo motivo pelo qual hook em Python cobre os três
shells que a doc lista, e `.sh` não cobre.

**A troca:** um wrapper `.cmd` bem feito resolve coisas que `python3` puro não resolve —
achar o venv, preferir o launcher `py -3`, conferir a versão mínima, e eliminar o alias
da Microsoft Store que se passa por `python.exe` e abre a loja em vez de executar.
Trocá-lo por `python3` joga essa proteção fora. Decida com o custo na mesa, e registre.

---

## Como usar esta lista

Ela não substitui a documentação; ela diz **onde não confiar na leitura rápida**. Antes
de concluir que algo é bug, confira se está aqui. E antes de confiar num
comportamento que esta ficha afirma, confira a data no topo — a doc muda toda semana, e
`verificar_fontes.py --drift` diz quais páginas mudaram desde que isto foi escrito.

---

*Fontes: `features-overview`, `memory`, `context-window`, `claude-directory`,
`how-claude-code-works`, `sub-agents`, `agents`, `agent-teams`, `hooks`, `hooks-guide`,
`skills`, `best-practices`. Os itens 6, 7, 14, 16 e 17 foram medidos em sessão real, não só lidos — o 16 e o 17
num projeto de terceiro, cujos cinco hooks estavam inertes sem ninguém saber. O 15 corrige uma
afirmação que estava errada na nossa própria documentação — ver DECISIONS 020.*
