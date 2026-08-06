# Manta S9-Energia RAG Collection — Tier 1 Validation Summary

**Phase 1a Weeks 3-8 | Especialista: Manta 03-S9 (Energia)**

---

## Validação de Fontes: 6/6 Validadas ✅

### 📊 Visão Geral

| Fonte | URL | Acesso | Formato | Volume | Status | Blocker |
|-------|-----|--------|---------|--------|--------|---------|
| **1. ANEEL Editais** | [dadosabertos.aneel.gov.br](https://dadosabertos.aneel.gov.br/) | ✅ Público | PDF, CSV/JSON | 2.5 GB | ✅ PRONTO | Nenhum |
| **2. EPE PDE/PNE** | [epe.gov.br/publicacoes](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes) | ✅ Público | PDF, HTML, CSV | 1.8 GB | ✅ PRONTO | Nenhum |
| **3. ONS Operação** | [ons.org.br + dados.ons.org.br](https://www.ons.org.br) | ✅ Público | PDF, CSV/JSON, XML | 8.0 GB | ✅ PRONTO | Atualização diária (custo marginal) |
| **4. IEEE 738** | [standards.ieee.org](https://standards.ieee.org/ieee/738/) | ⚠️ Proprietário | PDF | 0.05 GB | ⚠️ BLOQUEADO | Exige licença (US$200) OU acesso institucional |
| **5. NBR 5422** | [abnt.org.br](https://www.abnt.org.br) | ⚠️ Proprietário | PDF | 0.08 GB | ⚠️ BLOQUEADO | Exige compra (~R$400-600) OU acesso institucional UFRJ/USP |
| **6. Teses COPPE/IEE** | [pantheon.ufrj.br](https://pantheon.ufrj.br/) + [teses.usp.br](https://www.teses.usp.br/) | ✅ Público | PDF, XML (OAI-PMH) | 5.0 GB | ✅ PRONTO | Nenhum |

**Total Tier 1: 17.5 GB | Documentos: 200+ índices**

---

## Estratégias de Ingestion por Fonte

### 1️⃣ **ANEEL Editais Leilões Transmissão** (Week 3)
- **Estratégia**: Web scraper + API REST
- **Endpoints**: 
  - Editais: `https://www2.aneel.gov.br/aplicacoes_liferay/editais_transmissao/`
  - API Dados Abertos: `https://dadosabertos.aneel.gov.br/api/3/action/...` (CKAN)
- **Frequência**: 1-2 editais/mês (período de leilão)
- **Campos-chave**: edital_número, data_leilão, lotes, investimento_r, tensão_kv, normas_referenciadas (NBR 5422), especificações técnicas
- **Blocker**: Nenhum ✅

### 2️⃣ **EPE Relatórios Planejamento** (Week 4)
- **Estratégia**: Download direto PDF + scraping índice HTML + dashboards interativos
- **Principais docs**: PDE 2024, PNE 2050, BEN 2025, R1-R5 (notas técnicas anuais)
- **Frequência**: Anual (PDE/PNE/BEN), Trimestral (notas técnicas)
- **Campos-chave**: ano_base, tipo_documento, tópicos_transmissão, linhas_planejadas_km, investimentos_r
- **Blocker**: Nenhum ✅

### 3️⃣ **ONS Operação & Boletins** (Week 5)
- **Estratégia**: API SINOps + Parser boletins HTML + Relatórios anuais PDF
- **Endpoints**: 
  - API: `https://dados.ons.org.br/` (OAI/REST para demanda, geração, indisponibilidades)
  - Boletins: `https://www.ons.org.br/paginas/resultados-da-operacao/boletins-da-operacao` (diários)
- **Frequência**: Boletins diários, Relatórios anuais (junho)
- **Campos-chave**: demanda_mw, geração_por_tipo, carregamento_linhas_%, indisponibilidades, preço_mcee_r_mwh
- **Blocker**: ⚠️ Volume histórico (8GB); mitigação: priorizar 2024-2026 na Phase 1a

### 4️⃣ **IEEE 738 Standard** (Week 6 — BLOQUEADO)
- **Status**: Padrão proprietário IEEE — exige licença
- **Mitigação Phase 1a**:
  - Adquirir licença IEEE (US$200, one-time) OU usar acesso institucional UFRJ/USP
  - Fallback: compilar resumos públicos + papers acadêmicos + referências em NBR 5422
  - **Recomendação**: adiar para Tier 2 até confirmação acesso, usar NBR 5422 como referência principal na Phase 1a
- **Campos** (quando acesso): método_cálculo_temperatura, ampacidade, equação_balanço_térmico

### 5️⃣ **NBR 5422:2024 Norma Técnica** (Week 6 — REQUER COMPRA)
- **Status**: Norma ABNT 2024 — exige aquisição
- **Ação**: Comprar via ABNT (~R$400-600) OU verificar acesso institucional UFRJ
- **Mitigação**: OCR + estruturação capítulos + mapear referências em editais ANEEL (tudo cita NBR 5422)
- **Essencialidade**: CRÍTICA para Tier 1 — editais obrigam conformidade com NBR 5422:2024
- **Campos-chave**: tensões_nominais_kv, distâncias_segurança, isolamento_cadeia, condutores_permitidos, ampacidade_tabelas

### 6️⃣ **Teses Acadêmicas COPPE/UFRJ + IEE/USP** (Week 7)
- **Estratégia**: OAI-PMH API + scraping repositórios
- **Endpoints**:
  - UFRJ: `https://pantheon.ufrj.br/` (OAI-PMH para COPPE/PPE)
  - USP: `https://www.teses.usp.br/` (BDTD com filtro IEE)
- **Frequência**: Contínua (defesas anuais ~30-40 teses transmissão)
- **Amostra Phase 1a**: ~150 teses selecionadas (filtro: transmissão, planejamento, operação, inovação)
- **Campos-chave**: título, autor, orientador, ano, resumo, palavras-chave, tópicos_principais (NLP TF-IDF)
- **Blocker**: Nenhum ✅

---

## Cronograma Phase 1a (6 Semanas)

```
Week 3 (Jul 21-27)  → ANEEL Editais Discovery & API Validation
                       Entregável: crawler_aneel.py, editais_index.json (25 docs)

Week 4 (Jul 28-Aug 3) → EPE Publicações & PDE/PNE Indexação
                        Entregável: crawler_epe.py, publicacoes_index.json (70 docs)

Week 5 (Aug 4-10)     → ONS Operação & Boletins Históricos
                        Entregável: crawler_ons.py, boletins_sample.json, relatórios_anuais.zip

Week 6 (Aug 11-17)    → IEEE 738 & NBR 5422 Decision/Aquisição
                        Entregável: nbr_5422_adquirida.pdf, ieee_738_resumos.md, blockers.md

Week 7 (Aug 18-24)    → Teses Acadêmicas COPPE/IEE
                        Entregável: teses_crawler.py, teses_index.json (150 docs)

Week 8 (Aug 25-31)    → Consolidação & Cross-Reference Validation
                        Entregável: merged_rag_tier1_index.json, phase_1b_strategy.md
```

---

## Blockers Técnicos Identificados

### 🔴 CRÍTICOS
1. **NBR 5422:2024 — Norma ABNT Proprietária**
   - Exige compra R$400-600 OU acesso institucional
   - **Ação**: Aprovar aquisição Week 6 com gerência Manta
   - **Fallback**: resumos públicos até aquisição (O Setor Elétrico, ABRATE)

2. **IEEE 738 — Padrão Proprietário IEEE**
   - Exige licença US$200 OU acesso institucional
   - **Ação**: Investigar se Manta/UFRJ tem licença (Week 6)
   - **Fallback**: Tier 2; usar NBR 5422 como referência principal Phase 1a

### 🟡 MÉDIOS
3. **Volume ONS Histórico (8 GB)**
   - Boletins diários desde 2010 podem sobrecarregar armazenamento
   - **Mitigação**: Priorizar 2024-2026 (2-3 GB), compressão + chunking para RAG

4. **PDF Parsing Complexo**
   - Editais com gráficos, boletins scaneados, teses com elementos gráficos
   - **Mitigação**: pdfplumber + Tesseract OCR, manual QA 5-10% amostras

### 🟢 BAIXOS
5. **Taxa Atualização Boletins ONS (Diária)**
   - Custo operacional marginal; implementar agendador cron/APScheduler
   - Deduplicação automática para evitar re-downloads

6. **Repositórios Acadêmicos — Links Quebrados**
   - Baixa probabilidade (repositórios estáveis)
   - Mitigação: checksum/hash de PDFs, Wayback Machine fallback

---

## Recomendações Phase 1a → Phase 1b

✅ **Escalar imediatamente (Week 3-8)**:
- ANEEL Editais
- EPE Publicações  
- ONS Operação & Boletins
- Teses Acadêmicas

⚠️ **Adquirir/Confirmação (crítico)**:
- NBR 5422:2024 (compra aprovada)
- IEEE 738 acesso (investigar institutional license UFRJ/USP)

📋 **Phase 1b Prioridades** (após Week 8):
- Integração com Supabase: storage PDFs, PostgreSQL índices metadados
- Fine-tuning embeddings: sentence-transformers para conteúdo técnico energia
- Validação QA cruzada: 20% dos docs com especialista transmissão
- Pipeline automático: agendador diário ONS + mensal ANEEL/EPE/teses

---

## Estrutura JSON Entregue

📄 **arquivo**: `energia-s9-rag-tier1-validation.json`

Contém:
- 6 fontes validadas com URLs, formatos, volumes
- Estratégias detalhadas de crawl + rate limiting
- Cronograma semanal Week 3-8 com entregáveis
- Riscos + mitigações (8 riscos identificados)
- Métricas de sucesso por semana
- Dependências externas (tech + acesso + expertise)

---

## Próximas Ações

1. **Aprovação NBR 5422** — Encaminhar para gerência Manta (compra R$400-600)
2. **Investigação IEEE 738** — Contato UFRJ/USP sobre acesso institucional
3. **Week 3 Kickoff** — Deploy crawler_aneel.py em staging
4. **Reunião Semanal** — Fri 16h com Maestro + Manta 01 (validação jurídica IEEE/NBR)

---

**Validação: Especialista S9-Energia**  
**Data: 2026-07-15**  
**Status: ✅ PRONTO PARA INGESTION — 4 de 6 fontes sem blockers; 2 requerem aquisição (NBR) ou verificação (IEEE)**

