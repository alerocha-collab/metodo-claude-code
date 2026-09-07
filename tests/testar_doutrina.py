#!/usr/bin/env python3
"""Suite do índice de fontes e do detector de drift do plugin `doutrina`.

Balanceada: o caso "nada mudou, não acuse" vale tanto quanto os de alarme. Um
detector só testado contra drift passa acusando sempre — e alarme que sempre toca
é alarme desligado.

A busca de rede é **injetada**, nunca real. Teste que depende de rede falha por
motivo errado, e um dia é desativado por ser instável.

Rode: python3 tests/testar_doutrina.py
"""

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plugins", "doutrina", "scripts"))

import verificar_fontes as vf  # noqa: E402

FONTES_REAL = os.path.join(RAIZ, "plugins", "doutrina", "fontes.json")


def sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def doc_minimo(**ajustes):
    base = {
        "paginas": [
            {"id": "skills", "titulo": "Skills", "secao": "skills",
             "url": "https://exemplo.invalido/skills.md", "prioridade": "nucleo",
             "hash": None, "verificada_em": None, "fichas": []},
        ]
    }
    base.update(ajustes)
    return base


def escrever(caminho, texto):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with io.open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


# ---------------------------------------------------------------- estrutura

def casos_estrutura(base):
    """(nome, doc, raiz_referencias, deve_reprovar, trecho)"""
    vazio = os.path.join(base, "vazio")
    os.makedirs(vazio, exist_ok=True)

    # Espelha a estrutura real: fichas sao relativas a RAIZ DO PLUGIN, e podem estar
    # tanto em `referencias/` quanto em `skills/`.
    com_ficha = os.path.join(base, "com_ficha")
    ref = os.path.join(com_ficha, "referencias")
    escrever(os.path.join(ref, "duravel", "onde.md"), "# Onde colocar\n")
    escrever(os.path.join(ref, "volatil", "schema.md"),
             "# Schema\n\nurl: https://code.claude.com/docs/en/skills.md\n"
             "Verificado em 2026-09-06.\n")
    escrever(os.path.join(ref, "volatil", "sem-carimbo.md"), "# Schema solto\n")
    # Carimbo pela metade: tem a fonte, nao tem a data. E o caso mais provavel de
    # acontecer de verdade — quem copia um schema lembra de citar a origem e esquece
    # de datar, e sem data ninguem sabe se a copia ainda vale.
    escrever(os.path.join(ref, "volatil", "sem-data.md"),
             "# Schema\n\nurl: https://code.claude.com/docs/en/hooks.md\n")
    escrever(os.path.join(ref, "duravel", "orfa.md"), "# Ninguem me declarou\n")
    escrever(os.path.join(com_ficha, "skills", "uma", "SKILL.md"), "# Uma skill\n")

    # Fixture separada e impecavel: tudo que existe esta declarado, e o que e volatil
    # esta carimbado. E o caso que impede um verificador que reprova sempre — sem ele,
    # os sete acima aprovariam um validador quebrado.
    tudo_ok = os.path.join(base, "tudo_ok")
    escrever(os.path.join(tudo_ok, "referencias", "duravel", "onde.md"), "# Onde\n")
    escrever(os.path.join(tudo_ok, "referencias", "volatil", "schema.md"),
             "# Schema\n\nurl: https://code.claude.com/docs/en/skills.md\n"
             "Verificado em 2026-09-06.\n")
    escrever(os.path.join(tudo_ok, "skills", "uma", "SKILL.md"), "# Uma skill\n")

    def pag(**kw):
        d = {"id": "skills", "titulo": "S", "secao": "skills",
             "url": "https://x.invalido/s.md", "prioridade": "nucleo",
             "hash": None, "verificada_em": None, "fichas": []}
        d.update(kw)
        return d

    return [
        # --- DEVE reprovar ---
        ("sem lista de paginas", {"outra_coisa": []}, vazio, True, "paginas"),
        ("id repetido",
         {"paginas": [pag(), pag()]}, vazio, True, "id repetido"),
        ("pagina sem url",
         {"paginas": [pag(url=None)]}, vazio, True, "sem `url`"),
        ("prioridade invalida",
         {"paginas": [pag(prioridade="talvez")]}, vazio, True, "prioridade invalida"),
        ("ficha declarada que nao existe",
         {"paginas": [pag(fichas=["referencias/duravel/nao-existe.md"])]}, vazio,
         True, "nao existe"),
        ("ficha volatil sem carimbo nenhum",
         {"paginas": [pag(fichas=["referencias/volatil/sem-carimbo.md"])]}, com_ficha,
         True, "sem url de origem"),
        ("ficha volatil com fonte mas sem data",
         {"paginas": [pag(fichas=["referencias/volatil/sem-data.md"])]}, com_ficha,
         True, "sem data de verificacao"),
        ("ficha orfa em disco",
         {"paginas": [pag(fichas=["referencias/duravel/onde.md"])]}, com_ficha,
         True, "orfa"),
        ("corpo de skill orfo tambem acusa",
         {"paginas": [pag(fichas=["referencias/duravel/onde.md",
                                  "referencias/duravel/orfa.md",
                                  "referencias/volatil/schema.md",
                                  "referencias/volatil/sem-data.md",
                                  "referencias/volatil/sem-carimbo.md"])]},
         com_ficha, True, "skills/uma/SKILL.md"),
        # --- NAO deve reprovar ---
        ("indice sem ficha nenhuma", doc_minimo(), vazio, False, None),
        ("tudo declarado e carimbado: nao acusa",
         {"paginas": [pag(fichas=["referencias/duravel/onde.md",
                                  "referencias/volatil/schema.md",
                                  "skills/uma/SKILL.md"])]},
         tudo_ok, False, None),
    ]


# ---------------------------------------------------------------- drift

def casos_drift():
    """(nome, doc, buscar, esperado) onde esperado = (mudadas, indet, iguais)"""
    conteudo = "# Skills\n\nconteudo publicado\n"
    h = sha(conteudo)

    def busca_ok(url, timeout=30):
        return conteudo.encode("utf-8")

    def busca_outra(url, timeout=30):
        return b"# Skills\n\nOUTRA COISA\n"

    def busca_quebra(url, timeout=30):
        raise OSError("rede indisponivel")

    def pag(**kw):
        d = {"id": "skills", "url": "https://x.invalido/s.md",
             "prioridade": "nucleo", "hash": h}
        d.update(kw)
        return d

    return [
        # NAO deve acusar: o caso que impede um detector que acusa sempre
        ("nada mudou: nao acusa", {"paginas": [pag()]}, busca_ok, (0, 0, 1)),
        # DEVE acusar
        ("conteudo mudou", {"paginas": [pag()]}, busca_outra, (1, 0, 0)),
        ("sem hash registrado e indeterminado, nao `mudou`",
         {"paginas": [pag(hash=None)]}, busca_ok, (0, 1, 0)),
        ("falha de rede e indeterminado, nao `mudou`",
         {"paginas": [pag()]}, busca_quebra, (0, 1, 0)),
        # Paginas so indexadas ficam de fora por padrao
        ("pagina de indice e pulada sem --tudo",
         {"paginas": [pag(prioridade="indice")]}, busca_outra, (0, 0, 0)),
    ]


def main():
    base = tempfile.mkdtemp(prefix="doutrina-testes-")
    falhas, total = [], 0
    try:
        print("== estrutura ==")
        for nome, doc, raiz, deve_reprovar, trecho in casos_estrutura(base):
            total += 1
            problemas = vf.verificar_estrutura(doc, raiz)
            ok = bool(problemas) == deve_reprovar
            if ok and trecho:
                ok = any(trecho in p for p in problemas)
            print(f"  {'ok  ' if ok else 'FALHA'} {nome}")
            if not ok:
                falhas.append(f"{nome}: {problemas}")

        print("== drift ==")
        for nome, doc, buscar, esperado in casos_drift():
            total += 1
            m, i, ig = vf.verificar_drift(doc, buscar=buscar)
            obtido = (len(m), len(i), len(ig))
            ok = obtido == esperado
            print(f"  {'ok  ' if ok else 'FALHA'} {nome} -> {obtido}")
            if not ok:
                falhas.append(f"{nome}: esperava {esperado}, veio {obtido}")

        print("== nao escreve ==")
        total += 1
        antes = io.open(FONTES_REAL, encoding="utf-8").read()
        vf.verificar_drift(vf.carregar(), buscar=lambda u, timeout=30: b"outro")
        vf.verificar_estrutura(vf.carregar())
        ok = io.open(FONTES_REAL, encoding="utf-8").read() == antes
        print(f"  {'ok  ' if ok else 'FALHA'} detectar nao altera fontes.json")
        if not ok:
            falhas.append("verificar_* alterou fontes.json")

        print("== indice real ==")
        total += 1
        doc = vf.carregar()
        problemas = vf.verificar_estrutura(doc)
        ok = not problemas
        print(f"  {'ok  ' if ok else 'FALHA'} o indice deste repo e integro")
        if not ok:
            falhas.extend(problemas)

        total += 1
        n = len(doc.get("paginas") or [])
        ok = n >= 150
        print(f"  {'ok  ' if ok else 'FALHA'} indice cobre a doc inteira ({n} paginas)")
        if not ok:
            falhas.append(f"indice com apenas {n} paginas; a doc tem ~191")

        # O blog de engenharia foi o ponto cego original: a doutrina de arquitetura
        # de agentes nao esta na arvore de documentacao, e por isso ficou de fora.
        total += 1
        eng = [p for p in doc["paginas"] if p.get("secao") == "engenharia"]
        ok = len(eng) >= 10
        print(f"  {'ok  ' if ok else 'FALHA'} o blog de engenharia esta indexado ({len(eng)})")
        if not ok:
            falhas.append(f"so {len(eng)} paginas de engenharia indexadas")

        # Pagina de HTML precisa dizer que e HTML, senao o hash e calculado sobre os
        # bytes crus e o detector acusa a cada build do site.
        total += 1
        erradas = [p["id"] for p in eng if p.get("formato") != "html"]
        print(f"  {'ok  ' if not erradas else 'FALHA'} toda pagina de engenharia declara formato html")
        if erradas:
            falhas.append(f"paginas de engenharia sem formato html: {erradas[:5]}")

        print("== normalizacao de html ==")
        # Mesmo artigo, build diferente do site: nonce, classe com hash, script novo.
        # O hash TEM que ser o mesmo, ou o detector vira ruido semanal.
        a = ('<html><head><style>.a{color:red}</style>'
             '<script nonce="abc123">var buildId="x1"</script></head>'
             '<body><h1>Titulo</h1><p>O texto do artigo.</p></body></html>')
        b = ('<html><head><style>.b{color:blue}</style>'
             '<script nonce="zzz999">var buildId="y7"</script></head>'
             '<body><h1 class="css-8f3a">Titulo</h1><p>O texto do artigo.</p></body></html>')
        total += 1
        ok = vf.sha(a, "html") == vf.sha(b, "html")
        print(f"  {'ok  ' if ok else 'FALHA'} ruido de build nao muda o hash")
        if not ok:
            falhas.append("normalizacao nao absorveu nonce/classe/script")

        # E o inverso, sem o qual um normalizador que devolvesse "" passaria acima:
        # mudanca no TEXTO tem que mudar o hash.
        total += 1
        c_ = a.replace("O texto do artigo.", "O texto do artigo, revisado.")
        ok = vf.sha(a, "html") != vf.sha(c_, "html")
        print(f"  {'ok  ' if ok else 'FALHA'} mudanca de texto MUDA o hash")
        if not ok:
            falhas.append("normalizacao apagou o conteudo: texto diferente deu hash igual")

        # E o formato markdown nao pode passar pela normalizacao: um `<` legitimo
        # dentro de um bloco de codigo viraria espaco, e o hash mediria outra coisa.
        total += 1
        md = "# Titulo\n\nUse `if x < 10:` no exemplo.\n"
        ok = vf.sha(md) != vf.sha(md, "html")
        print(f"  {'ok  ' if ok else 'FALHA'} markdown nao passa pela normalizacao de html")
        if not ok:
            falhas.append("sha() tratou markdown como html")
    finally:
        shutil.rmtree(base, ignore_errors=True)

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
