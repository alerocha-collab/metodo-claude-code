# 021 — o marketplace, e a portabilidade provada num repositório limpo

## Problema

O documento de arquitetura diz, sobre os dois plugins:

> nenhum deles jamais rodou fora deste repositório.

Isso não é um detalhe pendente — é **a premissa do desenho inteiro**. `metodo` existe
para carregar a metodologia *entre* projetos; `doutrina` foi separado em plugin próprio
justamente porque instalar um segundo plugin provaria a portabilidade. Se a instalação
não funcionar, os dois são bibliotecas de um repositório só, com cerimônia de plugin.

Até hoje tudo rodou por `--plugin-dir`, que é o modo de **desenvolvimento**: aponta para
a pasta local, não copia, não resolve fonte, não passa pelo cache. Ele não exercita nada
do caminho de instalação.

O que falta é o `marketplace.json`. Ele foi adiado na Fase 1 com uma razão explícita —
"cerimônia antes do segundo projeto" — e o segundo projeto agora é o ponto.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Só `--plugin-dir`, que não exercita instalação | `claude plugin install` funciona, medido |
| A portabilidade é premissa | É resultado de um exercício registrado |
| Nada liga `version` do plugin ao que se publica | A suíte reprova se os dois divergirem |

## Critérios de aceitação

- [ ] `.claude-plugin/marketplace.json` na **raiz do repositório** — não dentro de
      `plugins/`, e não junto de nenhum `plugin.json`
- [ ] As duas entradas usam `source` de caminho relativo (`./plugins/<nome>`), que é o
      que funciona com o marketplace e os plugins no mesmo repositório
- [ ] `claude plugin validate .` passa na raiz, e entra no CI ao lado das duas
      validações de plugin que já existem
- [ ] `tests/testar_marketplace.py`, conjunto balanceado: o marketplace real passa, e
      marketplaces inventados com defeito **reprovam** — `source` apontando para pasta
      que não existe, `name` divergindo do `plugin.json` de destino, `version`
      divergindo, e falta de campo obrigatório
- [ ] **Negativo:** um marketplace inventado que está *correto* precisa passar. Sem
      esse caso, um validador que reprova tudo passaria na suíte
- [ ] O exercício de instalação é feito **num repositório limpo, fora deste**, e o
      resultado é registrado — inclusive se falhar
- [ ] O README diz como instalar de verdade, e mantém `--plugin-dir` nomeado como o
      modo de desenvolvimento que é

## Fora de escopo

- Publicar num marketplace de terceiros ou anunciar o repositório
- `dependencies` entre os dois plugins: `doutrina` e `metodo` são independentes de
  propósito, e declarar dependência agora desfaria a separação da Fase 2
- Automatizar o bump de `version`: continua disciplina, e a suíte só o torna visível

## Verificação

O exercício, num repositório descartável que não é este:

1. adicionar o marketplace por caminho local, com escopo de projeto
2. instalar `doutrina`
3. abrir uma sessão ali e fazer **uma das perguntas da bateria** — se a skill não
   aparecer ou não responder, a portabilidade não está provada, e o resultado negativo
   vale tanto quanto o positivo

O escopo de projeto importa: mantém o exercício dentro da pasta descartável em vez de
escrever na configuração do usuário.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
