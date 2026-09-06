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

# Nome do caso que exercita a clausula de guarda; o laco em main() o trata
# a parte, porque e o unico que precisa da arvore limpa.
ARVORE_LIMPA = "arvore limpa: nada a verificar"


def rodar(hook, evento):
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, hook)],
        input=json.dumps(evento) if evento is not None else "",
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode


def rodar_cp1252(hook, evento, proj):
    """Roda o hook forcando a codificacao de console do Windows.

    Sem forcar, este caso passa em qualquer maquina cujo locale ja seja UTF-8 —
    e passaria sem provar nada, que e a pior propriedade de um teste. O evento
    vai como bytes UTF-8, que e o que o Claude Code manda de verdade.
    """
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    proc = subprocess.run(
        [sys.executable, os.path.join(HOOKS, hook)],
        input=json.dumps(evento, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        timeout=120,
        env=env,
        cwd=proj,
    )
    return proc.returncode, proc.stderr.decode("utf-8", "replace")


def git(proj, *args):
    subprocess.run(["git", *args], cwd=proj, capture_output=True, text=True, timeout=60)


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

    # Repo git de verdade: a clausula de guarda do portao decide por
    # `git status`, e um diretorio sem git responderia "na duvida, verifique",
    # mascarando justamente o caso de arvore limpa.
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "teste@exemplo.invalido")
    git(proj, "config", "user.name", "teste")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    return proj


def monorepo(base):
    """Monorepo com a config so na RAIZ e o trabalho dentro de um pacote.

    E a forma que a doc recomenda para repositorio grande — iniciar a sessao dentro
    do pacote — e a que quebrava o portao antes da busca subir ate a raiz.
    """
    proj = os.path.join(base, "mono")
    pacote = os.path.join(proj, "packages", "api")
    os.makedirs(os.path.join(proj, ".claude"))
    os.makedirs(os.path.join(pacote, "tests"))
    with open(os.path.join(pacote, "src.py"), "w") as f:
        f.write("print(1)\n")
    with open(os.path.join(pacote, "tests", "test_a.py"), "w") as f:
        f.write("def test_x():\n    pass\n")
    with open(os.path.join(proj, ".claude", "metodo.json"), "w") as f:
        f.write('{"verificacao":{"comando":"exit 0","descricao":"suite"}}')
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@exemplo.invalido")
    git(proj, "config", "user.name", "t")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    with open(os.path.join(pacote, "src.py"), "a") as f:
        f.write("print(2)\n")  # arvore suja, para o portao nao liberar por guarda
    return proj, pacote


def sem_adesao(base):
    """Repositorio git SEM `.claude/metodo.json` — instalado, nao adotado."""
    proj = os.path.join(base, "sem_adesao")
    os.makedirs(os.path.join(proj, "tests"))
    with open(os.path.join(proj, "tests", "test_a.py"), "w") as f:
        f.write("def test_x():\n    pass\n")
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@exemplo.invalido")
    git(proj, "config", "user.name", "t")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    return proj


def sujar(proj):
    """Deixa a arvore com mudanca nao commitada."""
    with open(os.path.join(proj, "src.py"), "a", encoding="utf-8") as f:
        f.write("print(2)\n")


def limpar(proj):
    git(proj, "checkout", "--", ".")


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
        # A cláusula de guarda, e o que ela protege: sem ela, uma sessão do papel
        # `operador` seria barrada por suíte vermelha que não foi ela quem
        # quebrou — regra de construção barrando operação, o inverso exato do
        # sintoma que motivou separar papéis.
        (ARVORE_LIMPA, "verificar_suite.py", {"cwd": proj}, LIBERA, vermelha),
        # --- proteger_testes DEVE bloquear (projeto ADERENTE: config presente) ---
        ("Edit em teste existente", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("tests", "test_a.py")}}, BLOQUEIA, verde),
        ("Write sobre teste existente", "proteger_testes.py",
         {"tool_name": "Write", "tool_input": {"file_path": t("tests", "test_a.py")}}, BLOQUEIA, verde),
        ("Edit em teste que nao resolve, dentro do projeto", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("tests", "test_sumiu.py")}}, BLOQUEIA, verde),
        ("Edit em spec .ts", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("tests", "a.spec.ts")}}, BLOQUEIA, verde),
        ("Edit em conftest.py", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("conftest.py")}}, BLOQUEIA, verde),
        # --- proteger_testes NAO deve bloquear ---
        ("Write de teste NOVO", "proteger_testes.py",
         {"tool_name": "Write", "tool_input": {"file_path": t("tests", "test_novo.py")}}, LIBERA, verde),
        ("Edit em codigo de producao", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": t("src.py")}}, LIBERA, verde),
        ("Bash nao e ferramenta de edicao", "proteger_testes.py",
         {"tool_name": "Bash", "tool_input": {"command": "rm tests/test_a.py"}}, LIBERA, verde),
        ("stdin vazio", "proteger_testes.py", None, LIBERA, verde),
        # Caminho fora de qualquer projeto aderente: o plugin nao opina. Antes da
        # clausula de adesao este caso bloqueava — e bloquear ali era justamente o
        # comportamento agressivo que a fatia 018 veio corrigir.
        ("caminho fora de projeto aderente: nao age", "proteger_testes.py",
         {"tool_name": "Edit", "tool_input": {"file_path": "/nao/existe/tests/test_z.py"}}, LIBERA, verde),
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
            # Todo caso do portão pressupõe árvore suja, salvo o que testa
            # explicitamente a árvore limpa. `.claude/metodo.json` está fora do
            # git, então escrevê-lo não suja nada por si.
            if nome == ARVORE_LIMPA:
                limpar(proj)
            else:
                sujar(proj)
            obtido = rodar(hook, evento)
            marca = "ok  " if obtido == esperado else "FALHA"
            print(f"  {marca} {nome} (exit {obtido})")
            if obtido != esperado:
                falhas.append(f"{nome}: esperava {esperado}, veio {obtido}")

        # --- escopo de aplicacao ---
        print()
        proj_mono, pacote = monorepo(base)
        proj_sem = sem_adesao(base)
        escopo = [
            # A sessao comeca DENTRO do pacote e a config so existe na raiz. Antes da
            # busca subir, isto bloqueava todo turno dizendo "nao ha verificacao".
            ("monorepo: acha a config da raiz a partir do pacote",
             "verificar_suite.py", {"cwd": pacote}, LIBERA),
            # Com adesao, o proteger_testes segue barrando como antes.
            ("com adesao: editar teste existente e negado",
             "proteger_testes.py",
             {"tool_name": "Edit",
              "tool_input": {"file_path": os.path.join(pacote, "tests", "test_a.py")}},
             BLOQUEIA),
            # E o caso que a guarda existe para produzir: instalado nao e adotado.
            ("sem adesao: nao age, nem comenta",
             "proteger_testes.py",
             {"tool_name": "Edit",
              "tool_input": {"file_path": os.path.join(proj_sem, "tests", "test_a.py")}},
             LIBERA),
        ]
        for nome, hook, evento, esperado in escopo:
            obtido = rodar(hook, evento)
            ok = obtido == esperado
            print(f"  {'ok  ' if ok else 'FALHA'} {nome} (exit {obtido})")
            lista.append(nome)
            if not ok:
                falhas.append(f"{nome}: esperava {esperado}, veio {obtido}")

        # --- codificacao ---
        # O Claude Code manda UTF-8 no stdin; o Python do Windows decodifica com
        # cp1252. A mensagem do assistente vem no evento e costuma ter tabela,
        # seta e emoji — tudo fora do cp1252. Sem tratamento, `sys.stdin.read()`
        # cai, e o hook bloqueia dizendo "erro inesperado": falso positivo, que
        # e caro porque com hook nao se negocia.
        sujar(proj)
        escrever_config(proj, '{"verificacao":{"comando":"exit 0","descricao":"s"}}')
        for rotulo, texto in [
            ("box-drawing", "tabela ┌───┐ seta →"),
            ("emoji", "pronto 👋"),
            ("travessao", "texto — com travessao"),
        ]:
            evento = {"cwd": proj, "hook_event_name": "Stop",
                      "last_assistant_message": texto}
            codigo, err = rodar_cp1252("verificar_suite.py", evento, proj)
            ok = codigo == LIBERA and "Unicode" not in err
            nome = f"stdin cp1252 com {rotulo}: suite verde libera"
            print(f"  {'ok  ' if ok else 'FALHA'} {nome} (exit {codigo})")
            lista.append(nome)  # so para a contagem final
            if not ok:
                falhas.append(f"{nome}: exit={codigo} stderr={err[:120]!r}")
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
