#!/usr/bin/env python3
"""Bateria: a destilação **responde**, ou só existe?

A suíte estrutural verifica que os arquivos existem e estão ligados. Isso não é a
mesma coisa que responderem — a destilação inteira poderia estar bem escrita,
carimbada e íntegra, e ainda assim não decidir nada. É a mesma distinção que custou
dois tickets nesta sessão: **testar o script não é testar o sistema.**

## Como a asserção é feita, e por quê

Cada pergunta declara duas coisas na ficha que deveria respondê-la:

- **âncoras** — termos técnicos que não se reescrevem sem mudar o sentido
  (`permissions.deny`, `exit 2`, `paths:`). **Todas** precisam estar presentes.
- **conceitos** — grupos de sinônimos. Basta **um de cada grupo**.

A asserção é assim de propósito. Uma bateria que exigisse frase literal quebraria a
cada ajuste de redação, e bateria que quebra por motivo cosmético é desativada em
semanas. Aqui, para reprovar, é preciso remover o **conceito** — que é exatamente
quando ela deve reprovar.

**Não chama modelo nenhum.** Verificação que depende de inferência não é
determinística, custa a cada execução e não roda no CI.

Rode: python3 tests/testar_bateria.py
"""

import io
import re
import os
import shutil
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(RAIZ, "plugins", "doutrina")

# O console do Windows e cp1252, e as perguntas tem acento. Sem isto o proprio teste
# cai — e caiu, na primeira execucao. E o bug que a ficha `hooks-eventos-e-codigos`
# documenta, cometido pelo arquivo que verifica essa ficha.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# (pergunta, ficha, ancoras, grupos de conceito, a doc erra ou omite?)
PERGUNTAS = [
    ("Isto deve ser hook ou CLAUDE.md?",
     "skills/onde-colocar/SKILL.md",
     ["permissions.deny", "hook"],
     [["pedido"], ["garantia"], ["autoridade"]], False),

    ("Qual precedencia vale quando uma skill e uma rule conflitam?",
     "referencias/duravel/precedencias.md",
     ["managed", "project", "user"],
     [["inverte", "inversão", "invertem"], ["skills"], ["rules", "Rules"]], True),

    ("O que sobrevive ao compact?",
     "referencias/duravel/compaction.md",
     ["paths:"],
     [["reinjetad", "relid", "do disco"], ["compaction", "compact"]], False),

    ("O indice de skills sobrevive ao compact?",
     "referencias/armadilhas.md",
     ["compaction"],
     [["índice", "indice"], ["omite", "omit"]], True),

    ("Como paralelizo uma mudanca grande?",
     "skills/paralelizar/SKILL.md",
     ["worktree", "subagente"],
     [["quem segura o plano"], ["intermediári"], ["isola"]], False),

    ("Escrevi um hook e ele nao bloqueia. Por que?",
     "skills/garantir/SKILL.md",
     ["exit", "127"],
     [["não bloqueia", "nao bloqueia"], ["confiada"], ["stdout"]], False),

    ("Minha skill nao dispara. Por que?",
     "skills/escrever-skill/SKILL.md",
     ["description", "frontmatter"],
     [["encurtad", "truncad"], ["disponíveis", "disponiveis", "listagem", "lista"]],
     False),

    ("O que faco quando o contexto enche?",
     "skills/contexto/SKILL.md",
     ["subagente"],
     [["duas vezes", "mais de duas"], ["recomeç", "recomec"], ["não deixar entrar",
                                                               "nao deixar entrar"]],
     False),

    ("Como escopo o Claude num monorepo?",
     "skills/distribuir/SKILL.md",
     ["settings.json", "paths:"],
     [["herdad"], ["camadas", "por diretório", "por diretorio"]], True),

    ("Onde vivem os resultados intermediarios de cada mecanismo?",
     "referencias/duravel/matriz.md",
     ["subagente"],
     [["intermediári"], ["variáveis de script", "variaveis de script"]], False),

    ("Quais campos o frontmatter de uma skill aceita?",
     "referencias/volatil/frontmatter-de-skill.md",
     ["disable-model-invocation", "allowed-tools", "context"],
     [["fork"], ["description"]], False),

    ("Que exit code bloqueia um hook?",
     "referencias/volatil/hooks-eventos-e-codigos.md",
     ["PreToolUse", "127"],
     [["bloqueia"], ["stderr"]], False),

    ("Onde vao as skills dentro de um plugin?",
     "referencias/volatil/plugin-json.md",
     [".claude-plugin", "skills/"],
     [["raiz do plugin"], ["namespace", "namespaced"]], False),

    ("Como nego leitura de um caminho?",
     "referencias/volatil/regras-de-permissao.md",
     ["deny", "Read("],
     [["primeira que casa", "first match"], ["sandbox"]], False),

    # A pergunta que vem ANTES de escolher mecanismo, e que o doutrina nao respondia:
    # a doutrina de arquitetura de agentes nao esta na arvore de documentacao.
    ("Isto deve ser agente ou workflow?",
     "skills/arquitetar/SKILL.md",
     ["workflow", "agente"],
     [["degrau", "escada"], ["previsível", "previsivel", "predefinid"]], True),

    ("Quanto custa montar multiagente?",
     "referencias/duravel/arquitetura-de-agentes.md",
     ["15", "90,2%"],
     [["token"], ["1.000", "2.000"]], True),

    ("Meu harness precisa mudar quando sai um modelo novo?",
     "referencias/duravel/arquitetura-de-agentes.md",
     ["remova", "meça"],
     [["obsolesc", "envelhec"], ["suposição", "suposicao", "desconfian"]], True),

    ("Como sei se o meu verificador e bom?",
     "skills/avaliar/SKILL.md",
     ["regress", "negativ"],
     [["cobertura"], ["otimiza", "gargalo"]], True),

    ("Devo relatar pass@k ou pass^k?",
     "skills/avaliar/SKILL.md",
     ["pass@k", "pass^k"],
     [["toda vez", "usuário", "usuario"], ["diverg", "despenca"]], True),

    ("Meu revisor acha problema em tudo. Isso e bom?",
     "referencias/duravel/evals.md",
     ["transcript", "calibr"],
     [["grader"], ["balanceado", "negativ"]], True),

    # Medidas num projeto de terceiro, cujos cinco hooks estavam inertes sem
    # ninguem saber — inclusive o agente que escreveu o mapa daquele projeto.
    ("Meu hook falhou. Eu consigo ver isso?",
     "referencias/armadilhas.md",
     ["exit 2"],
     [["não bloqueante", "nao bloqueante"], ["usuario", "usuário"],
      ["cego", "nunca"]], True),

    ("Que caminho uso num hook no Windows?",
     "referencias/armadilhas.md",
     ["Git Bash", "cmd"],
     [["python3"], ["contrabarra", "barra"]], True),
]


def responde(raiz_plugin, ficha, ancoras, grupos):
    """Devolve a lista do que falta. Vazia significa que a ficha responde."""
    caminho = os.path.join(raiz_plugin, ficha)
    if not os.path.isfile(caminho):
        return [f"ficha ausente: {ficha}"]
    try:
        texto = io.open(caminho, encoding="utf-8").read()
    except OSError as erro:
        return [f"ficha ilegivel: {erro}"]

    # Casamento sem distinguir caixa: um termo no comeco de frase aparece com
    # maiuscula, e exigir a forma exata faria a bateria reprovar por motivo
    # tipografico — que e a fragilidade que ela existe para nao ter.
    baixo = texto.lower()
    faltando = [f"ancora ausente: {a!r}" for a in ancoras if a.lower() not in baixo]
    for grupo in grupos:
        if not any(g.lower() in baixo for g in grupo):
            faltando.append(f"nenhum de {grupo}")
    return faltando


def main():
    falhas, total = [], 0
    cobertas = set()

    print("== a destilacao responde? ==")
    for pergunta, ficha, ancoras, grupos, doc_erra in PERGUNTAS:
        total += 1
        cobertas.add(ficha)
        faltando = responde(PLUGIN, ficha, ancoras, grupos)
        marca = "ok  " if not faltando else "FALHA"
        selo = "   <- a doc erra ou omite" if doc_erra else ""
        print(f"  {marca} {pergunta}{selo}")
        if faltando:
            falhas.append(f"{pergunta} -> {ficha}: {'; '.join(faltando)}")

    # Toda ficha do plugin precisa de ao menos uma pergunta. Ficha que nenhuma
    # pergunta alcanca e ficha que ninguem sabe se serve — e o proposito da bateria
    # e justamente medir serventia, nao existencia.
    print("== toda ficha tem pergunta? ==")
    total += 1
    no_disco = set()
    for topo in ("skills", "referencias"):
        base = os.path.join(PLUGIN, topo)
        for pasta, _, arquivos in os.walk(base):
            for nome in arquivos:
                if nome.endswith(".md"):
                    rel = os.path.relpath(os.path.join(pasta, nome), PLUGIN)
                    no_disco.add(rel.replace(os.sep, "/"))
    sem_pergunta = sorted(no_disco - cobertas)
    print(f"  {'ok  ' if not sem_pergunta else 'FALHA'} "
          f"{len(cobertas)} de {len(no_disco)} fichas cobertas")
    if sem_pergunta:
        falhas.append("ficha sem pergunta: " + ", ".join(sem_pergunta))

    # A doc oficial erra ou omite pelo menos duas destas respostas. Sao elas que
    # provam que a destilacao vale mais que um link para a fonte.
    print("== perguntas que a doc erra ou omite ==")
    total += 1
    marcadas = sum(1 for *_, doc_erra in PERGUNTAS if doc_erra)
    print(f"  {'ok  ' if marcadas >= 2 else 'FALHA'} {marcadas} pergunta(s) marcada(s)")
    if marcadas < 2:
        falhas.append(f"apenas {marcadas} pergunta(s) em que a doc erra; minimo 2")

    # O teste inverso. Sem ele, uma bateria que sempre aprova passaria despercebida —
    # que e exatamente o defeito que ela existe para nao ter.
    print("== apagar o trecho central faz reprovar? ==")
    total += 1
    base = tempfile.mkdtemp(prefix="bateria-inverso-")
    try:
        copia = os.path.join(base, "doutrina")
        shutil.copytree(PLUGIN, copia)
        alvo = os.path.join(copia, "referencias", "duravel", "precedencias.md")
        texto = io.open(alvo, encoding="utf-8").read()
        # Apaga o CONCEITO, não uma grafia dele: `inverte`, `invertem`, `inversão`.
        # Na primeira tentativa apaguei só duas das três formas, e a bateria aprovou —
        # o teste inverso pegou a fraqueza do próprio teste inverso.
        io.open(alvo, "w", encoding="utf-8", newline="\n").write(
            re.sub(r"invert\w*|invers\w*", "", texto, flags=re.IGNORECASE))
        faltando = responde(copia, "referencias/duravel/precedencias.md",
                            ["managed", "project", "user"],
                            [["inverte", "inversão", "invertem"], ["skills"],
                             ["rules", "Rules"]])
        ok = bool(faltando)
        print(f"  {'ok  ' if ok else 'FALHA'} sem o conceito, a bateria acusa")
        if not ok:
            falhas.append("apagar o conceito central nao fez a bateria reprovar")
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
