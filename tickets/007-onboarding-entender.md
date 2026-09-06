# 007 — `onboarding-entender`: o mapa do que existe

## Problema

A metodologia sabe partir de uma spec. Não sabe partir de um repositório que já
existe — e a maior parte do trabalho real é esse. Sem uma etapa de entendimento, o
agente começa a fatiar sobre suposições, e a primeira fatia descobre que o sistema
funciona de outro jeito.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| A trilha começa em `fatiar`, que pressupõe entendimento | Existe `/metodo:onboarding-entender`, que produz o mapa antes |
| O que se sabe do projeto vive na cabeça de quem já mexeu | Vive em disco, legível por uma sessão nova |

## Critérios de aceitação

- [ ] A skill produz um **artefato em disco**, não uma resposta em chat — a próxima
      sessão precisa lê-lo sem repetir o trabalho
- [ ] O mapa cobre, no mínimo: como se roda o projeto, como se roda a verificação, os
      pontos de entrada, e as fronteiras externas de que ele depende
- [ ] O mapa registra **o que não foi entendido**, nomeadamente. Um mapa com lacunas
      declaradas é útil; um que finge cobertura completa é pior que nenhum
- [ ] O texto segue a regra de durabilidade: descreve interfaces e contratos, **não**
      caminhos de arquivo nem números de linha
- [ ] A skill **não** propõe mudanças, não critica o código e não abre tickets — quem
      entende ainda não sabe o suficiente para julgar
- [ ] A skill busca os fatos sozinha em vez de perguntar o que consegue ler
- [ ] **Negativo:** rodá-la duas vezes não duplica o artefato; ela atualiza ou recusa
- [ ] **Negativo:** ela não escreve `CLAUDE.md` nem `AGENTS.md` já existentes

## Fora de escopo

- Julgar qualidade de código — é a Fase 5, e vem depois da conformidade
- Extrair o glossário de domínio: é o ticket 008
- Comparar com um alvo: é o ticket 009
- Suporte a monorepo com múltiplos projetos independentes

## Verificação

A suíte cobre o que for script. O formato do artefato se verifica rodando a skill
num repositório real e conferindo se uma sessão nova consegue trabalhar só com ele.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
