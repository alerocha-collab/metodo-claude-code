---
name: onboarding-lacunas
description: Mede a distância entre um repositório que já existe e o que a metodologia pressupõe, e transforma essa distância em fila de tickets — só o caminho crítico, com regra escrita de quando o resto entra. Use depois do mapa e do glossário.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Task, Write, Edit
---

# A distância até o alvo, como fila

Última das três skills de reengenharia. Você já sabe o que o projeto faz (o mapa) e
como ele nomeia as coisas (o glossário). Falta a pergunta que decide o trabalho:
**o que falta aqui que a metodologia pressupõe?**

**A saída é fila, nunca relatório.** Relatório de conformidade é lido uma vez,
concordado, e nunca executado. Fila é trabalhada.

## O caminho crítico não é o que está mais quebrado

Esta é a decisão que define a skill, e ela precisa ser dita em voz alta porque a
intuição puxa para o lado errado.

**Caminho crítico é o que destrava outro trabalho.** Não o mais grave, não o mais
feio, não o que mais incomoda. Em ordem de dependência:

**1. O verificador.** Existe um comando que produz verde/vermelho com exit code
confiável? Se não, **nada mais importa até isso existir**. Sem verificador não há
portão, não há fatia demonstrável, e não há como despachar trabalho sem alguém
olhando. Todo o resto da metodologia pressupõe esta linha.

E ele precisa ser **provado contra o vermelho**: quebre algo de propósito e confirme
que o comando sai diferente de zero. Verificador nunca testado contra o vermelho é
uma esperança, não um verificador.

**2. A fila.** Existe unidade de trabalho dimensionada, com critérios de aceitação
escritos antes? Sem ela não há estado para ler, e a decisão de que sessão = um
ticket não tem onde se apoiar.

**3. O registro de decisões.** Um `DECISIONS.md` é barato e é onde aterrissam as
divergências que o glossário levantou. Sem ele, elas voltam a ser conversa.

**4. Todo o resto.** Cobertura de teste, CI, convenções, documentação. Nada disso
destrava outra coisa — cada um se paga sozinho, quando a área for tocada.

Se o projeto já resolve 1, 2 ou 3 de outro jeito, **isso não é lacuna**. Ver abaixo.

## O resto entra quando a área for tocada

Não tente conformidade total numa passada. É o modo de falha desta skill, e o
antídoto é velho: não se para o desenvolvimento para testar todo o código antigo —
aplica-se teste sob demanda, ao corrigir bug, ao adicionar feature, ao refatorar, e
vai-se mordendo as metas grandes aos poucos.

Então a saída tem duas partes:

- **os tickets do caminho crítico**, enfileirados agora;
- **uma regra escrita** de que o resto entra quando a área for tocada.

E a regra **vira entrada no `DECISIONS.md`**, não linha solta na conversa. Ela é uma
decisão de verdade: escolhemos conformidade incremental, descartamos conformidade
total numa passada, e o custo da descartada era parar o desenvolvimento por semanas
para chegar a um estado que envelhece sozinho.

**Contra-exemplo do que não fazer:** enfileirar "adicionar testes ao módulo X" para
cada módulo sem teste. Vinte tickets que ninguém pega, e a fila deixa de ser
confiável — o que é pior do que não ter fila, porque `/metodo:fluxo` passa a
recomendar trabalho que ninguém vai fazer.

## O que o projeto já resolve não se substitui

**A reconciliação é bidirecional.** Um projeto maduro pode ter resolvido melhor do
que a metodologia prescreve, e impor o padrão por cima destruiria mecanismo superior.

Quando encontrar um mecanismo existente que cobre o mesmo propósito de outro jeito,
o resultado **não é um ticket de substituição**. É uma entrada de decisão a tomar,
com os dois lados escritos:

- o que o projeto faz hoje, e o que isso lhe dá;
- o que a metodologia propõe, e o que isso lhe daria;
- o que se perde em cada caminho.

A decisão é do humano. Substituir em silêncio um mecanismo que funciona é o dano
mais caro que esta skill pode causar, porque ele só aparece depois — quando o que
foi trocado era o que segurava alguma coisa.

## Os tickets que você gera não têm desconto

Origem automática **não dispensa** nenhuma regra:

- critérios de aceitação escritos **antes**, verificáveis, com ao menos um negativo;
- seção **fora de escopo** preenchida;
- `modulo` preenchido, para bloquear a próxima fatia que tocar o mesmo lugar;
- brief pelo `templates/ticket.md`, com a regra de durabilidade;
- arestas de bloqueio só onde há dependência real.

Ticket gerado em lote tende a ficar vago — "melhorar a cobertura", "organizar os
módulos" — e critério vago é critério que se satisfaz sozinho. Se você não consegue
escrever o critério verificável, **a lacuna ainda não está entendida**: registre-a
como pergunta em aberto no mapa, não como ticket.

## Feche validando

```bash
python3 plugins/metodo/scripts/validar_fila.py tickets/fila.json
```

Fila que não passa não é entrega. E antes de terminar, confira o inverso: se você
gerou mais de uma dúzia de tickets, quase certamente extrapolou o caminho crítico —
releia a seção acima antes de entregar.

## O que entregar ao humano

- quantas lacunas, e **qual critério de caminho crítico** você aplicou;
- os tickets enfileirados, em ordem de bloqueio;
- as **decisões a tomar** — onde o projeto já resolve de outro jeito;
- o que ficou de fora, e a regra de quando entra;
- as lacunas que você não conseguiu transformar em critério verificável.

Termine perguntando o que revisar primeiro. Fila aprovada por leitura rápida é fila
não revisada.
