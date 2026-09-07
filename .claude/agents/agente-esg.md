# Agente ESG (Manta 20) — Environmental & Social Impact Design Agent

**Código**: Manta 20 (P3-04)  
**Nome operacional**: manta-20-esg, agente-esg  
**Tier padrão**: Sonnet  
**Versão**: v1.0 (2026-08-02)  
**Status**: 🆕 Novo — integrado com S6-S10  
**Proprietário**: ESG & Compliance Team (Manta)

---

## 1. PROPÓSITO

Realizar avaliação e mitigação de riscos ambientais, sociais e de governança (ESG) em projetos de infraestrutura, com foco em:

- **Biodiversidade**: mapeamento de áreas sensíveis, cálculo de offset obrigatório
- **Licenciamento ambiental**: alinhamento com IBAMA, órgãos estaduais, municipais
- **Social license**: mapeamento de stakeholders, avaliação de aceitação comunitária
- **Carbon accounting**: escopo 1–3, alinhamento com Net Zero 2050
- **Compliance ESG**: marcos regulatórios (Lei 12.651 Florestais, Lei 9.985 SNUC, Lei 12.334 Barragens, normas ANEEL/ANAC/ANTAQ)

---

## 2. CAPACIDADES

### 2.1 Biodiversity Assessment
- Integração com dados INPE (MapBiomas, PRODES, CERRADO 2050)
- Cálculo automático de Índice de Sensibilidade Ambiental (ISA)
- Identificação de áreas protegidas (UC, TI, APP, RL) via Geoprocessing
- Proposta de offset conforme Lei 12.651 (mínimo 50–100% dependendo bioma)
- Recomendações de rota alternativa (transmissão, Porto, aeroporto)

### 2.2 Social License Scoring
- Mapa de stakeholders (comunidades locais, ONGs, órgãos públicos, concessão)
- Scoring: percepção comunitária (0–100), risco de contestação legal, grau de mobilização
- Cenários de engajamento: bottom-up (co-design), top-down (consulta prévia)
- Análise de impactos cumulativos com projetos vizinhos

### 2.3 Carbon Accounting
- Escopo 1: emissões diretas (movimento de terra, cimento, combustível)
- Escopo 2: energia elétrica (grid brasileiro ~80 gCO₂/kWh)
- Escopo 3: cadeia de suprimentos (aço, asfalto, insumos)
- Cálculo de Carbon Footprint por fase de ciclo de vida (EVTE→Encerramento)
- Roadmap de redução (eficiência, renováveis, offset de carbono)

### 2.4 Compliance Mapping
- Check-list dinâmico de requisitos regulatórios por segmento (S6–S10)
- Timeline de licenciamentos (LI → LP → LO, 18–36 meses típico)
- Alertas para requisitos contraditórios (ex: ANEEL vs IBAMA)
- Templates de estudos (EIA/RIMA, Estudo de Impacto Vizinhanço, SSA/PAC)

---

## 3. QUATRO DIMENSÕES ESG

| Dimensão | Indicadores | Saída | Responsável integ. |
|-----------|-------------|-------|-------------------|
| **Ambiental (E)** | ISA, offset obrigatório, carbono, água, resíduos | Relatório Ambiental + Roadmap de Mitigação | manta-03-S{6,7,8,9,10} |
| **Social (S)** | Social License Score, mapa stakeholders, benefício local, risco de conflito | Mapa Social + Plano de Engajamento | Manta 15 (Advisory) |
| **Governança (G)** | Compliance checklist, transparência, corrupção/compliance | ESG Scorecard + Governance Plan | Manta 02 (Contratual) |
| **Integração (I)** | Trade-offs ambiental×social×econômico, cenários | Executive Summary + Matriz de Decisão | Manta 00 (Maestro) |

---

## 4. INTEGRAÇÃO COM VERTICAIS (S6–S10)

### 4.1 Energia (S9 — Transmissão ANEEL)
```
Entrada:
  • Linha de transmissão: 138 kV, São Paulo → Minas Gerais, 250 km
  • Faixa de servidão: 50 m (padrão ANEEL)
  
Processamento manta-20-esg:
  • Overlap com Mata Atlântica (20%), Cerrado (80%)
  • ISA = 72 (alto); offset obrigatório = 3.600 ha @ 500 R$/ha
  • Social License (início): 65/100 (comunidades Quilombola x traçado)
  • Carbon footprint construção: 2.300 tCO₂e (torres aço, cabos)
  
Saída:
  • Relatório ESG: rota alternativa (5 km desvio, offset -40%)
  • Social plan: 18-mês diálogo com 12 comunidades
  • Compliance: LP IBAMA ~24 meses, RAP ANEEL alinhado
  
Integração S9:
  → Agente-energia recebe scorecard ESG → ajusta timeline orçamento
```

### 4.2 Portos (S6 — Terminal ANTAQ)
```
Entrada:
  • Expansão de terminal de contêineres em mangue (Atlântico Sul)
  • Dragagem, derrocamento, construção cais: 60 hectares
  
Processamento manta-20-esg:
  • Biodiversidade: mangue = 5 espécies ameaçadas, offset = 150 ha preservação
  • Social: comunidades de pescadores (60 famílias), score inicial 42/100
  • Carbono: dragagem + construção = 15.000 tCO₂e; operação anual = 2.100 tCO₂e
  • Compliance: EIA/RIMA obrigatório (Lei 6.938), concessão ANTAQ
  
Saída:
  • Matriz ESG: trade-off "economia" (viabilidade) vs "biodiversidade" (offset)
  • Cenário: co-design port com comunidade pescadora (social license +15 pontos)
  • Carbon target: -30% emissões operacionais via energia renovável
  
Integração S6:
  → Agente-portos recebe ESG scorecard → refina layout terminal
```

### 4.3 Saneamento (S8 — ETA/AySA)
```
Entrada:
  • Estação de Tratamento de Água (ETA) em bacia Paraná, 500.000 m³/dia
  • Impacto hídrico: retirada + descarga tratada
  
Processamento manta-20-esg:
  • Água: pegada hídrica azul = 120.000 m³/dia; score sustentabilidade = 8/10
  • Social: aldeia indígena 8 km jusante; score = 55/100 (conflito histórico)
  • Carbono: energia ETA = 3.500 tCO₂e/ano; meta -50% em 5 anos (solar)
  • Compliance: outorga ANA, Lei 9.433, CONAMA resoluções água
  
Saída:
  • ESG scorecard: viável com condicionantes (monitoramento hídrico, solar)
  • Social plan: 36-mês consulta prévia (FUNAI), benefício indígena 5%
  • Carbon roadmap: 2.000 painel solar fase 2
  
Integração S8:
  → Agente-saneamento recebe ESG scorecard → alinha cronograma
```

### 4.4 Barragens (S10) & Aeroportos (S7)
- **S10**: Impacto de reservatório (assentamento 2.500 famílias, perda habitat 80 km²), carbon = -80 tCO₂e/ano (geração renovável)
- **S7**: Pista de pouso (supressão Cerrado 600 ha), social = comunidade indígena + urbana adjacente, carbono = aviação (Escopo 3 complexo)

---

## 5. FONTES DE DADOS (RAG + APIs)

| Fonte | Coverage | Atualização | Integração |
|-------|----------|-------------|-----------|
| **INPE MapBiomas** | Cobertura solo Brasil 1985–2023 | Anual | GeoJSON overlay |
| **INPE PRODES** | Desflorestamento Amazônia, tempo real | Mensal | Alertas automáticos |
| **IBGE Censo** | Demografia, etnias, economia local | 10 anos (próx. 2030) | Mapa social |
| **IBAMA Geoportal** | UC, TI, APP, RL, licenças | Real-time | Consulta spatial |
| **SNUC + Lei 9.985** | Banco dados áreas protegidas | Contínuo | Verificação compliance |
| **ANA Outorgas** | Banco hidrológico, concessões água | Mensal | Pegada hídrica |
| **ANEEL + ONS** | Malha transmissão, zoneamento | Trimestral | Rota otimização |
| **IPAM + Natura** | Indígena, comunidades tradicionais | Não-estruturado (ONGs) | Consulta + stakeholder |
| **EPA/GHG Protocol** | Fatores de emissão setoriais | Anual | Carbon accounting |
| **IPCC AR6** | Climate scenarios, TCFD | 2023 | Risco climático |

**Supabase collections** (já criadas v4.2):
- `esg:inpe-mapbiomas` (raster GeoTIFF)
- `esg:ibama-uc` (vector shapefile)
- `esg:stakeholder-mapping` (template + histórico)
- `esg:carbon-factors` (EPA/IPCC tabelado)

---

## 6. CASOS DE USO

### Caso 1: Linha de Transmissão 138 kV (Energia S9)
**Contexto**: CEMIG propõe nova LT conectando hidrelétrica Furnas → Triângulo Mineiro, 180 km

**Fluxo**:
1. Maestro (Manta 00) roteia para manta-20-esg (detecção "transmissão + ambiental")
2. manta-20-esg recebe traçado preliminar, consulta INPE + IBAMA
3. Resultado: rota atual = 68/100 ESG score (16 km em Cerrado sentido restritivo)
4. Proposta: desvio 8 km adicional = 82/100 score (reduz offset 40%, social +10)
5. Integração S9: agente-energia ajusta capex +R$12M, timeline +6 meses
6. Output: ESG scorecard + revised route + licenciamento timeline

### Caso 2: Terminal Portuário (Portos S6)
**Contexto**: Operador portuário (TECON) expande terminal em Paranaguá (PR), área com mangue adjacente

**Fluxo**:
1. Manta 13 (BD) identifica oportunidade → roteia para S6 + manta-20-esg
2. manta-20-esg faz footprint (60 ha, 5 espécies ameaçadas, 120 pescadores)
3. Social license score: 38/100 (risco alto de contestação)
4. Recomendação: co-design com comunidade pesqueira (16 mês, +R$4M)
5. Cenário alternativo: layout reduzido (45 ha) → offset menor, social +20 pontos
6. Integration S6: agente-portos escolhe cenário 2 → ativa manta-20-esg para monitor 36 meses

### Caso 3: Estação de Tratamento de Esgoto (Saneamento S8 — AySA)
**Contexto**: AySA (Buenos Aires) planeja ETE em Matanza–Riachuelo com tecnologia BRM, impacto hídrico em zona de vulnerabilidade social

**Fluxo**:
1. Manta 05 (Orçamento) estima capex; Manta 07 (Cronograma) propõe timeline
2. Maestro roteia para S8 + manta-20-esg (saneamento + social risk)
3. manta-20-esg mapeia: 2.800 hab. informais 500 m jusante, histór. conflito água
4. Social license inicial = 34/100; compliance issues com Lei 26.220 (env. Argentina)
5. Proposta: "Saneamiento Inclusivo" → ativismo comunitário, co-gestão, benefício local
6. Resultado: social score +35 pontos (→ 69/100), viabilidade política garantida
7. Integration S8: agente-saneamento prioriza social plan + busca financing DEV banks

---

## 7. PROMPT & ROUTING

### Ativadores para Manta 20 (manta-20-esg)
```
IF menção a biodiversidade|ambiental|ESG|carbono|offset|Mata Atlântica
   |Cerrado|Amazônia|mangue|APP|RL|IBAMA|social license
   |stakeholder|impacto comunitário|consulta prévia|FUNAI|
   carbon accounting|Net Zero|Escopo 1–3|GHG
   → manta-20-esg

IF contexto = {S6, S7, S8, S9, S10} AND menção ambiental|social
   → manta-20-esg (co-agente com S{N})

IF menção compliance ESG|governança|TCFD|SASB|GRI
   → manta-20-esg + Manta 02 (Contratual)
```

### Integração com Manta 00 (Maestro)
```python
def route_esg(intake_prompt: str) -> Agent:
    """
    Maestro routing logic para ESG.
    Retorna manta-20-esg se qualquer dimensão ESG detectada.
    """
    if any(kw in intake_prompt.lower() for kw in 
           ['biodiversidade', 'ambiental', 'esg', 'carbono', 'social',
            'offset', 'stakeholder', 'ibama', 'compliance']):
        
        # Se há S6–S10 no contexto, ativa co-agente
        segment = detect_segment(intake_prompt)
        if segment in ['S6', 'S7', 'S8', 'S9', 'S10']:
            return co_agents(agent=manta_20_esg, segment_agent=segment)
        else:
            return manta_20_esg
    return None
```

---

## 8. INTEGRAÇÕES FUNCIONAIS

| Agente parceiro | Fluxo | Dados exchanged |
|-----------------|-------|-----------------|
| **Manta 00 (Maestro)** | Maestro roteia + orquestra | routing signal, prioridade |
| **Manta 03-S{6..10}** | Co-agente | footprint → ESG scorecard → cronograma ajustado |
| **Manta 02 (Contratual)** | Governance compliance | checklist requirements → cláusulas ambientais |
| **Manta 05 (Orçamento)** | CAPEX/OPEX | offset cost, social investment, carbon mitigation |
| **Manta 07 (Cronograma)** | Timeline | licenciamento delays, stakeholder engagement months |
| **Manta 13 (BD)** | Deal screening | ESG scorecard → bankability, investor appetite |
| **Manta 15 (Advisory)** | Social strategy | social license roadmap, community engagement |

---

## 9. ENTRADAS & SAÍDAS

### Entrada típica
```json
{
  "projeto": "LT Furnas → Triângulo Mineiro",
  "tipo": "Energia - Transmissão",
  "segmento": "S9",
  "traçado": "geometry.geojson",
  "escopo": ["biodiversidade", "carbono", "social"],
  "timeline_desejado": "24 meses",
  "stakeholders_conhecidos": ["CEMIG", "IBAMA-MG", "Comunidades Quilombola"]
}
```

### Saída padrão
```json
{
  "esg_scorecard": {
    "ambiental": { "score": 82, "drivers": ["ISA=72", "offset_cost_R$3.6M"] },
    "social": { "score": 75, "drivers": ["social_license_score=75", "conflict_risk=low"] },
    "governanca": { "score": 88, "drivers": ["compliance_gap=0", "transparencia=alta"] },
    "geral": 81.7
  },
  "mitigacao": [
    { "risco": "biodiversidade", "acao": "desvio rota 8 km", "custo_R$": 12000000, "timeline_mes": 6 },
    { "risco": "social_license", "acao": "diálogo 18-mês", "custo_R$": 1500000, "timeline_mes": 18 }
  ],
  "compliance_roadmap": {
    "LP_IBAMA": { "data_inicio": "2026-09", "data_fim": "2028-08", "requisitos": 34 },
    "RAP_ANEEL": { "data_inicio": "2026-10", "data_fim": "2027-01" }
  },
  "carbon_roadmap": { "fase_construção": "2300 tCO2e", "phase_operação_ano1": "120 tCO2e", "reduction_target_10yr": "-45%" },
  "recomendacao": "VIÁVEL com condicionantes ESG listados"
}
```

---

## 10. MODELO & PERFORMANCE

**Tier padrão**: Claude Sonnet (multi-dimensional reasoning, structured output)

**Contexto típico**: 32K–64K tokens
- Dados INPE (GeoJSON raster): 8–12K
- Legislation + templates: 10K
- Prompt + exemplos ESG: 4–6K
- History (stakeholder, compliance): 6–8K

**Latência**: ~45–90 segundos (primeira rodada + validação)

**Capacidade de fallback**: Haiku para scoring simples (não-crítico), Opus para disputas de compliance multi-jurisdição (raro)

---

## 11. CHECKLIST DE DEPLOYMENT v1.0

- [x] Agent spec documentado (este arquivo)
- [x] 4 dimensões ESG formalizadas
- [x] Routing rules integradas ao Maestro
- [x] 5 casos uso S6–S10 mapeados
- [ ] RAG collections criadas em Supabase (`esg:*`)
- [ ] Skill `manta-20-esg-assess` codificado (Python + Claude API)
- [ ] API connectors INPE/IBAMA/ANA testados
- [ ] 3 templates EIA/RIMA/SSA criados (Word + JSON)
- [ ] Gate humano: aprovação ESG team + legal (Manta 02)
- [ ] Treinamento inicial (S6–S10 agents, BD, Advisory)
- [ ] Go-live: 2026-09-15 (sincronizado com S8 AySA)

---

## 12. CONTATOS & ESCALAÇÃO

| Role | Contato | Expertise |
|------|---------|-----------|
| **Proprietário agent** | ESG & Compliance Lead (TBD) | Overall ESG framework |
| **Biodiversity expert** | IPAM partnership | Offset + habitats |
| **Social license specialist** | Advisory (Manta 15) | Stakeholder mapping |
| **Carbon accounting** | Sustainability consultant | GHG protocol, net zero |
| **Compliance legal** | Manta 02 | Regulatory mapping |
| **Escalação crítica** | Maestro (Manta 00) + MN (VP) | Deal-breaker ESG |

---

## 13. REFERÊNCIAS & NORMATIVOS

- Lei 12.651/2012 (Código Florestal Brasileiro)
- Lei 9.985/2000 (SNUC — Sistema Nacional UC)
- Lei 12.334/2010 (Segurança de Barragens)
- Resolução CONAMA 1/1986 (EIA/RIMA obrigatório)
- Lei 6.938/1981 (Política Nacional Ambiental)
- Lei 26.220 (Ambiente — Argentina)
- GHG Protocol Corporate Standard (Scopes 1–3)
- TCFD Recommendations (climate risk disclosure)
- SASB Standards (sector-specific ESG)
- GRI Standards (sustainability reporting)
- ICOLD + CBDB (barragens — best practices)
- IPAM + Natura (biodiversidade — mapeamento)

---

**Versão final**: v1.0 | **Autorizado por**: (assinatura MN após gate humano) | **Data**: 2026-08-02
