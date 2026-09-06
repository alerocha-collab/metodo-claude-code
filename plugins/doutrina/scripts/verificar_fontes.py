#!/usr/bin/env python3
"""Verifica o índice das fontes e detecta drift na documentação.

Faz duas coisas, e a distinção importa porque só a primeira funciona offline:

  **Estrutura** (sem rede) — o índice é coerente? Toda página do núcleo tem ficha
  local? Toda ficha tem fonte? Toda ficha volátil tem carimbo?

  **Drift** (com rede) — o markdown publicado ainda tem o hash que registramos?

**Detecta. Nunca atualiza.** Um índice que corrige o próprio hash perde a única
propriedade que o torna confiável: a de poder estar visivelmente errado. Reescrever
uma ficha exige julgamento, e julgamento continua humano.

FAIL-CLOSED no que não consegue determinar. Página sem hash, hash ilegível, falha de
rede: todos contam como "não sei", e "não sei" sai diferente de zero. Não conseguir
olhar nunca vira "está em dia".

Uso:
  python3 verificar_fontes.py                 # só estrutura, sem rede
  python3 verificar_fontes.py --drift         # estrutura + drift do núcleo
  python3 verificar_fontes.py --drift --tudo  # drift de todas as 191
"""

import argparse
import hashlib
import io
import json
import os
import sys

RAIZ_PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTES = os.path.join(RAIZ_PLUGIN, "fontes.json")

# Caminhos de ficha sao relativos a RAIZ DO PLUGIN, nao a `referencias/`: uma ficha
# tanto pode ser o corpo de uma skill quanto um arquivo de referencia, e as duas
# precisam ser rastreaveis ate a pagina de origem.
PASTAS_DE_FICHA = ("referencias", "skills")

# Uma ficha volátil copia schema, campo e número — coisas que envelhecem em semanas.
# Sem carimbo, ninguém sabe se ainda vale, e um agente responde com confiança a partir
# de um schema morto. Estes dois marcadores são o mínimo exigido.
MARCAS_CARIMBO = ("url:", "http")
MARCA_DATA = "verificado em"

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def carregar():
    with io.open(FONTES, encoding="utf-8") as f:
        return json.load(f)


def buscar_padrao(url, timeout=30):
    """Busca o markdown bruto. Isolada para os testes poderem injetar outra."""
    from urllib.request import Request, urlopen
    req = Request(url, headers={"User-Agent": "metodo-doutrina/verificador"})
    with urlopen(req, timeout=timeout) as r:
        return r.read()


def sha(dados):
    return hashlib.sha256(dados).hexdigest()


def verificar_estrutura(doc, raiz_plugin=RAIZ_PLUGIN):
    """Coerência do índice. Devolve a lista de problemas; vazia significa íntegro."""
    problemas = []
    paginas = doc.get("paginas")
    if not isinstance(paginas, list) or not paginas:
        return ["fontes.json nao traz uma lista `paginas`"]

    vistos = set()
    fichas_declaradas = set()

    for p in paginas:
        pid = p.get("id")
        if not pid:
            problemas.append("pagina sem `id`")
            continue
        if pid in vistos:
            problemas.append(f"id repetido: {pid}")
        vistos.add(pid)

        if not p.get("url"):
            problemas.append(f"{pid}: sem `url`")
        if p.get("prioridade") not in {"nucleo", "indice"}:
            problemas.append(f"{pid}: prioridade invalida: {p.get('prioridade')!r}")

        fichas = p.get("fichas") or []
        if not isinstance(fichas, list):
            problemas.append(f"{pid}: `fichas` precisa ser lista")
            continue

        for ficha in fichas:
            fichas_declaradas.add(ficha)
            caminho = os.path.join(raiz_plugin, ficha)
            if not os.path.isfile(caminho):
                problemas.append(f"{pid}: ficha declarada nao existe: {ficha}")
                continue
            if "volatil" in ficha.split("/"):
                problemas.extend(conferir_carimbo(caminho, ficha))

    # O inverso: ficha em disco que ninguem declarou e ficha orfa — ninguem sabe de
    # onde ela veio, e portanto ninguem sabe quando ela ficou velha.
    for topo in PASTAS_DE_FICHA:
        base = os.path.join(raiz_plugin, topo)
        if not os.path.isdir(base):
            continue
        for pasta, _, arquivos in os.walk(base):
            for nome in arquivos:
                if not nome.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(pasta, nome), raiz_plugin)
                rel = rel.replace(os.sep, "/")
                if rel not in fichas_declaradas and not rel.startswith("_"):
                    problemas.append(f"ficha orfa, sem fonte declarada: {rel}")

    return problemas


def conferir_carimbo(caminho, rotulo):
    try:
        with io.open(caminho, encoding="utf-8") as f:
            texto = f.read(4000).lower()
    except OSError as erro:
        return [f"{rotulo}: nao pode ser lida: {erro}"]
    faltando = []
    if not any(m in texto for m in MARCAS_CARIMBO):
        faltando.append("url de origem")
    if MARCA_DATA not in texto:
        faltando.append("data de verificacao")
    if faltando:
        return [f"{rotulo}: ficha volatil sem {' e sem '.join(faltando)}"]
    return []


def verificar_drift(doc, buscar=buscar_padrao, tudo=False):
    """Compara o hash publicado com o registrado.

    Devolve (mudadas, indeterminadas, iguais). `indeterminadas` existe separada de
    `mudadas` de proposito: nao saber nao e a mesma coisa que ter mudado, e tratar as
    duas igual esconde falha de rede atras de alarme de conteudo.
    """
    mudadas, indeterminadas, iguais = [], [], []
    for p in doc.get("paginas") or []:
        if not tudo and p.get("prioridade") != "nucleo":
            continue
        pid, url, registrado = p.get("id"), p.get("url"), p.get("hash")
        if not registrado:
            indeterminadas.append(f"{pid}: sem hash registrado")
            continue
        try:
            atual = sha(buscar(url))
        except Exception as erro:  # noqa: BLE001 — qualquer falha e indeterminacao
            indeterminadas.append(f"{pid}: nao consegui buscar: {type(erro).__name__}")
            continue
        (iguais if atual == registrado else mudadas).append(pid)
    return mudadas, indeterminadas, iguais


def main(argv=None):
    p = argparse.ArgumentParser(description="Verifica o indice e detecta drift.")
    p.add_argument("--drift", action="store_true", help="tambem consulta a rede")
    p.add_argument("--tudo", action="store_true", help="drift de todas, nao so do nucleo")
    args = p.parse_args(argv)

    if not os.path.isfile(FONTES):
        print(f"fontes.json nao encontrado: {FONTES}", file=sys.stderr)
        return 1
    try:
        doc = carregar()
    except (OSError, json.JSONDecodeError) as erro:
        print(f"fontes.json ilegivel: {erro}", file=sys.stderr)
        return 1

    paginas = doc.get("paginas") or []
    nucleo = [x for x in paginas if x.get("prioridade") == "nucleo"]
    print(f"INDICE      {len(paginas)} pagina(s) · {len(nucleo)} nucleo · "
          f"{len(paginas) - len(nucleo)} so indexadas")

    problemas = verificar_estrutura(doc)
    if problemas:
        print(f"ESTRUTURA   {len(problemas)} problema(s)")
        for pr in problemas:
            print(f"  - {pr}")
    else:
        print("ESTRUTURA   integra")

    if not args.drift:
        print("\nDRIFT       nao verificado (rode com --drift)")
        return 1 if problemas else 0

    mudadas, indeterminadas, iguais = verificar_drift(doc, tudo=args.tudo)
    print(f"\nDRIFT       {len(iguais)} igual(is) · {len(mudadas)} mudada(s) · "
          f"{len(indeterminadas)} indeterminada(s)")
    for pid in mudadas:
        print(f"  MUDOU        {pid}")
    for i in indeterminadas:
        print(f"  NAO SEI      {i}")

    if mudadas or indeterminadas:
        print("\nNada aqui atualiza o hash, de proposito. Releia a pagina, decida se a")
        print("ficha ainda descreve o mecanismo, e so entao recarimbe a mao.")

    return 1 if (problemas or mudadas or indeterminadas) else 0


if __name__ == "__main__":
    sys.exit(main())
