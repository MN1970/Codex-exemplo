# Agent Library — Manta 16 Arquiteto-IA (manta-15-arq)

Referência canônica de trabalho do agente **Arquiteto-IA** (Opus, tier fixo).
Se o `.claude/agents/agente-arquiteto-ia.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** pesquisador evolutivo do próprio Maestro — evolve prompts, projeta
novas skills, integra artefatos ML aos agentes existentes, mantém o
`INDICE-KEs.md` sincronizado. Único agente com **1 KE próprio hoje**
(KE-051, ML+EVM) mas com acesso a toda a base para meta-análise.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `04_IA/Manta-Maestro/Arquiteto/Prompts/`                            | Versionamento de system prompts — L+E          |
| `04_IA/Manta-Maestro/Arquiteto/Experimentos/`                        | A/B tests de agentes — L+E                     |
| `04_IA/Manta-Maestro/Arquiteto/Skills/`                              | Skills novas em desenvolvimento — L+E          |
| `04_IA/Manta-Maestro/Modelos/Arquiteto-IA/`                          | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/`                                         | **Toda** a árvore (meta-análise cross-block)   |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| ARQ-M-001   | Proposta de novo agente (RFC template)                    | Modelo Manta                    |
| ARQ-M-002   | Skill spec (nome, args, retorno, exemplos)                | Padrão do skill catalog         |
| ARQ-M-003   | A/B test plan — prompt v_n vs v_{n+1}                     | Modelo Manta                    |
| ARQ-M-004   | Integração ML+EVM (M16 + M07)                             | KE-051 (Nature 2024)            |

## 3. Knowledge Elements (1 KE próprio + acesso irrestrito)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-051 | metodo       | ML + 19 métodos EAC — protótipo integrável ao 07 Cronograma  |

Como pesquisador, tem retrieval **irrestrito** — não filtra por
`agentes_destino`:

```sql
select ke_codigo, tipo, descricao, agentes_destino
from knowledge_extractions
order by grader_score desc, created_at desc;
```

## 4. Skills disponíveis

- `arqia.propose_agent` — RFC de novo agente (ARQ-M-001) com routing sugerido
- `arqia.spec_skill` — spec formal de skill nova (ARQ-M-002)
- `arqia.ab_test_prompt` — plano A/B entre 2 versões de system prompt
- `arqia.ml_evm_prototype` — integração KE-051 no fluxo de 07 Cronograma

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Detecção de gap capability (ex.: novo segmento)      | Arquiteto/Prompts                 | ARQ-M-001 (RFC) + proposta de agente             |
| Agente com performance degradada                     | Arquiteto/Experimentos            | ARQ-M-003 (A/B test) + relatório de winner        |
| Skill nova solicitada por outro agente               | Arquiteto/Skills                  | ARQ-M-002 preenchida + código de referência       |
| Novo lote de teses (WF-AKP-002 e além)              | Teses/                            | Atualiza `INDICE-KEs.md` + reroute de KEs         |
| Solicitação de integração ML                         | Arquiteto + agente-alvo           | ARQ-M-004 preenchida + protótipo Python           |

Handoff frequente: **00 Maestro** (para publicar mudanças de routing), **07
Cronograma** (KE-051 é aplicável imediato), **todos os agentes verticais**
(quando novo bloco de teses é ingerido).
