# Decisões

> **Append-only.** Entradas novas vão no fim. Uma decisão errada não se apaga — se
> revoga com uma entrada nova que a substitui, citando o número da antiga.
>
> A barra de entrada aqui é mais baixa que a de um ADR. ADR é para decisão difícil
> de reverter, surpreendente sem contexto e resultado de um trade-off real. Aqui
> entra tudo que alguém perguntaria "por que está assim?" daqui a três meses.

---

## Formato

```
## NNN — <título em uma linha>

**Data:** AAAA-MM-DD · **SHA:** <sha curto do commit em que a decisão vale>

**Contexto.** O que estava em jogo, em duas ou três frases.

**Decisão.** O que foi decidido, na voz ativa.

**Alternativa descartada.** O que não se escolheu, e o custo de tê-la escolhido.

**Como saber que envelheceu.** O sinal que indica revisitar isto.
```

A linha *Alternativa descartada* é obrigatória. Decisão sem alternativa registrada
não é decisão — é o caminho default, e não precisava de entrada.

---

## 001 — <primeira decisão>

**Data:** — · **SHA:** —

**Contexto.**

**Decisão.**

**Alternativa descartada.**

**Como saber que envelheceu.**
