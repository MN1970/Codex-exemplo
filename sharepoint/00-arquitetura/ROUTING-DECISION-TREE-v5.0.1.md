# Maestro Routing Decision Tree — v5.0.1 LIVE

**Versão:** 5.0.1 (2026-08-02)  
**Status:** 17 agentes operacionais  
**Última atualização:** 2026-08-02

---

## Como o Maestro Roteia (Intake Q1)

Quando um usuário entra com uma pergunta, o **Maestro** (Manta 00) faz triagem automática por **pattern matching** em palavras-chave. Este documento mostra a árvore de decisão completa.

---

## 1. FLUXO PRINCIPAL — Intake Q1

```
┌─────────────────────────────────────────────────────┐
│ Entrada: Pergunta do usuário                        │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │ Análise de menção   │
        │ (keywords)          │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────────────────────┐
        │ Segmento detectado? (S1–S10)         │
        │ (Ou horizontal se não houver)        │
        └──────────┬──────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
   SIM            NÃO             │
    │              │              │
    │         Horizontal?     Ambíguo?
    │              │              │
    ▼              ▼              ▼
 Vertical      Horizontal    Multi-agente
 (S1-S10)      (Manta 1-16)   (handoff)
```

---

## 2. AGENTES VERTICAIS (S1-S10) — KEYWORDS MAPEADAS

### 🏗️ S1 — Rodovias (agente-infraestrutura S1)

**Palavras-chave:**
- rodovia, rodovia federal, rodovia estadual, estrada
- pavimento, pavimentação, asfalto, CBUQ, BGS, macadame
- base, sub-base, terraplenagem, aterro
- DNIT, DNER, SICRO, SNVP, PRU
- SAT, PER, pavimento rígido, concreto (rodovia)
- drenagem (rodovia), canaleta, descida d'água
- caixa de ligação, sarjeta, bueiro

**Exemplo:** "Qual é a vida útil de CBUQ em clima tropical?" → **agente-infraestrutura S1**

---

### 🌉 S2 — OAE (agente-infraestrutura S2) + S5 (Túneis)

**Palavras-chave:**
- ponte, viaduto, passarela, OAE (Obra de Arte Especial)
- fundação, estaca, tubulão, sapata
- estrutura de concreto, estrutura metálica, estrutura mista
- NBR 7187 (projeto), NBR 6118 (concreto), NBR 8800 (aço)
- pilar, encontro, laje, tabuleiro, doca
- aparelhos de apoio, junta de dilatação, algeroz
- inspeção, manutenção, reforço estrutural

**Exemplo:** "Como dimensionar uma ponte em CFRD?" → **agente-infraestrutura S2** (estrutura do tabuleiro)

**Túneis** (S5):
- túnel, galeria, sistema de ventilação, iluminação
- NATM (New Austrian Tunnelling Method), suporte provisório
- revestimento definitivo, impermeabilização
- túnel rodoviário, túnel ferroviário, túnel de metrô
- → Encaminha para **agente-infraestrutura S2** ou **S4** conforme contexto

---

### 🚂 S3 — Ferrovia (agente-infraestrutura S3)

**Palavras-chave:**
- ferrovia, via permanente, trilho, dormente, lastro, pátio ferroviário
- AMV (aparelho de mudança de via), agulha
- estação ferroviária, pátio de classificação
- transporte ferroviário, carga, passageiro, ramal
- ABNT NBR 8277 (geometria), ABNT NBR ISO 6954 (trilho)
- DNIT ferroviário, ALL, Rumo, MRS Logística
- sinalização (ferrovia), bloqueio, CTC (Centralized Traffic Control)

**Exemplo:** "Qual é o espaçamento máximo entre dormes?" → **agente-infraestrutura S3**

---

### 🚇 S4 — Metrô (agente-infraestrutura S4) + S5 (Túneis em metrô)

**Palavras-chave:**
- metrô, metrô de superficie, VLT (Veículo Leve sobre Trilhos)
- estação (metrô), plataforma, linhas
- NATM (metrô em NATM), STBPP, tuneladora, TBM
- sistema de ventilação (metrô), ar-condicionado
- sinalização (metrô), sistema de controle, automação
- ABNT NBR normas metrô, UITP
- linha L4, linha L5 (exemplos São Paulo), linha 1 (exemplos Brasília)
- PSD (Platform Screen Door), ATO (Automatic Train Operation)
- obras urbanas (metrô), interferências, remanejamentos

**Exemplo:** "Como dimensionar ventilação para estação de metrô profunda?" → **agente-infraestrutura S4**

---

### 🚢 S6 — Portos (agente-portos)

**Palavras-chave:**
- porto, terminal, berço, cais, píer, molhe, quebra-mar
- dragagem, derrocamento, dessilagem
- contêiner, granel sólido (minério), granel líquido (petróleo)
- ANTAQ (Agência Nacional de Transportes Aquáticos)
- calado, capacidade de berço, comprimento de cais, área de pátio
- TUP (Terminal de Uso Privado), TPS (Terminal de Portos Secos)
- retroárea, acesso rodoviário, acesso ferroviário
- PIANC (Permanent International Association of Navigation Congresses)
- ROM (Register of Shipping and Offshore), projeto executivo porto
- hidrosedimentologia (porto), correntes marítimas
- arrendamento portuário, concessão portuária

**Exemplo:** "Qual é o calado máximo para Panamax no Porto de Santos?" → **agente-portos**

---

### ✈️ S7 — Aeroportos (agente-aeroportos)

**Palavras-chave:**
- aeroporto, aeródromo, base aérea
- pista, runway (RWY), taxiway (TWY), via de saída rápida
- TPS (Terminal de Passageiros), TECA (Terminal de Cargas), garagem
- balizamento visual (PAPI, T-VASI), ILS (Instrument Landing System)
- código de referência (ICAO), distância declarada, PCN (Pavement Classification Number)
- ANAC (Agência Nacional de Aviação Civil), RBAC 154 (projeto)
- ICAO Annex 14, FAA Advisory Circulars
- pátio, gates, jetway (ponte de embarque)
- sistema de drenagem (aeroporto), valas, bueiros
- concessão aeroportuária, aviação regional, aviação geral
- distância mínima de obstáculos, zona de proteção

**Exemplo:** "Qual é o espaçamento mínimo entre gates para aeronaves B787?" → **agente-aeroportos**

---

### 💧 S8 — Saneamento (agente-saneamento) ⭐ PRIORIDADE AYSÁ

**Palavras-chave:**
- saneamento, saneamento básico, infraestrutura de água/esgoto
- ETA (Estação de Tratamento de Água), água potável, captação
- adutora, adução, vazão, pressão, golpe de aríete
- ETE (Estação de Tratamento de Esgoto), esgoto, coleta
- esgoto sanitário, esgoto industrial, esgoto misto
- distribuição de água, rede de distribuição, abastecimento
- elevatória, bomba (água), subestação ETA/ETE
- SNIS (Sistema Nacional de Informações sobre Saneamento)
- Lei 14.026/2020, universalização saneamento, metas 2033
- PMSB (Plano Municipal de Saneamento Básico), EVTE saneamento
- AySA (Agua y Saneamientos Argentinos), ERAS (Entidad Reguladora de Agua y Saneamiento, Córdoba)
- ANA (Agência Nacional de Águas), ARSESP, agências estaduais
- drenagem urbana, microdrenagem, macrodrenagem
- resíduos sólidos, coleta, transbordo, aterro sanitário
- NBR 12211-12218 (saneamento), NBR 9648-9651 (esgoto)
- CONAMA 357/430 (qualidade de água, lançamento)
- IWA (International Water Association)
- reúso de água, reúso industrial, PPU (reúso potável planejado)
- UASB, lodo ativado, MBR (Membrane BioReactor), DAF (Dissolved Air Flotation)
- RAP (Relatório de Avaliação Prévia), EEE (Elevatória de Esgotos Sanitários)

**Exemplo:** "Qual é o procedimento de concessão integrada pós-Lei 14.026?" → **agente-saneamento** (prioridade Brasil)  
**Exemplo:** "Como estruturar o projeto de expansão AySA no Riachuelo?" → **agente-saneamento** (prioridade Argentina)

---

### ⚡ S9 — Energia (agente-energia) ⭐ PRIORIDADE ANEEL

**Palavras-chave:**
- energia, eletricidade, setor elétrico, sistema elétrico
- transmissão, LT (linha de transmissão), tronco, subestação
- geração, usina hidrelétrica (UHE), usina eólica, usina solar, PCH, CGH
- distribuição, rede de distribuição, consumidor
- ANEEL (Agência Nacional de Energia Elétrica), R1–R5 (procedimentos)
- EPE (Empresa de Pesquisa Energética), ONS (Operador Nacional), RdN
- PDE (Plano Decenal de Expansão), PDSA, matriz energética
- leilão de transmissão, leilão de geração, ACL, ACR, MRE
- RAP (Relatório de Avaliação Prévia), LT 138/230/345/500/765 kV
- correntes de transmissão (AWG, CAA, ACSR, ATSR, ATSP)
- estruturas de torre (estaiada, aço, concreto, mista)
- fundações, compatibilização RF/MV (radio frequency/microwave)
- IEC 60826 (design loads), IEEE, Standard 605
- descomissionamento, encerramento de LT, aproveitamento de corredor
- reforços de transmissão, bypass de subestação
- integração de fontes renováveis, grid modernization
- subgrupos tarifários (B4, A4, A3, A2, A1)

**Exemplo:** "Qual é o processo de licitação ANEEL para LT 765 kV?" → **agente-energia**

---

### 🏰 S10 — Barragens (agente-barragens)

**Palavras-chave:**
- barragem, vertedouro, tomada de água
- CFRD (Concrete Face Rockfill Dam), CCR (Roller Compacted Concrete), RCC
- terra, enrocamento, alteamento (montante, jusante, linha de centro)
- rejeitos, TSF (Tailings Storage Facility), mineração (rejeitos)
- Lei 12.334/2020, Lei 14.066/2020, SNISB (Sistema Nacional de Informações de Segurança de Barragens)
- CBDB (Conselho Brasileiro de Barragens), ICOLD (International Commission on Large Dams)
- PAE (Plano de Ação de Emergência), PSB (Plano de Segurança de Barragens)
- drenagem interna, filtros, núcleo impermeável
- filtragem de rejeitos, dry stack, pasta, rejeitos espessados
- hidroeletricidade, abastecimento urbano, irrigação
- descomissionamento, descaracterização de barragem, rompimento
- altura, volume, área do reservatório
- hidrologia, vazão de projeto, cheia 1000 anos
- geotecnia (barragem), estabilidade de taludes, permeabilidade
- segurança operacional, inspeção, monitoramento

**Exemplo:** "Qual é a altura máxima para CFRD com drenagem interna?" → **agente-barragens**

---

## 3. AGENTES HORIZONTAIS (MANTA 01-16) — WHEN TO HANDOFF

### Quando Usar Agentes Horizontais (Sem dispatch primário S1-S10)

```
PERGUNTA DO USUÁRIO
        │
        ▼
┌──────────────────────────────┐
│ Tópico de atividade horizontal?    │
│ (contrato, orçamento, cronograma,  │
│  claims, apresentação, advisor)    │
└──────────────────────────────┘
        │
    ┌───┴───┬──────┬────────┬─────────┐
    ▼       ▼      ▼        ▼         ▼
   Claims Claims Contrato Orçamento Crono
(Manta 01) Apex (Manta 02)(Manta 05)(Manta 07)
```

| Atividade | Agente | Quando handoff |
|-----------|--------|---|
| **Claims** | Manta 01 (claims, 02-C) | "Tenho uma reclamação de garantia" / "Pleito de trabalhos adicionais" / "Aditivo por paralisação" |
| **Contrato** | Manta 02 (contratual) | "Como estruturar concessão saneamento?" / "Edital de licitação" / "Cláusula de força maior" |
| **Orçamento** | Manta 05 (orçamento) | "Qual é o SINAPI para tubulação PVC?" / "Composição de custo para dragagem" |
| **Modelagem** | Manta 06 (modelagem) | "Modelo financeiro (VPL, TIR)" / "Análise estrutural" / "Simulação hidráulica (EPANET, SWMM)" |
| **Cronograma** | Manta 07 (cronograma) | "Caminho crítico" / "Sequência de atividades" / "Alocação de recursos" |
| **Imobiliário** | Manta 04 (imobiliário) | "Zoneamento urbano" / "Ocupação do solo" / "Propriedade e terreno" |
| **BD / Negócio** | Manta 13 (BD) | "Pipeline de negócios" / "Identificação de oportunidades" |
| **Apresentação** | Manta 14 (apresentações) | "Montar um deck de pitch" / "Relatório executivo" |
| **Advisory** | Manta 15 (advisory) | "Parecer técnico (segunda opinião)" / "Estratégia de projeto" / "Análise de risco consolidada" |
| **Arquitetura** | Manta 16 (arquiteto-IA) | "Design de orquestração" / "Decisão de arquitetura de sistema" |

---

## 4. CASOS AMBÍGUOS — MULTI-AGENTE (HANDOFF)

Quando a pergunta toca **dois ou mais segmentos** ou **atividades cruzadas**, o Maestro:

1. **Despacha para o segmento primário** (S1-S10 com maior confiança)
2. **Oferece handoff** para agentes secundários (horizontal ou outro vertical)

### 4.1 Casos Reais

| Pergunta | Dispatch Primário | Handoff | Motivo |
|----------|---|---|---|
| "Barragem de rejeitos com hidroeletricidade: como dimensionar?" | agente-barragens (S10) | agente-energia (S9) | Estrutura da barragem = S10; geração + LT = S9 |
| "ETE com subestação elétrica: como dimensionar compatibilidade?" | agente-saneamento (S8) | agente-energia (S9) | Tratamento = S8; alimentação elétrica = S9 |
| "Porto com pista de carga aeroportuária: qual dimensão?" | agente-portos (S6) | agente-aeroportos (S7) | Terminais portuários = S6; pista = S7 |
| "Adutora que atravessa barragem de rejeitos: sequência de obra?" | agente-saneamento (S8) | agente-barragens (S10) | Adução = S8; rejeitos = S10; coordenação = ambos |
| "Claim de trabalhos adicionais por interferências urbanas em saneamento" | agente-saneamento (S8) | agente-claims (Manta 01) | Contexto técnico = S8; processamento claim = Manta 01 |

---

## 5. INTAKE Q2-Q4 (APÓS ROTEAMENTO)

Depois que Maestro roteia para o agente primário, este agente faz triagem adicional:

### Intake Q2: Qual fase do projeto?

```
(A) Estudo prévio / EVTE / Conceitual
(B) Projeto básico
(C) Projeto executivo
(D) Obra em execução
(E) Operação & Manutenção
(F) Concessão / Licitação
(G) Due Diligence / M&A
(H) Encerramento / Descomissionamento
```

### Intake Q3: País / Jurisdição?

```
(BR) Brasil — Lei 14.026 (saneamento), ANEEL (energia), ANTAQ (portos)
(AR) Argentina — AySA (saneamento), ERAS (Santa Fe, Córdoba)
(OT) Outro — Latam, África, Ásia
```

### Intake Q4: Como chegam os dados?

```
(a) DWG/DXF (CAD drawings)
(b) PMSB / estudo prévio / relatório
(c) Resultados analíticos (água/esgoto, qualidade)
(d) Dados de operação (curvas, características)
(e) Indicadores (SNIS, ERAS, ANEEL, ANTAQ)
(f) Múltiplos formatos
```

---

## 6. OBSERVAÇÕES IMPORTANTES

### ❌ Agentes NÃO OPERACIONAIS (Propostos, sem dispatch)

| Segmento | Agente | Status | Quando ativar |
|----------|--------|--------|---|
| S12 | agente-oleo-gas | 🔲 Proposto | Após gate MN (criar RAG, routing keywords, SP) |
| S13 | agente-edificacoes | 🔲 Proposto | Após gate MN (criar RAG, routing keywords, SP) |

**Até aprovação:** Maestro **não consegue despachar** para S12/S13, mesmo que usuário mencione "refinaria" ou "galpão logístico".

### 🆕 Phase 2 — Agentes de Sistema (Não Despacháveis Diretamente)

Estes 5 agentes **trabalham em background**, suportando S1-S10:

| Agent | Role |
|-------|------|
| Heartbeat Service | Monitora saúde dos agentes (5-min checks) |
| RAG Hierarchy | Seleciona coleção correta (san, ene, por, bar, editais) |
| Expert Finder | Rank agentes por confiança (blended scoring) |
| Composition Orchestrator | Orquestra multi-agente (5 padrões canônicos) |
| Observability | Coleta métricas e traces (OpenTelemetry + Jaeger) |

---

## 7. FLUXO COMPLETO — Exemplo Passo a Passo

**Entrada:** "Preciso dimensionar uma ETE com MBR para tratamento terciário pós-Lei 14.026. Como estruturar a concessão?"

**Passo 1 — Maestro Intake Q1:**
- Detecta: "ETE", "Lei 14.026", "concessão"
- Keywords: S8 (saneamento) + atividade A6 (contratual)
- **Decision:** Dispatch primário = `agente-saneamento` (S8)

**Passo 2 — Agente Saneamento (Q2-Q4):**
- Q2: Projeto executivo + concessão integrada → Fase C + F
- Q3: Brasil (Lei 14.026)
- Q4: Múltiplos formatos (PMSB + estudos de viabilidade)

**Passo 3 — Carga de Contexto (RAG):**
- RAG Hierarchy seleciona coleção `saneamento`
- Busca por: "Lei 14.026 + concessão + MBR + terciário"
- Retorna: 3-5 chunks com máxima relevância

**Passo 4 — Execução com Handoff:**
- Agente-saneamento analisa ETE (estrutura, normas NBR, tratamento)
- Detecta concessão → **Oferece handoff a `agente-contratual` (Manta 02)**
- Agente-contratual revisa cláusulas pós-Lei 14.026

**Passo 5 — Deliverable:**
- 1️⃣ Tese técnica (MBR vs. lodo ativado, área, custo operacional)
- 2️⃣ Estrutura de concessão (PPP, subsídio cruzado, WACC)
- 3️⃣ Cronograma (obra + concessão + operação)
- 4️⃣ Matriz de risco (tarifário, ambiental, social)

---

## 8. TROUBLESHOOTING — Se Maestro Routear Errado

| Problema | Causa | Solução |
|----------|-------|---------|
| "Meu pergunta sobre rodovia foi para agente-infraestrutura S2 (OAE) em vez de S1" | Keywords ambíguas (ex: "ponte em rodovia") | Ser mais específico: "obra de pavimentação" ou "estrutura de ponte" |
| "Pergunta sobre barragem de rejeitos foi para agente-barragens (S10), não agente-energia (S9)" | S10 é dispatch primário para rejeitos/TSF | Especificar "geração hidrelétrica na barragem" → força dispatch S9 + handoff S10 |
| "Maestro não entendeu que é uma pergunta de Port (S6), mandou para Horizontal" | Palavra-chave não no dicionário (ex: "berço marítimo" em vez de "berço portuário") | Use terminologia oficial: "berço", "calado", "ANTAQ", "dragagem" |

---

## 9. KEYWORDS COMPLETOS — CHEAT SHEET

```
S1 rodovia|pavimento|CBUQ|BGS|SICRO|DNIT
S2 ponte|viaduto|OAE|NBR 7187|estrutura|fundação
S3 ferrovia|trilho|via permanente|dormente|AMV
S4 metrô|estação|NATM|PSD|VLT|linha
S6 porto|terminal|ANTAQ|dragagem|molhe|berço|calado|contêiner
S7 aeroporto|pista|RWY|taxiway|TPS|TECA|ANAC|ICAO|ILS|balizamento
S8 saneamento|ETA|ETE|adutora|esgoto|AySA|Lei 14.026|SNIS|PMSB|reúso
S9 transmissão|LT|subestação|ANEEL|RAP|leilão|ONS|EPE|geração|fotovoltaica
S10 barragem|vertedouro|CFRD|CCR|rejeitos|TSF|ICOLD|CBDB|Lei 12.334|PAE
ESG (co-agent) biodiversidade|ESG|carbono|offset|ambiental|compliance|GHG|TCFD|SASB
```

---

**Documento canônico:** `/sharepoint/00-arquitetura/INDICE-CANONICO-v5.0.1.md`  
**Deployment status:** `DEPLOYMENT-REPORT-v5-0-PRODUCTION.md`  
**Perguntas?** Contatar MN ou slack `#manta-maestro-v5`

