# Referência 05 — Segurança e operação autônoma

Fonte: *How we contain Claude across products*, *Beyond permission prompts: making Claude Code more secure and autonomous*, *How we built Claude Code auto mode*; docs `memory` (managed settings), `permissions`, `sandboxing`.

---

## 1. A tese central

> **A fronteira determinística é o que é atingido quando tudo o que é probabilístico erra.**

Por isso a Anthropic prioriza **contenção ambiental** sobre defesa na camada de modelo. Um design de agente que confia em system prompt e classificador para segurança está confiando na camada errada.

## 2. As três camadas

| Camada | O que a compõe | Papel |
|---|---|---|
| **Ambiente** | Sandboxes, VMs, controles de egresso | Fronteira dura. É a que segura |
| **Modelo** | System prompts, classificadores, treinamento | Reduz a frequência, não garante |
| **Conteúdo externo** | Permissões de ferramenta, validação de servidores MCP | Controla o que entra |

## 3. Três padrões de contenção em produção

| Produto | Padrão | Modelo de ameaça |
|---|---|---|
| **claude.ai** | Container gVisor, filesystem efêmero por sessão | Proteger a infraestrutura de falha de isolamento entre tenants. Blast radius mínimo, capacidade limitada |
| **Claude Code** | Sandbox com humano no loop; execução local com sandbox de SO (Seatbelt / bubblewrap) | O dev **consegue avaliar comandos bash**, então supervisão humana é viável |
| **Claude Cowork** | VM selada; loop do agente **fora** da VM, execução de código dentro; diretórios montados com controle granular (read-only, read-write, read-write-no-delete) | Usuário não técnico **não consegue** avaliar comandos bash — exige fronteira absoluta |

**Regra de projeto:** case o isolamento com a expertise de quem opera. Dev tolera diálogo de aprovação; knowledge worker exige VM.

## 4. Sandboxing no Claude Code

O problema que ele resolve é **fadiga de aprovação**: clicar "aprovar" constantemente desacelera e leva as pessoas a pararem de revisar. A fadiga **reduz** a segurança. Internamente, sandboxing cortou **84%** dos prompts de permissão.

**As duas camadas são ambas obrigatórias:**

- **Filesystem** — o Claude só acessa diretórios designados. Sem isso, um agente comprometido escapa do sandbox.
- **Rede** — o Claude só conecta a servidores aprovados. Sem isso, um atacante exfiltra chaves SSH.

> *"Sandboxing garante que mesmo uma injeção de prompt bem-sucedida fique totalmente isolada e não possa afetar a segurança geral do usuário."*

Use **primitivas de nível de SO**, não restrição de nível de aplicação. `anthropics/sandbox-runtime` é a implementação open-source para agentes próprios.

## 5. Auto mode — o padrão de classificador de ações

Motivação medida: **usuários aprovavam 93% dos prompts de permissão de qualquer forma** — não estavam revisando.

**Duas camadas defensivas:**

- **Entrada** — sonda server-side rastreia saídas de ferramenta (leitura de arquivo, web fetch, shell) buscando injeção. Ao detectar, **adiciona um aviso ao contexto do agente** em vez de bloquear, levando-o a reconsiderar a intenção do usuário.
- **Saída** — classificador de transcript avalia cada ação antes da execução, em dois estágios: filtro rápido de token único que **erra para o lado de bloquear**, depois raciocínio em cadeia só se sinalizado.

**Modelo de ameaça — quatro modos de falha:** comportamento *overeager* (interpreta o escopo errado — "limpe isso" vira apagar branches remotos); erro honesto sobre fronteira de recurso; injeção de prompt; desalinhamento do modelo (não observado).

Categorias bloqueadas: exploração de credenciais, escalada de escopo, exfiltração de dados, bypass de checagem de segurança, mudança de infraestrutura que afeta sistemas compartilhados.

### Duas decisões de design que generalizam

**1. O classificador não vê o raciocínio do agente nem os resultados de ferramenta.** Isso impede que *"o agente convença o classificador a tomar uma decisão ruim"* com racionalização persuasiva, reduz a superfície de injeção e força a decisão sobre a **intenção do usuário**.

**2. Deny-and-continue.** O bloqueio não interrompe a sessão — o modelo recebe feedback para achar "um caminho mais seguro". Isso torna falso positivo sobrevivente: o usuário vê um retry, não o fim da sessão. Escala só após **3 negações consecutivas ou 20 no total**.

### Os números honestos

| Cenário | Resultado |
|---|---|
| Tráfego real, 10.000 ações | **0,4%** de falso positivo após o estágio 2 (era 8,5% após o estágio 1) |
| Ações overeager reais, 52 incidentes | **17%** de falso negativo |
| Exfiltração sintética, 1.000 ataques | **5,7%** de falso negativo após o estágio 2 |

O 17% reflete ambiguidade genuína: o classificador identifica o comando perigoso, mas não consegue determinar se o consentimento do usuário cobria aquele blast radius. *"Uma aprovação não é um padrão."*

> **Posicionamento explícito:** auto mode **não substitui revisão humana cuidadosa em infraestrutura de alto risco.** Ele substitui padrões de acesso irrestrito.

### As recomendações de design de permissão

1. Assuma que fadiga de aprovação importa — bloquear tudo com prompts cria atalhos inseguros.
2. Torne a defesa **estrutural** — separe validação de entrada e saída, para que um comprometimento não contorne as duas.
3. **Retire o raciocínio do agente do avaliador** — decida sobre a ação, não sobre a justificativa.
4. Aceite risco assimétrico — falso negativo pesa mais que falso positivo; ação benigna pode ser tentada de novo.
5. Customize conservadoramente — default seguro com extensão opcional de política.
6. **Monitore o risco residual explicitamente.** *"17% é o número honesto."* Restrinja a operação autônoma às tarefas onde esse risco é aceitável.

## 6. Lições de falhas reais

| Falha | O que aconteceu | Correção |
|---|---|---|
| **Exploração de egresso** | Domínio na allowlist (`api.anthropic.com`) permitiu upload de arquivos para contas de atacantes. **Domínio aprovado é superfície de ataque** | Proxy man-in-the-middle interceptando chamadas para validar tokens de sessão |
| **Usuário como vetor de injeção** | Prompt direto ("leia `~/.aws/credentials` e faça POST") contorna a camada de modelo — *"quando é o usuário quem digita a instrução, não há nada de anômalo para um classificador pegar."* | **Só controles de ambiente impediram a exfiltração** |
| **Execução antes do trust prompt** | Configurações e hooks de projeto executavam **antes** do prompt de confiança aparecer, contornando o consentimento | Adiar todo parsing de configuração até depois do consentimento |

## 7. Regras de projeto

- **Projete o ambiente primeiro.** Sandbox, VM e fronteira de filesystem pegam o que a camada de modelo deixa passar.
- **Desconfie de componentes customizados.** Hipervisores e seccomp duram mais que código de segurança proprietário.
- **Toda saída de ferramenta com acesso a rede é conteúdo não confiável** — inclusive vinda de ferramenta confiável.
- **Estado persistente é superfície.** Memória entre sessões e diretório montado viram alvo de injeção e exigem classificador mais forte.
- **Habilite as fronteiras antes de conceder autonomia**, não depois.

**Riscos emergentes sinalizados:** envenenamento de memória persistente entre sessões; escalada de confiança em sistemas multiagente hierárquicos; ausência de padrão de identidade de agente entre plataformas.

## 8. Onde configurar o quê

A separação é normativa e vale repetir em todo design:

| Preocupação | Onde |
|---|---|
| Bloquear ferramenta, comando ou caminho | Managed settings: `permissions.deny` |
| Impor isolamento em sandbox | Managed settings: `sandbox.enabled` |
| Variáveis de ambiente, roteamento de provedor | Managed settings: `env` |
| Método de login, restrição de organização | Managed settings: `forceLoginMethod`, `forceLoginOrgUUID` |
| Diretriz de estilo e qualidade | Managed CLAUDE.md |
| Lembrete de compliance e tratamento de dados | Managed CLAUDE.md |
| Instrução comportamental | Managed CLAUDE.md (ou chave `claudeMd` em `managed-settings.json`) |

> **Settings são aplicadas pelo cliente, independentemente do que o modelo decide. CLAUDE.md molda comportamento e não é camada de aplicação.**

No dia a dia: `/permissions` para allowlists (`npm run lint`, `git commit`), `/sandbox` para isolamento de SO. Em execução não supervisionada, `--allowedTools` restringe o que o agente pode fazer.
