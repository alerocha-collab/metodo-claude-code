# Referência 07 — Template do documento de arquitetura

Preencha todas as seções. Seção sem conteúdo é sinal de que o passo correspondente do procedimento não foi feito — volte e faça, não escreva "N/A".

---

```markdown
# Arquitetura — <nome do sistema>

## 1. Problema e critério de pronto

**O que se constrói:** <uma frase>
**Quem opera:** <dev que avalia comandos bash | knowledge worker | pipeline sem humano>
**Duração de uma execução:** <minutos | horas | múltiplas sessões>

**Pronto significa:** <critério verificável, não adjetivo>
**Fora de escopo:** <o que deliberadamente não se resolve aqui>

## 2. Degrau de complexidade

**Parada no degrau <0–4>: <nome>.**

Justificativa da parada: <por que o degrau anterior não bastava, e por que o próximo não se paga>

<Se degrau 3 ou 4:> **Custo declarado:** sistemas multiagente usam ~15× mais tokens que chat.
A tarefa justifica porque <razão concreta e mensurável>.

## 3. Loop de verificação

**Comando que produz pass/fail:** `<comando literal>`

**Qualidade do verificador:**
- Cobertura de casos negativos: <como>
- Proteção contra regressão: <como>
- Custo de contexto da saída: <estatística resumida? amostragem? formato parsável?>
- Confiança: <alta | média | baixa — e o que a melhoraria>

**Dureza do portão:** <no prompt | condição de /goal | Stop hook | subagente revisor>
Justificativa: <quanto de atenção humana se troca por setup>

**Quem dá a nota:** <o próprio executor | avaliador separado>
<Se separado:> critérios e pesos: <lista>. Calibração: <exemplos few-shot? leitura de logs?>

> Instrução obrigatória ao revisor: sinalizar apenas o que afeta corretude ou os requisitos
> declarados. O resto é opcional. Revisor solto produz superengenharia.

## 4. Alocação de mecanismos

| Responsabilidade | Mecanismo | Por quê | Custo de contexto |
|---|---|---|---|
| <ex.: convenções do repo> | CLAUDE.md | Precisa valer em toda sessão | Sempre — ~N linhas |
| <ex.: bloquear escrita em migrations> | Hook PreToolUse | Regra dura precisa de garantia, não de pedido | Zero |
| <ex.: checklist de release> | Skill `disable-model-invocation` | Procedimento com efeito colateral | Descrição sempre, corpo sob demanda |
| <ex.: auditoria de dependências> | Subagente read-only | Lê muitos arquivos; só o resumo importa | Isolado |

**Mecanismos deliberadamente não usados:** <e por quê — isto é tão informativo quanto o que foi usado>

## 5. Orçamento de contexto

| Camada | Conteúdo | Tamanho |
|---|---|---|
| **Sempre** | CLAUDE.md + rules sem `paths` + descrições de skills | ~N linhas / ~N tokens |
| **Sob demanda** | <corpos de skills, rules com paths, schemas MCP> | — |
| **Isolado** | <subagentes; contrato de retorno de 1.000–2.000 tokens> | — |
| **Zero** | <hooks> | — |

**Técnica de horizonte longo:** <compaction | context reset | note-taking estruturado | subagentes> — porque <a tarefa é de tipo X>

**Alerta:** CLAUDE.md acima de 200 linhas é dívida. Estado atual: <N linhas>.

## 6. Fronteira de segurança

**Filesystem:** <diretórios acessíveis>
**Rede:** <domínios permitidos — lembrar que domínio aprovado é superfície de ataque>
**Modo de permissão:** <manual | auto | sandbox | VM selada> — casado com o perfil de quem opera (§1)
**Enforcement:** <o que está em `permissions.deny` / `sandbox.enabled` em managed settings, e não em CLAUDE.md>

**Conteúdo não confiável:** <quais saídas de ferramenta têm acesso a rede e são tratadas como dados, nunca como instrução>
**Estado persistente:** <memória entre sessões? diretório montado? é superfície de injeção — como é tratado>

**Risco residual aceito:** <o que este desenho não previne, explicitamente>

## 7. Plano de evals

**Tarefas iniciais:** <20–50, vindas de quais falhas reais>
**Graders:** <determinísticos primeiro; onde LLM-as-judge entra; onde humano calibra>
**Métrica:** <pass@k ou pass^k — e por quê, dada a consequência de errar>
**Isolamento:** <como cada trial começa do zero>
**Cadência de revisão de transcript:** <quando alguém lê os traces>

## 8. Suposições e quando revisar

> Todo componente de harness codifica uma suposição sobre o que o modelo não faz sozinho.
> Essas suposições ficam obsoletas conforme os modelos melhoram.

| Componente | Suposição que codifica | Sinal de que virou peso morto |
|---|---|---|
| <ex.: avaliador separado> | O modelo não critica o próprio trabalho com rigor | Auto-avaliações passam a coincidir com o avaliador em N amostras seguidas |
| <ex.: decomposição em sprints> | O modelo perde coerência além de ~X minutos | Uma execução única completa a tarefa sem degradar |
| <ex.: context resets> | O modelo entra em "ansiedade de contexto" perto do limite | Não há mais encerramento prematuro observável |

**Gatilho de revisão:** chegada de modelo novo. **Procedimento:** remover um componente por vez e medir contra a suíte de evals da §7. Simplificar é o resultado esperado, não a exceção.

## 9. Divergências registradas

<Se o interlocutor optou contra uma recomendação depois de informado, registre aqui a
recomendação, a escolha feita e o risco assumido. Isto não é reprovação — é rastreabilidade.>

## 10. Fontes

<URLs que sustentam as decisões acima — ver referência 06>
```

---

## Checklist antes de entregar

- [ ] A §3 nomeia um comando literal, não uma intenção
- [ ] Cada componente da §4 tem justificativa de mecanismo, não só de função
- [ ] A §5 tem números, não adjetivos
- [ ] A §6 tem filesystem **e** rede, não só um
- [ ] A §7 escolhe entre `pass@k` e `pass^k` com razão declarada
- [ ] A §8 está preenchida com uma linha por componente do harness
- [ ] Nenhuma regra dura foi parar em CLAUDE.md ou skill
- [ ] Se há multiagente, o custo de ~15× está declarado
- [ ] Toda recomendação normativa tem fonte
- [ ] O documento menor que resolveria o mesmo problema foi considerado e descartado por escrito
