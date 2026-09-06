# 018 — `metodo`: onde a metodologia se aplica

## Problema

Dois defeitos com a mesma raiz — o plugin não sabe dizer **onde ele vale**.

**O `proteger_testes` age em todo lugar.** Hooks se fundem e disparam em toda sessão
que carrega o plugin. Instalado o `metodo`, ninguém consegue editar um teste existente
em repositório nenhum, tenha ele adotado a metodologia ou não. Para um plugin feito
para ser instalado amplamente, é agressivo demais — e o resultado previsível é a pessoa
desinstalar em vez de configurar.

**O portão não acha a configuração em monorepo.** `verificar_suite.py` procura
`.claude/metodo.json` só no `cwd`. Configuração de projeto **não é herdada de diretório
pai**, e a doc recomenda iniciar a sessão de dentro do pacote — então o portão bloqueia
todo turno, com "não há verificação declarada". Medido em árvore de teste; segue aberto.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O `proteger_testes` vale em qualquer repositório | Vale onde o projeto **aderiu** |
| O portão não acha a config a partir de um subdiretório | Acha, subindo até a raiz do repositório |

## Critérios de aceitação

- [ ] A busca de `.claude/metodo.json` sobe do diretório da sessão até a **raiz do
      repositório git**, e para lá — não segue subindo pelo sistema de arquivos
- [ ] Numa árvore de monorepo, iniciar de `packages/api/` encontra a configuração
      declarada na raiz
- [ ] O `proteger_testes` só age quando o projeto **aderiu** — presença de
      `.claude/metodo.json`, encontrada pela mesma busca
- [ ] Sem adesão, ele **libera** e não imprime nada: um plugin instalado não deve
      comentar em projeto que não o adotou
- [ ] A adesão é procurada a partir do **caminho do arquivo** que está sendo editado,
      não do `cwd` — num monorepo eles divergem
- [ ] **Negativo:** com adesão, tudo que bloqueava antes continua bloqueando. Os casos
      atuais da suíte seguem passando sem alteração
- [ ] **Negativo:** a busca não segue link simbólico para fora do repositório, nem sobe
      além da raiz git
- [ ] **Negativo:** o portão continua fail-closed. Não achar a raiz git não vira
      "libere"

## Fora de escopo

- A camada de `permissions` — ticket 019
- Suporte a múltiplas verificações por caminho num monorepo: aqui o alvo é **achar** a
  configuração, não declarar várias. Se for preciso, vira ticket próprio

## Verificação

A suíte cobre, com árvore de monorepo montada em diretório temporário: raiz com
config, pacote sem, e o hook chamado com `cwd` no pacote. Conjunto balanceado — o caso
que prova que **sem adesão não age** vale tanto quanto os que provam que com adesão age.

## Prefactoring

Necessário? ( ) não · (x) **sim, dentro da fatia** — os dois hooks vão precisar da
mesma função de "suba até a raiz e ache a config". Extrair antes de usar nos dois, e
não duplicar.
