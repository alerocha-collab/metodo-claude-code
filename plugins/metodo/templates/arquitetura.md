# Template — documento de arquitetura de um sistema com agentes

Copie para `docs/arquitetura.md` do seu projeto e preencha. **Seção sem conteúdo é sinal
de que o passo correspondente não foi feito** — volte e faça, não escreva "N/A".

Este arquivo é a **forma** do entregável. O **conteúdo** — quando usar agente, qual
padrão, como avaliar — vem do plugin `doutrina`: fichas `arquitetar`, `avaliar`,
`onde-colocar` e `garantir`. Sem ele, você preenche de memória, que é exatamente o modo
de falha que este documento existe para evitar.

---

## As sete regras que o documento precisa respeitar

Elas prevalecem sobre preferência de quem pede. Se a pessoa insistir depois de você
explicar, **registre a divergência na seção 9 e siga**.

1. **Todo componente proposto vem com a suposição que ele codifica, por escrito** — "este
   avaliador existe porque assumo que o modelo não critica o próprio trabalho" — e com o
   teste que a derruba. Componente sem suposição nomeada não entra.
2. **Nada é declarado pronto sem verificador executável.** Sem teste, build, linter, diff
   contra fixture ou screenshot comparável que produza pass/fail legível, o projeto está
   mal posto. Diga isso **antes** de desenhar qualquer outra coisa.
3. **Regra dura nunca vai para arquivo de instrução ou skill.** "Nunca edite X" é pedido.
   Regra que precisa valer sempre vira hook ou regra de permissão.
4. **Multiagente exige orçamento declarado.** ~15× mais tokens que chat. Nunca proponha
   sem afirmar por que a tarefa vale isso. Se não vale, proponha agente único.
5. **Cada mecanismo declara o custo de contexto:** carrega sempre, sob demanda, ou
   isolado. Design sem orçamento de contexto não é design.
6. **Cite a fonte** de toda recomendação normativa. Se não consegue citar, é opinião —
   marque como tal.
7. **Simplifique por padrão.** Entre dois desenhos que resolvem, o menor vence. Não
   invente camada por simetria.

## O viés a combater

O modo de falha dominante é **superengenharia**: propor planner + gerador + avaliador +
memória + quatro hooks para o que um prompt bem escrito resolve.

> *"Comece com a solução mais simples e só aumente a complexidade quando necessário."*

E harness envelhece. Componentes obrigatórios num modelo ficam desnecessários no
seguinte. Por isso a **seção 8 é obrigatória**: todo design diz quando revisitá-lo.

---

```markdown
# Arquitetura — <nome do sistema>

**SHA:** `<commit que este texto descreve>` · **Data:** <AAAA-MM-DD>

## 1. Problema e critério de pronto

**O que se constrói:** <uma frase>
**Quem opera:** <dev que avalia comandos | knowledge worker | pipeline sem humano>
**Duração de uma execução:** <minutos | horas | múltiplas sessões>

**Pronto significa:** <critério verificável, não adjetivo>
**Fora de escopo:** <o que deliberadamente não se resolve aqui>

## 2. Degrau de complexidade

**Parada no degrau <0–4>: <nome>.**
Por que o anterior não bastou: <...>
Por que o próximo não se paga: <...>

<Se 3 ou 4:> **Custo declarado:** ~15× os tokens de um chat.
A tarefa justifica porque <razão concreta e mensurável>.

## 3. Loop de verificação

**Comando que produz pass/fail:** `<comando literal>`

- Cobertura de casos negativos: <como>
- Proteção contra regressão: <como>
- Custo de contexto da saída: <resumo? amostragem? formato parsável?>
- Confiança: <alta | média | baixa — e o que a melhoraria>

**Dureza do portão:** <no prompt | na sessão | Stop hook | revisor em contexto novo>
**Quem dá a nota:** <e por que não é quem faz>

## 4. Alocação de mecanismos

| Mecanismo | Responsabilidade | Quando carrega | Autoridade |
|---|---|---|---|

## 5. Orçamento de contexto

| O que | Sempre / sob demanda / isolado | Custo medido |
|---|---|---|

## 6. Fronteira de segurança

Filesystem: <...> · Rede: <...> · Modo de permissão: <...>
O que nunca pode acontecer, e qual camada garante: <...>

## 7. Plano de evals

Tarefas iniciais (20–50, vindas de falhas reais): <...>
Graders: <código / modelo / humano, e por quê>
Métrica: <pass@k ou pass^k — e o motivo da escolha>

## 8. Suposições e quando revisar

| Suposição | O que a derruba |
|---|---|

**Gatilho de revisão:** <fim de fase, modelo novo, mudança relevante da plataforma>
Nunca por calendário — documento com data de revisão é documento que ninguém revisa.

## 9. Divergências registradas

<Onde quem pediu discordou de uma das sete regras, e o que se decidiu>

## 10. Fontes

<URL de cada recomendação normativa>
```

---

## Antes de entregar

- [ ] Cada seção preenchida, nenhuma com "N/A"
- [ ] O degrau escolhido tem justificativa nos **dois** sentidos: por que não o anterior,
      por que não o próximo
- [ ] Existe um comando literal que produz pass/fail
- [ ] Toda suposição da seção 8 tem o teste que a derruba
- [ ] Nenhuma recomendação normativa sem fonte, ou marcada como opinião
