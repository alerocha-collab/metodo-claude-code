# Baseline de smells — eixo Standards

Catálogo mínimo para o revisor do eixo Standards. Vai inteiro no briefing dele.

> **Precedência.** O repositório sobrepõe este baseline. Se uma convenção documentada
> do projeto contradiz algo daqui, a convenção local vence e **não** é reportada como
> achado. Este catálogo cobre o que o projeto não decidiu, não o que ele decidiu
> diferente.

## O smell que mais importa hoje

**Speculative Generality** — abstração, parâmetro, camada ou gancho acrescentado para
uma necessidade que a spec não tem.

> Remédio: apague. Faça o inline de volta. Espere a necessidade real aparecer.

Está no topo por um motivo que mudou recentemente. YAGNI nasceu contra ansiedade
humana — o programador que abstrai porque "um dia vai precisar". Hoje o antagonista é
outro: **gerar ficou quase gratuito, manter não.** Um agente produz uma camada
especulativa em segundos, com prosa convincente justificando-a, e a justificativa é
mais persuasiva que a do humano ansioso.

Sinais concretos: parâmetro que só tem um valor em todas as chamadas · interface com
uma só implementação · ponto de extensão que nada estende · tratamento de erro para
caso que não pode ocorrer · configuração que ninguém configura.

## O catálogo

| Smell | O que é | Remédio |
|---|---|---|
| **Duplicated Code** | A mesma lógica em mais de um lugar | Extraia. *Once and only once* |
| **Long Function** | Faz coisas demais; não cabe na cabeça de uma vez | Extraia funções com nome que diga a intenção |
| **Large Class** | Responsabilidades demais no mesmo lugar | Separe por eixo de mudança |
| **Long Parameter List** | Muitos parâmetros, ou muitos booleanos | Agrupe em objeto; considere que a função faz duas coisas |
| **Divergent Change** | Um módulo muda por razões independentes entre si | Separe: cada módulo, um eixo de mudança |
| **Shotgun Surgery** | Uma mudança obriga a tocar muitos módulos | O inverso do anterior: junte o que muda junto |
| **Feature Envy** | Uma função usa mais dados de outro objeto que do seu | Mova-a para onde os dados estão |
| **Data Clumps** | Os mesmos campos andando sempre juntos | Eles são um conceito. Dê nome a ele |
| **Primitive Obsession** | Tipos primitivos onde há um conceito de domínio | Crie o tipo. Ele documenta e valida |
| **Middle Man** | Uma classe que só delega | Remova o intermediário |
| **Refused Bequest** | Herda o que não usa, ou sobrescreve para desativar | A herança está errada; prefira composição |
| **Comments** | Comentário explicando o que um nome deveria dizer | Renomeie. Comentário sobre o **porquê** é bom; sobre o **quê**, é sintoma |
| **Speculative Generality** | Ver acima | Apague |

## O que **não** é achado

Nomear isto importa tanto quanto o catálogo, porque um revisor instruído a procurar
lacunas as encontra mesmo onde não há — e o resultado é superengenharia proposta pelo
revisor.

- **Preferência de estilo sem convenção documentada.** Se o repositório não decidiu,
  não é achado.
- **"Faltou tratamento de erro"** para um caso que não pode ocorrer. Código defensivo
  contra o impossível é Speculative Generality com outro nome.
- **"Faltou teste"** para caso que já está coberto por outro teste.
- **"Poderia ser mais genérico."** Poderia. A spec não pediu.
- **Reescrita proposta como achado.** "Eu teria feito diferente" não é defeito.

## Testes também têm smells

Dois merecem nome próprio, porque produzem suíte verde que não protege nada:

**Implementation-coupled** — o teste quebra ao refatorar, sem que o comportamento
mude. O tell é exatamente esse: refatoração sem mudança de comportamento não deveria
quebrar teste nenhum.

**Tautológico** — a asserção recomputa o esperado do mesmo jeito que o código. Passa
por construção, e nunca pode discordar. O valor esperado tem que vir de fora: do
enunciado do problema, não da implementação.

E o terceiro, estrutural: **teste que nunca foi vermelho não prova nada.** Se ninguém
o viu falhar, ele pode estar passando por acidente.
