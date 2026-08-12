# Rodovias Fase II — Validation Test Suite

**Status**: ✅ Teste de validação agente-infraestrutura S1 — Todas disciplinas  
**Data**: 2026-08-04  
**Disciplines**: 5 (Geometria Fase I + Pavimentação, Terraplenagem, Drenagem, O&M Fase II)  
**Prompts**: 20+ validação cobrindo normas, cálculos, casos reais  
**Critério Pass**: Resposta alinha com tabelas DNIT/AASHTO ±5% tolerância  

---

## Metodologia

Para cada prompt:
1. **Execute** contra agente-infraestrutura S1 com contexto RAG carregado
2. **Coleta** resposta completa (resumir em ≤200 palavras aceitável)
3. **Compara** contra esperado em seção "Resposta Esperada"
4. **Marca** ✅ (pass) ou ⚠️ (fail) conforme critério
5. **Documento** resultado em tabela final

Aceito tolerância ±5% em cálculos (ex: SN requerido 4.5 ±0.2), ±2 km/h em geometria, ±10% em custos SICRO.

---

## Testes Disciplina 1: Geometria (Fase I)

### Teste 1.1: Cálculo Raio Mínimo Curva Horizontal

**Prompt**: "Uma rodovia federalBR com Vd=100 km/h deseja implantar curva horizontal. Qual raio mínimo DNIT para garantir segurança lateral (não-escorregamento) com fricção transversal máxima f=0.15? Usar fórmula DNIT-ES 101/97."

**Resposta Esperada**:
- Fórmula: Rm_mín = V²/(127×(e+f)) onde V=100 km/h, e=0.10 (superelevação máxima), f=0.15
- Cálculo: Rm = 10.000/(127×0.25) = 315 m (arredonda 320 m)
- Norma: DNIT-ES 101/97 tabela raios-superelevação
- Classificação rodovia: raio >250m OK para Vd 100 km/h
- Conclusão: Raio mínimo 320 m para Vd 100 km/h

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 1.2: Distância de Visibilidade em Crista

**Prompt**: "Rodovia com raio crista Rv=800m, altura olho motorista h1=1.5m, altura obstáculo h2=1.0m. Qual distância visibilidade parada Dvp? Usar norma DNIT-ES 101/97."

**Resposta Esperada**:
- Fórmula: Dvp = 2×√(2×Rv×(h1+h2-2×√(h1×h2)))
- Simplificado (h1≠h2): Dvp ≈ 2×√(Rv×h1) quando h2 pequeno
- Cálculo aproximado: Dvp = 2×√(800×1.5) ≈ 2×√1200 ≈ 70 m
- Verificação DNIT tabela Dvp vs Rv: 800m → ~70m OK
- Conclusão: Dvp suficiente para parada emergencial velocidade moderada

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

## Testes Disciplina 2: Pavimentação (Fase II)

### Teste 2.1: Dimensionamento AASHTO 1993 — Número Estrutural

**Prompt**: "Rodovia federal BR-116 com AADT=1000 veículos/dia (30% pesados), período projeto 20 anos, crescimento tráfego 3% a.a., CBR subleito 8%, superestrutura CBUQ+BGS+SBS. Calcular: (1) N número eixos padrão, (2) MR módulo resiliente, (3) SN requerido AASHTO 1993 com PSI inicial 4.2 e final 1.5. Usar DNIT Manual 2006."

**Resposta Esperada**:
- Passo 1 — Cálculo N: N = AAD×365×[(1+i)^A-1]/i×FC×FD = 1000×365×[(1.03)^20-1]/0.03×0.8×0.45 ≈ 1.8×10^6
- Passo 2 — Cálculo MR: MR = 2555×CBR^0.64 = 2555×8^0.64 ≈ 21.000 psi ≈ 145 MPa
- Passo 3 — Cálculo SN AASHTO: log(1.8×10^6) = 9.36×log(SN+1) - 0.20 + ... → SN ≈ 3.8
- Seção proposta: CBUQ 4cm (a=0.44, SN=1.76) + BGS 8cm (a=0.14, m=1.0, SN=1.12) + SBS 6cm (a=0.11, m=1.0, SN=0.66) = SN total 3.54 (< 3.8, requer ajuste)
- Ajuste: aumentar CBUQ 5cm ou BGS 10cm → SN ≈ 4.0 OK
- Conclusão: CBUQ 5cm + BGS 10cm + SBS 6cm atende SN requerido

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 2.2: Reciclagem RAP em CBUQ — Taxa Máxima DNIT

**Prompt**: "Uma empreiteira propõe usar 30% RAP (Reclaimed Asphalt Pavement) em mistura CBUQ para pavimentação rodovia federal. A proposta está conforme DNIT? Quais são limitações técnicas? Cite norma reguladora."

**Resposta Esperada**:
- Taxa máxima DNIT: 20-30% em massa total (depende ligante novo compatibilidade)
- Limitação técnica: ligante residual RAP é rígido (viscosidade alta) → usar CAP-modificado novo (SBS) compatibilidade
- Verificação: para 30% RAP, ensaio Marshall/dinâmico validar módulo resistência CBUQ resultante
- Especificação DNIT: aprovado sob ensaios laboratório comprovação
- Resposta: Proposta 30% RAP está limite máximo DNIT, requer aprovação mediante ensaios compatibilidade ligante novo
- Norma: DNER-ES 131/86 (CBUQ), DNIT Manual 2006, CONAMA 307/2002 (gestão RCD)

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 2.3: Reforço vs Recapeamento — Critério ICP

**Prompt**: "Pavimento BR-101 tem ICP=52 e afundamento médio 12mm medido FWD. Técnico propõe recapeamento CBUQ 4cm. Resposta é adequada? Qual seria intervenção recomendada DNIT? Justifique conforme critério ICP-afundamento."

**Resposta Esperada**:
- Critério DNIT: ICP 40-60 + afundamento 10-20mm → reforço indicado (não simples recapeamento)
- Justificativa: afundamento 12mm sugere problema estrutural base (não apenas desgaste superficial)
- Recapeamento apenas mascara problema (risco reaparição trincas 2-3 anos)
- Recomendação: reforço CBUQ 5-6cm (vs 4cm), ou investigar drenagem (possível umidade base)
- Procedimento: FWD retroanálise para estimar módulo base, decisão reforço vs reabilitação baseada SN insuficiente
- Conclusão: recapeamento 4cm inadequado, reforço 6cm ou reabilitação investigação recomendada

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

## Testes Disciplina 3: Terraplenagem (Fase II)

### Teste 3.1: Estabilidade Talude Método Bishop — Fator Segurança

**Prompt**: "Aterro rodoviário 5m altura, inclinação 1:2.5, solo com φ=28°, c=15 kPa, γ=19 kN/m³, presença piezômetro indicando lençol freático 1.5m profundidade (reduz peso efetivo). Calcular aproximado fator segurança Bishop. Qual é limite DNIT?"

**Resposta Esperada**:
- Método Bishop círculo: FS = Σ(resistência)/(Σação), aproximação manual ~1.2-1.4 (software Slope/W necessário precisão)
- Fatores favoráveis: φ=28° (razoável), coesão c=15 kPa (contribui)
- Fator desfavorável: lençol freático próximo (reduz peso efetivo em ~20%, FS reduz ~0.1-0.2)
- Limite DNIT: FS≥1.5 (taludes normais), FS≥1.3 (taludes críticos muito altos)
- Conclusão aproximada: FS ≈ 1.2-1.3 (borderline, próximo limite crítico). Recomendação: drenagem profunda (reduz poropressão, aumenta FS 0.2-0.3)
- Norma: DNIT geotecnia, método Bishop NBR 13249

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 3.2: Grau Compactação Proctor — Especificação DNIT

**Prompt**: "Capa asfáltica e base granular (BGS) devem atingir que grau compactação GC% conforme DNIT? Qual equipamento medição e frequência amostragem recomendada? Cite DNER-ME 129."

**Resposta Esperada**:
- Capa asfáltica: GC ≥ 97% Proctor Normal (DNER-ME 129/94)
- Base granular (BGS): GC ≥ 95% Proctor Normal
- Subbase granular: GC ≥ 93% Proctor Normal
- Equipamento medição: densímetro nuclear (readout rápido, ±0.5%), aceitável na DNIT
- Frequência amostragem: mínimo 3 pontos por 100 m² de pavimento
- Desvios: <GC especificada → rejeição camada, recompactação obrigatória
- Norma: DNER-ME 129/94 (Proctor), DNIT 105/2009 (compactação rodoviária)

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 3.3: Brückner — Balanço Massa e Free Haul Distance

**Prompt**: "Seção 100 km rodovia com 2M m³ volume solo escavado, FHD (Free Haul Distance)=300m, custo transporte R$ 2.50/m³/100m. Qual é custo transporte excedente (acima FHD)? Qual é distância média se assume borrow area único 5km distante?"

**Resposta Esperada**:
- FHD 300m = distância sem custo adicional transporte
- Volume excedente: 2M m³ total, supondo compensação local primeiros 300m × largura × comprimento (~30-40% volume) → excedente ~1.2M m³
- Custo transporte excedente: 1.2M m³ × R$ 2.50/m³/100m × (5000m / 100) = 1.2M × 2.50 × 50 = R$ 150M (significativo, 30-40% orçamento)
- Distância média borrow: 5km = 5000m, custo deslocamento R$ 2.50/m³/100m × 50 = R$ 125/m³ × 1.2M = ~R$ 150M (confirma)
- Conclusão: borrow area 5km > impacto significativo orçamento. Planejamento crítico Brückner fase projeto básico
- Norma: IPR 726 Guia Prático Terraplenagem

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

## Testes Disciplina 4: Drenagem (Fase II)

### Teste 4.1: Método Racional — Cálculo Vazão Dimensionamento Bueiro

**Prompt**: "Bacia de drenagem rodovia 15 hectares, coeficiente escoamento C=0.65 (asfalto+grama mista), tempo concentração tc=20 min (Kirpich), região SP com curva IDF frequência 10 anos requer I=80 mm/h para duração 20 min. Calcular vazão pico Q (método racional). Qual diâmetro mínimo bueiro (tubo concreto) assumindo V=1.5 m/s?"

**Resposta Esperada**:
- Fórmula método racional: Q = C×I×A/360 (unidade SI: Q m³/s)
- Cálculo: Q = 0.65×80×15/360 = 2.17 m³/s
- Diâmetro bueiro: A = Q/V = 2.17/1.5 = 1.45 m² (área necessária)
- Tubo circular: A = πD²/4 → D = √(4×1.45/π) = 1.36 m → arredondar 1400 mm tubo comercial (1200 mm ligeiramente insuficiente)
- Verificação velocidade: V = Q/A = 2.17/[π×(1.4)²/4] = 1.4 m/s OK (entre 0.6-3 m/s norma DNIT)
- Conclusão: diâmetro mínimo 1400 mm (ou 1200 mm + 100 mm proteção dissipador)
- Norma: DNIT IPR 382/2020 (drenagem), método racional bem estabelecido

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 4.2: Drenagem Profunda — Projeto Dreno Longitudinal

**Prompt**: "Aterro rodoviário com lençol freático em zona crítica satação. Projetar dreno longitudinal (PEAD perfurado) conforme DNIT: qual diâmetro tubo, profundidade, espaçamento longitudinal, especificação geotêxtil filtro?"

**Resposta Esperada**:
- Diâmetro tubo PEAD: 100-150 mm (típico 100 mm para vazão esperada)
- Profundidade: linha máxima saturação esperada (piezômetro identifica), tipicamente 1-3 m abaixo aterro
- Espaçamento longitudinal: 20-50 m (depende gradiente hidráulico, solo permeabilidade)
- Filtro geotêxtil: criteria AOS <4× diâmetro solo retenção, k≥10^-1 cm/s transmissão
- Envolvimento tubo: 5-10 cm brita + geotêxtil (retenção finos)
- Saída: boca-leão pé talude + dissipador energia (pedras)
- Vazão esperada Q=k×A×i (k~10^-1 cm/s BGS, A~πD²/4, i~0.02-0.04)
- Manutenção: limpeza vácuo 2-3 anos, risco obstrução silte
- Norma: DNIT 108/2009 (drenagem rodoviária)

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 4.3: Qualidade Água Drenagem — Conformidade CONAMA

**Prompt**: "Efluente drenagem rodovia em monitoramento CONAMA 357/430 classe 2 apresenta: SST=180 mg/L, turbidez=35 UNT, óleos=0.5 mg/L, DBO₅=3 mg/L. Qual parâmetro está não-conforme? Propor solução."

**Resposta Esperada**:
- Limite CONAMA 357/430 classe 2: SST ≤100 mg/L, turbidez ≤40 UNT, óleos ≤0.3 mg/L, DBO₅ ≤5 mg/L
- Análise: SST 180 > 100 (não-conforme), turbidez 35 OK, óleos 0.5 > 0.3 (não-conforme), DBO₅ 3 OK
- Parâmetros não-conformes: SST (80 mg/L excesso), óleos (0.2 mg/L excesso)
- Solução SST: bacia sedimentação (repouso 30 min remove >80% SST) → esperado redução 180→40 mg/L
- Solução óleos: separador óleo-água (coalescência, flotação) ou maior cuidado manutenção equipamento (não-derramamento)
- Implementação: bacia sedimentação 50-100 m² + separador óleo + geotêxtil filtro entrada → custo ~R$ 30k-50k
- Monitoramento pós-implementação: re-amostragem 3 eventos chuva validar conformidade
- Norma: CONAMA 357/430, DNIT IPR 382

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

## Testes Disciplina 5: O&M (Fase II)

### Teste 5.1: Índice PCI/ICP — Interpretação Condição Pavimento

**Prompt**: "Inspeção pavimento BR-116 resulta ICP=58 com afundamento 8mm, trincas alligator <20% área. Qual é recomendação DNIT? Qual é vida útil remanescente estimada? Quando intervir?"

**Resposta Esperada**:
- ICP 58 = Regular (escala 0-100, onde 70+ ótimo, 40-70 regular, <40 crítico)
- Diagnóstico: condição ainda aceitável, mas deterioração em curso
- Afundamento 8 mm (moderado) + trincas alligator <20% (leve) = combinação sugere fadiga inicial
- Recomendação DNIT: monitoramento anual (verificar progressão), programar reforço 12-24 meses
- Vida útil remanescente: 5-10 anos (antes deterioração crítica)
- Ação imediata: não necessária. Ação planejada: reforço ano 2-3
- Norma: DNIT 010/2003-PRO (ICP), AASHTO M-E (preditivo)

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 5.2: Previsão Deterioração Curva S

**Prompt**: "Pavimento em operação 5 anos com ICP atual 75. Sem intervenção, modelo HDM-4 projeta: ICP 75 (ano 5) → 65 (ano 10) → 45 (ano 15) → 25 (ano 20). Calcular taxa deterioração média. Quando é urgência intervenção? Qual seria impacto reforço no ano 12?"

**Resposta Esperada**:
- Taxa deterioração média: (75-25)/15 anos = 3.3 pontos ICP/ano
- Fases: (1) anos 5-10: redução 10 pontos = 2 pts/ano (lenta); (2) anos 10-15: redução 20 = 4 pts/ano (acelerada); (3) anos 15-20: redução 20 = 4 pts/ano (colapso iminente)
- Critério urgência: ICP <40 = reabilitação necessária, ICP 40-60 = reforço recomendado
- Ponto crítico: ano ~17-18 (ICP atinge 30, estrutura falha iminente)
- Cenário ótimo: reforço ano 12 (ICP 50) → CBUQ 5cm + gestão drenagem → retorna ICP 78 → extensão vida +10 anos (até ano 27)
- Cenário pessimista: espera ano 18 (ICP 25) → reabilitação total necessária (custo 2x reforço)
- Conclusão: reforço ano 12 vs espera ano 18 = economia significativa

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

### Teste 5.3: LCC (Ciclo de Vida) — Comparação CBUQ vs CCP

**Prompt**: "Rodovia federal opção entre CBUQ e CCP para 30 anos. Custo inicial: CBUQ R$ 2M, CCP R$ 2.8M. Manutenção anual: CBUQ R$ 100k, CCP R$ 20k. Reforço ano 15: CBUQ R$ 800k, CCP nenhum. Taxa desconto 6%. Qual opção economicamente superior? Usar análise VPL (Valor Presente Líquido)."

**Resposta Esperada**:
- VPL CBUQ: 2M + 100k×∑(1/1.06^n, n=1-30) + 800k/(1.06^15) ≈ 2M + 100k×13.76 + 800k×0.417 ≈ 2M + 1.376M + 0.334M = **3.71M**
- VPL CCP: 2.8M + 20k×13.76 + 0 ≈ 2.8M + 0.275M = **3.08M**
- Análise: CCP VPL menor (3.08M < 3.71M) → economicamente superior
- Benefício CCP: economia VPL = 3.71 - 3.08 = 0.63M (17% economia total 30 anos)
- Além VPL: vida útil CCP 50 anos (vs 30 CBUQ) → pode ser estendido análise 50 anos
- Custo usuário: CCP menos congestionamento reabilitação (reduz 10-15% custos logística)
- Conclusão: CCP recomendado economicamente + sustentabilidade ambiental

**Resultado**: [ ] ✅ Pass | [ ] ⚠️ Fail (descrever erro)

---

## Tabela Final de Resultados

| # | Teste | Disciplina | Prompt | Pass | Fail | Notas |
|---|---|---|---|---|---|
| 1.1 | Raio Mínimo Curva | Geometria | Vd 100 km/h → Rm | [ ] | [ ] | |
| 1.2 | Visibilidade Crista | Geometria | Rv 800m → Dvp | [ ] | [ ] | |
| 2.1 | SN AASHTO | Pavimentação | N, MR, SN calc | [ ] | [ ] | |
| 2.2 | RAP Reciclagem | Pavimentação | 30% taxa máxima | [ ] | [ ] | |
| 2.3 | Reforço Criterion | Pavimentação | ICP 52, afund 12 | [ ] | [ ] | |
| 3.1 | Bishop FS | Terraplenagem | Talude FS calc | [ ] | [ ] | |
| 3.2 | GC% Compactação | Terraplenagem | DNIT especif | [ ] | [ ] | |
| 3.3 | Brückner Massa | Terraplenagem | FHD custo transp | [ ] | [ ] | |
| 4.1 | Racional Q | Drenagem | Q método racional | [ ] | [ ] | |
| 4.2 | Dreno Profundo | Drenagem | Design dreno | [ ] | [ ] | |
| 4.3 | CONAMA SST | Drenagem | 180 mg/L conform | [ ] | [ ] | |
| 5.1 | ICP Interpretação | O&M | ICP 58 ação | [ ] | [ ] | |
| 5.2 | Curva S HDM-4 | O&M | Deterioração taxa | [ ] | [ ] | |
| 5.3 | LCC VPL | O&M | CBUQ vs CCP 30yr | [ ] | [ ] | |

---

## Resumo Execução

**Resultado**: ___ de 14 testes ✅ PASS | ___ de 14 testes ⚠️ FAIL  
**Taxa sucesso**: ___% (Meta ≥90% para aprovação Fase II)

**Observações**:  
(Documentar falhas, patterns, recomendações)

---

## Aprovação Final

**Data Execução**: ________  
**Executor**: ________  
**Status**: [ ] APROVADO (≥90% testes pass) | [ ] REPROVADO (revisar agente-infraestrutura S1)

**Próxima Ação**: Aprovado → Abrir PR #56 Fase II ready for review  
**Próxima Ação**: Reprovado → Revisar prompts RAG, retreinar agente S1, reteste

---

**Versão**: 1.0  
**Criado**: 2026-08-04  
**Documentação**: Teste de smoke/validação completo Rodovias Fase II
