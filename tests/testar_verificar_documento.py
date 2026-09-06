#!/usr/bin/env python3
"""Suite do detector de desatualização de documento.

Balanceada: o caso "em dia" vale tanto quanto os de alarme. Um detector só
testado contra documentos velhos passaria acusando sempre — e um alarme que
sempre toca é um alarme que se desliga.

Rode: python3 tests/testar_verificar_documento.py
"""

import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plugins", "metodo", "scripts"))

import verificar_documento as vd  # noqa: E402

DOC = os.path.join("docs", "arquitetura.md")


def git(proj, *args):
    return subprocess.run(
        ["git", *args], cwd=proj, capture_output=True, text=True, timeout=60
    )


def escrever(proj, caminho, texto):
    absoluto = os.path.join(proj, caminho)
    os.makedirs(os.path.dirname(absoluto), exist_ok=True)
    with open(absoluto, "w", encoding="utf-8") as f:
        f.write(texto)


def novo_repo(base, nome):
    proj = os.path.join(base, nome)
    os.makedirs(proj)
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@exemplo.invalido")
    git(proj, "config", "user.name", "t")
    escrever(proj, "src.py", "print(1)\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    return proj


def sha(proj):
    return git(proj, "rev-parse", "--short", "HEAD").stdout.strip()


def cenarios(base):
    out = []

    # Em dia: o documento carimba o commit em que foi commitado, e nada mudou
    # depois. Este caso e o que impede um detector que acusa sempre.
    proj = novo_repo(base, "em_dia")
    escrever(proj, DOC, "# Arquitetura\n\nSHA: `PLACEHOLDER`\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "doc")
    s = sha(proj)
    escrever(proj, DOC, f"# Arquitetura\n\nSHA: `{s}`\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "--amend", "--no-edit")
    out.append(("documento em dia nao acusa", proj, DOC, "em-dia"))

    # Editar o proprio documento nao o torna desatualizado: corrigir uma frase
    # nele nao muda o desenho que ele descreve. Sem excluir o arquivo do diff,
    # todo documento nasceria velho — alarme que toca desde o primeiro dia e
    # alarme que se desliga.
    proj = novo_repo(base, "so_o_doc_mudou")
    s = sha(proj)
    escrever(proj, DOC, f"# Arquitetura\n\nSHA: `{s}`\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "doc")
    escrever(proj, DOC, f"# Arquitetura\n\nSHA: `{s}`\n\nUma frase a mais.\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "ajusta o texto do doc")
    out.append(("so o documento mudou: continua em dia", proj, DOC, "em-dia"))

    proj = novo_repo(base, "atrasado")
    s = sha(proj)
    escrever(proj, DOC, f"# Arquitetura\n\nSHA: `{s}`\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "doc")
    escrever(proj, "src.py", "print(2)\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "muda o codigo")
    out.append(("documento atrasado acusa", proj, DOC, "desatualizado"))

    # O carimbo escrito como o documento real o escreve: em negrito. A primeira
    # versao da expressao nao tolerava o `**` e nao reconhecia o unico documento
    # que existia — achado ao rodar o detector nele.
    proj = novo_repo(base, "carimbo_em_negrito")
    s = sha(proj)
    escrever(proj, DOC, f"# Arquitetura\n\n**SHA:** `{s}` · **Data:** 2026-09-06\n")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "doc")
    out.append(("carimbo em negrito e reconhecido", proj, DOC, "em-dia"))

    proj = novo_repo(base, "sem_carimbo")
    escrever(proj, DOC, "# Arquitetura\n\nSem carimbo nenhum aqui.\n")
    out.append(("sem carimbo acusa", proj, DOC, "sem-carimbo"))

    proj = novo_repo(base, "carimbo_falso")
    escrever(proj, DOC, "# Arquitetura\n\nSHA: `deadbeef`\n")
    out.append(("carimbo inexistente acusa", proj, DOC, "carimbo-invalido"))

    proj = novo_repo(base, "ausente")
    out.append(("documento ausente acusa", proj, DOC, "documento-ausente"))

    return out


def main():
    base = tempfile.mkdtemp(prefix="metodo-doc-")
    falhas = []
    try:
        lista = cenarios(base)
        for nome, proj, caminho, esperado in lista:
            em_dia, rotulo, _ = vd.avaliar(proj, caminho)
            ok = rotulo == esperado and (em_dia == (esperado == "em-dia"))
            print(f"  {'ok  ' if ok else 'FALHA'} {nome} -> {rotulo}")
            if not ok:
                falhas.append(f"{nome}: esperava {esperado!r}, veio {rotulo!r}")

        # O detector nao pode escrever nada. Um carimbo que se atualiza sozinho
        # e a propriedade que este script existe para impedir.
        proj = os.path.join(base, "atrasado")
        caminho = os.path.join(proj, DOC)
        antes = open(caminho, encoding="utf-8").read()
        vd.avaliar(proj, DOC)
        ok = open(caminho, encoding="utf-8").read() == antes
        print(f"  {'ok  ' if ok else 'FALHA'} nao altera o documento que le")
        lista.append(("nao altera", None, None, None))
        if not ok:
            falhas.append("avaliar() alterou o documento")
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
