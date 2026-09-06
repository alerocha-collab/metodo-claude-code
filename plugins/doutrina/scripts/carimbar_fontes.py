#!/usr/bin/env python3
"""Registra o hash atual de páginas da documentação. **Ato deliberado.**

Este script existe separado do `verificar_fontes.py` de propósito, e a separação é
o desenho, não organização: **quem detecta não carimba.**

Um detector que atualiza o próprio hash ao encontrar diferença nunca acusa nada — ele
apenas registra a realidade nova e chama isso de estar em dia. O carimbo precisa ser
um ato humano, porque a pergunta que ele responde não é "o conteúdo mudou?" (isso a
máquina sabe) e sim "a ficha que escrevi ainda descreve este mecanismo?" (isso ela
não sabe).

Então o fluxo é: o detector acusa → uma pessoa relê a página e a ficha → a pessoa
corrige a ficha se precisar → e só então roda isto.

Uso:
  python3 carimbar_fontes.py --nucleo          # as paginas destiladas
  python3 carimbar_fontes.py skills hooks      # paginas especificas, por id
  python3 carimbar_fontes.py --tudo            # todas as 191
"""

import argparse
import datetime
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import verificar_fontes as vf  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def main(argv=None):
    p = argparse.ArgumentParser(description="Registra o hash atual das paginas.")
    p.add_argument("ids", nargs="*", help="ids especificos a carimbar")
    p.add_argument("--nucleo", action="store_true", help="todas as de prioridade nucleo")
    p.add_argument("--tudo", action="store_true", help="todas as paginas")
    args = p.parse_args(argv)

    if not (args.ids or args.nucleo or args.tudo):
        p.error("diga o que carimbar: ids, --nucleo ou --tudo")

    doc = vf.carregar()
    paginas = doc.get("paginas") or []

    if args.tudo:
        alvo = paginas
    elif args.nucleo:
        alvo = [x for x in paginas if x.get("prioridade") == "nucleo"]
    else:
        pedidos = set(args.ids)
        alvo = [x for x in paginas if x.get("id") in pedidos]
        faltando = pedidos - {x.get("id") for x in alvo}
        if faltando:
            print(f"id(s) nao encontrado(s) no indice: {', '.join(sorted(faltando))}",
                  file=sys.stderr)
            return 1

    hoje = datetime.date.today().isoformat()
    novos, iguais, falhos = 0, 0, []

    for pagina in alvo:
        pid = pagina["id"]
        try:
            atual = vf.sha(vf.buscar_padrao(pagina["url"]))
        except Exception as erro:  # noqa: BLE001
            falhos.append(f"{pid}: {type(erro).__name__}")
            print(f"  FALHOU  {pid}")
            continue
        if pagina.get("hash") == atual:
            iguais += 1
            pagina["verificada_em"] = hoje
            print(f"  igual   {pid}")
        else:
            antes = "novo" if not pagina.get("hash") else "MUDOU"
            pagina["hash"] = atual
            pagina["verificada_em"] = hoje
            novos += 1
            print(f"  {antes:7} {pid}")

    with io.open(vf.FONTES, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    print(f"\n{novos} carimbada(s), {iguais} inalterada(s), {len(falhos)} falha(s).")
    for erro in falhos:
        print(f"  - {erro}")

    if novos:
        print("\nCarimbar NAO revisa a ficha. Se alguma destas paginas tem ficha local,")
        print("releia a ficha antes de confiar nela — o hash so diz que a fonte mudou,")
        print("nao que a sua destilacao continua certa.")

    return 1 if falhos else 0


if __name__ == "__main__":
    sys.exit(main())
