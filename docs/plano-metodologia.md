# Plano — Construir a metodologia como plugin, e reconciliar o FirstAxiom com ela

## Contexto

Ao longo desta sessão consolidamos a doutrina da Anthropic, cruzamos com XP, engenharia clássica e o set de skills do Matt Pocock, e fechamos **nove decisões de metodologia**. O passo seguinte é materializá-las.

O objetivo declarado: um conjunto próprio de skills que codifique as melhores práticas para **todo projeto novo**, e que sirva também para **reconciliar o FirstAxiom** — já codificado — com esse desenho.

**Achado que reenquadra a segunda metade.** A exploração do FirstAxiom mostrou um projeto muito mais maduro do que o pressuposto. Ele já tem `CLAUDE.md`, `CONTEXT.md` com glossário canônico, 4 ADRs, `docs/agents/*` (o `setup-matt-pocock-skills` já rodou), dois subagentes no padrão gerador/avaliador (`apurador-dossie` → gate → `revisor-dossie`), hooks ligados a validadores, **139 regras como JSON com severidade**, test runner *fail-closed* (suíte ausente = falha) e fixtures negativas que devem reprovar. Seu princípio declarado — *"geração é probabilística, aceitação é determinística"* — é a doutrina do loop de verificação formulada de forma independente.

Consequência: **a reconciliação é bidirecional.** Impor o set novo por cima destruiria mecanismos superiores aos do set de referência. O FirstAxiom é, em parte, fonte da metodologia — não só destino dela.

**Resultado pretendido:** um repositório versionado, instalável como plugin, que carregue a metodologia entre projetos; e um caminho de reconciliação do FirstAxiom que não jogue fora o que ele já resolveu melhor.

## Decisões que este plano executa

| # | Decisão fechada |
|---|---|
| 1 | Fase = spec · ticket = fatia dimensionada por janela · **sessão = um ticket + commit** |
| 2 | Separação por **papel** (não por ambiente); barreira dura em `permissions.deny` |
| 3 | Estado estruturado + git durante; documento de arquitetura carimbado com SHA no fim; hook **detecta, nunca atualiza** |
| 4 | Spec dimensionada pela autonomia; **o ticket é a spec** (resolvida por consequência da nº 1) |
| 5 | Prefactor antes · nunca durante · achado de revisão vira **ticket automático** |
| 6 | Agente redige os critérios, você valida; **entram antes da implementação e não são editados durante** |
| 7 | Entrevistar por gatilho, não por regra |
| 8 | Hooks em três escopos: universal no `settings.json` · papel no agente · fluxo na skill |
| 9 | Sem registro de risco de projeto, conscientemente |

**Restrição de ambiente registrada:** sandbox não roda em Windows nativo (só macOS, Linux, WSL2). A barreira dura disponível hoje é `permissions.deny`. Risco residual aceito.

## Arquitetura da metodologia

Repositório próprio, versionado, instalável como plugin:

```
metodologia/                          ← repo git próprio
├── .claude-plugin/plugin.json
├── skills/
│   ├── fluxo/SKILL.md                ← orquestrador: lê estado, diz o próximo passo
│   ├── onboarding-entender/          ← prefixo de reengenharia (1 de 3)
│   ├── onboarding-modelar/           ← prefixo (2 de 3)
│   ├── onboarding-lacunas/           ← prefixo (3 de 3)
│   └── <core adaptado do Matt>/
├── agents/
│   ├── construtor.md
│   ├── operador.md
│   └── arquiteto.md                  ← já existe em ~/.claude, migra para cá
├── hooks/                            ← scripts referenciados pelos settings do projeto
└── templates/
    ├── DECISIONS.md
    └── settings.exemplo.json
```

### O orquestrador `/fluxo` — lê estado, não decora sequência

O problema relatado ("não lembrava qual skill chamar") **não é de memória, é de estado**. Qual skill vem a seguir é determinado por onde o projeto está, e esse estado já existe em disco pela decisão nº 3.

`/fluxo` é um `git status` da metodologia: lê tickets + git + presença de artefatos, reporta onde o projeto está, recomenda o próximo passo — **e sabe recomendar pular** quando o trabalho é pequeno demais para o rito completo.

Três restrições de projeto, derivadas dos riscos identificados:

- **Roteia, não executa.** Se reimplementar o que as outras skills fazem, vira ponto único de doutrina e duplicação.
- **Corpo enxuto.** O corpo de uma skill permanece em contexto pelo resto da sessão; um manual de 300 linhas é custo recorrente.
- **Relata verde/vermelho; não garante.** A garantia é hook — `/goal` para a sessão, `Stop` hook nas settings para valer sempre.

**Reuso a explorar antes de escrever:** `/goal` é literalmente *"um wrapper em torno de um Stop hook prompt-based com escopo de sessão"*, com avaliador em modelo separado. Limitação que restringe o desenho: **o avaliador não roda comandos nem lê arquivos** — julga só o que apareceu no transcript. A condição precisa ser demonstrável pela saída.

### O prefixo de reengenharia — três skills, não um modo

As trilhas divergem apenas no início e depois **convergem por completo**:

| Etapa | Projeto novo | Reengenharia |
|---|---|---|
| Entender o que existe | — | `onboarding-entender` |
| Modelo de domínio | `domain-modeling` pela conversa | `onboarding-modelar` (extrai do código) → `domain-modeling` normal |
| Diferença vs. alvo | — | `onboarding-lacunas` |
| Daí em diante | `grilling` → spec → tickets → implementa → revisa | **idêntico** |

Descartadas: ramificar por modo dentro de cada skill (complexidade paga em contexto sempre) e set paralelo (divergiria em meses).

**TDD não precisa de modo:** a diferença mora **no ticket**. Ticket de reengenharia diz "escreva o teste de caracterização do comportamento atual, depois altere". A skill `tdd` fica intocada.

**Formato da saída do prefixo, com respaldo no retrofitting do XP:** não tentar conformidade total numa passada. Beck é explícito — não pare o desenvolvimento para testar todo o código antigo; aplique testes sob demanda (ao corrigir bug, ao adicionar feature, ao refatorar) e vá mordendo as metas grandes incrementalmente. Logo `onboarding-lacunas` entrega **o mapa + os tickets do caminho crítico + a regra de que o resto entra quando a área for tocada** — nunca um relatório.

### O que absorver do FirstAxiom

Mecanismos que o projeto resolveu melhor que o set de referência e que devem subir para a metodologia:

| Mecanismo | Onde vive hoje | Por que absorver |
|---|---|---|
| **Regras como JSON com severidade** | `docs/regras/*.json` (139) | Governança verificável por script, não por leitura. JSON resiste à reescrita pelo modelo |
| **Runner fail-closed** | `scripts/testar_tudo.py` | Suíte ausente conta como falha — fecha o buraco do "passou porque não rodou" |
| **Fixtures negativas** | `fixtures/quebrados/` | Conjunto balanceado: testa quando *deve* e quando *não deve* passar. É a doutrina de evals aplicada |
| **Gerador/avaliador já em produção** | `.claude/agents/apurador-dossie.md`, `revisor-dossie.md` | Padrão validado no campo, com gate entre os dois |
| **Artefato imutável endereçado por hash** | `scripts/publicar_arte.py`, `registrar_aprovacao.py` | O carimbo de aprovação aponta para o hash do que foi julgado |

## Fases

**Fase 0 — Exaurir a doutrina que falta.** Não cobrimos: plugins e marketplace (é o que faz a metodologia viajar), dynamic workflows, `/batch`, scheduled tasks, `context: fork` em skill, statusline, `/doctor`, checkpointing. Ler antes de escrever skill, para não reimplementar o que já existe.

**Fase 1 — Esqueleto do repositório + plugin.** Estrutura acima, `plugin.json`, e migração do `arquiteto` de `~/.claude` para o repo.

**Fase 2 — `/fluxo` e os agentes.** O orquestrador que lê estado; `construtor` e `operador` com hooks no frontmatter; o `Stop` de verificação como primeiro e único hook universal.

**Fase 3 — Core adaptado.** As skills de fluxo, derivadas do set do Matt com as nove decisões aplicadas — sobretudo a nº 5 (achado vira ticket automático) e a nº 6 (critérios antes, não editados durante).

**Fase 4 — Prefixo de reengenharia.** As três skills de onboarding.

**Fase 5 — Reconciliação do FirstAxiom.** Rodar o prefixo no projeto real. É o primeiro caso de teste, e o mais exigente.

## Lacunas do FirstAxiom já identificadas

Entram como insumo da Fase 5, não como escopo deste plano:

1. **Congelamento de evidência ausente.** A proveniência hoje é `fonte:` (URL), `data-do-dado:`, `tier` e `verificacao-cruzada`; **não há snapshot, hash nem data de captura**. A garantia é re-execução — o `revisor-dossie` reabre as URLs e derruba o claim que não abrir. Isso cobre link morto, mas **não cobre a página mudar de conteúdo mantendo a URL viva**: o claim segue "válido" apontando para algo que já não diz aquilo. Para um produto cuja tese se sustenta em fatos, é o risco mais sério encontrado.
2. **Sem CI** — o enforcement é o hook `pre-commit` local, que qualquer `--no-verify` contorna.
3. **Cobertura de testes rala** — ~1 arquivo de teste para cada 3 scripts de produção.
4. **Sem fila de tickets** — há comandos (`apurar`, `modulo`) mas não a unidade de trabalho da decisão nº 1.
5. **Sem `DECISIONS.md`** — há 4 ADRs, mas falta a camada leve de decisões que não passam na barra de ADR.

## Verificação

1. **Plugin instala e as skills aparecem.** Instalar em um repositório limpo e confirmar que `/fluxo` e as demais aparecem no menu `/`, com `/context` mostrando custo baixo.
2. **`/fluxo` acerta o estado em quatro cenários montados**: repo vazio · spec sem tickets · tickets prontos · diff pendente de revisão. Em cada um, deve nomear o próximo passo certo e, no caso trivial, recomendar pular o rito.
3. **O `Stop` hook barra de verdade.** Quebrar um teste de propósito e confirmar que o turno não encerra.
4. **Orçamento de contexto medido**, não estimado: `/context` antes e depois de invocar `/fluxo`; se o corpo dele pesar, cortar.
5. **O prefixo roda no FirstAxiom e produz fila, não relatório** — tickets em ordem de bloqueio, com critérios de aceitação escritos antes.
6. **Nada do FirstAxiom é sobrescrito sem decisão explícita.** Toda substituição de mecanismo existente entra no `DECISIONS.md` com a alternativa descartada.

## Estado da sessão — handoff para a próxima

**Parada em:** fim da Fase 0 parcial. Nada foi implementado. Nenhum arquivo da metodologia existe ainda.

### Duas decisões pendentes, bloqueiam a Fase 1

1. **Nome do plugin.** Vira o prefixo de toda skill (`/<nome>:fluxo`) e será digitado para sempre. Candidatos discutidos: `fx` (curtíssimo, opaco), `metodo` (equilíbrio), `axiom` (amarra à marca, mas sugere que é específica do FirstAxiom, e não é).
2. **Repositório: GitHub.** Decidido em princípio — o usuário tem conta, e o remoto é o que entrega a durabilidade que motivou a escolha (a pasta não entrega; `git push` entrega). Estrutura: um repo que é marketplace **e** host do plugin, com `.claude-plugin/marketplace.json` na raiz apontando `"source": "./plugins/<nome>"`.

   **Três camadas, que resolvem o risco de cópia-de-trabalho-igual-a-cópia-instalada:** clone local (edição, carregado com `--plugin-dir`, isolado por sessão) · GitHub (fonte de verdade e distribuição) · outros projetos (`/plugin install`, versionado).

   Sub-pendências:
   - **Público ou privado** — privado exige credencial git em toda máquina que instale.
   - **Caminho do clone local** — candidato: `C:\Users\alero\Downloads\Projetos\`. Fora do FirstAxiom.
   - **Não criar o `marketplace.json` na Fase 1.** Ele só se paga ao instalar num segundo projeto; antes disso é cerimônia. Começar com repo + `--plugin-dir`.
   - **`gh` não está instalado** (ausente do PATH). Não é obrigatório, mas sem ele o agente cai em requisições não autenticadas com rate limit. Instalar antes da Fase 1.
   - **Bump de `version` a cada release** — sem isso, quem instalou fica com a cópia em cache. Candidato a item de checklist ou hook.
   - **CI de graça:** `claude plugin validate` no GitHub Actions a cada push — fecha, na metodologia, a lacuna nº 2 identificada no FirstAxiom.

   Identidade git já configurada: `Alerocha / alerochabreu@outlook.com`.

### Fase 0 — o que já foi lido (não refazer)

**Plugins** (`/docs/en/plugins`):
- Só `plugin.json` vai dentro de `.claude-plugin/`. **`skills/`, `agents/`, `hooks/`, `.mcp.json`, `settings.json` ficam na raiz do plugin.** A doc marca o contrário como "common mistake".
- Hooks do plugin vivem em `hooks/hooks.json`, mesmo formato do bloco `hooks` do `settings.json`.
- **Namespacing obrigatório:** skills de plugin são sempre `/<nome-do-plugin>:<skill>`. Daí a decisão pendente nº 1 importar.
- `settings.json` na raiz do plugin aceita **apenas** `agent` e `subagentStatusLine`. A chave `agent` ativa um agente do plugin como thread principal.
- Loop de desenvolvimento: `claude --plugin-dir ./<pasta>` carrega sem instalar · `/reload-plugins` recarrega sem reiniciar · `claude plugin validate ./<pasta>` valida. **Marketplace só é necessário para distribuir** — dá para trabalhar todo o desenvolvimento com `--plugin-dir` e montar o marketplace no fim.
- `claude plugin init <nome>` scaffolda em `~/.claude/skills/<nome>/` e auto-carrega como `<nome>@skills-dir`, sem marketplace. Alternativa de dev loop ainda mais curta.
- **Caveat que protege a Fase 5:** *"Project and user `.claude/agents/` definitions override same-named plugin agents."* O FirstAxiom já tem `apurador-dossie` e `revisor-dossie`; agentes do plugin com nome igual **não** os sobrescrevem.

**Marketplaces** (`/docs/en/plugin-marketplaces`):
- `.claude-plugin/marketplace.json` na raiz do repo, com `name`, `owner` (objeto com `name`), `plugins[]` (cada um com `name` e `source`).
- Um repo só pode ser marketplace **e** conter o plugin: `source: "./plugins/<nome>"`, relativo à raiz do marketplace.
- Instalação: `/plugin marketplace add <owner>/<repo>` → `/plugin install <plugin>@<marketplace>`.
- **Sem bump de `version` o usuário fica com a cópia em cache.** Versionar sempre ao publicar.

### Fase 0 — o que falta ler

`dynamic workflows` · `/batch` · `scheduled tasks` · `context: fork` em skill · `statusline` · `/doctor` · `checkpointing`. Nenhum bloqueia a Fase 1; todos importam da Fase 2 em diante.

### Documentos desta sessão

`melhores-praticas-anthropic-claude-code.md`, `analise-cruzada-metodologias.md` e `decisoes-metodologia.md` estão no workspace temporário da sessão, que **é apagado quando a sessão deixa de existir**. Foram entregues em anexo na conversa e podem ser baixados de lá. Ao criar o repositório da metodologia na Fase 1, re-hospedá-los em `docs/` dele.

## Fora de escopo

- **RAG.** Capacidade de projeto, não componente de metodologia. O caso real do FirstAxiom é **captura de evidência com proveniência**, não busca semântica sobre corpus estático — e a lacuna nº 1 acima é a forma correta de atacá-lo.
- **Sandbox / WSL2.** Adiado por decisão; risco residual registrado.
- **Auditoria de qualidade de código do FirstAxiom.** A conformidade vem primeiro, porque é ela que constrói o receptáculo onde achados de código aterrissam.
- **Registro de risco de projeto** (decisão nº 9).
