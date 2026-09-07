#!/usr/bin/env python3
"""Suite do `estado.py` — os cenários que o `/fluxo` precisa acertar.

É a verificação nº 2 do plano da metodologia, e ela pôde ser automatizada
porque a recomendação depende só de leitura de disco. Cada cenário se monta
num diretório temporário e se compara com o rótulo esperado.

Comparar rótulo, e não texto de prosa, é deliberado: senão a suíte quebraria
a cada ajuste de redação, e uma suíte que quebra por motivo cosmético é
abandonada em semanas.

Rode: python3 tests/testar_estado.py
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plugins", "metodo", "scripts"))

import estado  # noqa: E402


def git(proj, *args):
    subprocess.run(["git", *args], cwd=proj, capture_output=True, text=True, timeout=60)


def escrever(caminho, texto):
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def commitar(proj, mensagem):
    git(proj, "add", "-A")
    git(proj, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", mensagem)


def novo_projeto(base, nome):
    proj = os.path.join(base, nome)
    os.makedirs(os.path.join(proj, ".claude"))
    with open(os.path.join(proj, "src.py"), "w", encoding="utf-8") as f:
        f.write("print(1)\n")
    with io.open(os.path.join(proj, ".claude", "metodo.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write('{"verificacao":{"comando":"exit 0"}}\n')
    git(proj, "init", "-q", "-b", "main")
    git(proj, "config", "user.email", "t@exemplo.invalido")
    git(proj, "config", "user.name", "t")
    git(proj, "add", "-A")
    git(proj, "commit", "-q", "-m", "base")
    return proj


def escrever_fila(proj, tickets, com_briefs=True):
    os.makedirs(os.path.join(proj, "tickets"), exist_ok=True)
    for t in tickets:
        if com_briefs and t.get("brief"):
            caminho = os.path.join(proj, t["brief"])
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(f"# {t['id']}\n")
    with io.open(os.path.join(proj, "tickets", "fila.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"tickets": tickets}, ensure_ascii=False, indent=2) + "\n")


def t(tid, estado_="pronto", bloqueado_por=None):
    return {
        "id": tid,
        "titulo": f"ticket {tid}",
        "estado": estado_,
        "bloqueado_por": bloqueado_por or [],
        "brief": f"tickets/{tid}.md",
    }


def sujar(proj):
    with open(os.path.join(proj, "src.py"), "a", encoding="utf-8") as f:
        f.write("print(2)\n")


# Cada cenário devolve o rótulo que `estado.montar` deve produzir.
def cenarios(base):
    out = []

    proj = novo_projeto(base, "sem_fila")
    out.append(("repo sem fila", proj, "sem-fila"))

    proj = novo_projeto(base, "fila_invalida")
    escrever_fila(proj, [t("001", bloqueado_por=["002"]), t("002", bloqueado_por=["001"])])
    out.append(("fila com ciclo de bloqueio", proj, "fila-invalida"))

    # A fila inválida tem que ser reportada ANTES de qualquer recomendação de
    # passo, mesmo quando há um ticket aparentemente pronto para pegar.
    proj = novo_projeto(base, "fila_invalida_com_pronto")
    escrever_fila(proj, [t("001"), t("002", bloqueado_por=["999"])])
    out.append(("fila invalida vence ticket pronto", proj, "fila-invalida"))

    proj = novo_projeto(base, "em_andamento")
    escrever_fila(proj, [t("001", "em-andamento"), t("002")])
    out.append(("ticket em andamento", proj, "em-andamento"))

    proj = novo_projeto(base, "prontos")
    escrever_fila(proj, [t("001", "concluido"), t("002", bloqueado_por=["001"])])
    out.append(("proximo ticket liberado", proj, "proximo-ticket"))

    # O grafo manda, não a ordem numérica: 003 vem antes de 002 porque o
    # bloqueador de 002 ainda está aberto.
    proj = novo_projeto(base, "grafo_manda")
    escrever_fila(proj, [t("001"), t("002", bloqueado_por=["001"]), t("003")])
    out.append(("grafo manda sobre ordem numerica", proj, "proximo-ticket"))

    proj = novo_projeto(base, "diff_pendente")
    escrever_fila(proj, [t("001", "concluido")])
    sujar(proj)
    out.append(("diff pendente sem ticket em curso", proj, "diff-pendente"))

    # Ticket em andamento COM árvore suja é trabalho normal em curso, não
    # "revise": o ticket vence.
    proj = novo_projeto(base, "andamento_sujo")
    escrever_fila(proj, [t("001", "em-andamento")])
    sujar(proj)
    out.append(("ticket em andamento vence arvore suja", proj, "em-andamento"))

    proj = novo_projeto(base, "tudo_feito")
    escrever_fila(proj, [t("001", "concluido"), t("002", "descartado")])
    out.append(("fila sem trabalho pendente", proj, "fila-vazia"))

    return out


def main():
    base = tempfile.mkdtemp(prefix="metodo-estado-")
    falhas = []
    try:
        lista = cenarios(base)
        for nome, proj, esperado in lista:
            _, _, rotulo = estado.montar(proj)
            ok = rotulo == esperado
            print(f"  {'ok  ' if ok else 'FALHA'} {nome} -> {rotulo}")
            if not ok:
                falhas.append(f"{nome}: esperava {esperado!r}, veio {rotulo!r}")

        # O rótulo `proximo-ticket` não diz QUAL ticket. Esse é o critério
        # que importa — o grafo manda sobre a ordem numérica —, então ele
        # precisa de asserção própria.
        proj = os.path.join(base, "grafo_manda")
        fila = json.load(io.open(os.path.join(proj, "tickets", "fila.json"),
                                 encoding="utf-8"))
        escolhido = (estado.proximo_liberado(fila) or {}).get("id")
        ok = escolhido == "001"
        print(f"  {'ok  ' if ok else 'FALHA'} escolhe 001 (liberado), nao 002 (bloqueado)")
        lista.append(("escolhe o liberado", None, None))
        if not ok:
            falhas.append(f"proximo_liberado devolveu {escolhido!r}, esperava '001'")

        # E com 001 fechado, o proximo passa a ser 002 — nao 003, que tambem
        # esta liberado mas vem depois na fila.
        for tk in fila["tickets"]:
            if tk["id"] == "001":
                tk["estado"] = "concluido"
        escolhido = (estado.proximo_liberado(fila) or {}).get("id")
        ok = escolhido == "002"
        print(f"  {'ok  ' if ok else 'FALHA'} destravado 001, o proximo vira 002")
        lista.append(("destrava na ordem", None, None))
        if not ok:
            falhas.append(f"apos fechar 001, devolveu {escolhido!r}, esperava '002'")

        # --- o relato de documentos carimbados ---
        # A propriedade que importa nao e "aparece a linha": e que a linha NAO
        # muda o cenario nem o passo recomendado. Detecta, nao bloqueia.
        proj = os.path.join(base, "prontos")
        linhas_antes, passo_antes, rotulo_antes = estado.montar(proj)

        docs = os.path.join(proj, "docs")
        os.makedirs(docs, exist_ok=True)

        # (a) documento SEM carimbo nao e cobrado. Carimbar e o ato de aceitar
        # a vigilancia; cobrar quem nao pediu treina a pessoa a ignorar o aviso.
        escrever(os.path.join(docs, "sem_carimbo.md"), "# nota solta\nsem carimbo\n")
        linhas, _, _ = estado.montar(proj)
        citadas = [l for l in linhas if "sem_carimbo.md" in l]
        ok = not citadas
        print(f"  {'ok  ' if ok else 'FALHA'} documento sem carimbo nao e cobrado")
        lista.append(("sem carimbo", None, None))
        if not ok:
            falhas.append(f"cobrou documento sem carimbo: {citadas}")

        # (b) documento carimbado no HEAD -> em dia
        escrever(os.path.join(docs, "arq.md"), "# arquitetura\n\ncarimbo abaixo\n")
        commitar(proj, "cria o documento")
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=proj,
                             capture_output=True, text=True).stdout.strip()
        escrever(os.path.join(docs, "arq.md"),
                 "# arquitetura\n\n**SHA:** `" + sha + "`\n")
        commitar(proj, "carimba")
        linhas, _, _ = estado.montar(proj)
        citadas = [l for l in linhas if "arq.md" in l]
        ok = bool(citadas) and "em dia" in citadas[0]
        print(f"  {'ok  ' if ok else 'FALHA'} documento carimbado no HEAD -> em dia")
        lista.append(("carimbo em dia", None, None))
        if not ok:
            falhas.append(f"esperava 'em dia' para arq.md, veio {citadas}")

        # (c) o repositorio anda, o carimbo fica: tem que acusar
        escrever(os.path.join(proj, "src.py"), "print(2)\n")
        commitar(proj, "muda o codigo")
        linhas, passo, rotulo = estado.montar(proj)
        citadas = [l for l in linhas if "arq.md" in l]
        ok = bool(citadas) and "DESATUALIZADO" in citadas[0]
        print(f"  {'ok  ' if ok else 'FALHA'} carimbo velho -> DESATUALIZADO")
        lista.append(("carimbo velho", None, None))
        if not ok:
            falhas.append(f"esperava DESATUALIZADO para arq.md, veio {citadas}")

        # (d) E O CASO QUE JUSTIFICA OS TRES ACIMA: nada disso mudou o cenario
        # nem o passo. Sem esta assercao, o relato poderia ter virado trava e os
        # outros continuariam verdes.
        ok = rotulo == rotulo_antes and passo == passo_antes
        print(f"  {'ok  ' if ok else 'FALHA'} documento desatualizado NAO muda cenario nem passo")
        lista.append(("relato nao bloqueia", None, None))
        if not ok:
            falhas.append(
                f"o relato mudou a recomendacao: {rotulo_antes!r} -> {rotulo!r}")

        # (e) projeto sem pasta docs/: nao pode quebrar nem inventar cobranca
        linhas, _, _ = estado.montar(os.path.join(base, "sem_fila"))
        ok = not [l for l in linhas if l.startswith("DOCUMENTO")]
        print(f"  {'ok  ' if ok else 'FALHA'} projeto sem docs/ nao inventa cobranca")
        lista.append(("sem docs", None, None))
        if not ok:
            falhas.append("reportou documento em projeto sem docs/")

        # O `/fluxo` não pode escrever nada. Um roteador que altera estado
        # deixa de ser roteador.
        proj = os.path.join(base, "prontos")
        antes = json.load(io.open(os.path.join(proj, "tickets", "fila.json"),
                                  encoding="utf-8"))
        estado.montar(proj)
        depois = json.load(io.open(os.path.join(proj, "tickets", "fila.json"),
                                   encoding="utf-8"))
        ok = antes == depois
        print(f"  {'ok  ' if ok else 'FALHA'} nao altera a fila que le")
        lista.append(("nao altera a fila", None, None))
        if not ok:
            falhas.append("estado.montar alterou tickets/fila.json")
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
