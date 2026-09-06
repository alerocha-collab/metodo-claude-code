# Decisões em aberto para a metodologia — versão 2

> Substitui a versão de seis decisões. Três nasceram da discussão sobre janela de contexto e ambientes; duas foram reescritas; quatro seguem como estavam.
>
> Cada decisão traz os caminhos, o que se ganha e se perde, o **modo de falha característico** (como você percebe que escolheu errado), a **variável determinante** (o que de fato decide) e uma recomendação minha, marcada **[minha]** para você discordar.

---

## Ordem de decisão

As decisões se bloqueiam. Decidir na ordem errada custa retrabalho: se você escolher o formato da spec antes de saber onde cai a fronteira de sessão, vai dimensionar a spec para o handoff errado.

```
CAMADA 1 — ESTRUTURAIS (decidem as outras)
  1. Unidade de trabalho: onde cai a fronteira de sessão
  2. Separação: por papel ou por ambiente
  3. Estado entre sessões: qual artefato

CAMADA 2 — PROCESSO (bloqueadas pela camada 1)
  4. Quanto de especificação          ← bloqueada por 1 e 3
  5. Refatoração: antes, durante ou depois  ← bloqueada por 1
  6. Quem escreve os critérios de aceitação
  7. Entrevistar ou sintetizar        ← bloqueada por 4

CAMADA 3 — GARANTIA (aplicam-se sobre tudo)
  8. Hooks: quanto, e onde eles vivem ← bloqueada por 2
  9. Registro de risco
```

**Se quiser cortar:** as nº 7 e nº 9 são as de menor alavancagem no seu contexto e podem ser adiadas sem travar as outras. As nº 1, 2 e 3 são as que realmente importam agora.

---

# CAMADA 1 — Estruturais

## 1. Unidade de trabalho: onde cai a fronteira de sessão

### O que está em jogo

Você planeja em fases de produto — dez fases, por exemplo — e a sessão termina onde a janela acabar. A fronteira de sessão cai **no meio de uma tarefa**, e é por isso que o handoff dói. A alternativa é dimensionar a fatia para caber numa sessão, e a fronteira vira uma escolha sua em vez de um acidente.

Esta é a decisão de maior alavancagem da lista, porque ela determina o custo de várias outras.

### Caminho A — fatia dimensionada pelo produto (fases)

**Vantagens**
- O plano espelha valor de negócio; é a linguagem do cliente.
- Fácil de comunicar e de aprovar.
- Menos cerimônia: dez fases geram dez conversas, não cem.

**Desvantagens**
- A fronteira de sessão cai onde a janela acabar, quase sempre no meio da implementação.
- O handoff precisa transferir **estado mental** — o que eu estava fazendo, por que parei aqui, o que já tentei e descartei. Isso é caro de escrever e caro de ler.
- Você compensa com documentação, que consome exatamente o recurso que estava faltando.

**Modo de falha característico:** você escreve um handoff de 500 linhas, e a sessão nova gasta 20% da janela lendo antes de escrever a primeira linha de código. O remédio virou a doença.

### Caminho B — fatia dimensionada pela janela (tracer bullet)

**Vantagens**
- O handoff é **sempre entre tarefas, nunca no meio**: "fatia N pronta, commitada, testes verdes; próxima é a N+1". Estado mental a transferir: zero.
- Cada fatia é demonstrável sozinha, o que torna a revisão possível.
- É o que o `to-tickets` já produz — *"each slice is sized to fit in a single fresh context window"* —, e é o que a Anthropic prescreve com o padrão de uma feature por sessão.

**Desvantagens**
- Fatiar assim dá trabalho, e é trabalho de julgamento que não dá para delegar inteiro.
- Fatias pequenas demais geram cerimônia desproporcional: ticket, commit, revisão para vinte linhas.
- A fase de produto vira um agregado de N tickets, e você perde a legibilidade do plano para quem está de fora.

**Modo de falha característico:** quarenta tickets de quinze minutos, e você gasta mais tempo administrando a fila do que teria gasto implementando.

### Caminho C — dois níveis

A fase de produto continua existindo, para você e para o cliente; ela é **decomposta** em fatias dimensionadas por janela, para o agente. É exatamente o que o pipeline `to-spec` → `to-tickets` faz: a spec é a fase, os tickets são as fatias, e as arestas de bloqueio preservam a ordem.

### A variável determinante

**Se o handoff dói, a fatia está maior que a sessão.** É medível: se você precisa de mais de três linhas para explicar "onde paramos", a fronteira caiu no lugar errado. **[minha]**

### Recomendação **[minha]**

Caminho C. Mantenha as dez fases como spec e como unidade de conversa; decomponha cada fase em tickets dimensionados por janela; **sessão = um ticket, commit no final**. O handoff deixa de ser um documento e passa a ser uma consequência.

---

## 2. Separação: por papel ou por ambiente

### O que está em jogo

No mainframe, ambiente e papel são a mesma linha: o programador não alcança produção nem se quiser, porque a barreira é física e de acesso. Com agentes num repositório, os dois eixos **se descolam** — construtor e operador atuam no mesmo código, na mesma máquina, com minutos de diferença.

O sintoma que revelou isso: um hook com regra de operação ("não rodar A antes de B") barrando uma sessão de ajuste de código. O hook está escopado ao repositório; a regra pertence ao papel.

### Caminho A — separar por ambiente (duas árvores)

**Vantagens**
- Espelha o modelo mental que você já domina.
- Isolamento visível: dá para apontar a pasta.
- Erro em desenvolvimento não toca produção por construção.

**Desvantagens**
- **Cria um problema de sincronização.** A mesma mudança precisa existir nas duas árvores, e você passaria a precisar da ferramenta de promoção que hoje alguém te entrega pronta.
- Git já faz isso com branch e tag; duplicar a árvore é duplicar a função dele.
- **Não resolve o problema que motivou a ideia.** Os dois papéis continuam operando na árvore de desenvolvimento; o hook do operador continua barrando o construtor.

**Modo de falha característico:** as duas árvores divergem em silêncio, e você descobre em produção.

### Caminho B — separar por papel (uma árvore, agentes distintos)

**Vantagens**
- Resolve a dor diretamente: a definição de subagente carrega **hooks, ferramentas, permissões, skills e modelo próprios**. A regra de ordem passa a existir só dentro do papel que a tem como obrigação.
- `claude --agent operador` roda a sessão inteira naquele papel.
- Git continua sendo a única fonte de versão; ambiente vira configuração (credencial, banco, endpoint).

**Desvantagens**
- **A separação é lógica, não física.** Nada impede fisicamente que uma sessão de operação edite código — só a ausência das ferramentas na definição do agente.
- Exige disciplina de lembrar qual papel invocar.

**Modo de falha característico:** você esquece o `--agent`, roda como construtor num contexto de operação, e o agente "conserta" algo que estava certo.

**Mitigação:** a barreira dura não vem da pasta nem do agente — vem de `permissions.deny` em managed settings e de sandbox (filesystem **e** rede). É lá que a separação deixa de depender de disciplina.

### A variável determinante

**Onde está a fronteira dura de verdade.** Se produção roda em outra máquina ou container, a separação física já existe e a árvore duplicada é redundante. Se roda na mesma máquina, a árvore duplicada não dá barreira nenhuma — dá a *sensação* de barreira, que é pior que não ter. **[minha]**

### Recomendação **[minha]**

Caminho B, com a barreira dura em permissões e sandbox, não em pasta. O que é comum (domínio, glossário, comandos, convenções) vive no `CLAUDE.md` da raiz; o que é específico vive no arquivo do agente. Sua intuição sobre a forma estava certa — comum na raiz, específico no específico. O "específico" é o papel, não o ambiente.

---

## 3. Estado entre sessões: qual artefato

### O que está em jogo

Esta decisão estava escondida dentro da antiga nº 2. Ela é sobre o **formato** do que atravessa a fronteira de sessão — não sobre o tamanho da spec.

Vale registrar o achado que a motiva: **não existe feature nativa para estado de plano.** Auto memory serve para preferências, correções e referências — pula deliberadamente o que é derivável do código, tem teto de 200 linhas e é local à máquina. Quando a Anthropic atacou este problema exato, a resposta foi um **arquivo**.

### Caminho A — documento em prosa

**Vantagens**
- Legível por humano; captura nuance e o *porquê* das decisões.
- Um artefato só, fácil de achar.

**Desvantagens**
- Custa janela **toda sessão**, e é a janela o recurso em falta.
- O modelo reescreve Markdown com facilidade. A escolha de JSON pela Anthropic é explícita e pelo motivo oposto: *"o modelo tem menos chance de alterar ou sobrescrever inapropriadamente arquivos JSON do que arquivos Markdown."*
- **Se for atualizado automaticamente, você perde a capacidade de detectar quando ficou errado.** Um documento que parece sempre atual é a pior propriedade possível num artefato de handoff.

**Modo de falha característico:** o documento diz uma coisa, o código faz outra, e ninguém percebe — porque o documento "está sempre atualizado".

### Caminho B — estado estruturado + git + decisões append-only

Três artefatos com funções distintas:

| O quê | Onde | Quem atualiza |
|---|---|---|
| Onde paramos | `git log` + commit por fatia | O commit, automaticamente |
| O que vem agora | Tickets numerados com "Blocked by" e status (saída do `to-tickets`), ou JSON de features | O agente, marcando um campo |
| O que já foi decidido, e por quê | Arquivo de decisões / ADRs, **append-only** | Você, quando a decisão acontece |

**Vantagens**
- O que muda todo dia fica em formato que o modelo não reescreve por acidente.
- "Onde paramos" vem do git, que é verdade por construção, não por redação.
- Decisões em arquivo append-only só crescem — nada se perde numa reescrita.
- Custo de janela baixo: um `SessionStart` hook imprime branch, últimos commits e o próximo ticket não bloqueado.

**Desvantagens**
- Menos legível para alguém de fora do projeto.
- Exige disciplina de commit por fatia — se você commita de hora em hora, o git para de contar a história direito.
- Precisa de um `SessionStart` para montar a visão inicial, que é configuração a manter.

**Modo de falha característico:** o ticket está marcado como concluído mas ninguém verificou de verdade. É o problema da decisão nº 6, e é por isso que as duas se conectam.

### A variável determinante

**Quem é o leitor.** Se é o agente, formato estruturado. Se é um humano de fora, prosa. Se são os dois, **são dois artefatos com propósitos diferentes** — e o de prosa se escreve no fim, não durante. **[minha]**

### Sobre o hook que você propôs

A ideia é boa, com uma correção importante. Separe as duas metades:

- **Detectar desatualização** é determinístico e barato: o documento guarda o SHA em que foi escrito; o hook roda `git diff <sha>..HEAD --stat` e avisa ou bloqueia. Faça.
- **Julgar se a arquitetura mudou** exige julgamento. Existe hook `type: prompt` (avaliação LLM de um turno) e `type: agent` (multi-turno, **experimental**), mas ambos produzem falso positivo — e falso positivo em hook é caro, porque não se negocia com hook.

**O hook detecta e bloqueia. Nunca atualiza.** Desatualização é sinal para decisão humana, não coisa a curar sozinha.

### Recomendação **[minha]**

Caminho B durante, A no final. Estado estruturado + git durante a implementação; documento de arquitetura gerado ao encerrar a fase, carimbado com o SHA, e o hook de detecção de desatualização em cima dele.

---

# CAMADA 2 — Processo

## 4. Quanto de especificação antes de codificar

> **Reescrita.** O argumento "preciso de documentação extensa para o handoff" saiu daqui e virou a decisão nº 3. O que resta é a pergunta original, e ela é mais estreita do que parecia.

### O que está em jogo

XP diz o mínimo: o cartão é lembrete de uma conversa. O `to-spec` pede muito: *"a LONG, numbered list of user stories"* cobrindo todos os aspectos. A Anthropic fica no meio e precifica: *"se você consegue descrever o diff em uma frase, pule o plano"*.

### Caminho A — especificação mínima

**Vantagens**
- Velocidade; não se gasta escrevendo o que vai mudar de qualquer forma.
- Descoberta pelo sistema real em vez de pela especulação.

**Desvantagens**
- **O agente não conversa.** Em XP o cartão funciona porque o cliente está sentado ali. O agente preenche a lacuna sozinho, com plausibilidade, e sem avisar que preencheu.
- Você descobre a divergência no diff, não no diálogo.
- Sem spec não existe eixo Spec na revisão. Você fica com metade do `mp-code-review`.

**Modo de falha característico:** o agente entrega algo que funciona, é bem feito, e resolve o problema ao lado do seu.

### Caminho B — especificação extensa

**Vantagens**
- Dá contrato ao agente que roda sem você.
- **A seção "out of scope" é a mais barata e a mais valiosa** — é o que impede gold-plating.
- Escrever revela ambiguidade que você não sabia que tinha. O benefício acontece durante a escrita.

**Desvantagens**
- Custo de atenção pago adiantado.
- Quanto mais detalhe, mais superfície para envelhecer.
- Overhead puro em tarefa pequena.

**Modo de falha característico:** a spec erra em três pontos que só apareceriam ao codar, e o agente implementa fielmente os três erros.

### A variável determinante

**Quanto tempo o agente roda sem você** — não o tamanho da feature. Uma mudança grande acompanhada ao vivo precisa de pouca spec; uma pequena despachada para a fila precisa de spec completa. **Dimensione pela autonomia.** **[minha]**

E um eixo inegociável, em que os três corpos modernos concordam: a spec é **comportamental, não procedimental**. A extensão nunca vem de detalhar implementação — vem de cobrir casos, fronteiras e escopo excluído.

### Recomendação **[minha]**

| Autonomia | Especificação |
|---|---|
| Você acompanha ao vivo | Uma frase + o comando de verificação |
| Uma sessão, revisada no final | Brief comportamental: comportamento atual → desejado, interfaces-chave, critérios de aceitação, out of scope |
| Fila, dias até alguém olhar | Spec completa do `to-spec` |

Teste de suficiência: **a spec está pronta quando responde as perguntas que o agente faria.**

---

## 5. Refatoração: antes, durante ou depois

### O que está em jogo

O ciclo canônico de Beck é red → green → **refactor**. O skill `tdd` do Matt Pocock corta o terceiro tempo: *"Refactoring is not part of the loop. It belongs to the review stage."* A escolha define **o que o diff de uma fatia contém**.

### Caminho A — dentro do loop (Beck ortodoxo)

**Vantagens**
- O design não apodrece; a dívida é paga onde é contraída.
- Contexto fresco: quem acabou de escrever sabe por que ficou feio.
- Evita o "grande refactor" que precisa ser aprovado e nunca é.

**Desvantagens**
- **O diff deixa de ser revisável**: você não separa mudança de comportamento de mudança de estrutura.
- **O agente não tem freio social** — segue a cadeia de dependências e reescreve arquivos vizinhos.
- Ambiguidade na falha: quebrou por causa da feature ou da limpeza?
- Refatorar exige ler mais arquivos, inflando a janela no meio da implementação.

**Modo de falha característico:** PR de 40 arquivos em que 3 são a feature. Você aprova sem revisar, porque revisar custaria mais que reescrever.

### Caminho B — fora do loop, na revisão

**Vantagens**
- O diff da fatia é legível: só comportamento. É o que torna o eixo Spec da revisão possível.
- A fatia termina mais rápido e com menos contexto.

**Desvantagens**
- **Risco alto de nunca acontecer.** Refatoração adiada é refatoração cancelada.
- A dívida acumula entre fatias, e cada fatia nova é escrita sobre a bagunça anterior.
- Quem refatora depois perdeu o contexto do porquê.

**Modo de falha característico:** seis fatias depois, o módulo tem seis variações da mesma lógica.

### Caminho C — os três tempos que o set do Matt já implementa

Ele não é só "fora do loop". O `to-tickets` manda prefatorar **antes**, como ticket próprio: *"Look for opportunities to prefactor the code to make the implementation easier. Make the change easy, then make the easy change"* — e *"any prefactoring should be done first"*.

| Momento | Refatora? |
|---|---|
| **Antes** da fatia | **Sim** — prefactoring, ticket próprio |
| **Durante** o red → green | **Não** |
| **Depois**, na revisão | **Sim** — achado do eixo Standards |

Para refactors de raio amplo há mecanismo próprio: **expand–contract** — adiciona a forma nova ao lado da antiga, migra os chamadores em lotes dimensionados pelo raio (cada lote um ticket), e deleta a antiga só no fim. Cada passo mantém o CI verde.

### A variável determinante

**Quão cuidadosamente você revisa cada diff.** Se revisa linha a linha, o Caminho A é viável. Se aprova por amostragem — o realista quando o agente produz mais rápido do que você lê —, misturar comportamento e estrutura é abrir mão da revisão.

### Recomendação **[minha]**

Caminho C, com uma emenda: **todo achado de smell aceito vira ticket na hora**, com bloqueio para a próxima fatia que tocar o mesmo módulo. Sem isso, o Caminho B degenera no seu modo de falha em poucas semanas.

---

## 6. Quem escreve os critérios de aceitação

### O que está em jogo

XP: o cliente escreve os testes funcionais, com apoio técnico. O `to-tickets`: o agente propõe os critérios, você aprova. É uma **transferência real de autoria** — e a mais silenciosa das nove, porque acontece por padrão se você não decidir nada.

### Caminho A — você escreve

**Vantagens**
- O critério reflete sua intenção, não a leitura que o agente fez dela.
- **Escrever força você a decidir o que "pronto" significa** — o trabalho intelectual irredutível.
- Última linha de defesa contra o agente satisfazer a própria interpretação.

**Desvantagens**
- Caro, e exige expressar intenção em termos testáveis.
- Você vira o caminho crítico.

### Caminho B — o agente escreve, você aprova

**Vantagens**
- Rápido, e o agente é genuinamente bom nisso. Compare o exemplo bom do `AGENT-BRIEF.md` — *"Running `gh issue list --label needs-triage` returns issues that have been through initial classification"* — com o ruim — *"Triage should work correctly"*. A maioria das pessoas escreve o segundo.

**Desvantagens**
- **O agente escreve o critério que ele sabe satisfazer.** É auto-avaliação disfarçada de contrato.
- Aprovação por leitura rápida é fraca: critérios complacentes são, por construção, plausíveis.
- Viola o princípio central: **quem dá a nota não pode ser quem faz o trabalho.**

**Modo de falha característico:** todos os critérios marcados, suíte verde, e a feature não faz o que você queria — porque os critérios descreviam o que foi construído.

### Caminho C — separar a autoria da condição e a da expressão

Você escreve **a condição de pronto** em uma frase: o que precisa ser verdade no mundo. O agente **expande** em critérios testáveis. E os critérios entram **antes** da implementação, idealmente por um contexto diferente do que vai implementar.

É o **sprint contract** da Anthropic: gerador e avaliador acordam o que será construído e como será verificado antes de qualquer código.

### A variável determinante

**Quão bem você detecta um critério complacente numa leitura rápida.** Quase todo mundo aprova o que parece bem escrito.

### Recomendação **[minha]**

Caminho C, com regra dura: **os critérios entram no ticket antes de a implementação começar e não são editados durante.** Critério alterado no meio é o agente ajustando o alvo ao tiro. Se um se revelar impossível, isso é conversa com você, não edição.

---

## 7. Entrevistar antes, ou sintetizar do que já foi dito

> Baixa alavancagem — pode ser adiada. Incluída porque, sem regra, ela é decidida por omissão.

### O que está em jogo

`to-spec`: *"Do NOT interview the user; just synthesize what you already know."* A Anthropic: entreviste-me antes de escrever a spec. Não é contradição — a entrevista está no `grilling`, a montante. Resta decidir **quando ela se paga**.

### Caminho A — entrevistar

**Vantagens:** descobre o que você não sabia que não sabia; o `grilling` reduz o custo com rodadas e resposta recomendada em cada pergunta; e a regra *"finding facts is your job, never the user's"* — despachar subagente em vez de perguntar — corta a maior parte do atrito.

**Desvantagens:** custa atenção humana, que é o recurso que você tenta economizar; em escopo dominado, é atrito puro.

**Modo de falha:** três rodadas para uma tarefa que caberia em duas frases.

### Caminho B — sintetizar

**Vantagens:** zero atrito; aproveita o contexto que a conversa já produziu; é o uso para o qual o `to-spec` foi desenhado — depois da discussão, não no lugar dela.

**Desvantagens:** sintetiza também os mal-entendidos; o que ficou ambíguo vira ambiguidade congelada num artefato com aparência de autoridade.

**Modo de falha:** a spec fica boa, plausível e errada, e você aprova porque *parecia* certa.

### A variável determinante

**Quantas decisões continuam em aberto** — não o tamanho da feature. Você está escolhendo quem paga o custo da ambiguidade: entrevistar paga agora em atenção, sintetizar paga depois em retrabalho — mas só se houver ambiguidade.

### Recomendação **[minha]**

Gatilho, não regra. Entreviste quando qualquer um for verdadeiro: (1) o critério de pronto não cabe numa frase; (2) há mais de um caminho razoável e você não sabe qual quer; (3) o trabalho vai para a fila sem supervisão. Caso contrário, sintetize.

---

# CAMADA 3 — Garantia e risco

## 8. Hooks: quanto, e onde eles vivem

> **Reescrita.** Deixou de ser só "quanto de garantia" — a conversa revelou que a pergunta difícil é **onde o hook vive**.

### O caveat que decide tudo

**Hooks se fundem entre camadas de configuração; eles não se sobrescrevem.** Todos os hooks registrados disparam no evento correspondente, venham de managed, user, project ou local. **Não existe desligar um hook de projeto colocando outro no local.**

É exatamente por isso que a regra do operador barrou a sessão de construção: ela está no `settings.json`, e o `settings.json` vale para tudo.

### Caminho A — tudo advisório (estado atual do set do Matt)

**Vantagens:** portabilidade (skills viajam entre máquinas, hooks não); zero manutenção; o agente exerce julgamento quando a regra não se aplica; falha suave.

**Desvantagens:** a aderência cai conforme o contexto enche — justamente quando você mais precisa da regra; em execução não supervisionada, "pedido" não significa nada.

**Modo de falha:** a suíte completa não roda no final porque a instrução tinha 200 mensagens de idade.

### Caminho B — hooks, todos no `settings.json`

**Vantagens:** garantia real, custo de contexto zero, funciona mesmo quando o modelo esqueceu.

**Desvantagens:** **é o seu problema de hoje.** Sem escopo por papel, toda regra vale para todo mundo. Falso positivo é caro porque não se negocia com hook, e o `Stop` tem teto de 8 bloqueios consecutivos.

**Modo de falha:** você escreve seis hooks numa tarde, um fica sutilmente errado, e duas semanas depois desliga todos porque "atrapalham".

### Caminho C — hooks em três níveis, por escopo

| Escopo | Onde vive | Exemplo |
|---|---|---|
| **Universal** — vale em qualquer papel | `.claude/settings.json` | Lint pós-edição; bloquear escrita em `.env`; `Stop` de verificação |
| **Por papel** — só naquele agente | Frontmatter do agente (`hooks:`) | Ordem da apuração, no `operador` |
| **Por fluxo** — só enquanto a skill roda | Frontmatter da skill (`hooks:`) | Validação específica de um workflow |

Escape para hook que precise ficar no `settings.json` mesmo: cláusula de guarda no script, que lê um marcador de papel e sai com `exit 0` quando não se aplica. Funciona, mas é remendo — prefira o frontmatter.

### O critério de decisão

Um hook se paga quando **o custo de a regra falhar uma vez é maior que o custo de mantê-la**. Teste prático: **se você já corrigiu o agente três vezes pela mesma regra, ela deveria ser um hook.** **[minha]**

E a repartição por natureza:

| Natureza da regra | Onde |
|---|---|
| Exige julgamento, depende do caso | Skill ou CLAUDE.md |
| Binária e verificável por script | **Hook** |
| Nunca deve acontecer, em hipótese alguma | `permissions.deny` em managed settings |

### Recomendação **[minha]**

Caminho C. E, na prática, comece migrando o que já existe: tire do `settings.json` tudo que é regra de operação, deixe lá só o universal, e mova o resto para o frontmatter do `operador`. Se for construir do zero, comece com **um** hook — o `Stop` de verificação —, porque é o que fecha o loop e converte sessão assistida em sessão da qual você pode sair.

---

## 9. Registro de risco: adotar do clássico, ou aceitar não ter

> Baixa urgência — pode ser adiada. Mas o ponto cego é real e vale registrar.

### O que está em jogo

Só Sommerville/Pressman tem gestão formal de risco. E vale nomear o ponto cego com precisão: **a doutrina de agentes gerencia risco do agente, não risco do projeto.** Sandbox, permissões, verificação e contenção protegem você do que o agente pode fazer de errado. Nada disso avisa que o fornecedor de dados vai mudar a API em março, ou que você é a única pessoa que entende o módulo de apuração.

### Caminho A — adotar o registro

**Vantagens:** único instrumento dos quatro corpos que força a pensar no que dá errado **fora** do código; barato (uma tabela); e muda decisões técnicas de verdade — "risco: o fornecedor X é ponto único de falha" justifica uma camada de abstração que, sem o registro, seria Speculative Generality. **O registro é o que distingue abstração defensiva de abstração ansiosa.**

**Desvantagens:** vira ritual morto se ninguém revisa — e registro desatualizado é pior que nenhum, porque dá falsa cobertura; probabilidade × impacto costuma ser teatro numérico.

### Caminho B — não ter, conscientemente

**Vantagens:** menos cerimônia; em ciclo de feedback curto, o risco se materializa e você reage — a aposta do XP, feedback no lugar de previsão.

**Desvantagens:** cegueira para risco não técnico, que é o que mata projeto. E a aposta do XP só vale quando o ciclo de feedback é mais curto que o tempo de materialização do risco — um contrato que muda em seis meses não é detectável por iteração semanal.

### Caminho C — versão leve

A seção **"Suposições e quando revisar"** do template do subagente `arquiteto` já é um proto-registro de risco técnico. Estendê-la com três a cinco linhas de risco **não técnico** — dependência externa, prazo com terceiro, concentração de conhecimento — captura a maior parte do valor. Sem coluna de probabilidade: só **risco / sinal de que está se materializando / o que fazer**.

### A variável determinante

**Existe alguém além de você dependendo do prazo ou do resultado?** Se não, o Caminho B é defensável. Se sim, a ausência de registro transfere para essa pessoa um risco que ela não sabe que corre.

### Recomendação **[minha]**

Caminho C, com a revisão ancorada num evento que já acontece — fim de fase, release — e não num calendário. Registro com data de revisão é registro que ninguém revisa.

---

# Quadro-resumo

| # | Decisão | Variável que decide | Recomendação **[minha]** |
|---|---|---|---|
| **1** | Unidade de trabalho | Se o handoff dói, a fatia é maior que a sessão | Dois níveis: fase = spec, ticket = fatia, **sessão = um ticket + commit** |
| **2** | Papel ou ambiente | Onde está a fronteira dura de verdade | Por **papel**, com barreira em permissões e sandbox, não em pasta |
| **3** | Estado entre sessões | Quem é o leitor | Estruturado + git durante; prosa no fim; hook **detecta, nunca atualiza** |
| **4** | Quanto de spec | Quanto o agente roda sem você | Três níveis por autonomia; pronta quando responde o que o agente perguntaria |
| **5** | Refatoração | Quão a fundo você revisa cada diff | Prefactor antes · nunca durante · achado da revisão vira **ticket automático** |
| **6** | Critérios de aceitação | Se você detecta critério complacente na leitura | Você escreve a condição, o agente expande, **antes** e sem editar durante |
| **7** | Entrevistar ou sintetizar | Quantas decisões seguem em aberto | Gatilho, não regra |
| **8** | Hooks | Custo de falhar × custo de manter | Três escopos: universal no settings, papel no agente, fluxo na skill |
| **9** | Registro de risco | Se alguém além de você depende do resultado | Versão leve, ancorada em evento |

## O fio comum

Sete das nove têm a mesma estrutura por baixo: **onde você coloca o esforço humano — antes ou depois.** Especificar antes ou corrigir depois; entrevistar antes ou retrabalhar depois; escrever critério antes ou descobrir desalinhamento depois; hook que impede antes ou correção depois; fatiar antes ou fazer handoff depois.

A resposta é a mesma nas sete: **conforme a autonomia do agente aumenta, o esforço migra para antes.** Não porque "antes" seja melhor — XP passou vinte anos demonstrando que não é —, mas porque o "depois" do XP pressupunha um humano presente para corrigir o rumo. Em execução autônoma, esse humano não está lá.

Isso não ressuscita cascata: continua fatia vertical, ciclo curto, escopo como alavanca, YAGNI. O que muda é a **distribuição do esforço dentro de cada fatia**, não o formato do ciclo. **[interpretação]**
