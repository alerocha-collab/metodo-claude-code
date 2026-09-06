# NNN — <título em uma linha, no imperativo>

> Este arquivo é a **spec desta fatia**. Ele existe porque o agente não pode
> perguntar: quando alguém pegar este ticket, a conversa que o originou já não
> estará disponível.
>
> **Durabilidade acima de precisão.** Este texto pode ficar parado por semanas
> enquanto o código muda. Escreva-o para continuar útil depois que arquivos forem
> renomeados, movidos ou refatorados: descreva **interfaces, tipos e contratos de
> comportamento**. Não cite caminho de arquivo. Não cite número de linha. Eles
> envelhecem primeiro e levam o resto junto.
>
> **Comportamental, não procedimental.** Bom: "o tipo `Config` deve aceitar um
> campo opcional `schedule`". Ruim: "abra src/tipos.ts e some um campo na linha 42".

## Problema

O que está errado ou faltando hoje, do ponto de vista de quem usa. Duas ou três
frases. Se você precisa de mais, ou a fatia é grande demais, ou o problema não está
entendido.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| | |

## Critérios de aceitação

> **Regra dura.** Estes critérios entram **antes** de a implementação começar e
> **não são editados durante**. Critério alterado no meio é o alvo se ajustando ao
> tiro. Se um se revelar impossível ou mal formulado, isso é conversa com o humano —
> não edição de quem está sendo medido por ele.

Cada critério é uma condição **verificável**, não um adjetivo. O teste: alguém que
não participou desta conversa consegue decidir se ele foi atendido, sozinho?

- [ ] Bom: "rodar `<comando>` com `<entrada>` retorna `<saída>`"
- [ ] Ruim: "a triagem deve funcionar corretamente"

## Fora de escopo

A seção mais barata e a mais valiosa do ticket — é o que impede gold-plating.
Nomeie explicitamente o que **não** entra, sobretudo o que seria tentador fazer de
passagem.

-

## Verificação

O comando que decide verde/vermelho para esta fatia, e o que se espera dele. Se a
verificação do projeto (`.claude/metodo.json`) já cobre, escreva "a suíte cobre" e
siga.

## Prefactoring

Se esta fatia fica mais fácil com uma mudança estrutural antes dela, **essa mudança
é outro ticket**, e este fica bloqueado por ele. Refatoração não acontece dentro do
ciclo vermelho → verde.

- Necessário? ( ) não · ( ) sim, ticket NNN
