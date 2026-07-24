# S1-V6 ROADMAP EXECUTIVO — GUIA DE IMPLEMENTAÇÃO
**MNT-2026-S1-SEISMIC-RESILIENCE | Versão Ação 1.0**

---

## ⚡ SEMANA 1–2: KICKOFF (24 JUL – 6 AGO 2026)

### Tarefas Imediatas (próximos 10 dias)

- [ ] **Enviar RFC a MN + C-level** (hoje)
  - Anexar: S1-SEISMIC-EVOLUTION-EXECUTIVE-SUMMARY.md
  - Tom: "Proposta de evolução S1; alinhada com Jericó 2024; timeline 12 meses"
  - SLA decisão: 5 dias

- [ ] **Agendar almoço / reunião com Agente-05 lead** (48h)
  - Pauta: SICRO adaptado (itens sísmicos não existentes)
  - Precisamos: Composições CBUQ elástico, geotêxtil reforçado, dreno sísmico
  - Sair com: Lista de 5–10 itens a criar / adaptar

- [ ] **Contatiar especialistas (email / call)**
  - [ ] UFOP Ouro Preto: Contato geotecnia/sísmica → dados Jericó
  - [ ] CPRM (Serviço Geológico): Mapas PGA, relatório Jericó
  - [ ] Defesa Civil Minas Gerais: Relatório damages Jericó
  - [ ] USP / COPPE UFRJ: Papers liquefação Brasil
  - **Prazo resposta**: 1–2 semanas

- [ ] **Setup repositório**
  ```bash
  cd /home/user/Codex-exemplo
  git checkout -b feat/s1-seismic-v2
  mkdir -p docs/s1-seismic-v2/{1-knowledge,2-algorithms,3-tests,4-cases}
  git add .
  git commit -m "Initial structure for S1 V6 Seismic Evolution"
  ```

- [ ] **Criar doc compartilhado no SharePoint**
  - Pasta: `Documentos Compartilhados/04_IA/Projetos-Ativos/S1-SEISMIC-2026/`
  - Conteúdo: Roadmap, status semanal, links, contacts
  - Compartilhar com: MN, Arquiteto-ia, Agente-05 lead, BD

---

## 📚 SPRINT 1 (7–30 AGO 2026): KNOWLEDGE INTAKE

### Objetivo
Coletar, catalogar e ingerir toda documentação símica/geotécnica necessária.

### Deliverables

#### 1. Coleção de Normas (Documents)

```
📁 docs/s1-seismic-v2/1-knowledge/normas/
├─ ISO-14383-1-2016.pdf (ou resumo executivo)
├─ ASCE-7-22-seismic-section.pdf
├─ Eurocode-8-EN1998-1.pdf (resumo)
├─ NBR-8681-2003.pdf
├─ NBR-15421-2006.pdf
├─ USGS-Global-Seismic-Hazard-Map.pdf
└─ DNIT-PRO-Sísmica-Proposto.docx (criar esboço)
```

- [ ] Coletar ISO 14383 (via biblioteca digital Manta ou ABNT)
- [ ] Download ASCE 7-22 (open access via ASCE library)
- [ ] PDF USGS PGA map (https://earthquake.usgs.gov/earthquakes/events/2016chileseismic/neic2016slap/models/)
- [ ] Contato DNIT: Propor ES-Sísmica (email a setor de engenharia)
- [ ] **Deadline**: 15 AGO

#### 2. Papers Científicos (Repositório Local)

```
📁 docs/s1-seismic-v2/1-knowledge/papers/
├─ Tokimatsu-Yoshida-1983-Liquefaction-Susceptibility.pdf
├─ Youd-et-al-2001-Liquefaction-Resistance.pdf
├─ Newmark-1965-Effects-Earthquakes-Embankments.pdf
├─ Imai-Tonouchi-1982-Vs30-Correlation.pdf
├─ Kramer-1996-Geotechnical-Earthquake-Engineering.pdf
├─ Boore-2004-Vs-Correlation-USA.pdf
├─ Okada-2003-Vs-Japan.pdf
└─ Younes-Method-Permanent-Strain.pdf
```

- [ ] Buscar via Google Scholar, ResearchGate, SSRN
- [ ] Solicitar cópias a universidades parceiras (UFOP, COPPE)
- [ ] Montar pasta local com índice (BibTeX)
- [ ] **Deadline**: 20 AGO

#### 3. Dados Regionais — Jericó 2024

```
📁 docs/s1-seismic-v2/1-knowledge/jerico-2024/
├─ CPRM-Relatorio-Jerico-Sismo-2024.pdf
├─ Defesa-Civil-MG-Damages-Report.pdf
├─ Acelerograma-Jerico-Estacao-IPOC.txt (ou gráfico)
├─ Mapa-Geologia-Jerico.pdf (fonte: CPRM)
├─ Sondagens-SPT-Entorno-Jerico.xlsx (compilar de projetos)
├─ Fotos-Pre-Pos-Evento.zip
└─ Estimativa-LI-Jerico-Preliminary.xls
```

- [ ] Solicitar a CPRM (Serviço Geológico do Brasil)
- [ ] Contatar Defesa Civil MG
- [ ] Buscar acelerograma via IPOC (Integrated Plate Boundary Observatory Andes)
- [ ] Compilar SPT de projetos viários históricos próximos
- [ ] **Deadline**: 25 AGO

#### 4. Mapas USGS & Zoneamento Sísmico Brasil

```
📁 docs/s1-seismic-v2/1-knowledge/usgs-maps/
├─ USGS-Global-Hazard-Map-0p01g.tif (ou PNG)
├─ Brazil-PGA-0.10-Overlay.png
├─ Jerico-PGA-Contours.shp (shapefile)
├─ Ceara-Sismicidade-Historica.pdf
├─ Espirito-Santo-Zonas-Risco.pdf
└─ USGS-Hazard-Curve-Jerico.csv
```

- [ ] Download via https://earthquake.usgs.gov
- [ ] Converter para GIS (QGIS) + gerar contornos Brasil
- [ ] Compilar curvas hazard para 10 cidades-chave
- [ ] **Deadline**: 28 AGO

#### 5. Matriz de Conhecimento RAG (Indexação)

Criar documento estruturado:

```
📄 docs/s1-seismic-v2/1-knowledge/RAG-INDEX.xlsx

| Tipo | Assunto | Arquivo | Tags | Prioridade | Status |
|------|---------|---------|------|------------|--------|
| Norma | Liquefação | Tokimatsu-1983 | liq, spт | P1 | ✅ Coletado |
| Norma | Design Sísmico | ISO-14383 | design, norm | P1 | ✅ Coletado |
| Mapa | Jericó PGA | USGS-Hazard-Jerico | pga, jerico, zo | P1 | ✅ Coletado |
| ... | ... | ... | ... | ... | ... |
```

- [ ] Indexar 50+ documentos
- [ ] Criar tags padronizadas (`pga`, `liq`, `newmark`, `design`, `jerico`, etc.)
- [ ] **Deadline**: 30 AGO

---

## 🧮 SPRINT 2 (1–30 SET 2026): ESTRUTURA & ALGORITMOS INICIAIS

### Objetivo
Definir arquitetura V6, criar módulos D6.1–D6.2, implementar calculadoras.

### Deliverables

#### 1. Arquitetura V6 Formal

```markdown
📄 .claude/agents/agente-infraestrutura-S1-v2.md

# MANTA 03-S1 v2.0 — RODOVIAS + SÍSMICA & RESILIÊNCIA

## Vertentes (6 total)
- V1: Análise Técnica & Risco (existente)
- V2: Inteligência DNIT (existente)
- V3: Gestão de Obra (existente)
- V4: Document Intelligence (existente)
- V5: Pavimento & Terraplenagem (existente)
- V6: SÍSMICA & RESILIÊNCIA (NOVO)

## V6 Disciplinas (6 total — D6.1 a D6.6)
[detalhado conforme S1-GEOTECNIA-GEOLOGIA-EXPANSION.md]
```

- [ ] Escrever markdown formalizado
- [ ] Diagrama de fluxo (Mermaid)
- [ ] Tabela de módulos com linhas de responsabilidade
- [ ] **Deadline**: 10 SET

#### 2. Módulos D6.1 — Zoneamento Sísmico

```markdown
📄 docs/s1-seismic-v2/2-algorithms/D6.1-Zoneamento-Sismico.md

### 6.1.1 Mapa USGS & Classificação PGA
### 6.1.2 Espectro de Resposta (Sa, Sd, Sv)
### 6.1.3 Amplificação de Sítio (Vs30, Fa, Fv)
### 6.1.4 Normas Adaptadas Brasil
```

Conteúdo:
- Fórmulas de cálculo (em pseudocódigo Python)
- Tabelas de lookup (PGA × região)
- Exemplos numéricos (Jericó, Ceará, ES)
- Limites & disclaimers

- [ ] Escrever 4 sub-módulos (~500 linhas cada)
- [ ] Criar tabelas PGA Brasil (12 zonas)
- [ ] Validar com USGS data points
- [ ] **Deadline**: 15 SET

#### 3. Módulos D6.2 — Liquefação

```markdown
📄 docs/s1-seismic-v2/2-algorithms/D6.2-Liquefacao.md

### 6.2.1 Caracterização Geológica
### 6.2.2 Propriedades Dinâmicas
### 6.2.3 Índice de Liquefação (Tokimatsu v2)
### 6.2.4 Amplificação de Sítio
### 6.2.5 Remediação Geotécnica
```

- [ ] Escrever fórmulas Tokimatsu (com correções SPT)
- [ ] Criar tabela remediação (LI × FS → técnica + custo)
- [ ] Casos Jericó, Ceará, ES
- [ ] **Deadline**: 20 SET

#### 4. Calculadora PGA (Python/JS)

```python
# docs/s1-seismic-v2/2-algorithms/calculator-pga.py

def get_pga_usgs(latitude, longitude):
    """Query USGS API or lookup table → PGA (g)"""
    # Chamada USGS ou fallback tabela Brasil
    return pga_value, confidence_interval

def classify_sismicity(pga):
    """PGA → Classificação (baixo/moderado/alto/muito alto)"""
    if pga < 0.06: return "Baixo"
    elif pga < 0.12: return "Moderado"
    elif pga < 0.20: return "Alto"
    else: return "Muito Alto"

def amplification_factor(vs30):
    """Vs30 (m/s) → Fa, Fv (NEHRP)"""
    # Retorna tabela NEHRP
    return fa, fv
```

- [ ] Implementar API USGS (rate-limited)
- [ ] Fallback tabela local Brasil
- [ ] Testes unitários (100 pontos lat/lon aleatórios)
- [ ] **Deadline**: 25 SET

#### 5. Calculadora LI (Python/JS)

```python
# docs/s1-seismic-v2/2-algorithms/calculator-li.py

def calculate_li_tokimatsu(spt_n, depth, pga, mw=5.0):
    """
    SPT (N) → Liquefaction Index (Tokimatsu & Yoshida, 1983)
    
    Input:
      spt_n: SPT N value (golpes)
      depth: Profundidade (m)
      pga: Aceleração pico (g)
      mw: Magnitude sísmica (padrão 5.0)
    
    Output:
      li: Índice liquefação (0–1)
      risk: Classificação (baixo/moderado/alto/muito alto)
    """
    # Correção SPT → (N1)60_cs
    n1_60_cs = spt_correction(spt_n, depth)
    
    # Fator magnitude
    fl = magnitude_factor(mw)  # ~1.0 para Mw=5
    
    # Fórmula Tokimatsu
    li = fl * ((n1_60_cs + 37.3) / 37.3) ** -3.6
    
    # Classificação risco
    if li < 0.1: risk = "Baixo"
    elif li < 0.3: risk = "Moderado"
    elif li < 0.7: risk = "Alto"
    else: risk = "Muito Alto"
    
    return {"li": li, "risk": risk, "n1_60_cs": n1_60_cs}
```

- [ ] Implementar correções SPT (N60, profundidade, stress)
- [ ] Testes vs literatura (50 casos)
- [ ] ≥ 90% acurácia vs benchmarks
- [ ] **Deadline**: 28 SET

#### 6. Intake Q5 — Contexto Sísmico

Estender prompt S1:

```markdown
Q5: Contexto sísmico? (NOVO)

[ ] Baixo risco (PGA < 0.06 g)
    → Fluxo convencional S1 (V1–V5)

[ ] Moderado risco (0.06 < PGA < 0.12 g)
    → Ativa D6.1 (zoneamento) + D6.2 (liquefação básico)

[ ] Alto risco (0.12 < PGA < 0.20 g)
    → Ativa D6.1 + D6.2 + D6.3 (Newmark)

[ ] Muito alto (PGA > 0.20 g)
    → Ativa V6 completo + flag "handoff geotécnico recomendado"

[ ] Incerto (não sei)
    → ATIVA D6.1 automaticamente (lat/lon → USGS)
```

- [ ] Implementar routing condicional
- [ ] Testar com 10 casos (diferentes regiões)
- [ ] **Deadline**: 30 SET

---

## 🧪 SPRINT 3 (1–31 OUT 2026): ANÁLISE & DESIGN RESILIENTE

### Objetivo
Implementar D6.3–D6.4 (Newmark, design resiliente); integrar com V1.

### Deliverables

#### 1. Módulos D6.3 — Estabilidade Sísmica Taludes

```markdown
📄 docs/s1-seismic-v2/2-algorithms/D6.3-Estabilidade-Sismica.md

### 6.3.1 Newmark — Deformação Permanente
### 6.3.2 Coeficiente Sísmico
### 6.3.3 Monitoramento Pós-Evento
### 6.3.4 Casos Jericó
```

- [ ] Escrever fórmula Newmark (método sliding block)
- [ ] Integração com cálculo FS (Bishop/Spencer existente)
- [ ] Exemplos numéricos (3+ taludes)
- [ ] **Deadline**: 10 OUT

#### 2. Calculadora Newmark (Python)

```python
# docs/s1-seismic-v2/2-algorithms/calculator-newmark.py

def calculate_critical_acceleration(phi_degrees, beta_degrees, fs_static):
    """Aceleração crítica para deslizamento (sliding block)"""
    phi_rad = math.radians(phi_degrees)
    beta_rad = math.radians(beta_degrees)
    ac = (fs_static - 1) * 9.81 * math.tan(phi_rad)
    return ac

def calculate_permanent_deformation(acelerograma, ac_critical, dt=0.01):
    """Integração acelerograma → deformação permanente"""
    displacement = 0
    for i, a in enumerate(acelerograma):
        if a > ac_critical:
            # Integração dupla: v += (a - ac) × dt; x += v × dt
            pass
    return displacement
```

- [ ] Testes vs. benchmarks (15+ casos)
- [ ] Validação contra programa Newmark clássico (se disponível)
- [ ] **Deadline**: 15 OUT

#### 3. Módulos D6.4 — Design Resiliente

```markdown
📄 docs/s1-seismic-v2/2-algorithms/D6.4-Design-Resiliente.md

### 6.4.1 Pavimento Resiliente
### 6.4.2 Reforço Taludes
### 6.4.3 Muro Dinâmico
### 6.4.4 Barreira com Amortecedor
### 6.4.5 Drenagem Resiliente
### 6.4.6 Junta de Dilatação Sísmica
```

Conteúdo:
- Especificações técnicas (dimensões, materiais, camadas)
- Fatores de design (f = 1.0–1.3 baseado em PGA)
- Custo estimado por componente
- Casos de aplicação

- [ ] Escrever 6 sub-módulos (~400 linhas cada)
- [ ] Criar matriz tipologia × design factor
- [ ] **Deadline**: 25 OUT

#### 4. Artefato React — Novas Abas (Prototipo)

Adicionar ao artefato S1:

```jsx
// Abas novas:
<Tab label="Zoneamento Sísmico">
  <PGAMap lat={...} lon={...} pga={...} />
  <AmplificationTable vs30={...} />
</Tab>

<Tab label="Análise Liquefação">
  <LICalculator spt={...} />
  <RemediationMatrix />
</Tab>

<Tab label="Estabilidade Sísmica">
  <NewmarkChart acelerograma={...} />
  <DisplacementResult />
</Tab>

<Tab label="Design Resiliente">
  <ComponentSelector />
  <SpecificationTable />
</Tab>

<Tab label="Custeamento">
  <CostMatrix />
</Tab>
```

- [ ] Protótipo figma (ou mockup React)
- [ ] Testar com dados Jericó
- [ ] **Deadline**: 31 OUT

---

## 💰 SPRINT 4 (1–30 NOV 2026): CUSTEAMENTO & HANDOFF

### Objetivo
D6.5 (custos pós-desastre); handoff integrado agente-05.

### Deliverables

#### 1. Módulo D6.5 — Custeamento

```markdown
📄 docs/s1-seismic-v2/2-algorithms/D6.5-Custeamento-Pos-Desastre.md

### 6.5.1 SICRO Adaptado (Itens sísmicos)
### 6.5.2 Matriz de Custos (Emergencial vs Redesign)
### 6.5.3 Tempo de Retorno de Serviço (TRS)
### 6.5.4 Financiamento (FUNDO, BNDES, Seguros)
```

Conteúdo:
- SICRO items mapping (ex. CBUQ → CBUQ elástico = +15%)
- Tabela custos por remediação (dreno = 1.5x; substituição = 5.0x)
- Timeline restauração (desobstrução, estabilização, reparo)
- Programas de subsídio (pós-desastre)

- [ ] Compilar com agente-05: 20+ itens SICRO sísmico
- [ ] Criar lookup table custos (vs. convencional)
- [ ] Exemplo Jericó: reparo imediato vs. redesign (comparar VPL)
- [ ] **Deadline**: 15 NOV

#### 2. Handoff Agente-05 (Integração)

Criar interface:

```python
# Quando D6.5 ativa:
if user_context_seismic == "Alto":
    components_resilient = {
        "pavimento": "CBUQ_elastico_EBA",
        "base": "BGS_reforco_geotextil",
        "drenagem": "dreno_frances_seismic",
        "barreira": "defensa_com_amortecedor"
    }
    
    # Chamar agente-05:
    custo_adaptado = agente05.calcular_orcamento(
        componentes=components_resilient,
        regime_emergencial=True  # Se pós-desastre
    )
```

- [ ] Definir contrato API agente-05
- [ ] Testes mock (10 cenários)
- [ ] Validar output (custo deve ser 1.2–3.0x vs. convencional)
- [ ] **Deadline**: 30 NOV

---

## 📖 SPRINT 5 (1–31 DEZ 2026): CASOS & VALIDAÇÃO

### Objetivo
Banco de casos sísmicos documentados; validação contra realidade.

### Deliverables

#### 1. Caso Jericó 2024 — Detalhado

```markdown
📄 docs/s1-seismic-v2/3-tests/case-jerico-2024.md

# Estudo de Caso: Jericó 2024

## Dados Básicos
- Local: Estrada MG-120, Jericó/MG
- Evento: Sismo Mw 5.0 (2024-01-01)
- PGA: 0.18–0.20 g

## Análise S1-V6
- [ ] Zoneamento: Alto risco → LI esperado 0.25–0.45
- [ ] Liquefação: SPT (2–4 m, SM) → LI = 0.32
- [ ] Newmark: Δ perm ≈ 0.28 m → Risco moderado
- [ ] Design: Recomenda dreno + reforço geotêxtil
- [ ] Custo: Dreno 1.5x + reforço 1.2x = 1.8x total

## Validação vs. Realidade
- Observado: Pequenas fissuras, sem ruptura
- Predito: LI moderado, assentamento 5–10 cm
- Análise: [Investigar divergência]

## Lições
1. Incerteza em PGA pós-evento → necessário acelerograma real
2. Duração sísmica importante (PGA pico vs. PGA contínuo)
3. Próximas estruturas: Recomenda dreno preventivo
```

- [ ] Compilar dados reais (CPRM, Defesa Civil)
- [ ] Rodar S1-V6 contra caso
- [ ] Documentar previsões vs. observado
- [ ] **Deadline**: 10 DEZ

#### 2. Casos Ceará e Espírito Santo

Análogas a Jericó:

```markdown
📄 docs/s1-seismic-v2/3-tests/case-ceara.md
📄 docs/s1-seismic-v2/3-tests/case-espirito-santo.md
```

- [ ] Cada caso ~500 linhas (dados + análise + lições)
- [ ] Mínimo 5 casos para credibilidade
- [ ] **Deadline**: 20 DEZ

#### 3. Testes de Routing Q3 (30+ cenários)

```
Cenário 1: Usuário entra com lat/lon Jericó, sem Q3
→ Sistema deteta USGS PGA = 0.18 g → Auto-classifica "Alto"
→ Ativa V6 completo

Cenário 2: Talude em SP, Q3 = "Baixo"
→ Ativa D6.1 apenas (zoneamento educacional)
→ Não ativa remediação

Cenário 3: Areia úmida em Ceará, SPT N=6, incerto Q3
→ Deteta "arenoso + saturado" → Flag "Alto potencial liquefação"
→ Recomenda investigação antes redesign
```

- [ ] Criar matriz 30 casos (5 regiões × 6 cenários)
- [ ] Rodar routing; validar output
- [ ] Target: ≥ 90% acerto
- [ ] **Deadline**: 31 DEZ

---

## 🧪 SPRINT 6 (1–31 JAN 2027): INTEGRAÇÃO & UAT

### Objetivo
Testes integrados com agente-05/07/advisory; feedback usuários piloto.

### Deliverables

#### 1. Testes End-to-End (E2E) — 20 cenários

```
Cenário E2E 1: Jericó → D6.1 (PGA ok) → D6.2 (LI ok) → D6.3 (Newmark ok) 
               → D6.4 (recomendação ok) → D6.5 (custo via agente-05 ok)
               RESULTADO: ✅ Pass

Cenário E2E 2: Talude em Ceará + SPT → LI = 0.42 → Recomenda densificação
               → Agente-05 retorna SICRO "dynamic compaction"
               → Agente-07 timeline restauração 4 semanas
               RESULTADO: ✅ Pass

[... 18 mais ...]
```

- [ ] Executar 20 E2E tests
- [ ] Target: ≥ 95% pass rate
- [ ] Documentar failures e causas
- [ ] **Deadline**: 20 JAN

#### 2. Piloto com 3 Usuários

Selecionar:
1. Engenheiro civil (rodovias) — valida engenharia
2. Gerente de projeto — valida usabilidade
3. Consultor geotecnia — valida lógica sísmica

Fluxo:
- [ ] Treinamento S1-V6 (2h)
- [ ] 5 casos de teste (diferentes contextos)
- [ ] Feedback NPS, bug reports
- [ ] Iteração (bugs críticos = fix rápido)
- [ ] **Deadline**: 31 JAN

---

## ✍️ SPRINT 7 (1–28 FEV 2027): DOCUMENTAÇÃO FINAL

### Objective
Documentação completa, prompts de teste, SKILL.md estendido.

### Deliverables

#### 1. SKILL.md Estendido (V1–V6)

```markdown
# agente-infraestrutura-S1 — SKILL.md v2.0

## CAPACIDADES

### V1–V5 (Existente) [200 linhas]
...

### V6 — SÍSMICA & RESILIÊNCIA (NOVO) [300 linhas]

#### D6.1 Zoneamento Sísmico
- Entrada: Localização (lat/lon) ou projeto (arquivo DWG)
- Saída: Mapa PGA, classificação risco, espectro resposta
- Exemplo: "Análise sísmica para rodovia em Jericó"
- **Custo token**: ~800 (USGS lookup + tabela)

#### D6.2 Liquefação
- Entrada: SPT, profundidade, contexto geológico
- Saída: LI index, classificação risco, remediação recomendada
- Exemplo: "Estou com talude em solo arenoso saturado, como está liquefação?"
- **Custo token**: ~600

[... D6.3–D6.6 ...]

## ROUTING ESTENDIDO

Q3 (NOVO): Contexto sísmico?
├─ Baixo → V1–V5
├─ Moderado → D6.1 + D6.2 básico
├─ Alto → D6.1 + D6.2 + D6.3
└─ Incerto → Auto-detecção USGS

## HANDOFFS
- agente-05: Custeamento resiliente (D6.5)
- agente-07: Timeline restauração (D6.5)
- agente-advisory: VPL/TIR redesign (pós-desastre)

## EXEMPLOS DE PROMPTS

1. "Analisar estabilidade sísmica para talude em Jericó com SPT N=8 (2–4m)"
2. "Quanto custa redesenhar rodovia com componentes sísmicos em zona de risco?"
3. "Qual é o tempo de retorno de serviço pós-desastre para pavimento?"

## LIMITAÇÕES & DISCLAIMERS
- Análise D6.2–D6.3 é preliminar; designs sísmicos executivos requerem agente geotécnico
- USGS PGA é 10k-year probability; eventos reais podem diferir
- SICRO ainda não tem items sísmicos oficiais (usando composições Manta)
```

- [ ] Escrever SKILL.md v2.0 (~600 linhas)
- [ ] Incluir exemplos de prompt (10+)
- [ ] **Deadline**: 14 FEV

#### 2. README & Arquitetura

```markdown
📄 docs/s1-seismic-v2/README.md
📄 docs/s1-seismic-v2/ARQUITETURA-S1-V6.md
```

- [ ] README: Contexto, timeline, links
- [ ] ARQUITETURA: Diagramas, módulos, handoffs
- [ ] **Deadline**: 21 FEV

#### 3. Prompts de Teste (Routing)

```python
# docs/s1-seismic-v2/3-tests/prompts-s1-seismic.yaml

test_cases:
  - name: "jerico-talude"
    prompt: "Talude em Jericó (MG), inclinação 30°, SPT N=8 (2–4m solo arenoso saturado)"
    expected_output: "LI=0.32, risco moderado, recomenda dreno"
    
  - name: "ceara-liquefacao-alta"
    prompt: "Rodovia em Quixeramobim (CE), solo arenoso, NPT=0.8m. Qual LI?"
    expected_output: "LI≈0.40–0.45, risco alto, avaliar densificação"
    
  [... 28 mais ...]

target_pass_rate: 0.90
```

- [ ] 30+ test cases (cobrindo routing Q1–Q5)
- [ ] Automação teste (CI/CD)
- [ ] **Deadline**: 28 FEV

---

## 🚀 SPRINT 8 (1–30 JUN 2027): DEPLOY & GO-LIVE

### Objetivo
Merge produção, RAG deploy, go-live monitorado.

### Deliverables

#### 1. PRs & Code Review

- [ ] PR #1: .claude/agents/agente-infraestrutura-S1-v2.md (agent definition)
- [ ] PR #2: D6.1–D6.6 modules + calculators (core algorithms)
- [ ] PR #3: Artefato React novas abas (UI)
- [ ] PR #4: SKILL.md estendido + prompts (documentation)
- [ ] PR #5: Testes unitários + E2E (test suite)

Target: ≥ 95% code review approval rate

#### 2. RAG Deploy (Supabase)

```sql
-- docs/s1-seismic-v2/4-deploy/supabase-migration-s1-seismic.sql

INSERT INTO rag_chunks (prefix, title, content, tags, version)
VALUES 
  ('rod:seism:norm', 'ISO 14383-1:2016', '...', ['norm', 'design'], 'v2.0'),
  ('rod:seism:pga', 'USGS Hazard Brazil', '...', ['pga', 'map'], 'v2.0'),
  ('rod:seism:liq', 'Tokimatsu & Yoshida', '...', ['liq', 'formula'], 'v2.0'),
  ...
```

- [ ] 8 sub-collections criadas (rod:seism:norm, pga, liq, ana, des, cost, case, geo)
- [ ] 100+ chunks indexados
- [ ] Tested em staging
- [ ] **Deadline**: 15 JUN

#### 3. SharePoint Deploy

```
Documentos Compartilhados/01-agentes-fundamentais/agente-infraestrutura-S1/
├── SKILL.md (v2.0 estendido)
├── README.md
├── ARQUITETURA-S1-V6.md
├── refs/ (normas, papers, mapas compilados)
└── prompts/ (exemplos routing Q1–Q5)
```

- [ ] Upload documents (via SharePoint MCP ou manual)
- [ ] Compartilhar com equipes-chave (BD, advisory, clientes)
- [ ] **Deadline**: 20 JUN

#### 4. Go-Live Monitorado (Canário)

```
Fase 1 (Semana 1): Canário 10% usuários (3 piloto + MN + Arquiteto)
Fase 2 (Semana 2): Canário 50% usuários
Fase 3 (Semana 3): 100% (se KPIs verdes)

Monitores:
- Taxa erro (target: <1%)
- Latência API USGS (target: <2s)
- Handoff agente-05 sucesso (target: >95%)
- Feedback usuário (NPS target: >40)
```

- [ ] Setup monitoring (dashboards Grafana ou Datadog)
- [ ] Plano rollback (feature flag)
- [ ] On-call suporte (1º mês)
- [ ] **Deadline**: 30 JUN

---

## 📊 MACRO-TIMELINE (VISUAL)

```
2026
JUL    |  AGO   |  SET   |  OUT   |  NOV   |  DEZ
Kick   | S1:Know| S2:Algo| S3:Anal| S4:Cost| S5:Case
off    | intake | D6.1/2 | D6.3/4 | D6.5   | validate
       |        | calc   |        | handoff| test
|------|--------|--------|--------|--------|--------|

2027
JAN    |  FEV   |  MAR   |  ABR   |  MAI   |  JUN
S6:UAT | S7:Docs| S8:Prep| S8:Deploy (canário)
pilot  | SKILL  | Supabase| Phase 1-3 go-live
       | final  | RAG    |        |        | 🎯 LIVE
|------|--------|--------|--------|--------|--------|
```

---

## 📋 CHECKLIST FINAL (PRÉ-GO-LIVE)

- [ ] RFC aprovado por MN
- [ ] 100% sprints 1–7 completos
- [ ] ≥95% testes passando (unit + E2E)
- [ ] ≥90% routing Q1–Q5 acertos
- [ ] UAT piloto NPS ≥40
- [ ] Handoff agente-05 funcional
- [ ] RAG collections (rod:seism:*) indexadas
- [ ] SKILL.md publicado SP
- [ ] Documentação 100% (README, ARQUITETURA, casos)
- [ ] Code review aprovado (todas PRs)
- [ ] Monitoramento configurado (dashboards)
- [ ] Plano rollback pronto
- [ ] Suporte on-call escalado (1º mês)
- [ ] ✅ MN gate: Aprovação final

---

## 💬 PRÓXIMOS PASSOS (HOJE)

### ✅ Fazer Agora

1. **Email RFC a MN** (15 min)
   ```
   Assunto: RFC — Evolução Agente-infraestrutura S1 com Sísmica & Resiliência
   Anexar: S1-SEISMIC-EVOLUTION-EXECUTIVE-SUMMARY.md
   Solicitar: Aprovação para começar Sprint 1 (7 AGO)
   ```

2. **Criar branch feat/s1-seismic-v2** (5 min)
   ```bash
   cd /home/user/Codex-exemplo
   git checkout -b feat/s1-seismic-v2
   mkdir -p docs/s1-seismic-v2/{1-knowledge,2-algorithms,3-tests,4-deploy}
   git add .
   git commit -m "Initialize S1 V6 Seismic Evolution structure"
   git push -u origin feat/s1-seismic-v2
   ```

3. **Agendar reunião Agente-05 lead** (email 48h)
   ```
   Assunto: Almoço — SICRO adaptado para rodovias sísmicas
   Data: Próxima semana
   Duração: 1h
   Pauta: CBUQ elástico, geotêxtil sísmico, drenagem resiliente
   ```

4. **Criar SharePoint folder** (10 min)
   ```
   Caminho: Documentos Compartilhados/04_IA/Projetos-Ativos/S1-SEISMIC-2026/
   Conteúdo: Roadmap, status semanal, links
   Compartilhar com: MN, arquiteto-ia, agente-05, BD
   ```

### ⏰ Fazer Esta Semana

- [ ] Receber aprovação RFC (MN)
- [ ] Contatar especialistas (UFOP, CPRM, Defesa Civil, IPOC)
- [ ] Coletar papers-chave (Tokimatsu, Youd, Newmark)
- [ ] Download USGS maps + dados Jericó
- [ ] Primeira reunião com agente-05

### 📅 Semana Entrante (7 AGO)

- [ ] **SPRINT 1 KICKOFF**
- [ ] Iniciar knowledge intake
- [ ] Primeira daily standup (equipe S1)

---

## 📞 STAKEHOLDERS & SPONSORSHIP

| Role | Name | Email | Função |
|------|------|-------|--------|
| **Sponsor** | MN | mn@manta.com.br | Aprovação gate |
| **Tech Lead** | Arquiteto-ia | arquiteto@manta.com.br | Design V6 |
| **Product Owner** | BD Lead | bd@manta.com.br | Market feedback |
| **Agente-05 Liaison** | Orçamento | orcamento@manta.com.br | SICRO adaptado |
| **QA/Piloto 1** | Eng. Civil | [name] | Validação técnica |
| **QA/Piloto 2** | Gerente Projeto | [name] | Usabilidade |
| **QA/Piloto 3** | Consultor Geotec | [name] | Lógica sísmica |

---

## 🎯 RESUMO EXECUTIVO

**Manta 03-S1 evoluirá para agente de referência em rodovias resilientes,** com:

✅ **12 meses de desenvolvimento** (Q3 2026 → Q2 2027)  
✅ **8 sprints estruturados** (conhecimento, algoritmos, design, custeamento, casos, integração, docs, deploy)  
✅ **6 disciplinas sísmicas** (D6.1–D6.6, 23 módulos)  
✅ **3 calculadoras críticas** (PGA, LI, Newmark)  
✅ **Integração sistêmica** (handoff agente-05/07/advisory)  
✅ **Validação contra realidade** (casos Jericó, Ceará, ES)  

**Resultado Q2 2027**: Agente-infraestrutura S1 v2.0 operacional, com V6 sísmica & resiliência 🚀

---

**Documento**: MNT-2026-S1-SEISMIC-EVOLUTION — Roadmap Executivo  
**Versão**: 1.0 (Ação)  
**Data**: 2026-07-24  
**Status**: 📋 Pronto para Kickoff — *Aguardando aprovação RFC*
