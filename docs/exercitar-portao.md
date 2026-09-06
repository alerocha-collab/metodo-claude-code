# Exercitar o portão

Roteiro manual para verificar que os hooks do papel `construtor` funcionam **dentro
de uma sessão**, e não apenas como scripts.

## Por que isto não é automatizado

As suítes provam o **contrato dos scripts**: exit 2 bloqueia, exit 0 libera. Não
provam que o Claude Code recusa encerrar o turno quando recebe 2, nem que
`${CLAUDE_PLUGIN_ROOT}` resolve dentro do `hooks:` do frontmatter de agente — que a
doc não cobre.

Automatizar exigiria dirigir uma sessão interativa, o que custa mais que o valor de
uma verificação que se faz uma vez por plataforma. Registre o resultado no
`DECISIONS.md` e siga.

## Preparação

Cria uma falha deliberada. O arquivo está no `.gitignore`, então não há risco de
commitá-lo por engano.

```bash
printf 'import sys\nprint("falha proposital")\nsys.exit(1)\n' > tests/testar_zzz_proposital.py
```

Confirme que a suíte ficou vermelha antes de abrir a sessão:

```bash
python3 tests/testar_tudo.py
```

## A sessão

Num terminal de verdade, na raiz do repositório:

```bash
claude --plugin-dir ./plugins/metodo --agent metodo:construtor
```

Se `--agent metodo:construtor` não for aceito, tente `--agent construtor`. **Qual das
duas formas funciona é parte do que este roteiro descobre** — anote.

### Os cinco casos

| # | O que fazer | O que deve acontecer |
|---|---|---|
| 1 | Peça qualquer coisa trivial ("diga oi") e deixe o turno terminar | **Barrado.** A mensagem do portão aparece, citando a suíte vermelha |
| 2 | Peça para editar um teste que já existe — por exemplo, mudar uma linha de `tests/testar_hooks.py` | **Negado**, com a mensagem do hook sobre não editar testes |
| 3 | Peça para criar um teste novo, num arquivo que não existe | **Permitido** |
| 4 | Apague a falha: `rm tests/testar_zzz_proposital.py`. Peça algo trivial de novo | **Turno encerra normalmente.** O portão não bloqueia sempre |
| 5 | Confirme que o caso 1 barrou por conta do portão, e não por outro motivo | A mensagem tem que ser a do `verificar_suite.py`, com o nome do comando |

O caso 3 e o caso 4 são os que impedem o falso positivo: um hook que bloqueia **tudo**
passaria nos casos 1 e 2 e seria inútil.

## Registrar

No `DECISIONS.md`, com o **texto literal** do bloqueio — não uma paráfrase. Registre
também qual forma do `--agent` funcionou, e em que plataforma o roteiro rodou.

Se o portão **não** barrar, isso é uma falha e vira ticket de correção. Não arredonde
para "funcionou": um portão que não barra é pior que nenhum, porque dá a sensação de
cobertura.

## Limpeza

```bash
rm -f tests/testar_zzz_proposital.py
python3 tests/testar_tudo.py
```
