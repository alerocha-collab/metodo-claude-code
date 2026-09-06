# 004 — Declarar e verificar a dependência de python3

## Problema

Os dois hooks e os dois scripts exigem `python3` no PATH. O plugin não declara essa
dependência em lugar nenhum e não a verifica. Numa máquina sem `python3`, o portão
**bloqueia todo turno** com `can't open file` — fail-closed, portanto seguro, mas com
uma mensagem que não diz o que fazer.

A escolha por Python foi deliberada: hooks rodam em `sh` no macOS/Linux, Git Bash no
Windows, ou PowerShell quando Git Bash não está instalado, e um `.sh` não cobriria os
três. O problema não é a escolha — é ela ser tácita.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Dependência tácita | Declarada no README, na seção de instalação |
| Falha com mensagem críptica do interpretador | Falha nomeando a dependência ausente e como resolver |

## Critérios de aceitação

- [ ] O README declara a dependência e a versão mínima
- [ ] Numa máquina sem `python3`, a mensagem que o usuário vê **nomeia** a dependência
      ausente — não apenas `can't open file`
- [ ] A verificação continua **fail-closed**: ausência de interpretador bloqueia,
      nunca libera
- [ ] O CI cobre o caso, rodando ao menos um cenário em que a dependência falta
- [ ] **Negativo:** nenhuma reescrita dos hooks para outra linguagem. O escopo é
      declarar e diagnosticar, não trocar a base

## Fora de escopo

- Empacotar um interpretador junto do plugin
- Python 2, ou versões abaixo da mínima declarada
- Resolver `python` vs `python3` em toda plataforma: declarar `python3` e documentar o
  contorno basta

## Verificação

A suíte cobre, mais o cenário novo no CI.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
