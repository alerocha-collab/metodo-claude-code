# metodo — metodologia de engenharia com agentes, como plugin

Repositório que carrega a metodologia entre projetos. O que vive aqui são as skills,
os agentes e os hooks que codificam nove decisões de método já fechadas — não código
de aplicação.

**Estado:** o pipeline está completo — seis skills, dois papéis, e o portão de
verificação exercitado numa sessão real. Falta o prefixo de reengenharia, para partir
de um repositório que já existe.

## Verificação

```bash
python3 tests/testar_tudo.py
```

Doze suítes, 177 casos, todas com **conjunto balanceado**: metade verifica que a trava
age quando deve, metade que ela **não** age quando não deve. Uma suíte só com casos
positivos aprova uma trava que bloqueia tudo.

O runner é *fail-closed*: nenhuma suíte encontrada conta como **falha**. Sem isso,
apagar os testes deixaria o runner verde — e o portão passaria a aprovar um
repositório sem verificação nenhuma.

Este repositório usa o próprio portão que distribui: `.claude/metodo.json` aponta
para o runner.

## O que o plugin instala num projeto

| Artefato | Onde | Para quê |
|---|---|---|
| `metodo.json` | `.claude/` | Declara o comando que decide verde/vermelho. Sem ele, o portão bloqueia. **Copie o template — o formato não é adivinhável** |
| `fila.json` | `tickets/` | Estado dos tickets e o grafo de bloqueio. JSON porque muda toda sessão |
| `ticket.md` | `tickets/NNN-*.md` | A spec de uma fatia. Markdown porque é prosa escrita uma vez |
| `DECISIONS.md` | raiz | Decisões append-only, abaixo da barra de um ADR |
| `settings.exemplo.json` | `.claude/settings.json` | A camada de **garantia dura**. Copie e adapte — o plugin não instala sozinho |

### A camada de permissões

As skills e os agentes são **pedido**: o modelo lê e decide. Os hooks são garantia
**condicional**: disparam sempre, mas dão timeout e saem com código que não bloqueia.
`permissions` é a única camada **dura** — aplicada pelo cliente antes de o modelo agir.

> Este README já afirmou que hooks *"não rodam em pasta não confiada"*. **Estava
> errado**, e a doc é explícita sobre por quê: a confiança de workspace barra o que
> **concede** — `permissions.allow` e `additionalDirectories` —, não o que executa.
> `deny` e `ask` valem sempre, *since they only restrict*. **Hooks rodam antes de você
> confiar em qualquer coisa**, venham de settings, de skill de projeto ou de plugin. Se
> a preocupação é código de terceiro rodando na sua máquina, a defesa é `--bare`,
> `--setting-sources user` ou `disableAllHooks`, não confiança. Ver armadilha nº 15.

O plugin **não** a instala sozinho, de propósito: regra de permissão que aparece sem
alguém ter escolhido é a forma mais rápida de perder a confiança de quem instalou.
Copie `templates/settings.exemplo.json`, adapte, e **apague as chaves que começam com
`$`** — elas são comentário, e `settings.json` não aceita comentário de verdade.

Valide a fila com:

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

## Estrutura

```
.
├── docs/                        doutrina e decisões que fundamentam a metodologia
├── .claude-plugin/
│   └── marketplace.json         anuncia os dois plugins para instalação
└── plugins/
    ├── doutrina/                a documentação do Claude Code destilada
    │   ├── skills/              as seis fichas, por pergunta
    │   ├── referencias/         durável × volátil, carregado sob demanda
    │   └── fontes.json          210 fontes indexadas, com hash
    └── metodo/                  a metodologia propriamente dita
        ├── agents/              papéis: construtor, operador, arquiteto
        ├── skills/              as do pipeline, mais o onboarding
        ├── hooks/               hooks.json + os dois hooks do portão
        ├── scripts/             fila, estado, transição de ticket
        └── templates/           artefatos que o plugin instala em projetos
```

Os plugins ficam em `plugins/<nome>/`, não na raiz, para que
`.claude-plugin/marketplace.json` — que existe, na raiz — os anuncie com
`"source": "./plugins/<nome>"` sem nada precisar se mover.

## Requisitos

**`python3` 3.8 ou mais novo, no PATH.** Os hooks e os scripts do plugin são Python.

A escolha é deliberada: a doc do Claude Code diz que hooks rodam em `sh` no
macOS/Linux, em Git Bash no Windows, ou em PowerShell quando Git Bash não está
instalado. Um script `.sh` não cobriria os três; Python cobre.

**Se `python3` faltar, o portão de verificação bloqueia** — não libera. Sem tratamento
ele falharia aberto, porque o shell sai com 127 e a doc classifica 127 como não
bloqueante; por isso o comando no `hooks/hooks.json` termina em `|| exit 2`. A
mensagem que aparece é a do shell, `python3: command not found`, que nomeia o que
falta.

**Risco residual:** `|| exit 2` é sintaxe POSIX. No caso restrito de Windows **sem**
Git Bash, onde os hooks rodam em PowerShell, a rede não vale e a ausência de `python3`
volta a poder falhar aberta. Não há contorno portátil conhecido; registrado aqui em
vez de escondido.

## Instalar

Os dois plugins são anunciados por `.claude-plugin/marketplace.json`, na raiz deste
repositório. No projeto onde você quer usá-los:

```bash
claude plugin marketplace add alerocha-collab/metodo-claude-code --scope project
```

```bash
claude plugin install doutrina@metodo-claude-code --scope project
```

`--scope project` grava em `.claude/settings.json` do projeto, versionado com ele, em vez
de na configuração do seu usuário. Troque `doutrina` por `metodo` para o outro. Os dois
são independentes: nenhum depende do outro.

> ⚠️ **O preço do escopo de projeto:** `extraKnownMarketplaces` vindo do repositório
> **não carrega até a pasta ser confiada**. Quem clonar o projeto não recebe os plugins
> antes de aceitar o diálogo — inclusive em `-p`, onde ele nunca aparece. Se você quer os
> plugins disponíveis sem esse passo, instale com `--scope user`, ao custo de eles não
> virem versionados com o repositório.

### O passo que quase todo mundo esquece

As skills do `doutrina` são curtas de propósito e carregam o detalhe sob demanda, de
arquivos empacotados no plugin. **Esses arquivos ficam fora do diretório de trabalho da
sessão** — no cache de plugins, ou na pasta de origem. Sem acesso a eles a skill dispara,
roteia certo, nomeia o arquivo e **não entrega**.

Onde ficam depende de como você instalou: fonte remota vai para
`~/.claude/plugins/cache/<marketplace>/<plugin>/<versão>/`; fonte `directory` (caminho
local) resolve para a **pasta de origem**. Confira com `claude plugin list`.

O que funciona de imediato, por sessão:

```bash
claude --add-dir ~/.claude/plugins/cache
```

O permanente são **duas coisas, e as duas são necessárias**. Primeiro, a regra no
`.claude/settings.json` do projeto:

```json
{ "permissions": { "additionalDirectories": ["~/.claude/plugins/cache"] } }
```

Segundo, **aceitar o diálogo de confiança** — rode `claude` interativamente na pasta uma
vez. `additionalDirectories` concede capacidade, e é exatamente essa classe de regra que
a confiança segura. Sem ela a regra acima é **ignorada**, e a mensagem diz isso:
*"Ignoring 1 permissions.additionalDirectories entry from `.claude/settings.json`: this
workspace has not been trusted."*

Medido nos dois estados, mesmo repositório e mesmo `settings.json`, trocando só a
confiança: **não confiado**, a skill roteia e nomeia o arquivo mas não o abre;
**confiado**, ela lê e cita o caminho.

> ⚠️ Em clone novo, sessão headless ou CI o diálogo nunca aconteceu — lá o único caminho
> é `--add-dir`.

O sintoma sem nada disso engana: a skill **dispara**, roteia certo, nomeia o arquivo — e
não entrega. Parece skill mal escrita, e é fronteira de diretório. Registrado como
armadilha nº 14 em `plugins/doutrina/referencias/armadilhas.md`.

## Usar em desenvolvimento

Sem instalar, isolado por sessão — aponta para a pasta local e **não exercita nada do
caminho de instalação**:

```bash
claude --plugin-dir ./plugins/metodo
```

`/reload-plugins` recarrega sem reiniciar. Para validar antes de publicar:

```bash
claude plugin validate ./plugins/metodo --strict
```

E o manifesto do marketplace, validado a partir da raiz:

```bash
claude plugin validate . --strict
```

`--strict` não é opcional aqui: `version` divergente entre a entrada do marketplace e o
`plugin.json` é **aviso**, não erro. E no install o `plugin.json` vence em silêncio — quem
sobe só a entrada acha que publicou, e o cache continua servindo a versão antiga.

## As skills

| Skill | Para quê |
|---|---|
| `/metodo:decidir` | Fecha decisões em aberto, em rodadas, antes de construir |
| `/metodo:dominio` | Constrói e afia o vocabulário do projeto |
| `/metodo:fatiar` | Transforma trabalho descrito em fila de tickets |
| `/metodo:implementar` | Conduz uma fatia do ticket ao commit |
| `/metodo:revisar` | Revisa em dois eixos, Standards e Spec, em contextos separados |
| `/metodo:fluxo` | Diz onde o projeto está e qual é o próximo passo |

E o prefixo de reengenharia, para partir de um repositório que já existe. As três
rodam em ordem, e depois a trilha converge com a de projeto novo:

| Skill | Para quê |
|---|---|
| `/metodo:onboarding-entender` | Levanta o mapa: como roda, como verifica, fronteiras, e o que ficou sem entender |
| `/metodo:onboarding-modelar` | Extrai o vocabulário do código e registra as divergências |
| `/metodo:onboarding-lacunas` | Mede a distância até o alvo e a transforma em fila |

## Namespacing

Tudo que o plugin distribui carrega o prefixo `metodo:`. Skills se invocam como
`/metodo:arquiteto-claude-code`; agentes aparecem no typeahead como
`metodo:arquiteto`.

### A assimetria que pega quem instala

**Skills de plugin coexistem com as locais.** Elas são namespaced, então
`/metodo:fatiar` e um `/fatiar` seu vivem lado a lado; nenhuma sobrescreve a outra.

**Agentes de plugin, não.** Uma definição em `.claude/agents/` do projeto, ou em
`~/.claude/agents/`, **sobrepõe silenciosamente** a do plugin com o mesmo nome — e o
plugin só volta a valer quando a local sai. Se você já tem um `construtor`, um
`operador` ou um `arquiteto` locais, é a sua versão que roda, e nada avisa.

As duas regras estão documentadas, em páginas diferentes, e nenhuma menciona a outra.
Se o agente do plugin parecer não ter carregado, procure um homônimo local antes de
procurar bug.

### Custo de contexto

As descrições das skills carregam em **todo request** — hoje ~4.500 caracteres,
~1.100 tokens, somando `metodo` e `doutrina`. `tests/testar_orcamento.py` mantém isso
sob teto: passar dele exige podar uma descrição ou registrar uma decisão para subir o
teto, e não subir em silêncio.

O motivo não é só espaço. Quando a listagem estoura o orçamento, as descrições são
**encurtadas** — e o que se perde são as palavras-chave que fazem a skill disparar.

## Publicar

**Todo release exige bump de `version` no `plugin.json`** — sem isso, quem já instalou
continua com a cópia em cache. E o bump é em **dois lugares**: `plugin.json` e a entrada
correspondente no `marketplace.json`. `tests/testar_marketplace.py` reprova se os dois
divergirem, porque o validador oficial só avisa.

**Isso é mecanismo, não disciplina.** `scripts/verificar_bump.py` roda no CI e reprova
quando conteúdo de plugin mudou e `version` não:

```bash
python3 scripts/verificar_bump.py HEAD~1
```

As duas metades fecham o problema: `testar_marketplace.py` pega **subir errado**, este
pega **esquecer de subir**. Mexer só em `README.md`, em `tests/` ou no CI não exige
bump — se exigisse, todo commit de manutenção viraria release.

O que segue humano é a **magnitude**: o detector compara commits, não julga se
`0.1.0 → 0.2.0` era o salto certo.

## Documentos

| Arquivo | O que é |
|---|---|
| [docs/plano-metodologia.md](docs/plano-metodologia.md) | O plano que este repositório executa, fase a fase |
| [docs/fase-0-mecanismos.md](docs/fase-0-mecanismos.md) | O que a plataforma já entrega, e o que isso muda no plano |
| [docs/decisoes-metodologia.md](docs/decisoes-metodologia.md) | As nove decisões de método, com alternativas e modos de falha |
| [docs/analise-cruzada-metodologias.md](docs/analise-cruzada-metodologias.md) | XP × engenharia clássica × set do Matt Pocock × doutrina Anthropic |
| [docs/melhores-praticas-anthropic-claude-code.md](docs/melhores-praticas-anthropic-claude-code.md) | Doutrina Anthropic consolidada |
| [DECISIONS.md](DECISIONS.md) | Decisões sobre **este** repositório, append-only |
