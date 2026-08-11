# Manta 02-CONTRATUAL-GEO — Riscos Geotécnicos & Alocação Contratual

**Versão:** 1.0 | **Data:** 2026-08-11 | **Status:** 🆕 Novo módulo  
**Responsável:** Arquitetura Manta 02 (Contratual) | **Escalação:** Manta 15 (Advisory)

---

## 1. COMPETÊNCIAS CORE

### 1.1 Cláusulas de Variabilidade Geotécnica
- **Ensaios de confirmação** → direitos de revisão de preço pré-obra (sondagem + SPT)
- **Alterações geológicas previstas vs reais** → cláusulas de variabilidade (Rock vs Solo), Condições Anormais
- **Direitos de mudança de projeto** → empreiteiro vs contratante (quem absorve o delta CBR)
- **Revisão de preço por variação** → índices SICRO, combustível, salário (IPCA, INCC)
- **Multas por atraso** → exclusão de dias perdidos por força maior climática

### 1.2 Limites de Responsabilidade
- **Projetista** → responsável por relatório geotécnico (adequação normas, sondagem suficiente)
- **Empreiteiro** → responsável por execução conforme projeto (compactação, drenagem, qualidade)
- **Contratante** → responsável por variação geológica não prevista (rocha, água subterrânea anômala)

### 1.3 Contingenciamento & Força Maior
- **Rocha não prevista** → preço unitário pré-definido (R$/m³) ou aditivo contratual
- **Água subterrânea** → responsabilidade contratante (drenagem adicional, bombeamento)
- **Chuva extrema** → força maior, prorrogação automática (curva pluviométrica retorno 10-100 anos)
- **Encontro de objetos/serviços** → paralisação sem custo adicional até resolução

### 1.4 Garantias & Vida Útil
- **Garantia de pavimento** → 5-10 anos (NBR 15486), multa por falha precoce (-10-20% VR)
- **Garantia de compactação** → grau mínimo 100% Proctor, medição TCF/estática
- **Cobertura de retrabalho** → falhas de qualidade primeiras 24 meses (zero custo ao contratante)

---

## 2. IMPACTO EM CUSTOS

| Cenário | Impacto | Mitigação | Savings |
|---------|--------|-----------|---------|
| Risco geotécnico mal alocado | +10-20% overrun | Cláusulas claras, ensaios pré-obra | -15% |
| Contrato vago (Condições Anormais) | Disputa, arbitragem 1-2 anos | Definição BEM CLARA (rocha, água) | -8% (rapidez) |
| Revisão preço inadequada | -3-5% margem | Índice ajustável (SICRO/combustível/salário) | +2-3% |
| Garantia ausente | +1-2% custo anual (manutenção) | Garantia 5+ anos (zero manutenção) | +1-2% |
| Atraso climático não definido | Multiplicação custos indiretos (+50%) | Força maior com prorrogação automática | -30-40% |

**Impacto total contrato bem estruturado:** -8-15% custo final + redução risco jurídico (80% menos disputas)

---

## 3. INTAKE — ROUTING DE ENTRADA

**Trigger palavras-chave (Maestro → Manta 02-GEO):**
- Risco geológico, Condições Anormais
- Cláusula de variabilidade, rocha não prevista
- Revisão de preço, atraso climático, força maior
- Garantia de pavimento, multa por falha precoce
- Aditivo contratual, disputa geotécnica
- Direito de mudança de projeto, contingenciamento
- CACC (Câmara Arbitral), jurisprudência, case law

**Fluxo de intake:**
1. Usuário menciona risco geotécnico ou cláusula contratual
2. Maestro roteia para Manta 02
3. Manta 02-GEO carrega: tipo de contrato (Empreitada, Preço Unitário, Concessão) + modelo de risco
4. Resposta: redação de cláusula específica + análise caso jurisprudência + recomendação alocação risco

---

## 4. INTEGRAÇÃO COM ECOSSISTEMA MANTA

### Manta 03-S1 (Infraestrutura / Geotecnia)
- **Input:** análise CBR, variabilidade esperada, jazida, rocha prevista/não prevista
- **Output:** recomendação para cláusula de revisão de preço, limite responsabilidade

### Manta 03-S1-HIDRO (Hidrologia)
- **Input:** risco de chuva (período retorno 10/50/100 anos), encontro de água subterrânea
- **Output:** cláusula força maior (dias/cm de chuva), prorrogação automática

### Manta 02-CLAIMS (Litígios Contratuais)
- **Input:** jurisprudência em disputas geotécnicas (CACC, arbitragem, TJSP)
- **Output:** antecedentes de sentenças similares, argumentação defensiva

### Manta 05 (Orçamento)
- **Input:** custo unitário rocha, bombeamento, estabilização
- **Output:** BDI parametrizado por tipo de risco (contingência 5-15%)

---

## 5. RAG — COLEÇÕES E FONTES

**Prefixo Supabase:** `ctr-geo:`

| Fonte | Tipo | Aplicação |
|-------|------|-----------|
| ABNT NBR 15486 (Pavimentação garantia) | Norma | Vida útil, cobertura retrabalho, multas |
| DNIT 101-105 + Manual Pavimentação | Norma | Especificações técnicas (compactação, CBR) |
| Modelos de contrato BNDES | Referência | Cláusulas modelo (Empreitada, Preço Unitário) |
| Jurisprudência CACC + TJSP | Case law | Sentenças geotécnia (15+ casos 2020-2026) |
| ISO 14687 (Ciclo de vida) | Referência | Garantia vs manutenção preventiva |
| CBDB publicações | Pesquisa | Alocação risco geotécnico (melhor prática) |
| Histórico de projetos Manta | Projeto | 50+ contratos analisados, disputas resolvidas |

**Plano de carga:** Q3 2026 (inicial 150 docs), Q4 2026 (+50 jurisprudência)

---

## 6. ROADMAP — 3 TRIMESTRES

### Q3 2026 — Foundation
- [ ] Setup RAG: modelos de contrato BNDES, NBR 15486, jurisprudência 15 casos
- [ ] Templates de cláusulas: variabilidade, força maior, garantia, revisão preço
- [ ] Matriz de alocação risco por tipo de contrato (4 tipos × 7 riscos = 28 matrizes)

### Q4 2026 — Operacional
- [ ] Integração com Manta 05: cláusula revisão preço ↔ BDI parametrizado
- [ ] Integração com S1-GEOTEC: input variabilidade → redação cláusula automática
- [ ] Analisador de contrato: upload PDF → identifica gaps de risco geotécnico (score 0-100)

### Q1 2027 — Inteligência
- [ ] Modelo preditivo: risco de disputa por cláusula + jurisprudência
- [ ] Simulador cenários: teste da cláusula contra 5 cenários geotécnicos reais
- [ ] Dashboard: mapa de alocação risco por segmento (S1-S10)

---

## 7. TIPOS DE RISCO — ALOCAÇÃO TÍPICA

| Risco Geotécnico | Alocação Típica | Mitigação Recomendada |
|------------------|-----------------|----------------------|
| CBR < esperado (3-5%) | Empreiteiro | Ensaios de confirmação pré-obra, reajuste de preço |
| Rocha não prevista | Contratante | Preço unitário pré-definido (R$/m³) |
| Encontro água subterrânea | Contratante | Bombeamento, drenagem especial (responsabilidade contratante) |
| Instabilidade de talude | Empreiteiro | Projeto geo-técnico bem definido (responsabilidade projetista) |
| Variação de insumos SICRO | Compartilhado | Índice de reajuste (SICRO, combustível, salário) |
| Chuva extrema | Contratante | Força maior, prorrogação automática (retorno 10-100 anos) |
| Falha de compactação | Empreiteiro | Garantia 5+ anos, multa precoce (-10-20% VR) |

---

## 8. ESCALAÇÃO E GATEKEEPING

- **Interpretação de norma (NBR 15486, DNIT):** escalação para especialista técnico
- **Disputa jurisprudencial complexa:** Manta 02-CLAIMS (análise CACC/TJSP)
- **Trade-off custo vs risco:** Manta 15 (Advisory) para recomendação estratégica
- **Caso de concepção inovadora:** Manta 16 (Arquiteto-IA) para design contratual único

---

**Próximo passo:** Q3 Week 1 — setup RAG modelos BNDES + validação templates com projeto piloto (Rodovia/Metro).
