# Critérios de aceitação

Carregue este arquivo antes de escrever o primeiro critério de um ticket.

## O problema que estes critérios resolvem

Você redige os critérios; outra pessoa aprova. A transferência é deliberada — você é
genuinamente bom nisto, e a maioria das pessoas escreve critério ruim. Mas ela tem um
modo de falha específico e silencioso:

> **O agente escreve o critério que sabe satisfazer.**

O resultado é auto-avaliação disfarçada de contrato: todos os critérios marcados,
verificação verde, e a feature não faz o que se queria — porque os critérios
descreviam o que foi construído, não o que era necessário.

E não adianta contar com a revisão para pegar: **critério complacente é, por
construção, plausível.** Ele passa em leitura rápida justamente porque parece bem
escrito. A defesa tem que estar na escrita, não na aprovação.

## O teste que decide

> Alguém que **não participou desta conversa** consegue decidir sozinho se o
> critério foi atendido?

Se precisa perguntar o que você quis dizer, o critério não está pronto. Se precisa
ler o código para decidir, o critério descreve implementação e não comportamento.

## Bom e ruim

| Ruim | Por quê | Bom |
|---|---|---|
| "A triagem deve funcionar corretamente" | "Corretamente" segundo quem? Não é decidível | "Rodar `gh issue list --label needs-triage` devolve apenas issues que já passaram pela classificação inicial" |
| "O parser fica mais robusto" | Adjetivo comparativo sem linha de base | "Entrada com BOM UTF-8 é lida sem erro; hoje ela levanta `UnicodeDecodeError`" |
| "Adicionar validação de e-mail" | Descreve a tarefa, não o resultado | "Cadastro com e-mail sem `@` é recusado com mensagem citando o campo; com `@` é aceito" |
| "Refatorar o módulo de pagamento" | Não é comportamento; é trabalho | (Não é critério. Isso é um ticket de prefactoring, e o critério dele é "a verificação continua verde e nenhum comportamento observável mudou") |
| "Cobertura de testes acima de 80%" | Mede a suíte, não a feature. Satisfaz-se com teste vazio | "Os três caminhos de erro do fluxo de importação — arquivo ausente, formato inválido, linha malformada — têm teste que falha se o tratamento for removido" |
| "A performance melhora" | Sem número e sem condição | "A listagem de 10 mil registros responde em menos de 300 ms na máquina de CI" |

## Quatro armadilhas específicas

**1. Critério que se satisfaz apagando coisa.** "A suíte passa" satisfaz-se deletando
o teste que falha. Prefira "a suíte passa **e** o teste `X` continua existindo e
cobrindo `Y`". O hook que protege os testes existe pela mesma razão — mas o critério
não deve depender dele.

**2. Critério tautológico.** Se a verificação recomputa o esperado do mesmo jeito que
o código, ela passa por construção e nunca pode discordar. O valor esperado tem que
vir de fora — do enunciado do problema, não da implementação.

**3. Critério acoplado à implementação.** Se ele quebra quando alguém refatora sem
mudar comportamento, está descrevendo a estrutura, não o resultado. É o mesmo defeito
de citar caminho de arquivo no brief, e envelhece igual.

**4. Critério com "e também".** Dois critérios num só quase sempre significa que a
fatia é duas fatias.

## Quantidade

Três a seis por ticket costuma bastar. Um só normalmente significa que a fatia é
trivial ou que o critério está vago demais. Mais de oito costuma significar que a
fatia é grande demais — releia o dimensionamento antes de escrever o nono.

## Escreva também o negativo

Todo conjunto de critérios deve dizer também o que **não** deve acontecer, ao menos
uma vez. Conjunto só de casos positivos aprova uma implementação que faz o certo
**e** faz coisas erradas de passagem.

O exemplo mais barato: "nenhum comportamento existente coberto pela verificação atual
muda".

## Onde eles vivem

No brief do ticket, seção **Critérios de aceitação**, em caixinhas `- [ ]`.

Uma vez que a implementação começa, **eles não são editados**. Se um se revelar
impossível ou mal formulado, o construtor para e devolve a decisão ao humano. Um
critério corrigido no meio da implementação não é mais um contrato — é uma descrição
do que foi feito.
