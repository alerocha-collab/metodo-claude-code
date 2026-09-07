# 028 — A verificação precisa ser executada, não localizada

## Problema

Primeiro uso real do `onboarding-entender`, contra um projeto de verdade. O mapa
produzido é bom — 403 linhas, divisão durável × volátil, oito buracos declarados, três
afirmações conferidas e todas verdadeiras. E contém **uma frase falsa**, justamente
sobre a coisa mais importante:

> *"O portão do Stop roda de verdade."*

Não roda. Os cinco hooks daquele projeto declaram caminhos com `\`, o Claude Code roda
hooks em Git Bash naquela máquina, e o bash come as barras: `.claude\hooks\portao.cmd`
vira `.claudehooksportao.cmd`. Os hooks falharam **três vezes durante a própria sessão
que escreveu o mapa**.

## Por que não foi desatenção

Medido na doc: *"Stderr from a hook that exits 0 goes to the debug log only, never the
transcript, and Claude never sees it."* Falha não bloqueante mostra a primeira linha do
stderr **ao usuário**, no transcript da interface — e **exit 2 é o único código que
devolve o stderr ao modelo**.

O agente estava **estruturalmente cego**. Instruir "repare no erro do hook" seria
inútil: ele não recebe esse texto.

E ele fez o que a skill mandava. A instrução diz para **encontrar** como se verifica; ele
encontrou, rodou o comando à mão — inclusive descobrindo sozinho o `cmd //c` que o Git
Bash exige — e confirmou que o script sai 0. O que ninguém pediu foi confirmar que **a
ligação** funciona.

Verificar que o script funciona não é verificar que ele é executado. A diferença é o
modo de falha mais perigoso que existe: o portão que parece existir.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| A skill localiza o comando de verificação | Ela **executa** e registra a saída |
| Hook declarado é dado como ativo | Cada hook é provado, ou listado como não provado |
| Um projeto com portão desligado tira nota alta | O portão desligado vira o achado em destaque |

## Critérios de aceitação

- [ ] `onboarding-entender` passa a **executar** a verificação que encontrou, e a
      registrar a saída real no mapa — não a existência do comando
- [ ] Passa a provar cada hook declarado em `settings.json`: o comando **resolve** no
      shell em que os hooks rodam? Hook que não resolve é achado em destaque, não nota
      de rodapé
- [ ] O mapa distingue três estados, porque hoje ele só tem dois: **verificado
      rodando**, **declarado e não provado**, **ausente**
- [ ] A skill diz por que a prova é necessária: o modelo **não vê** falha de hook não
      bloqueante, então ausência de erro na tela não é evidência de nada
- [ ] Armadilha nova no `doutrina`: no Windows não existe caminho de hook que funcione
      em Git Bash **e** em cmd, e o Claude Code escolhe o shell pela presença do Git Bash
- [ ] A mesma armadilha registra que **só exit 2 devolve stderr ao modelo** — é o que
      decide se um agente consegue se autodiagnosticar
- [ ] **Negativo:** a skill continua sem propor mudanças. Ela relata que o portão está
      desligado; consertar é da `onboarding-lacunas` em diante

## Fora de escopo

- Consertar os hooks do projeto de teste. O mapa é reconhecimento, não conserto
- Ticket 027 (o portão barrando quem não adotou) segue separado

## Verificação

Reexecutar `/metodo:onboarding-entender` no mesmo projeto e conferir que o mapa novo
**acusa** os cinco hooks inertes. O projeto não muda entre as duas execuções, então a
diferença é só a skill — e a reexecução também exercita o caminho "atualize o mapa, não
crie um segundo", que nunca rodou.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
