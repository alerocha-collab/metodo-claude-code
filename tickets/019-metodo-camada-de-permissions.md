# 019 — `metodo`: a camada de garantia dura que nunca foi construída

## Problema

A decisão de método nº 2 diz: **barreira dura em `permissions.deny`**. Ela nunca foi
construída. O plugin tem pedido (skills, agentes) e garantia condicional (dois hooks),
e **zero** regras de permissão.

O `templates/settings.exemplo.json` que o plano original previa também nunca existiu —
e o propósito dele mudou quando os hooks foram para dentro do plugin, mas a lacuna de
permissões continuou.

A diferença importa: hook é best-effort — dá timeout, sai com código que não bloqueia,
não roda em pasta não confiada. `permissions` é aplicada pelo cliente antes de o modelo
agir. Para "isto nunca pode acontecer", só a segunda serve.

## Comportamento atual → desejado

| Hoje | Depois desta fatia |
|---|---|
| Nenhuma regra de permissão distribuída | Existe um exemplo que o projeto copia e adapta |
| Segredo em `.env` depende de o modelo não olhar | Depende de o cliente não deixar |

## Critérios de aceitação

- [ ] Existe `templates/settings.exemplo.json`, comentado, para o projeto copiar
- [ ] Traz `deny` de leitura para segredo — `.env` e afins — com a observação de que
      **negar leitura também bloqueia edição e escrita** naquele caminho, então é uma
      regra e não três
- [ ] Traz `deny` de leitura para saída de build e código gerado, com a razão: é
      contexto gasto em arquivo que ninguém quer ler
- [ ] Traz `allow` para o comando de verificação, com a razão declarada: aprovar o
      mesmo comando toda vez **treina a pessoa a aprovar sem ler**, e fadiga de
      aprovação reduz segurança em vez de aumentar
- [ ] Cada bloco explica **por que aquela regra existe**, não só o que ela faz — um
      exemplo que a pessoa copia sem entender vira configuração de carga cult
- [ ] O README diz onde o arquivo vai e o que precisa ser adaptado
- [ ] **Negativo:** o plugin **não** instala permissões sozinho. Regra de permissão que
      aparece sem alguém ter escolhido é a forma mais rápida de alguém desconfiar do
      plugin inteiro
- [ ] **Negativo:** nenhum `allow` largo. Um exemplo com `Bash(*)` ensina o oposto do
      que a ficha `regras-de-permissao` diz

## Fora de escopo

- Sandbox: não roda em Windows nativo, e a restrição já está registrada
- Managed settings: são configuração de organização, não de plugin

## Verificação

A suíte confere que o template é JSON válido, que não contém `allow` largo, e que toda
chave de `deny` casa a sintaxe documentada. Conjunto balanceado: um exemplo inventado
com regra larga tem que reprovar.

## Prefactoring

Necessário? (x) não · ( ) sim, ticket NNN
