# SPRINT 1 — IMPLEMENTAÇÃO INICIADA
**MNT-2026-S1-SEISMIC-RESILIENCE | Sprint 1 Kickoff (24 JUL – 30 AGO 2026)**

---

## ✅ APROVAÇÃO FORMAL

```
Status: ✅ APROVADO POR MN (maestro)
Ticket: MNT-2026-S1-SEISMIC-RESILIENCE
Sponsor: MN (aprovação gate)
Tech Lead: Arquiteto-IA
Go-Live Target: Q2 2027 (30 JUN)
```

---

## 🎯 SPRINT 1 OBJETIVOS

**Objetivo Geral**: Completar **knowledge intake** — coletar, organizar e ingerir toda documentação sísmica/geotécnica necessária em RAG.

**Saída Sprint 1**: 
- ✅ Repositório de conhecimento estruturado
- ✅ 100+ documentos indexados (normas, papers, mapas, dados)
- ✅ Coleção RAG parcial (rod:seism:* pronta)
- ✅ Matriz de conhecimento atualizada

---

## 📋 TAREFAS SEMANA 1 (24–30 JUL 2026)

### ✅ Feito (Hoje)

- [x] RFC aprovado por MN ✅
- [x] Planejamento estratégico completo (4 docs)
- [x] Roadmap 8 sprints documentado
- [x] Geotecnia/Geologia módulo desenhado

### 🔄 Em Progresso (Hoje–48h)

- [ ] **Criar estrutura repo** (15 min)
  ```bash
  cd /home/user/Codex-exemplo
  git checkout feat/s1-seismic-v2
  
  # Estrutura Sprint 1
  mkdir -p docs/s1-seismic-v2/1-knowledge/{normas,papers,dados,mapas}
  mkdir -p docs/s1-seismic-v2/RAG-index
  
  # Criar arquivo de índice RAG
  cat > docs/s1-seismic-v2/RAG-index/RAG-INDEX-S1-SEISMIC.xlsx << 'EOF'
  Tipo,Assunto,Arquivo,Tags,Prioridade,Status,Data-Coleta
  Norma,Design Sísmico,ISO-14383-1-2016.pdf,"norm;design;seismic",P1,Não Coletado,
  Norma,EUA Design,ASCE-7-22.pdf,"norm;design;usa",P1,Não Coletado,
  Norma,Brasil,NBR-8681-2003.pdf,"norm;br;geotecnia",P1,Não Coletado,
  Paper,Liquefação,Tokimatsu-Yoshida-1983.pdf,"liq;spт;formula",P1,Não Coletado,
  Mapa,PGA Global,USGS-Hazard-Map.pdf,"pga;map;global",P1,Não Coletado,
  Caso,Jericó 2024,Jerico-2024-Report.pdf,"caso;jerico;br",P1,Não Coletado,
  EOF
  ```

- [ ] **Email para especialistas** (30 min)
  ```
  Destinatários:
  
  1️⃣ UFOP Ouro Preto
     Assunto: Dados sísmico-geotécnicos Jericó 2024
     Contato: Depto Geotecnia (buscar via UFOP website)
     Solicitar: SPT histórico, perfil geológico, acelerograma
     SLA: 1–2 semanas
  
  2️⃣ CPRM (Serviço Geológico Brasil)
     Assunto: PGA maps e relatório técnico Jericó
     Contato: setor.sismologia@cprm.gov.br
     Solicitar: Mapa PGA Brasil, contornos Jericó, dados IPOC
     SLA: 1 semana
  
  3️⃣ Defesa Civil MG
     Assunto: Relatório damages Jericó 2024
     Contato: defesacivil@mg.gov.br
     Solicitar: Report oficial, fotos pré/pós, dados infraestrutura
     SLA: 2 semanas
  
  4️⃣ IPOC (Integrated Plate Boundary Observatory)
     Assunto: Acelerogramas zona Jericó
     Contato: www.ipoc-network.org
     Solicitar: Waveform data, station networks
     SLA: 1 semana
  
  5️⃣ USP / COPPE UFRJ
     Assunto: Papers liquefação Brasil / sísmica
     Contato: Pesquisadores geotecnia
     Solicitar: Access ResearchGate, cópias papers
     SLA: 1 semana
  ```

- [ ] **Agendar reunião agente-05** (email 48h)
  ```
  Assunto: Reunião — SICRO Adaptado para Rodovias Sísmicas
  
  Pauta:
  1. Items SICRO existentes que precisam variantes sísmicas
     - CBUQ → CBUQ elástico (EBA)
     - BGS → BGS c/ reforço geotêxtil
     - Dreno francês → Dreno resiliente pós-evento
     - Barreira → Barreira c/ amortecedor dinâmico
  
  2. Estimativa de custos relativos (vs. convencional)
     - CBUQ elástico: +10–15% vs CBUQ standard
     - Reforço geotêxtil: +5–8% vs BGS standard
     - Drenagem resiliente: +20–30% vs drenagem std
  
  3. Timeline criação composições (Q3/Q4 2026)
  
  Duração: 1h
  Próxima semana (29–30 JUL)
  ```

- [ ] **Criar SharePoint folder** (10 min)
  ```
  Caminho: Documentos Compartilhados/04_IA/Projetos-Ativos/S1-SEISMIC-2026/
  
  Estrutura:
  ├── Roadmap-Maestro.md
  ├── Status-Semanal.md
  ├── Documentos/
  │   ├── S1-SEISMIC-EVOLUTION-EXECUTIVE-SUMMARY.pdf
  │   ├── S1-GEOTECNIA-GEOLOGIA-EXPANSION.pdf
  │   ├── S1-ROADMAP-ACTIONABLE.pdf
  │   └── S1-ONE-PAGE-SUMMARY.pdf
  ├── Links/
  │   ├── Jericó dados
  │   ├── USGS maps
  │   └── Papers ref
  └── Contacts/
      ├── UFOP
      ├── CPRM
      └── Defesa Civil
  
  Compartilhar com: MN, arquiteto-ia, agente-05 lead, BD, conselheiros
  ```

---

## 📚 SEMANA 2–4 (31 JUL – 30 AGO): KNOWLEDGE INTAKE

### A. Coleta de Normas (Prazo: 15 AGO)

| Norma | Fonte | Prioridade | Status | Ação |
|-------|-------|-----------|--------|------|
| **ISO 14383-1:2016** | ABNT / biblioteca digital | P1 | ❌ | Solicitar via Manta library |
| **ASCE 7-22** | ASCE (open access) | P1 | ❌ | Download https://www.asce.org |
| **Eurocode 8** | CEN (EN 1998-1) | P2 | ❌ | Via biblioteca ou PDF cache |
| **NBR 8681** | ABNT | P1 | ❌ | Verificar Manta acervo |
| **NBR 15421** | ABNT | P1 | ❌ | Solicitar download |
| **DNIT PRO/ES** | DNIT (público) | P1 | ✅ | Já coletado (S1 existente) |

**Responsável**: Arquiteto-IA + Biblioteca Manta
**Blocker**: ISO 14383 (pago; buscar alternativa ou Open Access)

### B. Coleta de Papers Científicos (Prazo: 20 AGO)

```
Priority 1 (Implementação Sprint 2):
  ✅ Tokimatsu & Yoshida (1983) — Liquefaction Susceptibility
     Link: ResearchGate, Google Scholar (aberto)
     
  ✅ Youd et al. (2001) — Liquefaction Resistance
     Link: USGS (público)
     
  ✅ Newmark (1965) — Earthquake Effects Embankments
     Link: Google Scholar (público)
     
  ✅ Boore (2004) — Vs Correlation USA
     Link: Earthquake Spectra (subscription via EERI)
     
  ⚠️ Imai & Tonouchi (1982) — Vs Correlation Japão
     Link: ResearchGate (ask authors)

Priority 2 (Suporte):
  ⚠️ Kramer (1996) — Geotechnical Earthquake Engineering (livro)
     Link: Amazon, ou PDF caso exista
     
  ⚠️ Okada et al. (2003) — Site Effects, Vs30 Correlation
     Link: BSSA journal (subscription)
     
  ⚠️ Younes Method — Permanent Strain (diversos autores)
     Link: ASCE Library

**Responsável**: Tech Lead + pesquisadores UFOP/COPPE
**Prazo Google Scholar + ResearchGate**: 3–5 dias
**Prazo papers pagos**: 1–2 semanas (via university subscriptions)
```

### C. Coleta de Dados Regionais — Jericó 2024 (Prazo: 25 AGO)

```
📊 JERICÓ — Essencial

Documento                           | Fonte          | Prazo | Acesso
────────────────────────────────────┼────────────────┼───────┼─────────
CPRM Technical Report (Jericó)      | CPRM website   | 1 sem | Público
Defesa Civil Damages Report         | Defesa Civil MG| 2 sem | Solicitar
Acelerograma Jericó (raw data)      | IPOC / USGS    | 1 sem | Público
Mapa Geologia Jericó (escala 1:50k) | CPRM           | 1 sem | Público
SPT Histórico (entorno Jericó)      | Projetos Manta | 1 sem | Interno
Fotos Pré/Pós Evento                | Defesa Civil   | 2 sem | Solicitar
Estimativa PGA (Jericó)             | USGS Hazard    | 1 dia | Público

**Compilador**: BD + Especialistas (UFOP, CPRM)
**Destino**: docs/s1-seismic-v2/1-knowledge/jerico-2024/
**Formato**: PDF, shapefiles, CSV, imagens
```

### D. Coleta de Mapas USGS & Zoneamento Brasil (Prazo: 28 AGO)

```
📍 MAPAS & DADOS SÍSMICOS

Mapa/Dado                           | Fonte      | Formato   | Ação
────────────────────────────────────┼────────────┼───────────┼──────────────
USGS Global Seismic Hazard Map      | earthquake.usgs.gov | GeoTIFF | Download
Brazil PGA 0–500 años               | USGS       | Shapefile | Extract
Jericó PGA Contours (10k y)         | USGS       | GeoJSON   | Auto-gen
Ceará Sismicidade Histórica         | CPRM       | Shapefile | Solicitar
ES Zonas de Risco                   | CPRM / ANP | Shapefile | Solicitar
USGS Hazard Curves (12 cidades BR)  | USGS       | CSV       | Download + processar

**Ferramenta**: QGIS (processar shapefiles, gerar contornos)
**Compilador**: Tech Lead + Analista GIS (se houver)
**Output**: GeoJSON + PNG maps (embeded em artefato React)
```

---

## 🗂️ ESTRUTURA RAG INDEX (A CRIAR)

Documento: `docs/s1-seismic-v2/RAG-index/RAG-INDEX-MASTER.xlsx`

```
Columns:
  A: ID único (rod:seism:XXX:YYYYYY)
  B: Tipo (Norma / Paper / Mapa / Caso / Algoritmo)
  C: Assunto (Liquefação, Design, PGA, etc.)
  D: Arquivo local
  E: Tags (rod, seism, liq, pga, norm, geo, etc.)
  F: Prioridade (P1–P3)
  G: Status (Coletado / Não coletado / Processado)
  H: Data coleta
  I: Resumo 1-line
  J: Link fonte (se download)
  K: Versão/Edição
  L: Notas (acesso, restrições, etc.)

Target: 100+ documentos indexados até 30 AGO
```

---

## 🔄 STATUS SEMANAL (TEMPLATE)

Criar em SharePoint: `Documentos Compartilhados/.../Status-Semanal.md`

```markdown
# Sprint 1 — Status Semanal

## Semana 1 (24–30 JUL 2026)

### ✅ Completado
- [x] Aprovação MN ✅
- [x] Planejamento completo
- [x] Repo structure

### 🔄 Em Progresso
- [ ] Emails especialistas (enviar hoje)
- [ ] Reunião agente-05 (agendar)
- [ ] SharePoint folder (criar)

### ❌ Bloqueado
- (nenhum)

### 📊 Métricas
- Docs coletados: 0/100
- RAG indexed: 0/100
- Especialistas contactados: 0/5

### 📅 Próxima Semana
- Receber respostas especialistas
- Iniciar download USGS maps
- Primeira reunião agente-05

---

## Semana 2 (31 JUL – 6 AGO 2026)

[Atualizar semanalmente]
```

---

## 💾 BRANCH & COMMITS

### Iniciar desenvolvimento

```bash
# Status atual
git status  # Deve estar em branch feat/s1-seismic-v2

# Criar estrutura Sprint 1
mkdir -p docs/s1-seismic-v2/1-knowledge/{normas,papers,dados,mapas,casos}
mkdir -p docs/s1-seismic-v2/RAG-index
mkdir -p docs/s1-seismic-v2/2-algorithms  # Vazio por enquanto
mkdir -p docs/s1-seismic-v2/3-tests
mkdir -p docs/s1-seismic-v2/4-deploy

# Arquivo README (explicar estrutura)
cat > docs/s1-seismic-v2/README.md << 'EOF'
# S1-V6 Sísmica & Resiliência — Repositório de Desenvolvimento

## Estrutura

```
1-knowledge/       ← Docs coletadas (normas, papers, mapas, dados)
  ├── normas/      ← ISO, ASCE, NBR, DNIT, etc.
  ├── papers/      ← Tokimatsu, Youd, Newmark, etc.
  ├── dados/       ← Jericó 2024, Ceará, ES
  ├── mapas/       ← USGS PGA, zoneamento Brasil
  └── casos/       ← Estudos de caso documentados

2-algorithms/      ← D6.1–D6.6 módulos + calculadoras
3-tests/           ← Casos teste, routing, E2E
4-deploy/          ← RAG migrations, runbook
RAG-index/         ← Indexação master (rod:seism:*)

## Status Implementação

- Sprint 1 (AGO): Knowledge intake
- Sprint 2 (SET): Scaffold V6 + D6.1–D6.2
- Sprint 3 (OUT): D6.3–D6.4
- Sprint 4 (NOV): D6.5 + handoff
- Sprint 5 (DEZ): Casos + validação
- Sprint 6 (JAN): UAT piloto
- Sprint 7 (FEV): Documentação
- Sprint 8 (MAR–JUN): Deploy + go-live

## Contatos

- Tech Lead: [Arquiteto-IA]
- Sponsor: MN
- Agente-05: [Name]
EOF

# Commits
git add docs/s1-seismic-v2/
git commit -m "Sprint 1: Initialize S1-V6 knowledge structure

- Create folder hierarchy (1-knowledge, 2-algorithms, 3-tests, 4-deploy)
- Add RAG-index template
- Add README with timeline and structure

Status: Knowledge intake initiated
Target: 100+ docs indexed by 30 AUG 2026

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
MNT-2026-S1-SEISMIC-RESILIENCE | Ticket approved by MN (maestro)"

git push -u origin feat/s1-seismic-v2
```

---

## 🎯 CHECKLIST SPRINT 1 (FINAL)

**Até 30 AGO 2026:**

- [ ] RFC aprovado ✅
- [ ] Repositório estruturado ✅
- [ ] Emails especialistas enviados ✅
- [ ] Reunião agente-05 agendada ✅
- [ ] SharePoint folder criado ✅
- [ ] ≥50 documentos coletados (normas, papers, mapas)
- [ ] RAG INDEX preenchido 50%
- [ ] Dados Jericó compilados (básico)
- [ ] Status semanal atualizado (4 entradas)
- [ ] Sprint 2 planejado em detalhe

**Saída Sprint 1**: 
✅ Knowledge repository pronto  
✅ 50%+ documentos coletados  
✅ RAG indexação iniciada  
✅ Especialistas engajados  
✅ Ready para Sprint 2 (Scaffold V6)

---

## 📞 CONTATOS SPRINT 1

| Pessoa | Email | Assunto | Deadline |
|--------|-------|---------|----------|
| MN | mn@manta | RFC aprovado ✅ | 24 JUL ✅ |
| Arquiteto-IA | arq@manta | Lead técnico S1-V6 | Contínuo |
| UFOP Geotecnia | [buscar] | Dados Jericó | 7 AGO |
| CPRM | setor.sismologia@cprm | PGA maps, relatório | 31 JUL |
| Defesa Civil MG | defesa@mg | Damages report Jericó | 10 AGO |
| IPOC | contact@ipoc | Acelerogramas | 31 JUL |
| Agente-05 Lead | orcamento@manta | SICRO sísmico | 29 JUL (reunião) |
| BD Lead | bd@manta | Market feedback | Contínuo |

---

## 🚀 GO

**Sprint 1 oficialmente iniciado!**

Próxima ação: **Enviar emails especialistas hoje ou amanhã (25–26 JUL).**

```
📧 EMAIL TEMPLATE (customizar para cada um)

Assunto: Solicitação — Dados Técnicos Sísmica Jericó 2024 + Brasil

Prezados [Nome/Setor],

Estou coordenando a evolução de um agente IA especializado em rodovias 
com análise sísmica (Manta Associados). Estamos usando Jericó 2024 como 
caso-piloto e gostaríamos de acessar:

[Listar items específicos conforme contato]

Prazo: [1–2 semanas]
Uso: Análise técnica, validação de modelos, publicação futura

Agradeço antecipadamente pela colaboração!

[Seu nome]
Manta Associados | mneves@mantaassociados.com
```

**Status Geral**: 🟢 LIVE
**Timeline**: Sob controle
**Riscos**: Dados Jericó (pode demorar); ISO 14383 acesso (pago)
**Próximo Milestone**: 31 JUL (respostas especialistas)

---

*Documento atualizado: 2026-07-24 | Sprint 1 Kickoff | MN Aprovado*
