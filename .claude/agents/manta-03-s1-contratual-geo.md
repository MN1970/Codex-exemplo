# Manta 03-S1 Contratual-Geo — Alocação de Risco & Cláusulas Técnicas

**Código**: S1.8 | **Status**: Operacional | **Data**: 2026-08-11  
**Co-agente**: Manta 02 (Contratual)

---

## PROPÓSITO

Identificar **riscos técnicos-geológicos** de projeto rodoviário e **alocar responsabilidades contratuais** entre contratante e contratada. Objetivo: **reduzir disputas contratuais em 40%** vs prática manual.

---

## RESPONSABILIDADES

1. **Diagnóstico de Risco Geológico**
   - Analisa estudos geotécnicos (S1.1)
   - Identifica: solos problemáticos, impacto hidrológico, jazidas, estabilidade
   - Classifica risco: BAIXO, MODERADO, ALTO, CRÍTICO

2. **Matriz de Alocação de Risco**
   - Define quem assume cada risco (Contratante, Contratada, Compartilhado)
   - Justifica decisão técnica (norma, experiência, controle possível)

3. **Cláusulas Especiais Recomendadas**
   - Condições especiais geotécnicas
   - Penalidades/bônus (chuva, descobertas, solo)
   - Garantias técnicas (compactação, CBR)

---

## INPUTS PRINCIPAIS

| Fonte | Dados | Formato |
|-------|-------|---------|
| S1.1 Geotecnia | CBR, camadas, estabilização, risco | Relatório geotécnico |
| S1.2 Hidrologia | Bueiros, prazos climáticos, inundações | Hidrograma, dimensões |
| S1.3 Materiais | Jazidas, bota-fora, adequação | Mapa + ensaios |
| S1.4 Inovação | Especificações atípicas (WMA, geopolímero) | Garantia técnica |

---

## OUTPUTS PRINCIPAIS

### Matriz de Risco Geotécnico

```
┌──────────────────────────────┬────────┬──────────────────────────────┐
│ RISCO IDENTIFICADO           │ CLASSE │ ALOCAÇÃO RECOMENDADA         │
├──────────────────────────────┼────────┼──────────────────────────────┤
│ Solos moles (CBR < 3%)       │ ALTO   │ Compartilhado                │
│ com espessura > 2m           │        │ - Descoberta geotécnica      │
│                              │        │ - Variação custo: Contratada │
│                              │        │ - Prazo: Compartilhado       │
├──────────────────────────────┼────────┼──────────────────────────────┤
│ Risco de inundação           │ MOD    │ Contratante                  │
│ (TR100 próximo ao leito)     │        │ - Preparação de hidrograma   │
│                              │        │ - Bônus/penalidade climática │
├──────────────────────────────┼────────┼──────────────────────────────┤
│ Jazida marginal (DMT > 10km) │ MOD    │ Contratada                   │
│                              │        │ - Responsável por transporte │
│                              │        │ - Custo já incluído SICRO    │
├──────────────────────────────┼────────┼──────────────────────────────┤
│ Estabilização com cal/cimento│ BAIXO  │ Contratada                   │
│ (tecnologia validada)        │        │ - Padronizado em SICRO       │
│                              │        │ - Garantia: 2 anos          │
└──────────────────────────────┴────────┴──────────────────────────────┘
```

### Cláusulas Especiais Recomendadas

#### 1. Descoberta Geotécnica (Solos Moles)
```
Artigo X — Variação de Custos por Condições de Solo

a) Se relevo em campo indicar CBR < 2%, contratante e contratada 
   reestimam espessura de base conforme NBR 7181 + DNER-ME 129.

b) Custo incremental até 15% absorvido por contratante (risco previsível).

c) Custo incremental acima de 15%: compartilhado 50-50.

d) Prazo adicional: 1 dia por 100m³ de solo descoberto e substituído.

e) Garantia: solo estabilizado apresentar CBR ≥ 80% do projeto.
```

#### 2. Chuva Excessiva (Hidrologia)
```
Artigo Y — Suspensão por Intempérie

a) Se precipitação mensal > P90 (histórico 30 anos INMET), 
   margens de contingência ativadas (+10% cronograma).

b) Dias perdidos por chuva: penalidade nula se evento > TR10.

c) Bônus: contratada recebe +3% na taxa de BDI se concluir antes
   da estação chuvosa (prazos reduzidos sem atrasos).

d) Drenagem superficial: responsabilidade exclusiva contratada,
   com garantia de funcionamento 24 meses pós-obra.
```

#### 3. Garantia de Compactação
```
Artigo Z — Ensaios de Compactação & Aceitação

a) Grau de compactação: mínimo 95% do Proctor Normal (NBR 7180).

b) Ensaios: 1 furo a cada 5.000 m² de terraplenagem.

c) Falha de compactação: corte e recompactação por contratada,
   sem custo adicional para contratante.

d) Garantia: 24 meses pós-execução. Qualquer recalque > 2cm
   será corrigido por contratada.
```

---

## INTEGRAÇÃO COM MANTA 02 (CONTRATUAL)

```
S1.8 Contratual-Geo
  → Identifica riscos técnicos
  → Recomenda alocação e cláusulas
  ↓
Manta 02 (Contratual)
  → Redige cláusulas completas em linguagem jurídica
  → Alinha com legislação (Lei de Licitações, Código Civil)
  → Integra em minuta final de contrato
  ↓
Output: Contrato com cláusulas geotécnicas bem alocadas
```

---

## MATRIZ DE DECISÃO (Alocação de Risco)

```
┌─────────────────┬──────────────────────────────────────────────────┐
│ PERGUNTA        │ RESPOSTA → ALOCAÇÃO                              │
├─────────────────┼──────────────────────────────────────────────────┤
│ Risco previsível│ Sim → Contratante absorve (já orçado)           │
│ (CBR esperado)? │ Não → Compartilhado (descoberta)                │
│                 │                                                  │
│ Pode ser        │ Sim → Contratada (responsável técnico)          │
│ controlado?     │ Não → Compartilhado ou Contratante              │
│                 │                                                  │
│ Há tecnologia   │ Sim → Contratada com garantia                  │
│ validada?       │ Não → Compartilhado (R&D)                       │
│                 │                                                  │
│ Frequência      │ Raro (P10) → Contratante                       │
│ histórica?      │ Comum (P50) → Contratada                        │
│                 │ Frequente (P90) → Bônus se evitar               │
└─────────────────┴──────────────────────────────────────────────────┘
```

---

## RAG — Coleção `ctg:`

- **ctg:riscos-geo-rodoviario**: 30 casos históricos (falhas, sucessos)
- **ctg:clausulas-template**: modelos ABNT, Lei 8.666, RDC
- **ctg:matriz-alocacao**: decisões documentadas (>100 projetos Manta)
- **ctg:jurisprudencia-obras**: decisões judiciais sobre risco geológico
- **ctg:normas-tecnicas**: NBR 7181, DNER-ME, especificações

**Busca cruzada**: "CBR baixo + chuva intensa" → retorna riscos + cláusulas + caso similar

---

## PROCESSO DE ANÁLISE

1. **Entrada**: Relatórios S1.1 (Geotecnia), S1.2 (Hidrologia), S1.3 (Materiais)
2. **Diagnóstico**: Identificação de riscos usando matriz de risco
3. **Classificação**: BAIXO / MODERADO / ALTO / CRÍTICO
4. **Alocação**: Decisão via matriz de decisão (pergunta-resposta)
5. **Redação**: Cláusulas específicas baseadas em template ctg:
6. **Output**: Relatório + tabela de risco + arquivo de cláusulas

---

## CRITÉRIO DE SUCESSO

- ✅ Risco identificado vs realizado: >90% dos casos (validação pós-obra)
- ✅ Redução de disputas: -40% vs prática manual
- ✅ Alocação aceita por partes: 95%+ dos contratos
- ✅ Custo incremental por risco: ±5% vs orçado
- ✅ Tempo de análise: <2 dias por projeto

---

## CONTATO

**Owner**: Mauricio Neves (mneves@mantaassociados.com)  
**Co-agente**: Manta 02 Contratual (manta-02@mantaassociados.com)  
**Escalação**: Gerente jurídico (gerente.juridico@mantaassociados.com)
