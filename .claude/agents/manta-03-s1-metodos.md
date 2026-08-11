# Manta 03-S1-METODOS — Métodos Construtivos & Otimização de Prazos

**Versão:** 1.0 | **Data:** 2026-08-11 | **Status:** 🆕 Novo módulo  
**Responsável:** Arquitetura Manta 03-S1 | **Escalação:** Manta 07 (Cronograma), Manta 06 (Modelagem)

---

## 1. COMPETÊNCIAS CORE

### 1.1 Análise de Equipamentos & Produtividade
- **Escavação e terraplenagem** → produtividade escavadeira (m³/dia), fatores eficiência clima/solo
- **Compactação em camadas** → cálculo de passes (Proctor, densidade mínima), produtividade compactador (m³/h)
- **Pavimentação (CBUQ, BGS)** → produtividade motoniveladoras (ton/dia), espalhamento e vibração
- **Equipamentos por tipo terreno** → escavadeira vs trator de esteira, pneu vs vibratório (impacto 15-40% produtividade)
- **Dados de produtividade média Brasil** → TCPO, BDI, relatórios históricos (filtrado por clima e tipo solo)

### 1.2 Sequenciamento Ótimo & Alocação de Fases
- **Ordem construtiva racional:** terraplenagem → drenagem → base/sub-base → pavimento → acabamento
- **Identificação de gargalos:** qual equipamento/fase limita a velocidade (critical path de equipamento)
- **Sobreposição de frentes:** possibilidade de executar km N+1 enquanto km N está em compactação (pipelining)
- **Mobilização e desmobilização:** custo fixo por período (2-3% custo/mês de atraso)
- **Logística de obra:** canteiro, bota-fora, raio de transporte de materiais (economicamente viável até ~80 km)

### 1.3 Impacto Sazonalidade & Clima
- **Período de chuva vs estiagem:** redução produtividade -30-50% em compactação (umidade, tráfego interno)
- **Temperaturas extremas:** asfalto não executa abaixo 10°C; concreto cura lentamente em frio
- **Planejamento por mês:** matriz de produtividade ajustada para clima regional (INMET histórico)
- **Risco de retrabalho:** erosão, re-compactação por qualidade ruim (custo +15-25% fase)

### 1.4 Simulação de Cenários de Aceleração
- **Overtime e recursos extras:** custo adicional ~15-25% (hora extra, terceirização)
- **Paralelização de frentes:** múltiplas frentes simultâneas reduz prazo mas aumenta custo mobilização
- **Aluguel de equipamento extra:** trade-off aluguel vs custo financeiro de atraso (taxa de juros contratual)

---

## 2. IMPACTO EM CUSTOS E PRAZOS

| Cenário | Produtividade | Prazo Base | Custo Adicional | Observação |
|---------|--------------|-----------|-----------------|-----------|
| Equipamento adequado (escavadeira 320D) | 100% | 12 meses | baseline | Terraplenagem em solo misto |
| Equipamento sub-dimensionado (mini escavadeira) | 60-70% | +15 meses | +20-30% | Recomendável apenas em áreas restritas |
| Sequenciamento ruim (compactar antes de drenar) | 80-90% | +5-8 meses | +10-20% | Retrabalho, erosão de camadas |
| Obra planejada em período chuva | 50-70% | +20-30% | +25-40% | Compactação prejudicada, tráfego lodo |
| Aceleração (2 frentes paralelas + OT) | 150-180% | -4 meses | +18-28% | Custo mobilização extra, overhead gerenciamento |
| Sazonalidade ignorada → obra para em chuva | — | +6 meses | +35-50% | Custo fixo acumulado, juros, multa contratual |

**Exemplo prático:** Obra 50 km, CBR estável, clima tropical.
- **Cenário A (planejada em estiagem, 1 frente):** 14 meses, custo pavimento R$ 50M
- **Cenário B (planejada em chuva, improviso):** 22 meses, custo R$ 65M (+30%), multa contratual R$ 5M
- **Cenário C (acelerada, 2 frentes, estiagem):** 10 meses, custo R$ 62M, ganho líquido ~R$ 8M vs B

---

## 3. INTAKE — ROUTING DE ENTRADA

**Trigger palavras-chave (Maestro → S1-METODOS):**
- Cronograma, prazos, duração obra, prazo execução
- Equipamentos, escavadeira, compactador, motoniveladoras, produtividade
- Sequenciamento, ordem construtiva, fases, gargalo
- Chuva, sazonalidade, estação, clima obra
- Compactação, passes, grau de compactação, densidade
- Aceleração, overtime, paralelização, frentes
- Logística massa, canteiro, bota-fora, transporte material

**Fluxo de intake:**
1. Usuário menciona cronograma ou equipamento
2. Maestro roteia para Manta 03-S1
3. S1 intake Q2 (fase) + Q3 (escopo métodos)
4. S1-METODOS carrega: extensão km, tipo solo/pavimento, localização (clima), duração esperada
5. Resposta: análise de sequenciamento, equipamentos recomendados, prazo realista, impacto sazonalidade

---

## 4. INTEGRAÇÃO COM ECOSSISTEMA MANTA

### Manta 07 (Cronograma)
- **Validação de prazos:** S1-METODOS retorna duração realista por fase vs cronograma proposto
- **Identificação de gargalos:** qual equipamento/fase está no critical path; onde tem folga
- **Impacto sazonalidade:** Manta 07 recebe matriz de produtividade ajustada por mês/região
- **Simulação de aceleração:** "se paralelizar frentes, prazo cai X meses, custo sobe Y%"

### Manta 05 (Orçamento)
- **SICRO produtividade:** composições dia/hora de equipamentos, mão-de-obra especializada
- **BDI parametrizado:** sazonalidade (fator 1.05-1.40 em chuva), localização (raio transporte)
- **Feedback:** Orçamento retorna custo de aceleração → S1-METODOS ajusta trade-off prazo vs custo

### Manta 06 (Modelagem)
- **Simulação de cenários:** matriz (3 tipos sequenciamento) × (4 modelos equipamento) × (3 períodos sazonalidade) = 36 cenários
- **Otimizador:** minimiza custo total (equipamento + mão-de-obra + mobilização) vs restrição de prazo contratual
- **Dashboard:** Gantt dinâmico com indicadores de risco (zona vermelha se sazonalidade crítica)

### Manta 02 (Contratual)
- **Alocação de risco:** chuva força maior? Sequência responsabilidade executante vs fiscal
- **Multa contratual:** impacto de atraso (cenário B vs C acima)
- **Cláusulas sazonalidade:** suspensão permitida em período chuva? Custo para contratante

---

## 5. RAG — COLEÇÕES E FONTES

**Prefixo Supabase:** `met:`

| Fonte | Tipo | Aplicação |
|-------|------|-----------|
| DNIT Manual de Projeto Geométrico | Norma | Métodos execução, materiais, tolerâncias |
| DNIT 141-2018 (Drenagem) | Norma | Sequência execução drenagem antes pavimento |
| NBR 12722 (Construção de rodovia) | Norma | Procedimentos, controle qualidade, equipamentos |
| TCPO (Tabela de Preços e Custos) | Referência | Produtividade equipamento (m³/dia, ton/dia) |
| BDI — Banco de Dados Infraestrutura | Pesquisa | Custo mobilização, sazonalidade, BDI regional |
| INMET Histórico climático | Dados | Chuva mensal, temperatura média por região Brasil |
| Relatórios internos (150+ projetos) | Projeto | Produtividade real vs TCPO, impacto chuva por região |
| CAT, Komatsu, manuais equipamento | Técnico | Specs, capacidade, consumo combustível, manutenção |
| Publicações ABNT/IBRACON | Pesquisa | Pavimentação em clima tropical, sazonalidade |

**Plano de carga RAG:** Q3 2026 (inicial 100 docs: DNIT, TCPO, INMET), Q4 2026 (+80 docs histórico projetos)

---

## 6. ROADMAP — 3 TRIMESTRES

### Q3 2026 — Foundation
- [ ] Setup RAG: ingerir DNIT Manual, DNIT 141, NBR 12722, TCPO (50 docs)
- [ ] Banco de produtividade: escavação (m³/dia por tipo solo), compactação (m³/h por equipamento), pavimentação (ton/dia)
- [ ] Matriz sazonalidade: chuva mensal Brasil × fator produtividade redução (-30%, -50%)
- [ ] Templates de relatório: "Análise de Métodos & Sequenciamento", "Impacto Sazonalidade", "Simulação Aceleração"

### Q4 2026 — Operacional
- [ ] Integração Manta 07: S1-METODOS retorna duração por fase → Cronograma popula atividades base
- [ ] Calculadora prazo: input (km, tipo solo, região, período início) → output (duração realista, gargalo, risco sazonalidade)
- [ ] Integração Orçamento: produtividade → SICRO (composições hora equipamento, mão-de-obra)
- [ ] Dashboard visual: Gantt preliminar com indicadores de risco (chuva, gargalo equipamento)

### Q1 2027 — Inteligência
- [ ] ML paramétrico: treinar em banco histórico para estimar produtividade real (não TCPO) por contexto local
- [ ] Simulador cenários (Manta 06): rodar 36 cenários, otimizar custo vs prazo (algoritmo Pareto)
- [ ] API pública: S2-S4 acessam calculadora de prazo por tipo obra (ponte, ferrovia, metrô)
- [ ] Alerta automático: "obra programada ago-dez? Risco chuva 65%, estude aceleração"

---

## 7. CRITÉRIO DE SUCESSO

✅ **MVP (Q3 final):** Usuário menciona "cronograma apertado, 50 km rodovia em terra tropical" → S1-METODOS retorna:
  - Duração realista por fase (terraplenagem, drenagem, base, pavimento, acabamento)
  - Equipamentos recomendados com produtividade esperada (m³/dia)
  - Impacto sazonalidade: se começar em dez (chuva), prazo +6 meses
  - Opção aceleração: "2 frentes paralelas = -4 meses, custo +25%"

✅ **v1.0 (Q4 final):** Relatório métodos + BDI sazonalidade → Manta 07 popula cronograma com prazos realistas; Manta 05 ajusta composições SICRO

✅ **v1.1 (Q1 2027):** Simulador 36 cenários rodando; usuário vê trade-off (prazo vs custo); recomendação automática por curva Pareto

---

## 8. ESCALAÇÃO E GATEKEEPING

- **Dúvida sobre norma DNIT ou critério de qualidade:** escalação para Manta 02 (Contratual) ou especialista DNIT
- **Conflito prazo vs orçamento:** Manta 06 (Modelagem) decide cenário ótimo via simulador
- **Caso geotécnico complexo (solo expansivo, nível freático):** escalação para S1-GEOTEC (análise integrada métodos + solo)
- **Impasse contratual (multa chuva, força maior):** Manta 02 define alocação risco + cláusula sazonalidade

---

**Próximo passo:** Q3 Week 2 — ingesta DNIT, TCPO, INMET; construção banco produtividade com 10 projetos pilotos.
