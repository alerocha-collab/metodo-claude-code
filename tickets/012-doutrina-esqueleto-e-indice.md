# 012 — `doutrina`: esqueleto do plugin, índice das fontes e detector de drift

## Problema

A documentação do Claude Code tem 173 páginas e muda toda semana. Um agente que
precisa decidir arquitetura investiga do zero e quase nunca tem visão do todo — foi
assim que a "Fase 0" do `metodo` fechou sem nunca ter visto a página de monorepo.

Antes de destilar qualquer coisa, é preciso o esqueleto: um índice de **todas** as
páginas, para que nenhuma fique invisível, e um detector que diga quando uma ficha
destilada ficou velha. Sem o detector, a destilação vira o artefato que a decisão de
método nº 3 nomeia como o pior possível: o que parece sempre atual.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Nenhum inventário local; o agente descobre páginas por acaso | As 173 estão indexadas, com URL e título |
| Nada distingue página destilada de página só listada | O índice diz qual é qual |
| Nada detecta que a doc mudou | Um script compara hash e reporta o que mudou |

## Critérios de aceitação

- [ ] Existe `plugins/doutrina/` com `plugin.json` válido em
      `claude plugin validate --strict`
- [ ] `fontes.json` contém **as 173 páginas** do índice em inglês, cada uma com URL,
      título, seção e o campo que diz se foi destilada
- [ ] O script busca a página pela URL `.md`, calcula o hash e compara com o
      registrado — **sem depender de nenhuma ferramenta do Claude Code**, para poder
      rodar no CI
- [ ] O script **detecta e nunca atualiza** o hash registrado. Há caso de teste
      provando que ele não altera `fontes.json`
- [ ] **Fail-closed:** página sem hash registrado, hash ilegível, ou falha de rede
      contam como "não sei" e o script sai diferente de zero — nunca "está em dia"
- [ ] O script funciona **offline** para a parte estrutural: sem rede, ele ainda
      valida a integridade do índice e só reporta que não pôde verificar o drift
- [ ] Suíte estrutural: toda entrada `destilada: true` tem arquivo local; todo arquivo
      em `referencias/` tem entrada em `fontes.json`; toda ficha em `volatil/` tem
      URL e data de carimbo
- [ ] **Negativo:** o detector **não acusa** quando nada mudou. Conjunto balanceado —
      um detector só testado contra drift passa acusando sempre, e alarme que sempre
      toca é alarme desligado
- [ ] **Negativo:** nada no repositório atualiza hash automaticamente

## Fora de escopo

- Qualquer ficha destilada — é a fatia seguinte
- As 11 traduções e seus índices
- Baixar e guardar cópia das páginas: guardamos o **hash**, não o conteúdo

## Verificação

Suíte própria, descoberta pelo `tests/testar_tudo.py`. O caso de rede é testado com
uma função de busca injetada, não com rede de verdade — teste que depende de rede é
teste que falha por motivo errado.

## Prefactoring

Necessário? ( ) não · (x) **avaliar ao começar** — `verificar_documento.py` já
implementa o contrato "carimbo + detector + nunca atualiza". Se a lógica de carimbo
for reaproveitável, extrair antes; se só o padrão for comum, não force a abstração.
