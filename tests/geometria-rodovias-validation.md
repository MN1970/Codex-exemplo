# Testes de Validação — Geometria de Rodovias

**Data**: 2026-08-04  
**Agente Testado**: agente-infraestrutura S1 (Manta 03-S1)  
**Tipo**: Smoke Tests (5 prompts críticos)  
**Status**: Ready for Validation

---

## Teste 1: Cálculo de Raio Mínimo

### Prompt
```
Preciso projetar uma curva horizontal em uma BR federal (Vd=100 km/h). 
O raio disponível é 400m. Qual deve ser a superelevação? 
Qual o comprimento da clotóide? Preciso de recuo de banqueta?
```

### Saída Esperada
- ✅ Superelevação: e ≈ 4.7-5.0%
- ✅ Comprimento clotóide: L_c ≈ 110-120m
- ✅ Flecha de recuo: f ≈ 4.5-5.0m
- ✅ Referência: ES 101/97, Item 5.2

### Critério de Pass
- Respostas dentro de ±10% dos valores esperados
- Justificativa baseada em norma DNIT
- Cálculo demonstrado (não apenas resposta)

### Status
- [ ] Pass
- [ ] Fail
- [ ] Comentários

---

## Teste 2: Visibilidade em Curva

### Prompt
```
Tenho uma curva de 500m de raio em rodovia federal (Vd=100). 
A distância de parada é 137m. Qual flecha de recuo preciso abrir 
na banqueta de corte? Qual é a altura mínima de corte?
```

### Saída Esperada
- ✅ Flecha: f ≈ 4.7m (conforme fórmula ES 101/97)
- ✅ Justificativa: D²/(8R) - 0.6 → 137²/(8×500) - 0.6
- ✅ Altura mínima corte: 5m (conforme doc 06)
- ✅ Recomendação: Se corte > 5m, criar banqueta intermediária

### Critério de Pass
- Fórmula correta
- Valor dentro de ±5% do esperado
- Justificativa clara da visibilidade

### Status
- [ ] Pass
- [ ] Fail
- [ ] Comentários

---

## Teste 3: Orçamento com SICRO

### Prompt
```
Preciso orçar 1km de rodovia federal, pista simples, Vd=100 km/h, 
pavimento CBUQ 5cm, BGS 15cm. Qual quantitativo e custo SICRO estimado? 
Qual o valor total incluindo margem?
```

### Saída Esperada
- ✅ Pavimento CBUQ 5cm: 7.200 m² (1km × 7.2m)
- ✅ BGS 15cm: 7.200 m² 
- ✅ Custo unitário SICRO 2026 (atualizado):
  - CBUQ 5cm: ~R$95/m² → R$684k
  - BGS 15cm: ~R$18/m² → R$130k
- ✅ Subtotal: ~R$814k/km
- ✅ Com margem (10%): ~R$895k/km
- ✅ Total 1km: ~R$5.4M (incluindo terraplenagem estimada)

### Critério de Pass
- Quantitativo correto (área pavimento = 1km × largura)
- Valores SICRO realistas (2026)
- Cálculo de margem transparente

### Status
- [ ] Pass
- [ ] Fail
- [ ] Comentários

---

## Teste 4: Recomendação de Parâmetros Geométricos

### Prompt
```
Tenho uma rodovia estadual em topografia montanhosa. 
Volume de tráfego: 400k veículos/ano. 
Qual deve ser minha velocidade de projeto (Vd)?
Quais padrões geométricos (raio mínimo, superelevação, banqueta)?
```

### Saída Esperada
- ✅ Vd recomendado: 80 km/h (rodovia estadual, montanhosa)
- ✅ R_mín: 220m (conforme ES 101/97 para Vd=80)
- ✅ e_máx: 7.0%
- ✅ Largura faixa: 3.30m (padrão estadual)
- ✅ Taludes: 1:1.5 em corte, 1:2 em aterro
- ✅ Justificativa: tráfego moderado + topografia difícil → geometria segura

### Critério de Pass
- Vd coerente com dados de entrada
- Parâmetros consistentes com Vd escolhido
- Referência a normas DNIT

### Status
- [ ] Pass
- [ ] Fail
- [ ] Comentários

---

## Teste 5: Análise de Risco Geométrico

### Prompt
```
Identifiquei um trecho da BR com 4 acidentes em 2 anos. 
As curvas têm R=250m (Vd=100km/h). 
Qual é o risco geométrico? Como mitigá-lo?
```

### Saída Esperada
- ✅ Diagnóstico: Risco CRÍTICO (R=250m < R_mín=340m para Vd=100)
- ✅ Análise:
  - Superelevação máxima insuficiente
  - Visibilidade comprometida em curva
  - Histórico de acidentes confirma problema
- ✅ Opções de mitigação:
  1. Reduzir Vd de 100 para 80 → R_mín reduz para 220m (viável)
  2. Reengenharia: aumentar raio se possível (custos altos)
  3. Sinalização agressiva + redutor velocidade (temporário)
- ✅ Recomendação: Opção 1 (reduzir Vd) é mais viável economicamente

### Critério de Pass
- Identificação correta do risco
- Comparação com norma
- Mitigações realistas e hierarquizadas

### Status
- [ ] Pass
- [ ] Fail
- [ ] Comentários

---

## Resumo de Validação

| Teste | Descrição | Esperado | Resultado | Status |
|-------|-----------|----------|-----------|--------|
| 1 | Raio mínimo & superelevação | e≈4.7%, Lc≈110m, f≈4.7m | ? | ⏳ |
| 2 | Visibilidade em curva | f≈4.7m, H≥5m | ? | ⏳ |
| 3 | Orçamento SICRO | R$5.4M (1km) | ? | ⏳ |
| 4 | Parâmetros geométricos | Vd=80, R=220m, e=7% | ? | ⏳ |
| 5 | Análise de risco | Risco CRÍTICO, mitigar Vd | ? | ⏳ |

---

## Instruções de Execução

1. **Para cada teste**:
   - Copiar o prompt exato
   - Submeter ao agente-infraestrutura S1
   - Coletar resposta completa

2. **Validação**:
   - Comparar saída contra "Saída Esperada"
   - Permitir margem de erro (±5-10%)
   - Documentar discrepâncias

3. **Reportar**:
   - Preencher coluna "Resultado"
   - Marcar Pass/Fail
   - Comentar desvios significativos

4. **Ação se falhar**:
   - Investigar resposta do agente
   - Verificar se base de conhecimento foi carregada
   - Ajustar prompt se necessário
   - Re-testar

---

**Data de Criação**: 2026-08-04  
**Próxima Execução**: Após aprovação MN (Fase I)  
**Critério de Sucesso**: 5/5 testes com Pass ✅
