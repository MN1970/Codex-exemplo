# Manta 03-S1-GEOTEC — Geotecnia & Materiais (Otimização de Custos)

**Versão:** 1.0 | **Data:** 2026-08-11 | **Status:** 🆕 Novo módulo  
**Responsável:** Arquitetura Manta 03-S1 | **Escalação:** Manta 06 (Modelagem)

---

## 1. COMPETÊNCIAS CORE

### 1.1 Caracterização Geotécnica
- **Análise de CBR (Califórnia Bearing Ratio)** → correlação direta com espessura de pavimento (AASHTO, DNER-ME 049)
- **Classificação de solos** (USCS, HRB, MCT-M) → determinação de aptidão construtiva
- **Ensaios de laboratório** → SPT, pressiômetro, cone dinâmico, granulometria (NBR 7181, 7182)
- **Compactação & densidades** → Proctor normal/intermediário, grau de compactação mínimo 100%
- **Permeabilidade e drenabilidade** → impacto em vida útil do pavimento

### 1.2 Otimização de Materiais
- **Identificação de jazidas** → potencial, distância, transportabilidade, sazonalidade
- **Cálculo de bota-fora** → volume excedente, destino, custo de disposição (aterro, reuso)
- **Estabilização de solos** → cal, cimento, geopolímero (impacto CBR +200-400%)
- **Reuso de pavimento antigo** → reciclagem, características residuais
- **Controle de qualidade** → relatórios de ensaios, conformidade com DNIT, rastreabilidade

---

## 2. IMPACTO EM CUSTOS E PRAZOS

| Cenário | Impacto CBR | Espessura | Custo Pavimento | Ganho Potencial |
|---------|------------|-----------|-----------------|-----------------|
| CBR nativo baixo (3%) | — | +25% base | +15-25% | Estabilização: -20-30% |
| Estabilização (cal/cimento) | +200-400% | -30% | -25% | -25-35% material + obra |
| Reuso jazida local | +5-15% | -10% | -8-12% | -30-40% transporte |
| Bota-fora ineficiente | — | — | — | +20-40% custo adicional |

**Exemplo prático:** Km 0-10, CBR nativo 4% → espessura 60 cm vs CBR estabilizado 12% → espessura 42 cm = economia 30% pavimento.

---

## 3. INTAKE — ROUTING DE ENTRADA

**Trigger palavras-chave (Maestro → S1-GEOTEC):**
- CBR, solo argiloso, solo laterítico, expansivo
- Compactação, Proctor, grau de compactação
- Jazida, bota-fora, empréstimo, rejeito
- Estabilização (cal, cimento, geopolímero)
- SPT, ensaio laboratório, pedologia
- DNIT 101-105, AASHTO, DNER-ME

**Fluxo de intake:**
1. Usuário menciona geotecnia ou insumo material
2. Maestro roteia para Manta 03-S1
3. S1 intake Q2 (fase do projeto) + Q3 (escopo geotecnia)
4. S1-GEOTEC carrega contexto projeto + requisitos
5. Resposta: análise CBR, jazida, estabilização, BDI impacto

---

## 4. INTEGRAÇÃO COM ECOSSISTEMA MANTA

### Manta 05 (Orçamento)
- **SICRO composições:** estabilização cal (DNIT 019), cimento (DNIT 032), geopolímero (emergente)
- **BDI parametrizado:** segundo-plano: compactação sazonal, transporte distância variable
- **Feedback loop:** Orçamento retorna custo unitário → S1-GEOTEC ajusta recomendação jazida

### Manta 07 (Cronograma)
- **Prazos compactação:** por camada, clima (sazonalidade chuva reduz rendimento -30-50%)
- **Logistics material:** prazo mobilização jazida, raio de transporte (economia viável até ~80 km)
- **Ensaios de controle:** TCF, sondagem, perfuração (impacto caminho crítico +2-3 semanas)

### Manta 06 (Modelagem)
- **Simulação de cenários:** matriz (5 níveis CBR nativo) × (3 tipos estabilização) × (3 jazidas) = 45 cenários
- **Otimizador:** minimiza custo total (material + transporte + compactação) sujeito a restrições de prazo
- **Dashboard:** mapa de sensibilidade (CBR nativo vs economia de estabilização)

---

## 5. RAG — COLEÇÕES E FONTES

**Prefixo Supabase:** `geo:`

| Fonte | Tipo | Aplicação |
|-------|------|-----------|
| DNIT 101-105 (Pavimentação) | Norma | Método compactação, densidade mínima, CBR mínimo |
| DNER-ME 049 (CBR) | Norma | Procedimento de ensaio, correlação com espessura |
| NBR 6502 (Terminologia) | Norma | Definições solo, rocha, materiais |
| NBR 7181-7182 (Análise granulométrica) | Norma | Classificação, limites Atterberg |
| Manual de Pavimentação DNIT 2006 | Referência | Tabelas espessura vs CBR, estruturas típicas |
| ABMS Boletins técnicos | Pesquisa | Estabilização inovativa (geopolímero, RAP) |
| ISSMGE Working Groups | Pesquisa | Melhor prática internacional |
| Banco histórico (Manta) | Projeto | 150+ projetos: CBR real vs estimado, jazida performance |

**Plano de carga RAG:** Q3 2026 (inicial 200 docs), Q4 2026 (+100 docs histórico)

---

## 6. ROADMAP — 3 TRIMESTRES

### Q3 2026 — Foundation
- [ ] Setup RAG: ingerir DNIT 101-105, NBR, Manual DNIT (50 docs)
- [ ] Templates de relatório: "Análise Geotécnica & Estabilização", "Identificação Jazidas", "Controle Qualidade"
- [ ] KB interna: tabela CBR nativo → espessura (AASHTO), matriz estabilização
- [ ] Integração leitura de relatórios SPT/pedologia (OCR para histórico)

### Q4 2026 — Operacional
- [ ] Integração SICRO composições: cal (019), cimento (032), geopolímero (custom)
- [ ] Calculadora CBR → espessura: input (CBR, nível tráfego, clima) → output (espessura, custo SICRO)
- [ ] Integração Orçamento: relatório geotecnia → Manta 05 (insumos + BDI)
- [ ] Integração Cronograma: prazos compactação por clima + sazonalidade

### Q1 2027 — Inteligência
- [ ] ML paramétrico: treinar em banco histórico (150 projetos) para estimar CBR nativo antes de sondagem
- [ ] Simulador cenários (Manta 06): matriz 45 opções com otimizador de custo
- [ ] API pública: outros segmentos (S2-S4) acessam calculadora CBR & estabilização
- [ ] Dashboard: mapa de risco geotécnico (CBR < 4% → alerta vermelho)

---

## 7. CRITÉRIO DE SUCESSO

✅ **MVP (Q3 final):** Usuário menciona "CBR baixo, solo argiloso" → S1-GEOTEC retorna:
  - Recomendação estabilização com impacto CBR esperado
  - 3 opções de jazida com distância e transportabilidade
  - Comparativa de custo (+estabilização vs -bota-fora)

✅ **v1.0 (Q4 final):** Relatório geotecnia + recomendação estabilização → Manta 05 popula composição SICRO automaticamente

✅ **v1.1 (Q1 2027):** Simulador rodando com 45 cenários; usuário escolhe trade-off (custo vs prazo)

---

## 8. ESCALAÇÃO E GATEKEEPING

- **Dúvida sobre norma ou cálculo:** escalação para Manta 02 (Contratual) ou especialista ABMS
- **Impasse geotecnia-orçamento (custo vs estabilização):** Manta 06 (Modelagem) decide cenário ótimo
- **Caso de obra com histórico geotécnico complexo:** escalar para advisory (Manta 15)

---

**Próximo passo:** Q3 Week 1 — setup RAG + validação templates com projeto piloto (Rodovia XX).
