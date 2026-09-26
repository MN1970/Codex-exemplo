# Planejador do Maestro (N0) — planejar antes de executar

Versão: v1.0 (2026-09-26) · Introduzido na v5.5.0 do `CLAUDE.md`.

## Por quê

Sem planejamento, o Maestro tende a abrir vários agentes "por garantia".
Cada agente aberto custa tokens (a definição dele entra no contexto) e
ocupa janela de contexto, antecipando a compactação e a perda de
informação. O planejador troca isso por um passo barato e explícito:
**decidir o conjunto mínimo de agentes antes de carregar qualquer um**.

## Fluxo

```text
pedido do usuário
   │
   ▼
1. Roteamento determinístico (palavras-chave)      custo LLM: zero
   └─ src/maestro/planner.py  → tabela ROUTING_RULES
      (espelho de maestro_routing_keywords no Supabase)
   │
   ├─ 1 segmento claro ............ plano com 1 agente
   ├─ vários segmentos ............ plano com primário + handoffs (≤ 3)
   └─ nada casou / ambíguo ........ planejador LLM (Haiku) decide
   │
   ▼
2. Plano (JSON) — contrato abaixo
   │
   ├─ aprovação exigida? → mostrar o plano ao usuário e aguardar
   ▼
3. Execução: carregar SOMENTE os agentes do plano, na ordem do plano
   │
   ▼
4. Guardiões no fim (só se o entregável for documento externo)
   │
   ▼
5. Registro plano × executado (tabela maestro_plans)
```

## Contrato do plano

```json
{
  "pedido": "revisar orçamento da ETE Lote 3",
  "metodo": "palavras-chave",
  "passos": [
    {"ordem": 1, "agente": "agente-saneamento", "papel": "primario",
     "nivel": "N1", "modelo": "sonnet", "motivo": "ETE"},
    {"ordem": 2, "agente": "agente-orcamento", "papel": "handoff",
     "nivel": "N1", "modelo": "sonnet", "motivo": "orçamento"}
  ],
  "guardioes": ["consist-guard"],
  "teto_tokens": 200000,
  "requer_aprovacao": false,
  "motivos_aprovacao": []
}
```

`metodo` é `palavras-chave` quando o plano saiu do roteamento
determinístico e `llm` quando o planejador Haiku precisou decidir.

## Regras de contenção

| Regra | Valor padrão | Onde muda |
| --- | --- | --- |
| Agentes por plano sem aprovação | até 3 | `MAX_AGENTES_SEM_APROVACAO` |
| Agentes por plano (teto absoluto) | 5 | `MAX_AGENTES` |
| Opus | só com justificativa; sempre pede aprovação | `requer_aprovacao` |
| Guardiões | só no fim e só com entregável externo | `entregavel_externo=True` |
| Subagente devolve | resumo + conclusão, nunca conteúdo bruto | instrução no prompt do passo |
| Níveis de delegação | no máximo 2 (N0 → N1 → N2) | hierarquia abaixo |

Os tetos de tokens começam como estimativas conservadoras e devem ser
recalibrados com os dados reais de `maestro_plans` depois de 1–2
semanas de uso.

## Hierarquia de agentes

| Nível | Quem | Modelo padrão | Pode chamar | Teto de tokens por passo |
| --- | --- | --- | --- | --- |
| **N0** | Maestro / planejador | Haiku | N1 | 20 mil |
| **N1** | Orquestradores de segmento (S) e de atividade (A) | Sonnet | N2, N3 | 120 mil |
| **N2** | Especialistas e subagentes | Sonnet ou Haiku | N3 | 60 mil |
| **N3** | Guardiões e ferramentas determinísticas (aluci, consist, dedup, motor Cronos) | script ou Haiku | ninguém | 10 mil |

- Um nível nunca chama o próprio nível nem um nível acima.
- Opus é exceção justificada (claims complexos, arquitetura, second
  opinion crítico), nunca padrão.

## Carregamento sob demanda

- O Maestro consulta o **catálogo** (tabela compacta do `CLAUDE.md` ou
  `manta_agent_capabilities`) — não lê as definições completas.
- A definição completa (`.claude/agents/<slug>.md` ou o `SKILL.md` no
  SharePoint) só é lida para os agentes que estão no plano.
- Detalhes de arquitetura, histórico e gaps ficam em `docs/maestro/*` e
  só são lidos quando a tarefa exige.

## Uso

```bash
# plano a partir de um pedido (sem rede, sem LLM)
python -m src.maestro.planner "orçamento da ETE com subestação" --externo

# JSON para integração
python -m src.maestro.planner "porto com pista de carga" --json
```

```python
from src.maestro.planner import planejar

plano = planejar("orçamento da ETE com subestação", entregavel_externo=True)
if plano.requer_aprovacao:
    ...  # mostrar plano.resumo() ao usuário antes de executar
```

## Registro plano × executado

Migração candidata: `supabase/migrations/2026_09_26_maestro_plans.sql`
(**não aplicada** — requer gate MN). Cada execução grava os agentes
planejados, os efetivamente usados, os tokens gastos e o método do
plano. A view `v_maestro_plan_aderencia` mostra quantas execuções
chamaram agentes fora do plano, que é o principal indicador de que o
planejador precisa de ajuste.
