---
name: onboarding-entender
description: Levanta o mapa de um repositório que já existe — como se roda, como se verifica, quais são os pontos de entrada e as fronteiras externas — e escreve o que ficou sem entender. Use ao começar a trabalhar num projeto que você não conhece, antes de fatiar qualquer coisa.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Task, Write, Edit
---

# Entender o que já existe

A metodologia sabe partir de uma spec. Esta skill é a primeira das três que ensinam
a partir de um **repositório**, que é de onde a maior parte do trabalho real parte.

Você produz um mapa. **Não** propõe mudanças, **não** critica o código, **não** abre
tickets. Quem acabou de entender ainda não sabe o suficiente para julgar — e um
julgamento precoce contamina as duas etapas seguintes.

## Ache os fatos você mesmo

Não pergunte o que dá para ler. Rode, leia, procure. Um `--help`, um arquivo de
build, uma configuração de CI valem mais que três perguntas, e custam menos do que
a atenção que elas gastariam.

Para varredura ampla — "que convenções este repositório segue", "onde estão as
fronteiras externas" — despache subagentes. Eles devolvem a conclusão sem que os
arquivos que leram fiquem na sua janela.

Pergunte só o que o repositório não responde: por que algo é como é, o que está
planejado, qual dor motivou a sessão.

## O mapa, em duas metades

Esta separação é o coração do artefato.

### Metade durável — o que continua verdade depois de uma refatoração

- **O que o sistema faz**, em uma ou duas frases, do ponto de vista de quem usa.
- **Como se roda**, e **como se verifica**. Não basta achar o comando: **rode-o**, e
  registre a saída real. Se não houver comando que produza verde/vermelho, isso é o
  achado mais importante do mapa — registre em destaque, porque bloqueia tudo que vem
  depois.
- **Capacidades e contratos**: o que o sistema expõe e com que forma. "Aceita um
  arquivo de configuração em JSON e produz um relatório HTML" sobrevive a qualquer
  reorganização de pastas.
- **Fronteiras externas**: de que serviços, APIs, bancos e formatos de terceiro ele
  depende. É onde moram os riscos que ninguém controla.
- **Convenções observadas**: como este repositório faz as coisas, quando há padrão.

### Metade volátil — o que vai envelhecer, e está marcado como tal

Localizações. Onde fica o ponto de entrada, onde ficam os testes, onde mora a
configuração.

Isso é útil demais para omitir e frágil demais para confiar. Então vai numa seção
**explicitamente marcada como volátil**, com a instrução de conferir antes de usar,
e **com o SHA do commit em que foi levantada**.

A alternativa — escrever caminhos junto com o resto — produz um documento que parece
todo confiável e é metade mentira em dois meses. A separação é o que permite ao mapa
envelhecer **em público**.

## Prove que a verificação roda — não que ela existe

Achar o comando não é achar a verificação. Um repositório pode ter portão declarado,
script correto, suíte verde **e o portão desligado** — e é o pior caso possível, porque
tudo aparenta estar certo.

**Você é cego para isso por construção.** Falha de hook que não bloqueia manda a
mensagem para a tela do usuário, e **não para o seu contexto**: só `exit 2` devolve
stderr ao modelo. Ausência de erro na sua frente não é evidência de nada.

Então prove, em vez de supor. Para cada hook declarado em `.claude/settings.json`:

1. **O comando resolve no shell em que os hooks rodam?** Execute-o do mesmo jeito que o
   harness executaria. `command not found` ali é achado de destaque, não nota de rodapé.
2. **Rodar o script à mão não conta como prova da ligação.** Um caminho pode funcionar
   quando você o digita e falhar quando o harness o dispara — no Windows isso é o caso
   comum, não a exceção.

Registre cada verificação em um de **três** estados, nunca dois:

| Estado | Significa |
|---|---|
| **Verificado rodando** | você executou e viu a saída |
| **Declarado, não provado** | existe na configuração e você não conseguiu confirmar que dispara |
| **Ausente** | não há |

Um mapa que só distingue "existe" de "não existe" transforma portão desligado em
aprovação.

## Escreva o que você não entendeu

Seção obrigatória, e a mais valiosa do artefato.

Todo mapa tem buracos. O que separa um mapa útil de um perigoso é declarar quais são:
*"não entendi como a autenticação decide o escopo"*, *"há um diretório `legacy/` que
ninguém explicou"*, *"a suíte tem três testes marcados para pular há dois anos"*.

Um mapa que finge cobertura completa faz a próxima sessão confiar onde não devia. Um
mapa com buracos declarados diz exatamente onde perguntar.

## Reexecução

Se o mapa já existe, **atualize-o**; não escreva um segundo. Dois mapas divergentes
são pior que nenhum, porque quem lê não sabe qual vale.

Ao atualizar, o SHA da seção volátil muda junto. E o que era buraco e deixou de ser
sai da lista — buraco que já foi tapado e continua listado ensina a ignorar a lista.

## Não toque no que já é de outro

**Nunca crie `AGENTS.md` onde já existe `CLAUDE.md`, nem o contrário.** Se um dos dois
existir, e algo do mapa pertencer lá, proponha o trecho e deixe a decisão com o
humano. São arquivos que o projeto já governa.

O mapa é artefato novo, em `docs/`. Não sequestra os que já estão lá.

## Depois

O passo seguinte é `/metodo:onboarding-modelar`, que extrai o vocabulário do código
usando este mapa como ponto de partida — em vez de reler o repositório do zero.
