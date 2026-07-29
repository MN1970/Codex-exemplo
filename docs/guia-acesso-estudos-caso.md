# Guia de Acesso — Estudos de Caso com Análise de Custos
## Como encontrar análises de defensas/barreiras/atenuadores em rodovias brasileiras

---

## 1. RECURSOS MANTA ASSOCIADOS

### 1.1 Via Maestro (Manta 00) — Roteador de Agentes

**Prompt recomendado:**
```
"Preciso de estudos de caso de rodovias federais/estaduais brasileiras 
com análise de custos de defensas metálicas, barreiras rígidas e atenuadores. 
Inclua manutenção pós-obra, resultado operacional (redução de acidentes) 
e comparação econômica."
```

**O que acontece:**
1. Maestro (Haiku) faz triagem em ~1s
2. Identifica segmento → **agente-infraestrutura S1** (Rodovias)
3. Escalona para Sonnet (execução)
4. Agente consulta:
   - RAG Supabase → coleção `rod:` (rodovias)
   - SharePoint → pasta `03_Projetos/Rodovias/*`
   - Skills → `cad-quantifier`, `sicro-completo`, `consist-guard`

---

### 1.2 SharePoint Manta Associados

**Pasta recomendada:** `03_Projetos/Rodovias/*`

**Subpastas esperadas:**
- `Estudos_Previos/` — EVTEA, anteprojetos (custos preliminares)
- `Projetos_Executivos/` — memoriais com orçamentos detalhados
- `Concessões/` — editais e relatórios operacionais (PER)
- `Reabilitação/` — projetos de reforço (defensas adicionais)

**Documentos a procurar:**
- Memoriais de cálculo (defensas/barreiras por km)
- Planilhas orçamentárias (SICRO, BDI)
- Relatórios ANTT de rodovias concedidas
- Estudos de Impacto Técnico e Econômico (EVTEA)
- Projetos básicos com viabilidade econômica

---

### 1.3 Supabase — RAG (Retrieval-Augmented Generation)

**Coleção:** `rod:` (Rodovias)

**Prefixos específicos para buscar:**
```
rod:custos          → Análise econômica, tabelas de custo unitário
rod:defensa         → Defensa metálica — especificações, custos
rod:barreira        → Barreira rígida — New Jersey, Single Slope
rod:atenuador       → Atenuador impacto — implantação e manutenção
rod:manutencao      → Ciclos, periodicidade, custos operacionais
rod:cases           → Estudos de caso, projetos reais
rod:br-116          → BR-116 específico (maior volume de dados)
rod:br-101          → BR-101 específico
rod:concessoes      → Rodovias federais concedidas (ANTT data)
rod:sicro           → Integração com tabelas SICRO
```

**Como consultar via Supabase (se tiver acesso direto):**
```sql
SELECT * FROM rag_chunks 
WHERE prefix LIKE 'rod:%' 
AND content ILIKE '%defensa%manutenção%custo%'
LIMIT 20;
```

---

## 2. BANCO DE DADOS EXTERNO — SICRO

**O que é:** Sistema de Custos Rodoviários (DNIT)  
**Acesso:** https://www.dnit.gov.br/

**Dados disponíveis:**
- Tabelas de composição de serviços (defensas, barreiras)
- Custos unitários por unidade (metro linear, unidade, etc.)
- Desoneração regional (por estado/região)
- BDI (Benefício e Despesas Indiretas)

**Buscar por:**
- Código SICRO para defensa metálica
- Código SICRO para barreira rígida
- Código SICRO para atenuador impacto
- Custos de transportação (importante em SP/MG/RS)

**Exemplo de pesquisa:**
```
Serviço: "Defensa metálica em aço galvanizado"
Unidade: Metro linear
Componentes: Aço, galvanização, transporte, mão-de-obra
BDI: Aplicar conforme região
```

---

## 3. FONTES GOVERNAMENTAIS

### 3.1 ANTT (Agência Transportes Terrestre)

**Site:** https://www.antt.gov.br/

**Dados de rodovias concedidas:**
- Contratos de concessão (PDF com cláusulas de manutenção)
- Relatórios de fiscalização anual
- PER (Programa Exploração Rodovia) — obrigatório em cada contrato

**Rodovias federais com defensas/barreiras:**
- BR-116 (CCR, Odebrecht, OHL)
- BR-101 (múltiplos operadores)
- BR-381 (Rodovia do Aço)
- SP-280 (Rodovia dos Bandeirantes)
- Outras concessões longas

**O que procurar nos contratos:**
- Cláusula de manutenção de dispositivos de segurança
- Periodicidade de inspeção (anual, semestral)
- Custos de reposição em PERs
- Métricas de severidade de acidentes (para validar eficácia)

---

### 3.2 DNIT (Departamento Nacional Infraestrutura Transportes)

**Site:** https://www.dnit.gov.br/

**Publicações relevantes:**
- Manual de Projeto de Interseções (IPR-718)
- Manual de Segurança nas Rodovias
- Manual de Projeto Geométrico (IPR-706)
- Boletins técnicos (recentes: dispositivos de segurança)

**Estudos de caso:**
- DNIT publica relatórios de obras executadas
- Pode conter análise de defensas em rodovias federais
- Histórico de acidentes antes/depois (se disponível)

---

### 3.3 Operadores de Concessões

**Principais operadores:**
- **CCR** — BR-116 SP/RJ, BR-116 RS, BR-101 RJ/RN
- **Odebrecht TransportO** — BR-116 SC, BR-381
- **OHL** — BR-262 ES, BR-381 MG
- **Ecopistas** — Rodovia dos Bandeirantes (SP-280)

**Como acessar:**
1. Site do operador → Relatórios de Sustentabilidade / Relatórios Anuais
2. Investidor → apresentações com dados operacionais
3. Área de imprensa → releases com projetos de segurança

**Dados típicos:**
- Investimento em segurança (defensas/barreiras inclusos)
- Densidade de defensas (km de defensa por km de rodovia)
- Taxa de acidentes (antes/depois de reforços)
- Plano de manutenção (ciclos de reposição)

---

## 4. CONSULTORES E ENGENHARIAS ESPECIALIZADAS

**Empresas com portfólio em rodovias brasileiras:**
- **CONSULTEC** — Consultoria especializada em rodovias
- **FIESCAM** — Transportes e infraestrutura
- **Econsult** — Estudos econômicos de concessões
- **UFMG/UFRJ** — Laboratórios de pesquisa em segurança viária

**Como contactar:**
- Via Manta Associados (se têm parcerias)
- Diretamente (solicitar estudos de caso)
- Google Scholar → buscar publicações técnicas sobre o tema

---

## 5. PUBLICAÇÕES TÉCNICAS ACADÊMICAS

**Bases de dados:**
- **Google Scholar:** scholar.google.com
- **SciELO:** scielo.org (artigos em português)
- **ResearchGate:** pesquisadores brasileiros

**Palavras-chave:**
```
"defensa metálica" "custo" "rodovia" "Brasil"
"barreira rígida" "segurança viária" "manutenção"
"atenuador impacto" "rodovia federal" "concessão"
"dispositivos segurança" "acidentes" "custos operacionais"
"SICRO" "defensa" "custo unitário"
```

**Autores/Grupos notáveis:**
- Departamento de Engenharia Civil — UFMG (pesquisa em segurança)
- Núcleo de Pesquisa em Transportes — UFRJ
- Instituto de Pesquisas Rodoviárias — DNIT

---

## 6. FONTES INTERNACIONAIS (referência)

Se precisar de benchmarks internacionais para validar custos brasileiros:

**AASHTO (EUA):**
- Highway Safety Manual (HSM) — estima redução de acidentes por tipo de dispositivo
- Standard Specifications for Transportation Materials and Methods of Sampling — custos típicos

**Europa (ISO/IEC):**
- EN 1317 — Especificações de barreiras de segurança
- Custos tipicamente 20-40% acima do Brasil

**Mercosul:**
- Argentina (AySA tem dados de rodovias)
- Chile (dados de rodovias de montanha)

---

## 7. CHECKLIST — O QUE REUNIR

Para uma análise completa de custos + manutenção + resultado operacional:

### Custos
- [ ] Tabelas SICRO (unitários por km)
- [ ] Memoriais orçamentários de projetos executivos
- [ ] BDI regional aplicado
- [ ] Custos de transportação (defensa é produto pesado)
- [ ] Custos de instalação (mão-de-obra, equipamento)

### Manutenção Pós-Obra
- [ ] PER de concessões (ciclos de reposição)
- [ ] Manual ANTT (periodicidade de inspeção)
- [ ] Histórico de danos (estatística de impactos)
- [ ] Custos de serviços por km/ano
- [ ] Ciclo de reposição de atenuadores (alta frequência)

### Resultado Operacional
- [ ] Base de dados de acidentes (antes/depois de implantação)
- [ ] Indicadores de severidade (vítimas, danos materiais)
- [ ] Redução % em acidentes específicos (saída de pista)
- [ ] Valor economizado (menos indenizações)
- [ ] ROI da implantação de defensas

---

## 8. PRÓXIMOS PASSOS RECOMENDADOS

**Curto prazo (hoje):**
1. ✅ Você já tem: DNIT IPR-718, CONTRAN, referência técnica Manta
2. → **Usar Maestro** (prompt no item 1.1 acima)
3. → Agente S1 retornará com coleção `rod:` do Supabase

**Médio prazo (próxima semana):**
1. Acessar SharePoint → pasta `03_Projetos/Rodovias/`
2. Baixar 2-3 memoriais de concessões reais
3. Extrair tabelas de custos (defensa, barreira, atenuador)

**Longo prazo (próximo mês):**
1. Coletar históricos de manutenção (ANTT public data)
2. Cruzar custos com índices de acidentes
3. Compilar em ferramenta (Excel/Tableau) para decisões futuras

---

**Documento preparado para:** Análise de dispositivos viários em rodovias brasileiras  
**Data:** 29/07/2026  
**Status:** Guia de consulta — Manta Associados
