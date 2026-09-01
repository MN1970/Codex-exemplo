# Manta Maestro v5.0 — Agent Registry & Orchestration

**Registro mestre e especificação operacional dos agentes IA da Manta Associados.**

---

## O que é Manta Maestro v5.0?

Uma plataforma escalável de **20 agentes IA** (11 horizontais + 9 verticais S1–S10) sustentada por **8 pilares arquiteturais**:

1. **Routing Determinístico** — Maestro (R1) roteia prompts com 90%+ confiança
2. **Qualidade Vertical** — 5 novos agentes (S6–S10: Portos, Aeroportos, Saneamento, Energia, Barragens)
3. **Ciclo de Vida** — 8 fases: estudo prévio → encerramento
4. **RAG Híbrido** — BM25 + embedding + reranker em <50ms
5. **Tiering Automático** — Haiku/Sonnet/Opus via complexity score
6. **Observabilidade** — Run tracking imutável, custos, latência
7. **Orquestração Async** — APScheduler: reindex diário, feedback, limpeza
8. **Versionamento de Skills** — Checksums MD5, rollback automático, grace period 30d

---

## Arquivos Principais

### Documentação

| Arquivo | Propósito |
|---------|-----------|
| **CLAUDE.md** | Master registry: 20 agentes, 8 pilares, R1–R10, RAG, deploy checklist |
| **VERSIONS.json** | Checksums de todos 20 skills v5.0 + 9 RAG collections |
| **docs/ARQUITETURA-v5.0.md** | Detalhe dos 8 pilares (P1–P8) |
| **docs/DEPLOYMENT-GUIDE.md** | Step-by-step deploy (8 fases, 48h → go-live) |
| **docs/ROUTING-REFERENCE.md** | Especificação completa R1 (3-stage pipeline, keywords) |
| **DEPLOY-CHECKLIST.md** | Quick reference checklist (imprimir e marcar) |

### Scripts

| Script | Função |
|--------|--------|
| **scripts/healthcheck.py** | Valida checksums, RAG, CLAUDE.md, settings.json |
| **scripts/rag-reindex.py** | Reindexação RAG diária (APScheduler trigger) |
| **scripts/tiering-audit.py** | Auditoria R7 (formula complexity score) |

---

## Começar

### 1. Ler (15 min)
- Cabeçalho + 8 pilares em **CLAUDE.md**
- **docs/ARQUITETURA-v5.0.md**

### 2. Validar (5 min)
```bash
python3 scripts/healthcheck.py
```

### 3. Deploy (4–6h)
Siga **DEPLOY-CHECKLIST.md** (8 fases)

---

## Performance Targets

| Métrica | Target | v4.2 | Improvement |
|---------|--------|------|------------|
| Routing latency | <500ms | ~800ms | 37% faster |
| RAG query | <50ms | ~200ms | 75% faster |
| Cost/run | $0.05–$0.08 | $0.12 | 40% cheaper |
| Latency p95 | <5s | ~8s | 37% faster |

---

**Manta Maestro v5.0 — Ready for deployment**

*Generated: 2026-07-25*

---

## Draft em avaliação neste branch (PR #60)

Esta seção documenta o que **este branch** (`claude/org-modularizacao-melhorias-83i4zx`)
adiciona sobre o README acima, que é o conteúdo real e atual do `main`. Nada
abaixo está operacional; tudo está sujeito a revisão e aprovação MN antes de
qualquer merge ou promoção de status.

### 1. `.claude/agents/agente-performance.md` — Manta 03-PERF (🟠 Proposto)

Minuta de agente transversal de telemetria/desempenho operacional de ativos
de infraestrutura (RAM, MTBF, MTTR, OEE, health monitoring, digital twin),
atuando em paralelo aos verticais S1–S10 nas fases de O&M e due diligence do
ciclo de vida. Status **🟠 Proposto**, seguindo o mesmo padrão de sinalização
já usado no `CLAUDE.md` do `main` para S12 (Óleo & Gás) e S13 (Edificações):
não registrado em nenhuma tabela de segmentos oficial, sem coleção RAG, sem
rota SharePoint, sem keyword de routing — pendente de aprovação MN antes de
qualquer promoção a operacional.

**Overlap de escopo identificado**: o `main` já contém
`.claude/agents/agente-analytics-p3-07.md` (**Manta 23 — "Performance
Monitoring & Analytics"**), atualmente em fase de design ("Design Phase"),
cobrindo essencialmente a mesma área — KPI real-time, anomaly detection e
predictive maintenance para os segmentos S1–S10. A decisão de consolidar os
dois agentes em um só, diferenciar explicitamente seus escopos, ou
descontinuar um deles **fica pendente de revisão MN** e não é resolvida
neste branch.

### 2. Protótipo de routing — `src/router/maestro-router-v2.ts`

Protótipo isolado (zero dependências externas) de classificador/orquestrador
de routing, acompanhado de:

- `tests/router/maestro-router-v2.test.ts` — 16/16 testes `node:test` passando
- `tests/routing/prompts.md` — 14/14 casos do autoteste validados localmente

**Não deve ser confundido com** `infra/agent-registry/lib/maestro-v2-routing.ts`,
que já existe no `main` com o mesmo nome conceitual ("Maestro v2") mas é a
implementação real do roteador, integrada a Supabase/pgvector (busca híbrida
BM25 + semântica). O protótipo deste branch é um exercício isolado de lógica
de desambiguação/orquestração — não uma substituição, não integrado a
Supabase, e não pretende disputar espaço com a implementação do `main`.

### 3. Convenção de execução (exceção Python/pytest)

```bash
npm install && npm run test:router
npm run demo:router
```

Isso é uma **exceção deliberada** à convenção Python/pytest usada no restante
do repositório (`pytest.ini`, `scripts/test_routing.py`, etc.). O protótipo e
seus testes ficam propositalmente isolados em `src/router/` e `tests/router/`
(Node/TypeScript, via `tsx --test`) para não interferir com a suíte de testes
real do repositório.

### 4. Numeração de segmentos (S6–S10) — gap conhecido, não resolvido aqui

Os arquivos deste branch usam a convenção S6=Portos, S7=Aeroportos,
S8=Saneamento, S9=Energia, S10=Barragens. O `CLAUDE.md` do `main` já
documenta uma **inconsistência de numeração conhecida** entre essa convenção
("Convenção A") e uma convenção divergente usada em outros documentos
("Convenção B", S6=Edificações...S11=Barragens) — ver seção "GAPS ABERTOS /
PENDÊNCIAS" do `CLAUDE.md` no `main`. Este branch não tenta resolver essa
divergência; apenas sinaliza que ela existe e é pendência documentada
separadamente.
