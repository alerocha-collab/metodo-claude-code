#!/usr/bin/env python3
"""Suite da dependência de interpretador dos hooks.

O plugin depende de `python3` no PATH. Sem tratamento, a **ausência** dele faz o
shell sair com **127**, que a doc do Claude Code classifica como não bloqueante:

  "Any other exit code doesn't block on its own for most hook events."

Ou seja, o portão de verificação falharia **aberto** exatamente na máquina mal
configurada — o pior lugar possível para falhar aberto. O `|| exit 2` declarado
em `hooks/hooks.json` é a rede que converte isso em bloqueio.

Esta suíte prova que a rede funciona **e** que ela não atrapalha os dois casos
legítimos. Só a primeira metade aprovaria um `exit 2` incondicional, que
bloquearia para sempre.

Rode: python3 tests/testar_dependencias.py
"""

import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS_JSON = os.path.join(RAIZ, "plugins", "metodo", "hooks", "hooks.json")

BLOQUEIA = 2
LIBERA = 0


def sh(comando):
    """Roda no shell POSIX, que é onde o `||` do hooks.json é interpretado."""
    proc = subprocess.run(
        ["sh", "-c", comando], capture_output=True, text=True, timeout=60
    )
    return proc.returncode


CASOS = [
    # (nome, comando, exit esperado)
    ("interpretador ausente vira bloqueio",
     'python3quenaoexiste "x.py" || exit 2', BLOQUEIA),
    ("script ausente vira bloqueio",
     'python3 "/caminho/que/nao/existe/x.py" || exit 2', BLOQUEIA),
    ("sucesso continua liberando",
     'python3 -c "import sys; sys.exit(0)" || exit 2', LIBERA),
    ("bloqueio legitimo continua bloqueando",
     'python3 -c "import sys; sys.exit(2)" || exit 2', BLOQUEIA),
    # Sem a rede, o caso que importa falha ABERTO. Este caso existe para que a
    # suite quebre se alguem remover o `|| exit 2` achando que e enfeite.
    ("sem a rede, interpretador ausente NAO bloqueia",
     'python3quenaoexiste "x.py"', 127),
]


def main():
    if shutil.which("sh") is None:
        print("  pulado: `sh` indisponivel nesta maquina.")
        print("\n0 casos executados (ambiente sem shell POSIX).")
        return 0

    falhas = []
    for nome, comando, esperado in CASOS:
        obtido = sh(comando)
        ok = obtido == esperado
        print(f"  {'ok  ' if ok else 'FALHA'} {nome} (exit {obtido})")
        if not ok:
            falhas.append(f"{nome}: esperava {esperado}, veio {obtido}")

    # A rede tem que estar de fato declarada no hooks.json — testar o `||` em
    # abstrato nao prova que ele esta no lugar onde importa.
    with open(HOOKS_JSON, encoding="utf-8") as f:
        conteudo = f.read()
    ok = "|| exit 2" in conteudo and "verificar_suite.py" in conteudo
    print(f"  {'ok  ' if ok else 'FALHA'} hooks.json declara a rede no Stop")
    if not ok:
        falhas.append("hooks.json nao tem `|| exit 2` no comando do Stop")

    # E NAO pode estar no PreToolUse: aquele hook e desenhado para falhar
    # aberto, e a rede inverteria isso sem ninguem perceber.
    linhas_pre = [l for l in conteudo.splitlines() if "proteger_testes.py" in l]
    ok = bool(linhas_pre) and all("|| exit 2" not in l for l in linhas_pre)
    print(f"  {'ok  ' if ok else 'FALHA'} a rede NAO esta no PreToolUse")
    if not ok:
        falhas.append("proteger_testes nao deve ter `|| exit 2`: falha aberto por projeto")

    total = len(CASOS) + 2
    print()
    if falhas:
        print(f"{len(falhas)} de {total} FALHARAM:")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print(f"{total} casos, todos passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
