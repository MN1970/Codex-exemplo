# Teste de Validação — Fase II Rodovias (Pavimentação, Terraplenagem, Drenagem, O&M)

**Data**: 2026-08-04  
**Branch**: `claude/agente-rodovias-fase2-6jhqhc`  
**Status**: Pronto para execução contra agente-infraestrutura S1  
**Total testes**: 14 smoke tests

---

## Testes por Disciplina

### Pavimentação (4 testes)

**PAV-01**: Dimensionamento AASHTO 1993 vs M-E para pavimento asfáltico
- Expected: Diferença entre método empírico vs mecanístico, sensibilidade E*, referência DNIT
- Pass: [ ] Fail: [ ]

**PAV-02**: Misturas asfálticas CBUQ, SMA, porosa — aplicações rodovia Brasil
- Expected: Comparação tipos, custos relativos, quando usar cada, SICRO
- Pass: [ ] Fail: [ ]

**PAV-03**: Limite máximo RAP em CBUQ novo, impacto ligante envelhecido, ajustes
- Expected: Percentuais (30-50%), E*, compatibilidade, sustentabilidade
- Pass: [ ] Fail: [ ]

**PAV-04**: Falhas em pavimento asfáltico (alligator, trilho, panela, remendo) — soluções
- Expected: 3+ falhas, causas, reabilitação (reforço/recapeamento), custo SICRO
- Pass: [ ] Fail: [ ]

---

### Terraplenagem (3 testes)

**TERRA-01**: Método Bishop vs Janbu Simplificado — quando usar, diferença FS
- Expected: Iterativo vs manual, FS Bishop ±2-5% vs Janbu, software (Slope/W)
- Pass: [ ] Fail: [ ]

**TERRA-02**: Compactação Proctor Normal (592 kJ/m³) vs Modificado (2700 kJ/m³)
- Expected: Relação energia, densidade +7-10%, aplicações (tráfego pesado)
- Pass: [ ] Fail: [ ]

**TERRA-03**: Diagrama Brückner — Free Haul Distance, otimização custos borrow/rejeito
- Expected: FHD 500-1000m, custos >FHD, multi-seção, custo transporte
- Pass: [ ] Fail: [ ]

---

### Drenagem (4 testes)

**DREN-01**: Método Racional (Q=CIA) vs SCS — aplicação bacias <50 ha vs 50-2500 ha
- Expected: Hipóteses chuva uniforme, retenção S, bacias, software HEC-HMS
- Pass: [ ] Fail: [ ]

**DREN-02**: Dimensionamento bacia amortecimento para Q=3m³/s — profundidade, comprimento, pedra
- Expected: Repouso 0.5m, comprimento 2m, brita 5-10cm, V<1.5 m/s, custo R$ 2-5k
- Pass: [ ] Fail: [ ]

**DREN-03**: Dreno longitudinal — composição (PEAD, brita, geotêxtil), espaçamento, Darcy
- Expected: Q=k×A×i, 20-50m espaçamento, +30% vida pavimento, saída boca-leão
- Pass: [ ] Fail: [ ]

**DREN-04**: Geotêxtil em drenagem — critério AOS (abertura malha), retenção vs vazão
- Expected: AOS < 4× D85, k≥10^-1 cm/s, NBR 6835, tração ≥8 kN/m, custo R$ 3-8/m²
- Pass: [ ] Fail: [ ]

---

### O&M (3 testes)

**OM-01**: Índices PCI (ASTM) vs ICP (DNIT) — diferença escala, cálculo, vida restante
- Expected: 0-100 (PCI novo=100, ICP novo=100 inverso), amostragem 100m², ICP 70+=12-18 anos
- Pass: [ ] Fail: [ ]

**OM-02**: Análise LCC 30 anos CBUQ (R$ 2M inicial, 100k/ano O&M, reforço 800k ano 15) vs CCP
- Expected: VPL CBUQ ~R$ 6M vs CCP ~R$ 2.8M (desconto 6%), CCP + vida 50 anos
- Pass: [ ] Fail: [ ]

**OM-03**: Pavimento ICP 65, afundamento 8mm — espessura reforço, pré-requisitos
- Expected: 3-6cm CBUQ, CBR≥3%, drenagem funcional, compatibilidade ligante, +8-12 anos vida
- Pass: [ ] Fail: [ ]

---

## Critério Pass/Fail

**Pass**: Resposta contém informação técnica coerente + referência norma/SICRO/RAG ou caso real  
**Fail**: Resposta genérica, alucinação norma inexistente, ou "não tenho informação"

**Expectativa**: 14/14 pass (100%)

---

**Status**: ✅ Pronto para Step 3 (execução testes contra agente-infraestrutura S1)
