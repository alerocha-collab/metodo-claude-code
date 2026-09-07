#!/usr/bin/env python3
"""Mede a distância entre o carimbo de um documento e o `HEAD`.

**Detecta. Nunca atualiza.** Desatualização é sinal para decisão humana, não coisa
a curar sozinha — e um documento que se atualiza sozinho perde a única propriedade
que o torna confiável: a capacidade de estar visivelmente errado.

Um artefato que *parece* sempre atual é o pior handoff possível. Ele diz uma coisa,
o código faz outra, e ninguém percebe porque ele "está sempre atualizado".

FAIL-CLOSED no que não consegue determinar: SHA ausente, ilegível, ou que não existe
no repositório contam como **desatualizado**. Não conseguir olhar não é licença para
dizer que está em dia.

Uso:
  python3 verificar_documento.py [caminho] [--raiz .]
Saída: exit 0 se em dia; 1 se desatualizado ou indeterminado.
"""

import argparse
import io
import os
import re
import subprocess
import sys

PADRAO = os.path.join("docs", "arquitetura.md")

# O carimbo, na forma que o documento traz: uma linha com `SHA:` e um hash curto
# ou longo entre crases. Deliberadamente frouxo quanto ao resto da linha, para
# nao quebrar quando alguem reescrever a frase em volta.
CARIMBO = re.compile(r"SHA:\s*[*_`\s]*([0-9a-f]{7,40})", re.IGNORECASE)

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def git(raiz, *args):
    try:
        proc = subprocess.run(
            ["git", *args], cwd=raiz, capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip()


def extrair_sha(texto):
    achado = CARIMBO.search(texto)
    return achado.group(1) if achado else None


def outros_carimbados(raiz, caminho):
    """Caminhos, em estilo POSIX, a excluir do diff: o proprio e os vizinhos carimbados.

    "Carimbado" e o criterio, nao "esta em docs/": um documento sem carimbo nao e
    vigiado por ninguem, entao mudanca nele e mudanca de verdade e precisa contar.
    """
    fora = {caminho.replace(os.sep, "/")}
    pasta = os.path.join(raiz, "docs")
    if os.path.isdir(pasta):
        for nome in os.listdir(pasta):
            if not nome.endswith(".md"):
                continue
            try:
                with io.open(os.path.join(pasta, nome), encoding="utf-8",
                             errors="replace") as f:
                    if extrair_sha(f.read()):
                        fora.add("docs/" + nome)
            except OSError:
                continue
    return sorted(fora)


def avaliar(raiz, caminho):
    """Devolve (em_dia, rotulo, detalhes).

    `rotulo` nomeia o desfecho sem depender de casar prosa — os testes usam ele.
    """
    absoluto = os.path.join(raiz, caminho)
    if not os.path.isfile(absoluto):
        return False, "documento-ausente", [
            f"{caminho} nao existe. Ao encerrar uma fase, escreva-o e carimbe."
        ]

    try:
        with open(absoluto, encoding="utf-8") as f:
            texto = f.read()
    except OSError as erro:
        return False, "documento-ilegivel", [f"{caminho} nao pode ser lido: {erro}"]

    sha = extrair_sha(texto)
    if not sha:
        return False, "sem-carimbo", [
            f"{caminho} nao traz carimbo. Esperava uma linha com `SHA: <hash>`.",
            "Sem carimbo nao ha como medir distancia, e um documento que nao pode",
            "ficar visivelmente velho e um documento em que ninguem deveria confiar.",
        ]

    if git(raiz, "cat-file", "-e", f"{sha}^{{commit}}") is None:
        return False, "carimbo-invalido", [
            f"O carimbo aponta para {sha}, que nao existe neste repositorio.",
            "Historico reescrito, ou carimbo digitado a mao.",
        ]

    # O proprio commit do documento cria um diff contra o SHA que ele carimba —
    # o carimbo aponta para o estado DESCRITO, e o documento e escrito depois.
    # Sem excluir o proprio arquivo, todo documento nasceria desatualizado, e um
    # alarme que toca desde o primeiro dia e um alarme que se desliga.
    #
    # Pela mesma razao, os OUTROS documentos carimbados tambem saem do diff.
    # Cada um e vigiado pelo seu proprio carimbo; contar a mudanca do vizinho faz
    # dois documentos carimbados no mesmo commit se acusarem mutuamente para
    # sempre — recarimbar nunca converge, porque o ato de recarimbar um mexe no
    # que o outro esta medindo.
    stat = git(raiz, "diff", f"{sha}..HEAD", "--stat", "--",
               ".", *(f":(exclude){p}" for p in outros_carimbados(raiz, caminho)))
    if stat is None:
        return False, "git-indisponivel", [
            "Nao consegui rodar `git diff`. Tratando como desatualizado por precaucao."
        ]

    if not stat:
        return True, "em-dia", [f"Nada mudou desde {sha}."]

    linhas = stat.splitlines()
    resumo = linhas[-1] if linhas else ""
    arquivos = [l.strip() for l in linhas[:-1]][:15]
    detalhes = [
        f"{len(linhas) - 1} arquivo(s) mudaram desde o carimbo {sha}.",
        f"  {resumo}",
        "",
        "Isto NAO e um erro. E um sinal para voce decidir se o documento ainda",
        "descreve o desenho em vigor. Se descreve, recarimbe. Se nao, reescreva.",
        "Nada aqui atualiza o carimbo por voce, de proposito.",
        "",
        "Mudou:",
    ] + [f"  {a}" for a in arquivos]
    if len(linhas) - 1 > 15:
        detalhes.append(f"  ... e mais {len(linhas) - 1 - 15}")
    return False, "desatualizado", detalhes


def main(argv=None):
    p = argparse.ArgumentParser(description="Distancia entre o carimbo e o HEAD.")
    p.add_argument("caminho", nargs="?", default=PADRAO)
    p.add_argument("--raiz", default=".")
    p.add_argument("--rotulo", action="store_true", help="imprime so o rotulo")
    args = p.parse_args(argv)

    raiz = os.path.abspath(args.raiz)
    em_dia, rotulo, detalhes = avaliar(raiz, args.caminho)

    if args.rotulo:
        print(rotulo)
    else:
        print(f"DOCUMENTO   {args.caminho}")
        print(f"ESTADO      {'em dia' if em_dia else 'DESATUALIZADO'} ({rotulo})")
        print()
        for linha in detalhes:
            print(linha)
    return 0 if em_dia else 1


if __name__ == "__main__":
    sys.exit(main())
