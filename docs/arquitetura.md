# Arquitetura do plugin `metodo`

**SHA:** `83dd9d7` · **Data:** 2026-09-07

> Este documento descreve o desenho **em vigor**. A história de como se chegou nele
> está no [DECISIONS.md](../DECISIONS.md), append-only, e não é repetida aqui — duas
> fontes para a mesma coisa divergem, e a que o leitor encontra primeiro é aleatória.
>
> O carimbo acima é o commit cujo estado este texto descreve. Meça a distância com:
>
> ```bash
> python3 plugins/metodo/scripts/verificar_documento.py
> ```
>
> `estado` também reporta essa distância, para todo `docs/*.md` que traga carimbo — é
> onde alguém já está decidindo o próximo passo. **Não está no CI de propósito:** lá o
> detector ficaria vermelho em quase todo commit, e trava que grita sempre é trava que
> se aprende a ignorar.
>
> Nada atualiza o carimbo automaticamente, de propósito. Um documento que parece
> sempre atual é o pior artefato de handoff possível: diz uma coisa, o código faz
> outra, e ninguém percebe.

---

## 1. O que o plugin é

Um conjunto de skills, agentes e hooks que codifica um método de trabalho com
agentes, empacotado para viajar entre projetos.

Ele não é uma biblioteca nem uma ferramenta: é **convenção com garantia**. O que
exige julgamento vive em skill; o que é binário e verificável vive em hook.

## 2. As duas trilhas

```
projeto novo      decidir ──→ dominio ──┐
                                        ├──→ fatiar ──→ implementar ──→ revisar
reengenharia   entender → modelar → lacunas ┘
```

Divergem só na entrada e depois **convergem por completo**. É por isso que o prefixo
de reengenharia são três skills e não um "modo" dentro de cada skill: ramificar por
modo paga complexidade em contexto sempre, inclusive nas sessões em que o modo não se
aplica.

`fluxo` fica fora da linha: ele lê o estado e diz onde você está.

## 3. Os componentes, e a suposição que cada um codifica

### Agentes — separação por papel

`construtor` implementa um ticket e commita. `operador` executa procedimentos e não
altera código. `arquiteto` projeta harness e devolve documento.

A separação é **por papel, não por ambiente**. Duplicar a árvore de arquivos daria
sensação de barreira sem barreira nenhuma — os dois papéis operariam na mesma cópia
de qualquer jeito. Git já versiona; ambiente é configuração.

A barreira do `operador` é `disallowedTools`. Não há `permissions:` em frontmatter de
agente — verificado na doc.

### Hooks — a garantia

Dois, ambos em `hooks/hooks.json`, porque **`hooks:` no frontmatter de agente é
ignorado para agentes de plugin**.

`verificar_suite` é `Stop`: roda a verificação declarada pelo projeto e bloqueia o fim
do turno enquanto ela não passar. `proteger_testes` é `PreToolUse`: barra editar ou
sobrescrever teste que já existe.

Três propriedades deliberadas:

- **Fail-closed em duas metades.** Verificação ausente conta como falha; e qualquer
  erro do próprio script conta como falha, porque exit 1 **não** bloqueia — um
  traceback não tratado abriria o portão em silêncio.
- **Cláusula de guarda por árvore suja, não por papel.** O portão pergunta "há algo a
  verificar", não "quem sou eu". Árvore limpa libera, e é isso que impede o
  `operador` de ser barrado por vermelho que ele não criou. Vale para papéis que
  ainda não existem.
- **`|| exit 2` no comando.** Sem ele, `python3` ausente sai 127, que não bloqueia —
  o portão falharia aberto na máquina mal configurada.

### Scripts — o determinístico

| Script | Faz | Não faz |
|---|---|---|
| `validar_fila` | Detecta ciclo, aresta pendurada, mais de um em andamento | Corrigir |
| `marcar_ticket` | Recusa transição ilegal; revalida antes de gravar | Gravar fila inválida |
| `estado` | Lê disco e diz o próximo passo, **e relata a distância dos documentos carimbados** | Escrever, executar, bloquear |
| `verificar_documento` | Mede a distância entre carimbo e `HEAD` | Atualizar o carimbo |

O padrão é o mesmo nos quatro: **detectam e recusam; nunca curam sozinhos.**

### Artefatos que o plugin instala

`.claude/metodo.json` declara o comando de verificação — JSON, porque governa um
portão. `tickets/fila.json` carrega o que muda toda sessão — JSON, porque o modelo
reescreve Markdown por acidente. `tickets/NNN-*.md` é a prosa, escrita uma vez.
`DECISIONS.md` é append-only, abaixo da barra do ADR. `CONTEXT.md` é glossário e
nada mais.

A divisão é por **leitor e por taxa de mudança**, não por gosto.

## 4. O que não foi construído porque já existe

`/doctor` mede orçamento de contexto. `/batch` paraleliza por worktree. `context: fork`
paga o corpo de uma skill fora da sessão. `/rewind` **não** serve como rede — não
cobre mudança por Bash nem por subagente; a rede é git.

## 5. Suposições e quando revisar

| Componente | Suposição que codifica | Sinal de que caducou |
|---|---|---|
| `Stop` de verificação | O modelo declara "pronto" quando o trabalho *parece* pronto | O agente roda a verificação espontaneamente antes de encerrar, em 10 sessões seguidas |
| `proteger_testes` | Quem é medido por verde tem incentivo a reduzir o que é medido | **Não caduca por melhoria de modelo** — o incentivo é estrutural. Mantenha enquanto a métrica for "suíte verde" |
| Guarda por árvore suja | Não dá para descobrir o papel de forma documentada | Caducou em parte: `agent_type` **existe** no evento. Trocar só se a guarda atual se mostrar grosseira |
| `\|\| exit 2` | 127 não bloqueia | Se a doc passar a classificar 127 como bloqueante |
| Fila em JSON | O modelo reescreve Markdown por acidente | Se o modelo passar a preservar Markdown estruturado com a mesma fidelidade |
| `validar_fila` | Grafo de bloqueio errado não aparece na leitura | Não caduca: é propriedade do grafo, não do leitor |
| `estado` como script | Recomendação em prosa não é testável | Se houver mecanismo nativo que leia o mesmo estado |
| Skills em vez de workflow | Workflows são gated por plano e plataforma | Se deixarem de ser |
| Hooks em Python | `.sh` não cobre os três shells possíveis | Se hooks passarem a rodar num shell único e garantido |
| Este documento | O `DECISIONS.md` conta a história, não o desenho em vigor | Se alguém conseguir responder "como isto funciona" só lendo as decisões |

**Gatilho de revisão:** fim de fase, modelo novo, atualização relevante do Claude Code.
Não em calendário — documento com data de revisão é documento que ninguém revisa.

## 6. O que ainda não foi verificado

Duas entradas desta lista caíram no ticket 021. **Instalação por marketplace** e
**segundo projeto** deixaram de ser premissa: o `doutrina` foi instalado num repositório
git limpo, por `claude plugin install`, e as seis skills apareceram numa sessão que
nunca viu este repositório. O exercício também **achou um defeito** — links relativos
para os arquivos de referência não resolvem depois de instalado. Ver decisão 016.

O que sobra:

- **Se hooks dependem ou não de confiança.** Eles dispararam num workspace declarado
  não confiado, contra o que o README afirmava. A frase saiu de lá; a questão fica
  aberta em P12.

Caiu também, na decisão 018: **os hooks do `metodo` numa instalação de verdade**. O
drill de três casos rodou a partir de um plugin instalado — bloqueia com suíte vermelha,
solta com verde, nega edição de teste existente. A combinação que faltava era o
`metodo.json` no **projeto** e os hooks no **plugin**, que só se separam depois da
instalação.

### Plataforma: fora de escopo, não pendente

macOS e Linux **não** são pendência deste projeto: ele é usado em Windows, e listar
como dívida algo que ninguém vai cobrar é ruído que faz a lista inteira perder crédito.

A formulação anterior — *"o shell dos hooks é outro lá"* — sugeria risco onde ele é
menor, e desviava do risco de verdade:

| | Situação |
|---|---|
| **Linux** | Os scripts e as onze suítes rodam em `ubuntu-latest` **a cada push**. É a metade Python, coberta continuamente e sem esforço |
| **macOS/Linux, hooks** | Rodam em `sh`. `\|\| exit 2` é sintaxe POSIX: a rede que converte `python3` ausente em bloqueio funciona lá **por construção** |
| **Windows sem Git Bash** | Hooks caem em PowerShell, onde a rede POSIX **não vale** e a ausência de `python3` volta a falhar aberta |

O caso frágil é o terceiro — e é da própria família de plataformas em uso, não das
outras. Está no README como risco residual, sem contorno portátil conhecido.

Se alguém instalar a partir do repositório público em macOS ou Linux, o não exercitado
é o portão numa sessão real. O resto tem cobertura de CI.
