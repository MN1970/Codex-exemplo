# Status Semanal — Sprint 1 Seismic V2

**Sprint**: 1 | **Período**: 2026-07-24 a 2026-08-21 | **Duração**: 4 semanas
**Responsável**: Dev Lead | **Última atualização**: 2026-07-24

---

## 📊 Visão Geral

| Métrica | Target | Current | Status |
|---------|--------|---------|--------|
| Features completas | 12 | 0 | 🔴 Não iniciado |
| Code coverage | 80% | 0% | 🔴 Não aplicável |
| PRs abertos | 0 | 0 | 🟢 OK |
| Bugs encontrados | <5 | 0 | 🟢 OK |
| Documentação | 100% | 20% | 🟡 Em progresso |

---

## 🔷 SEMANA 1: 2026-07-24 a 2026-07-28 — Foundation

### ✅ Completado (Target: 3 tasks)

- [x] **Repository estruturado** — Dir principals criados (src/, docs/, data/)
  - Commits: 1 | Author: DevOps | Date: 2026-07-24
  - Proof: `git log --oneline | head -1`

- [x] **CLAUDE.md + SKILL.md criados** — Context para agent S1-Seismic
  - Commits: 1 | Author: Tech Lead | Date: 2026-07-24
  - Proof: `.claude/agents/s1-seismic/`

- [x] **GitHub Actions CI/CD template** — Base workflow (pytest + coverage)
  - Commits: 1 | Author: DevOps | Date: 2026-07-24
  - Proof: `.github/workflows/s1-seismic-ci.yml`

### 🔄 Em Progresso (Target: 4 tasks)

- [ ] **RAG Index v1.0** — 50+ documentos base indexados
  - Assigned to: Data Engineer
  - Target date: 2026-07-26
  - Progress: 0% — aguardando download de PDFs de USGS/IRIS
  - Blocker: None
  - Link: `data/rag/RAG-INDEX-*.csv`

- [ ] **Design doc: Seismic data pipeline** — Arquitetura end-to-end
  - Assigned to: Tech Lead
  - Target date: 2026-07-27
  - Progress: 10% — outline definido
  - Blocker: Aguardando validação de formato miniSEED
  - Link: `docs/sprint-1/architecture/seismic-pipeline-v1.md`

- [ ] **Setup SharePoint** — Pastas + permissões + links
  - Assigned to: Admin
  - Target date: 2026-07-26
  - Progress: 30% — pastas criadas, falta permissões
  - Blocker: Aguardando lista de stakeholders
  - Link: SharePoint > 03_Projetos/Seismic/

- [ ] **Requirements refinement** — User stories + acceptance criteria
  - Assigned to: Product Owner
  - Target date: 2026-07-28
  - Progress: 20% — draft iniciado
  - Blocker: Aguardando feedback do cliente
  - Link: `docs/sprint-1/planning/requirements-v1.md`

### 🔴 Bloqueado (Target: 0 tasks)

- **Nenhum bloqueio crítico reportado**

### 📈 Métricas da Semana 1

| KPI | Valor |
|-----|-------|
| Tasks completadas | 3/7 |
| Velocity (points) | 5 |
| Documentação % | 25% |
| Commits | 3 |
| PR Reviews | 0 |
| Bugs descobertos | 0 |

### 💬 Notas & Decisões

- ✅ Deciso de usar CSV em vez de xlsx para RAG-INDEX (fácil versionar no Git)
- ✅ GitHub Actions CI configurado para feat/s1-seismic-v2
- ⚠️  Aguardando acesso USGS API para RAG automático (low priority)
- ⚠️  Definir owner do RAG-INDEX (deve ser atualizado mensalmente)

---

## 🔷 SEMANA 2: 2026-07-31 a 2026-08-04 — MVP Core Phase 1

### Planejado (Target: 6 tasks)

- [ ] **Parser sísmico v0.1** — Ler miniSEED + USGS JSON
  - Assigned to: Backend Dev
  - Target date: 2026-08-02
  - User stories:
    - US-001: Parser miniSEED com obspy
    - US-002: Ingestão de Shakemap JSON
    - US-003: Validation & error handling

- [ ] **Espectro de resposta v0.1** — Cálculo conforme NBR 15421
  - Assigned to: Algorithm Specialist
  - Target date: 2026-08-03
  - User stories:
    - US-004: Cálculo de Sa, Sv, Sd
    - US-005: Amortecimento configurável (5%, custom)
    - US-006: Output em gráfico + tabela

- [ ] **Unit tests scaffold** — >50% coverage alvo
  - Assigned to: QA Engineer
  - Target date: 2026-08-04
  - User stories:
    - US-007: Testes de parser (10 casos)
    - US-008: Testes de spectrum (8 casos)

- [ ] **Versionamento + releases** — Tagging e changelog
  - Assigned to: DevOps
  - Target date: 2026-08-02
  - Deliverable: `RELEASES.md` + v0.2.0 tag

- [ ] **Documentação técnica v1.0** — API doc + examples
  - Assigned to: Tech Writer
  - Target date: 2026-08-04
  - Deliverable: `docs/technical-reference.md`

- [ ] **RAG search integration** — Query engine para docs
  - Assigned to: Data Engineer
  - Target date: 2026-08-03
  - Proof of concept: LLM prompt com RAG chunks

### ✅ Completado (Semana 2)

*Será preenchido ao fim da semana*

### 🔄 Em Progresso (Semana 2)

*Será preenchido durante a semana*

### 🔴 Bloqueado (Semana 2)

*Será preenchido conforme riscos apareçam*

### 📈 Métricas da Semana 2

*Será preenchido ao fim da semana*

| KPI | Target | Atual |
|-----|--------|-------|
| Tasks completadas | 6 | TBD |
| Code coverage | 50% | TBD |
| Commits | 15+ | TBD |

---

## 🔷 SEMANA 3: 2026-08-07 a 2026-08-11 — MVP Core Phase 2

### Planejado (Target: 5 tasks)

- [ ] **Análise de vulnerabilidade v0.1** — Damage ratios básicos
- [ ] **Integration tests** — End-to-end com dados reais
- [ ] **Performance benchmarks** — Latência & memory profile
- [ ] **Code review & refactoring** — Clean up MVP
- [ ] **User documentation** — Tutorial & quickstart

### 📈 Métricas da Semana 3

*Será preenchido ao fim da semana*

---

## 🔷 SEMANA 4: 2026-08-14 a 2026-08-21 — Testing & Docs

### Planejado (Target: 5 tasks)

- [ ] **Relatório técnico template** — Estrutura para laudo sísmico
- [ ] **Testes de carga** — Stress testing com dados grandes
- [ ] **Deploy checklist** — Readiness review
- [ ] **Training & handover** — Documentação para operações
- [ ] **Sprint review + retrospective** — Lições aprendidas

### 📈 Métricas da Semana 4

*Será preenchido ao fim da semana*

---

## 📋 Rastreamento de Riscos

| # | Risco | Probabilidade | Impacto | Mitigation | Owner |
|----|-------|---------------|---------|-----------|-------|
| R1 | Dados USGS/IRIS indisponíveis | Baixa (5%) | Alto | Mock data + local cache | Data Eng |
| R2 | Cálculo de espectro diverge de NBR | Média (30%) | Alto | Validação com especialista | Algo Spec |
| R3 | Delay em aprovação requisitos | Média (25%) | Médio | Daily sync com cliente | PO |
| R4 | Falta de compute power para testes | Baixa (10%) | Médio | Cloud infra (AWS/GCP) | DevOps |

---

## 📌 Próximos Passos (Final de Sprint)

1. **Semana 4**: Consolidar todas as métricas
2. **2026-08-21**: Sprint review com stakeholders
3. **2026-08-21**: Planning para Sprint 2 (MVP v1.0 → v2.0)
4. **2026-08-22**: Merge `feat/s1-seismic-v2` → `main` (se aprovado)

---

## 📞 Contatos Sprint 1

| Papel | Nome | Email | Telefone |
|-------|------|-------|----------|
| Tech Lead | João Silva | joao@manta.com | +55 11 98765-4321 |
| DevOps | Maria Santos | maria@manta.com | +55 11 98765-4322 |
| Data Engineer | Carlos Costa | carlos@manta.com | +55 11 98765-4323 |
| PO | Ana Oliveira | ana@manta.com | +55 11 98765-4324 |

---

## 📎 Anexos & Links

- **RAG Index**: [data/rag/RAG-INDEX-v1.0.csv](../../../data/rag/RAG-INDEX-v1.0.csv)
- **Architecture Docs**: [docs/sprint-1/architecture/](../architecture/)
- **Requirements**: [docs/sprint-1/planning/](../planning/)
- **GitHub Board**: https://github.com/manta/codex-exemplo/projects/S1-Seismic
- **SharePoint**: https://mantaassociados.sharepoint.com/sites/03_Projetos/Seismic/

---

**Última revisão**: 2026-07-24 | **Próxima revisão**: 2026-07-28 (EOW)
**Responsible**: Tech Lead | **Approved by**: Steering Committee
