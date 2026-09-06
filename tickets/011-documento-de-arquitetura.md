# 011 — Documento de arquitetura da fase, carimbado, com detector de desatualização

## Problema

A decisão de método nº 3 tem duas metades. A primeira — estado estruturado em git e
tickets **durante** a implementação — está exercitada há dez tickets. A segunda nunca
foi: **documento de arquitetura escrito ao encerrar a fase, carimbado com o SHA**.

E ela vem com uma condição que não é opcional: *"se for atualizado automaticamente,
você perde a capacidade de detectar quando ficou errado. Um documento que parece
sempre atual é a pior propriedade possível num artefato de handoff."*

Escrever o documento sem o detector o torna exatamente esse artefato.

Hoje quem chega neste repositório lê treze decisões em ordem cronológica, sem visão
de conjunto — o `DECISIONS.md` conta como se chegou aqui, não o que está de pé.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| O desenho vive espalhado em decisões e commits | Existe um documento que o descreve inteiro |
| Nada detecta quando ele fica velho | Um script mede a distância entre o carimbo e o `HEAD` |

## Critérios de aceitação

- [ ] O documento descreve o desenho **em vigor**, não a história de como se chegou
      nele — a história é o `DECISIONS.md`, e duplicá-la seria criar duas fontes
- [ ] Traz o **SHA** em que foi escrito, e a data
- [ ] Termina por "Suposições e quando revisar": cada componente com a suposição que
      codifica e o sinal de que ela caducou
- [ ] Existe um script que lê o SHA do documento e reporta o que mudou desde então
- [ ] O script **detecta e nunca atualiza**. Desatualização é sinal para decisão
      humana, não coisa a curar sozinha
- [ ] O script é fail-closed no que não consegue determinar: SHA ausente, ilegível ou
      inexistente no repositório conta como **desatualizado**, nunca como em dia
- [ ] Onde o desenho divergir da decisão de método nº 3, a divergência entra no
      `DECISIONS.md` com a alternativa descartada — não é implementada em silêncio
- [ ] **Negativo:** o script não bloqueia o commit nem o fim do turno por
      desatualização. Documento atrasado não é o mesmo que suíte vermelha, e falso
      positivo em hook é caro
- [ ] **Negativo:** nada no repositório atualiza o carimbo automaticamente

## Fora de escopo

- Gerar o documento a partir do código
- Verificar se o conteúdo do documento é **verdadeiro** — isso exige julgamento, e o
  script só mede distância
- Documento de arquitetura para outros projetos: o template vem quando houver segundo
  caso

## Verificação

Suíte própria, com conjunto balanceado: documento em dia **não** acusa; documento
atrasado acusa; SHA ausente, ilegível e inexistente acusam.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
