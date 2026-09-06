#!/usr/bin/env python3
"""Suite dos hooks do plugin `metodo`.

Conjunto deliberadamente BALANCEADO: metade dos casos verifica que o hook
bloqueia quando deve, metade verifica que ele NAO bloqueia quando nao deve. Uma
suite so com casos positivos aprova um hook que bloqueia tudo; uma so com
negativos aprova um hook que nunca bloqueia. As duas metades sao obrigatorias.

Contrato dos hooks, conforme a doc do Claude Code: exit 2 bloqueia, com a razao
em stderr; exit 0 nao objeta. Exit 1 NAO bloqueia — Claude Code o trata como
erro nao bloqueante e prossegue —, o que e exatamente por que o portao de
verificacao precisa capturar toda excecao e sair com 2.

Rode: python3 tests/testar_hooks.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(RAIZ, "plugins", "metodo", "hooks")

BLOQUEIA = 2
LIBERA = 0


def rodar(hook, evento):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, hook)],
        input=json.dumps(evento) if evento is not None else "",
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode


def projeto_temporario(base):
    proj = os.path.join(base, "proj")
    os.makedirs(os.path.join(proj, ".claude"))
    os.makedirs(os.path.join(proj, "tests"))
    with open(os.path.join(proj, "tests", "test_a.py"), "w") as f:
        f.write("def test_x():\n    pass\n")
    with open(os.path.join(proj, "tests", "a.spec.ts"), "w") as f:
        f.write("it('x', () => {})\n")
    with open(os.path.join(proj, "src.py"), "w") as f:
        f.write("print(1)\n")
    return proj


def escrever_config(proj, conteudo):
    caminho = os.path.join(proj, ".claude", "metodo.json")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)


def casos(proj):
    """Devolve (nome, hook, evento, esperado, config).

    `evento` None = stdin vazio. `config` e o conteudo de .claude/metodo.json a
    escrever ANTES de rodar o caso; None significa "apague o arquivo". Escrever
    no momento do caso, e nao aqui, e o ponto: montar a lista inteira antes de
    rodar faria todas as configs serem escritas em sequencia, e so a ultima
    valeria na hora da execucao.
    """
    t = lambda *p: os.path.join(proj, *p)
    verde = '{"verificacao":{"comando":"exit 0","descricao":"suite"}}'
    vermelha = '{"verificacao":{"comando":"exit 3","descricao":"suite"}}'
    lenta = json.dumps(
        {
            "verificacao": {
                "comando": f'"{sys.executable}" -c "import time; time.sleep(9)"',
                "timeout_segundos": 1,
            }
        }
    )

    return [
        # --- verificar_suite DEVE bloquear ---
        ("sem .claude/metodo.json", "verificar_suite.py", {"cwd": proj}, BLOQUEIA, None),
        ("comando nao preenchido", "verificar_suite.py", {"cwd": proj}, BLOQUEIA,
         '{"verificacao":{"comando":"SUBSTITUA-ME"}}'),
        ("suite vermelha", "verificar_suite.py", {"cwd": proj}, BLOQUEIA, vermelha),
        ("config ilegivel", "verificar_suite.py", {"cwd": proj}, BLOQUEIA, "nao e json"),
        ("suite estoura o timeout", "verificar_suite.py", {"cwd": proj}, BLOQUEIA, lenta),
        # --- verificar_suite NAO deve bloquear ---
        ("suite verde", "verificar_suite.py", {"cwd": proj}, LIBERA, verde),
        ("stop_hook_active (teto de 8)", "verificar_suite.py",
         {"cwd": proj, "stop_hook_active": True}, LIBERA, vermelha),
        # --- proteger_testes DEVE bloquear ---
        ("Edit em teste existente", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("tests", "test_a.py")}}, BLOQUEIA, None),
        ("Write sobre teste existente", "proteger_testes.py",
         {"tool_name": "Write", "tool_input": {"file_path": t("tests", "test_a.py")}}, BLOQUEIA, None),
        ("Edit em caminho irresolvivel", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": "/nao/existe/tests/test_z.py"}}, BLOQUEIA, None),
        ("Edit em spec .ts", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("tests", "a.spec.ts")}}, BLOQUEIA, None),
        ("Edit em conftest.py", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("conftest.py")}}, BLOQUEIA, None),
        # --- proteger_testes NAO deve bloquear ---
        ("Write de teste NOVO", "proteger_testes.py",
         {"tool_name": "Write", "tool_input": {"file_path": t("tests", "test_novo.py")}}, LIBERA, None),
        ("Edit em codigo de producao", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("src.py")}}, LIBERA, None),
        ("Bash nao e ferramenta de edicao", "proteger_testes.py",
         {"tool_name": "Bash", "tool_input": {"command": "rm tests/test_a.py"}}, LIBERA, None),
        ("stdin vazio", "proteger_testes.py", None, LIBERA, None),
    ]


def main():
    base = tempfile.mkdtemp(prefix="metodo-testes-")
    falhas = []
    try:
        proj = projeto_temporario(base)
        lista = casos(proj)
        caminho_config = os.path.join(proj, ".claude", "metodo.json")
        for nome, hook, evento, esperado, config in lista:
            if config is None:
                if os.path.exists(caminho_config):
                    os.remove(caminho_config)
            else:
                escrever_config(proj, config)
            obtido = rodar(hook, evento)
            marca = "ok  " if obtido == esperado else "FALHA"
            print(f"  {marca} {nome} (exit {obtido})")
            if obtido != esperado:
                falhas.append(f"{nome}: esperava {esperado}, veio {obtido}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if falhas:
        print(f"{len(falhas)} de {len(lista)} FALHARAM:")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print(f"{len(lista)} casos, todos passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
