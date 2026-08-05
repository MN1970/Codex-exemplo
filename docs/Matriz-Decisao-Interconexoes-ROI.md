# MATRIZ DE DECISÃO — ROI por Tipo de Interconexão e Dispositivo de Segurança

**Documento:** Guia de Decisão Rápida  
**Data:** 29/07/2026  
**Formato:** Matrizes de Decisão + Checklist  
**Classificação:** Referência Técnica — Manta Associados

---

## SUMÁRIO EXECUTIVO — RECOMENDAÇÕES CONSOLIDADAS

### Interconexões: Qual Tipo Escolher?

```
┌─────────────────────────────────────────────────────────────┐
│  VOLUME DE TRÁFEGO (VMD)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  VMD > 20.000 v/dia       ➜  ✅ TREVO COMPLETO             │
│  ROI: +R$ 243 M (30 anos)                                   │
│  VPL: +2.800 M                                              │
│  Payback: 2,5 anos                                          │
│  Razão: Economia de seguro + fluxo justificam CAPEX        │
│                                                              │
│  VMD 15.000-20.000 v/dia  ➜  ✅ TREVO PARCIAL (A4/B4)      │
│  ROI: +R$ 150-200 M (30 anos)                              │
│  VPL: +1.850-2.100 M                                        │
│  Payback: 3,0 anos                                          │
│  Razão: Equilíbrio CAPEX/benefícios operacionais           │
│                                                              │
│  VMD 10.000-15.000 v/dia  ➜  ⚠️  DIAMANTE OU PARCIAL       │
│  ROI: Marginal (análise de risco recomendada)              │
│  Decisão baseada em: espaço disponível, volume futuro      │
│                                                              │
│  VMD 8.000-10.000 v/dia   ➜  ✅ DIAMANTE                   │
│  ROI: CAPEX mínimo (R$ 21,4 M)                             │
│  VPL: +816 M                                                │
│  Payback: 2,3 anos                                          │
│  Razão: Simplicidade operacional                            │
│                                                              │
│  VMD < 8.000 v/dia        ➜  ❌ INTERSEÇÃO EM NÍVEL        │
│  Usar: Rótula ou T/Y com acomodação                        │
│  CAPEX: < R$ 10 M                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Defensas e Barreiras: Qual Especificar?

```
┌─────────────────────────────────────────────────────────────┐
│  VELOCIDADE OPERACIONAL (V85 km/h)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  V85 < 80 km/h            ➜  ✅ DEFENSA METÁLICA           │
│  Custo: R$ 525 k/km                                         │
│  Apropriada para acessos, rodovias rurais simples          │
│                                                              │
│  V85 80-100 km/h          ➜  ⚠️  DEFENSA + BARREIRA PARCIAL│
│  Estratégia: Defensa em retas, barreira em curvas/OAE      │
│  Custo médio: R$ 600 k/km (híbrida)                         │
│                                                              │
│  V85 > 100 km/h           ➜  ✅ BARREIRA RÍGIDA            │
│  Custo: R$ 670 k/km                                         │
│  OBRIGATÓRIA: viadutos, aproximações OAE, canteiro         │
│  ROI: -45% custo total (30 anos) vs defensa                │
│                                                              │
│  Canteiro central < 1,5 m  ➜  ✅ BARREIRA RÍGIDA SEMPRE    │
│  Razão: Risco de invasão de pista oposta                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## MATRIZ 1: SELEÇÃO POR VMD E ESPAÇO DISPONÍVEL

```
                        ESPAÇO DISPONÍVEL (hectares)
                  ┌──────────┬──────────┬──────────┐
                  │ RESTRITO │  MÉDIO   │ ABUNDANTE│
                  │ (<30 ha) │(30-50 ha)│ (>50 ha) │
        ┌─────────┼──────────┼──────────┼──────────┤
        │ > 20k   │ PARCLO A4│ TREVO C. │ TREVO C. │
    V   │ v/dia   │ (6 ramos)│(8 ramos) │ (8 ramos)│
    M   ├─────────┼──────────┼──────────┼──────────┤
    D   │15-20k   │PARCLO A2 │ TREVO C. │ TREVO C. │
        │ v/dia   │(4 ramos) │(8 ramos) │ (8 ramos)│
        ├─────────┼──────────┼──────────┼──────────┤
        │10-15k   │DIAMANTE+ │PARCLO    │ TREVO P. │
        │ v/dia   │  SEM     │A2/B2     │(4-6 ram) │
        ├─────────┼──────────┼──────────┼──────────┤
        │ 8-10k   │DIAMANTE  │DIAMANTE  │DIAMANTE+ │
        │ v/dia   │(básico)  │(upgrade) │(futuro)  │
        ├─────────┼──────────┼──────────┼──────────┤
        │ < 8k    │ RÓTULA   │ RÓTULA   │ RÓTULA   │
        │ v/dia   │(em nível)│(em nível)│ T/Y      │
        └─────────┴──────────┴──────────┴──────────┘

LEGENDA:
✅ RECOMENDADO (custo-benefício ótimo)
⚠️  ACEITÁVEL (análise adicional recomendada)
❌ NÃO RECOMENDADO (custo excessivo ou inadequado)
```

---

## MATRIZ 2: CUSTOS COMPARATIVOS — 30 ANOS (Valor Presente @ 7,5%)

```
                        R$ MILHÕES (30 anos, VP)
┌─────────────────┬────────┬────────┬────────┬────────┐
│ TIPO / EXTENSÃO │ CAPEX  │  O&M   │SEGUROS │ TOTAL  │
├─────────────────┼────────┼────────┼────────┼────────┤
│ DIAMANTE        │ 21,4   │ 19,2   │ 58,0   │ 98,6   │
│ (4 ramos)       │        │        │        │        │
├─────────────────┼────────┼────────┼────────┼────────┤
│ TREVO PARCIAL   │ 29,8   │ 17,0   │ 38,0   │ 84,8   │
│ A2/B2 (4-5 ram) │        │        │ (↓35%) │ (↓14%) │
├─────────────────┼────────┼────────┼────────┼────────┤
│ TREVO COMPLETO  │ 38,5   │ 25,8   │ 17,0   │ 81,3   │
│ (8 ramos)       │        │        │ (↓71%) │ (↓18%) │
├─────────────────┼────────┼────────┼────────┼────────┤
│ DEFENSA (10 km) │ 6,0    │ 5,76   │ 11,3   │ 23,1   │
├─────────────────┼────────┼────────┼────────┼────────┤
│ BARREIRA (10 km)│ 6,7    │ 1,58   │ 4,46   │ 12,7   │
│ (vs DEFENSA)    │ (+11%) │ (-73%) │ (-60%) │ (-45%) │
└─────────────────┴────────┴────────┴────────┴────────┘

INSIGHT: Barreira > Defensa economicamente em horizonte 30+ anos
         Trevo Completo > Diamante para VMD > 15.000
```

---

## MATRIZ 3: PERFORMANCE OPERACIONAL

```
                    VELOCIDADE    FLUXO        DELAY      SEMÁFORO
                    OPERACIONAL   EFETIVO      MÉDIO
┌───────────────────┬──────────┬──────────┬──────────┬──────────┐
│ DIAMANTE          │ 85 km/h  │ 2.4k v/h │  40-60s  │ SIM (2)  │
│ (com semáforo)    │          │          │ (parada) │          │
├───────────────────┼──────────┼──────────┼──────────┼──────────┤
│ TREVO PARCIAL     │ 75 km/h  │ 3.5k v/h │  15-30s  │ SIM (1-2)│
│ PARCLO A2/B2      │          │          │          │          │
├───────────────────┼──────────┼──────────┼──────────┼──────────┤
│ TREVO COMPLETO    │ 95 km/h  │ 4.5k v/h │   8-15s  │   NÃO    │
│ (sem semáforo)    │ (free)   │ (máximo) │ (manobra)│          │
├───────────────────┼──────────┼──────────┼──────────┼──────────┤
│ DEFENSA           │   N/A    │   N/A    │   N/A    │   N/A    │
│ (não afeta)       │          │          │          │          │
├───────────────────┼──────────┼──────────┼──────────┼──────────┤
│ BARREIRA          │   N/A    │   N/A    │   N/A    │   N/A    │
│ (não afeta)       │          │          │          │          │
└───────────────────┴──────────┴──────────┴──────────┴──────────┘

ANÁLISE CRÍTICA:
Trevo Completo ganha em: fluxo (+88% vs Diamante), velocidade (+12%)
Diamante vence em: CAPEX (-44% vs Trevo), simplicidade
Trade-off: +R$ 17 M em CAPEX vs +R$ 150-200 M em receita operacional
```

---

## MATRIZ 4: IMPACTO EM SEGURANÇA — DEFENSA vs BARREIRA

```
                    DEFENSA         BARREIRA        REDUÇÃO BARREIRA
┌───────────────────┬──────────┬──────────┬──────────────┐
│ VELOCIDADE 80 km/h                                      │
│ Penetração        │ 0,8-1,2 m│ 0,1-0,3 m│ -75% (crítico)│
│ Lesão grave       │  35-40% │  15-20% │ -50%         │
│ Fatalidades       │  8-12%  │  1-3%   │ -70%         │
├───────────────────┼──────────┼──────────┼──────────────┤
│ VELOCIDADE 110 km/h                                     │
│ Penetração        │ 1,5-2,0 m│ 0,3-0,6 m│ -80% (crítico)│
│ Lesão grave       │  65-75% │  25-35% │ -55%         │
│ Fatalidades       │ 15-25%  │  3-6%   │ -60%         │
├───────────────────┼──────────┼──────────┼──────────────┤
│ CUSTO POR SINISTRO                                      │
│ Custo médio       │ R$ 120 k│ R$ 85 k │ -29%         │
│ Anual (10 km)     │ R$ 3.28 M│ R$ 0.79M│ -76%         │
│ 30 anos (VP)      │R$ 11.3 M│ R$ 4.46M│ -60%         │
└───────────────────┴──────────┴──────────┴──────────────┘

CONCLUSÃO: Barreira reduz severidade em -55%, economiza R$ 6,8 M em seguros
```

---

## MATRIZ 5: CRITÉRIO RÁPIDO DE SELEÇÃO

### Por Tipo de Rodovia

```
┌───────────────────────────────────────────────────────────┐
│ RODOVIA FEDERAL (V85 > 100 km/h, pista dupla)            │
├───────────────────────────────────────────────────────────┤
│ ✅ INTERCONEXÃO:  Trevo Completo (VMD > 15k)             │
│    DEFESA:        Barreira rígida OBRIGATÓRIA            │
│    RESULTADO:     Fluxo máximo, segurança otimizada      │
│                                                            │
│ ⚠️  Se espaço restrito:                                   │
│    INTERCONEXÃO:  Trevo Parcial A4 (6 ramos)             │
│    DEFESA:        Barreira rígida                        │
│    CAPEX:         -R$ 8,7 M vs Completo                 │
│                                                            │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│ RODOVIA ESTADUAL (V85 85-100 km/h, pista dupla)          │
├───────────────────────────────────────────────────────────┤
│ ✅ INTERCONEXÃO:  Diamante com semáforo inteligente      │
│    DEFESA:        Defensa em retas + Barreira em curvas │
│    CAPEX:         R$ 21,4 M (interconexão)               │
│                   R$ 3-4 M (dispositivos híbridos)        │
│                                                            │
│ ✅ Se crescimento previsto (VMD > 10k em 10 anos):       │
│    INTERCONEXÃO:  Trevo Parcial (upgrade futura)         │
│    DEFESA:        Barreira em pontos críticos            │
│                                                            │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│ ACESSO URBANO (V85 50-80 km/h, pista simples)            │
├───────────────────────────────────────────────────────────┤
│ ✅ INTERCONEXÃO:  Rótula ou T/Y (em nível)               │
│    DEFESA:        Defensa metálica (custo-eficaz)        │
│    CAPEX:         < R$ 10 M (ambos)                      │
│    SEGURANÇA:     Velocidades reduzidas minimizam risco  │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## MATRIZ 6: ROI POR CENÁRIO DE VOLUME

```
                    VMD = 8.000      VMD = 15.000     VMD = 25.000
                    (baixo volume)   (médio volume)   (alto volume)
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ DIAMANTE        │              │              │              │
│ VPL (30 anos)   │  +R$ 817 M   │  +R$ 1.531 M │  +R$ 2.557 M │
│ IRR             │     35%      │     40%      │     47%      │
│ Payback         │   2.8 anos   │   2.5 anos   │   2.3 anos   │
│ Recomendação    │   ✅ ÓTIMO   │   ⚠️ MARGINAL│   ❌ PERDEDOR│
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ TREVO PARCIAL   │              │              │              │
│ VPL (30 anos)   │  +R$ 862 M   │  +R$ 1.784 M │  +R$ 2.800 M │
│ IRR             │     36%      │     42%      │     48%      │
│ Payback         │   3.2 anos   │   2.8 anos   │   2.5 anos   │
│ Recomendação    │   ✅ BOM     │   ✅ BOM     │   ✅ ÓTIMO   │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ TREVO COMPLETO  │              │              │              │
│ VPL (30 anos)   │  +R$ 880 M   │  +R$ 1.920 M │  +R$ 2.900 M │
│ IRR             │     35%      │     43%      │     48%      │
│ Payback         │   3.5 anos   │   2.8 anos   │   2.5 anos   │
│ Recomendação    │   ⚠️ ALTO CP │   ✅ ÓTIMO   │   ✅ ÓTIMO   │
│                 │   (acima BEC)│               │               │
└─────────────────┴──────────────┴──────────────┴──────────────┘

BEC (Break-Even Cost) ≈ VMD 12.000 para Trevo vs Diamante
```

---

## CHECKLIST EXECUTIVO — DECISÃO FINAL

### Passo 1: Dados de Entrada

```
☐ VMD (Volume Médio Diário): __________ v/dia
☐ Crescimento esperado: __________ % a.a.
☐ V85 (velocidade operacional): __________ km/h
☐ Espaço disponível: __________ hectares
☐ Tipo de via: ☐ Federal ☐ Estadual ☐ Acesso ☐ Concessão
☐ Comprimento: __________ km
☐ Horizonte econômico: __________ anos
☐ WACC (taxa desconto): __________
☐ Histórico de acidentes: __________ sinistros/ano
☐ Canteiro central: __________ metros
```

### Passo 2: Seleção de Interconexão

```
MATRIZ RÁPIDA:
┌─────────────────────────────────────────┐
│ VMD vs V85                              │
│                                         │
│ Se VMD > 15.000:                        │
│   → TREVO (Completo se espaço,          │
│          Parcial se restrito)           │
│   ➜ Resultado: ✅ SELEÇÃO               │
│                                         │
│ Se VMD 10-15.000:                       │
│   → Comparar: DIAMANTE vs PARCIAL       │
│   → Fazer sensibilidade WACC ±2%        │
│   ➜ Resultado: ⚠️ ANÁLISE               │
│                                         │
│ Se VMD < 10.000:                        │
│   → DIAMANTE (se pista dupla)           │
│   → RÓTULA/T/Y (se simples)             │
│   ➜ Resultado: ✅ SELEÇÃO               │
└─────────────────────────────────────────┘
```

### Passo 3: Seleção de Defensa/Barreira

```
MATRIZ RÁPIDA:
┌──────────────────────────────────────────┐
│ V85 vs Tipo de Via                       │
│                                          │
│ Se V85 > 100 km/h OU viaduto:            │
│   → BARREIRA RÍGIDA (obrigatória)        │
│   ➜ Resultado: ✅ SELEÇÃO                │
│                                          │
│ Se V85 80-100 km/h:                      │
│   → Retas: DEFENSA                       │
│   → Curvas/OAE: BARREIRA                 │
│   → Canteiro < 1,5m: BARREIRA SEMPRE     │
│   ➜ Resultado: ⚠️ HÍBRIDA                │
│                                          │
│ Se V85 < 80 km/h:                        │
│   → DEFENSA (adequada)                   │
│   ➜ Resultado: ✅ SELEÇÃO                │
└──────────────────────────────────────────┘
```

### Passo 4: Validação Econômica

```
☐ Calcular VPL para 2 cenários (otimista, pessimista)
☐ Validar Payback < 4 anos
☐ Validar IRR > 30%
☐ Análise de sensibilidade (WACC ±2%, VMD ±10%)
☐ Comparação com benchmark (rodovias similares)
☐ Aprovação de órgão regulador (ANTT, prefeitura)
```

### Passo 5: Documentação Final

```
ESPECIFICAÇÃO FINAL:
┌────────────────────────────────┐
│ Interconexão: _________________│
│ Extensão total: _____ km       │
│ CAPEX estimado: _____ M        │
│ O&M anual: _____ k             │
│ VPL (30 anos): _____ M         │
│ Payback: _____ anos            │
│ Dispositivos: Defensa/Barreira │
│ ________________________________│
│ Aprovado por: _________________│
│ Data: _________________________ │
└────────────────────────────────┘
```

---

## TABELA COMPARATIVA FINAL — VENCEDOR POR CENÁRIO

```
┌──────────────────────────────────────────────────────────────┐
│                       CENÁRIO DE VOLUME                      │
├──────────────┬─────────────┬──────────────┬─────────────────┤
│              │ BAIXO       │ MÉDIO        │ ALTO            │
│              │ (< 10k v/d) │ (10-15k)     │ (> 15k v/d)     │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ INTERCONEXÃO │ ✅          │ ⚠️           │ ✅              │
│ RECOMENDADA  │ DIAMANTE    │ PARCIAL      │ TREVO COMPLETO  │
│              │             │ (análise)    │                 │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ CAPEX        │ R$ 21,4 M   │ R$ 29,8 M    │ R$ 38,5 M       │
│ (base)       │ (menor)     │              │                 │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ SEGURO       │ R$ 58 M     │ R$ 45 M      │ R$ 17 M         │
│ (30 anos)    │             │              │ (melhor)        │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ FLUXO        │ 2.4k v/h    │ 3.5k v/h     │ 4.5k v/h        │
│ EFETIVO      │             │              │ (máximo)        │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ VPL (30 anos)│ +817 M      │ +1.784 M     │ +2.800 M        │
│ (base)       │ ✅          │ ✅           │ ✅              │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ PAYBACK      │ 2.8 anos    │ 2.8 anos     │ 2.5 anos        │
│              │ ✅          │ ✅           │ ✅ (melhor)     │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ DEFESA       │ ✅ DEFENSA  │ ⚠️ HÍBRIDA   │ ✅ BARREIRA     │
│ RECOMENDADA  │ METÁLICA    │ (se V85>90)  │ RÍGIDA          │
│              │             │              │ (obrigatória)   │
├──────────────┼─────────────┼──────────────┼─────────────────┤
│ CUSTO SEGURO │ +R$ 11 M    │ +R$ 8 M      │ +R$ 4 M         │
│ (30 anos)    │             │              │ (menor)         │
└──────────────┴─────────────┴──────────────┴─────────────────┘

RECOMENDAÇÃO FINAL:
✅ = Viável, recomendado
⚠️  = Requer análise adicional
❌ = Não recomendado (economia marginal)
```

---

## TEMPLATE PARA DOCUMENTAÇÃO

### Especificação de Interconexão Recomendada

```markdown
# PARECER TÉCNICO — SELEÇÃO DE INTERCONEXÃO

**Rodovia:** _______________________________________
**Localização:** ___________________________________
**Contratante:** ___________________________________

## DADOS DE PROJETO

- VMD (projeto): __________ v/dia (ano 10)
- V85 (velocidade operacional): __________ km/h
- Extensão de ramos: __________ km
- Área disponível: __________ hectares
- Horizonte econômico: __________ anos

## ANÁLISE COMPARATIVA

| Tipo | CAPEX | O&M (30a) | Seguro | TOTAL | VPL |
|------|-------|----------|--------|-------|-----|
| A    | $     | $        | $      | $     | $   |
| B    | $     | $        | $      | $     | $   |

## RECOMENDAÇÃO

✅ **TIPO SELECIONADO:** _________________________________

**Justificativa:**
- [Razão 1]
- [Razão 2]
- [Razão 3]

**CAPEX Estimado:** R$ __________ milhões
**O&M Anual:** R$ __________ mil
**Payback:** __________ anos
**VPL (30 anos):** R$ __________ milhões

**Dispositivos de Segurança:**
- Defensa: __________ km
- Barreira: __________ km
- Custo: R$ __________ milhões

---
Engenheiro: _______________  Data: ______________
Aprovado: __________________  Data: ______________
```

---

## REFERÊNCIAS RÁPIDAS

**Para análise detalhada ver:**
- Análise-Economica-Interconexoes-Rodovias.md (§ 2-6)
- Defensas-vs-Barreiras-Impacto-Seguranca-ROI.md (§ 4-8)

**Para especificação técnica ver:**
- dispositivos-viarios-interconexoes-seguranca.html (DNIT IPR-718)

---

**Versão:** 1.0  
**Data:** 29/07/2026  
**ID:** MNT-MATRIZ-DECISAO-20260729  
**Classificação:** Referência Técnica
