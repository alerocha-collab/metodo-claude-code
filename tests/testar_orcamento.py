#!/usr/bin/env python3
"""Orçamento de contexto: quanto os dois plugins custam em **todo request**.

As descrições das skills carregam no início de cada sessão para o Claude poder
escolher. Isso não é só espaço: quando a listagem estoura o orçamento que o Claude
Code reserva para ela, as descrições são **encurtadas** — e o que se perde são as
palavras-chave que fazem a skill disparar.

Uma descrição gorda não custa só o próprio tamanho. Ela empurra as vizinhas para
fora, e a skill que some é a que alguém precisava.

Por isso os dois tetos, e o segundo importa mais: o **total** avisa que o conjunto
cresceu; o **por skill** pega a próxima que nascer gorda, na hora, e não daqui a seis
skills quando o dano já está distribuído.

Os números foram medidos, não estimados. Ver `DECISIONS.md`.

Rode: python3 tests/testar_orcamento.py
"""

import io
import os
import re
import sys
from glob import glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tetos declarados. Passar deles nao e erro de sintaxe: e sinal de que o conjunto
# precisa de poda, ou de que o teto precisa de uma decisao registrada para subir.
TETO_TOTAL = 5000       # caracteres, somando as duas metades de todas as skills
TETO_POR_SKILL = 520    # a maior hoje esta em 486

# A fonte cita 1.536 caracteres como o teto por skill na listagem. Nosso teto e bem
# mais baixo de proposito: chegar perto do limite da plataforma ja significa estar
# consumindo o orcamento das outras.
TETO_DA_PLATAFORMA = 1536

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def medir(raiz=RAIZ):
    """Devolve [(caracteres, nome, caminho)], da maior para a menor."""
    itens = []
    for caminho in glob(os.path.join(raiz, "plugins", "*", "skills", "*", "SKILL.md")):
        texto = io.open(caminho, encoding="utf-8").read()
        m = re.search(r"^---\n(.*?)\n---", texto, re.S)
        fm = m.group(1) if m else ""
        d = re.search(r"^description:(.*?)(?=\n[a-z_-]+:|\Z)", fm, re.S | re.M)
        w = re.search(r"^when_to_use:(.*?)(?=\n[a-z_-]+:|\Z)", fm, re.S | re.M)
        tamanho = len((d.group(1) if d else "") + (w.group(1) if w else ""))
        nome = os.path.basename(os.path.dirname(caminho))
        itens.append((tamanho, nome, caminho))
    itens.sort(reverse=True)
    return itens


def main():
    falhas, total = [], 0
    itens = medir()

    soma = sum(t for t, _, _ in itens)
    print(f"== orcamento de descricao: {len(itens)} skills ==")
    for tamanho, nome, _ in itens[:5]:
        print(f"  {tamanho:5}  {nome}")
    print(f"  {'-'*5}")
    print(f"  {soma:5}  total (~{soma // 4} tokens em TODO request)")
    print()

    total += 1
    ok = bool(itens)
    print(f"  {'ok  ' if ok else 'FALHA'} ha skills para medir")
    if not ok:
        falhas.append("nenhuma skill encontrada — o medidor esta olhando o lugar errado")
        print(f"\n{len(falhas)} de {total} FALHARAM")
        return 1

    total += 1
    ok = soma <= TETO_TOTAL
    print(f"  {'ok  ' if ok else 'FALHA'} soma {soma} dentro do teto de {TETO_TOTAL}")
    if not ok:
        falhas.append(
            f"soma {soma} passou de {TETO_TOTAL}. Ou pode uma descricao, ou suba o "
            "teto com uma decisao registrada — mas nao suba em silencio")

    total += 1
    gordas = [(t, n) for t, n, _ in itens if t > TETO_POR_SKILL]
    print(f"  {'ok  ' if not gordas else 'FALHA'} nenhuma skill acima de "
          f"{TETO_POR_SKILL} (maior: {itens[0][0]})")
    if gordas:
        falhas.append("skill(s) gorda(s): " +
                      ", ".join(f"{n} com {t}" for t, n in gordas))

    # Nenhuma pode nem chegar perto do teto da plataforma: la a descricao e cortada,
    # e o corte leva as palavras-chave que fazem a skill disparar.
    total += 1
    perigosas = [(t, n) for t, n, _ in itens if t > TETO_DA_PLATAFORMA * 0.6]
    print(f"  {'ok  ' if not perigosas else 'FALHA'} nenhuma perto do teto da "
          f"plataforma ({TETO_DA_PLATAFORMA})")
    if perigosas:
        falhas.append("perto do corte da plataforma: " +
                      ", ".join(f"{n} com {t}" for t, n in perigosas))

    # E o inverso: descricao vazia nao dispara nunca. Um teto que so olha para cima
    # aprovaria uma skill sem descricao nenhuma.
    total += 1
    mudas = [n for t, n, _ in itens if t < 40]
    print(f"  {'ok  ' if not mudas else 'FALHA'} nenhuma skill sem descricao util")
    if mudas:
        falhas.append("skill(s) sem descricao: " + ", ".join(mudas))

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
