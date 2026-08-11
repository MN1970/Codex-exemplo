# Manta 03-S1-BIM-COST — Integração BIM & Orçamento Dinâmico

**Rodovias (S1) — Competência de cost estimation automática e sensibilidade paramétrica**

Versão: 1.0 | Criado: 2026-08-11 | Status: 🆕 Roadmap Q3 2026

---

## 1. COMPETÊNCIAS CORE

O módulo BIM-COST capacita equipes S1 a:

1. **Extração automática de volumes**
   - Integração nativa com Civil 3D (API Autodesk)
   - Parsing de superfícies, alinhamentos, seções transversais
   - Exportação automática para estrutura SICRO (composições de serviços)
   - Validação de consistência (volume estimado ↔ histórico de projeto similar)

2. **Cost estimation elemento-por-elemento**
   - BIM-based costing: cada seção da rodovia (terraplenagem, CBUQ, drenagem, sinalização)
   - Integração com base SICRO: aplicação de preços unitários por região/data
   - Curva de sensibilidade: se mudar espessura de CBUQ, custo automático recalcula
   - Relatório comparativo: "mudança de 0.5m de greide = R$ XX mil de impacto"

3. **Sensibilidade paramétrica**
   - Variáveis-chave: greide, largura de faixa, espessura de camadas, raio de curva
   - Tornado diagram: qual parâmetro impacta mais o custo final?
   - Cenários automáticos: conservador/base/otimista com 3 variantes em 1 dia (vs 2 semanas manual)

4. **Simulação de variantes geométricas**
   - Comparação automática: trevo vs diamante vs roundabout em tempo real
   - Inputs: raio mínimo, velocidade de projeto, demanda de tráfego
   - Outputs: volume de movimento de terra, metragem de pavimento, custo total por variante
   - Ranking de impacto: custo × viabilidade geométrica × impacto ambiental

5. **Rastreabilidade completa**
   - Versionamento: cada mudança no CAD gera snapshot automático com timestamp
   - Auditoria: quem alterou greide (e quando) → impacto no orçamento documentado
   - Linking: seção CAD ↔ composição SICRO ↔ linha do cronograma ↔ alocação orçamentária
   - Change log: relatório de "mudanças desde v1.0" com justificativa de impacto

6. **Validação cruzada & alertas**
   - Inconsistência detectada: volume de corte vs volume de aterro fora de tolerância
   - Flag: custo estimado > 25% acima de histórico similar (necessita revisão)
   - Integração com geotecnia: se SUCS mudou, aviso sobre impacto em custos de escavação
   - Alerta de risco: se sensibilidade mostra custo muito elástico em parâmetro crítico

---

## 2. IMPACTO EM CUSTOS

| Métrica | Ganho | Evidência |
|---------|-------|-----------|
| **Redução de erros de estimativa** | 15-25% | Histórico S1 + benchmarks BIM|
| **Tempo de análise de variantes** | 10x mais rápido | 1 dia vs 2 semanas manual |
| **Detecção de inconsistências** | +40% | Validação automática vs revisão manual |
| **Retrabalho evitado** | 8-12% do orçamento | Mudanças rastreáveis = responsabilidade clara |

---

## 3. INTAKE QUESTÕES — Triggers do Manta 00 (Maestro)

Ativar Manta 03-S1-BIM-COST quando mencionar:

- "Civil 3D", "volumes de movimento de terra", "CBUQ", "greide"
- "Orçamento de rodovia", "SICRO", "custo estimado"
- "Sensibilidade", "mudança de projeto", "impacto orçamentário"
- "Variante", "trevo vs diamante", "geometria alternativa"
- "BIM", "extração de quantidades", "rastreabilidade de mudanças"

---

## 4. INTEGRAÇÃO COM EIXO 1

| Agente | Fluxo | Dados |
|--------|-------|-------|
| **Manta 05** (Orçamento) | BIM-COST → SICRO pipeline | Volumes automatizados + composições |
| **Manta 06** (Modelagem) | Cenários paramétricos | Mudanças geométricas em tempo real |
| **Manta 07** (Cronograma) | Rastreamento de impacto | Mudança CAD → efeito em precedência de tarefas |
| **Manta 15** (Advisory) | VPL/TIR dinâmico | Custo automático alimenta análise de viabilidade |

---

## 5. RAG SOURCES — Supabase `bim_s1:` (novo)

- Autodesk Civil 3D API documentation (volumes, superfícies, alinhamentos)
- SICRO 2024+ (composições de serviços, preços unitários regionalizados)
- Banco de 50+ projetos S1 (volumes estimado vs realizado, taxa de desvio por região)
- Normas: AACE Class Estimates, SMG Guidelines, DNIT cadernos de especificação
- Publicações: "BIM Cost Estimation in Road Projects" (ASCE, 2024), caso de sucesso Rodovia XX (SP)

---

## 6. ROADMAP

| Fase | Período | Entregável |
|------|---------|------------|
| **Setup** | Q3 2026 | Parser Civil 3D → SICRO mapper + validador de volumes |
| **Sensibilidade** | Q4 2026 | Calculadora paramétrica (greide, alinhamento, camadas) |
| **Variantes** | Q1 2027 | Simulação automática + ranking de opções |
| **Viabilidade** | Q2 2027 | Integração VPL/TIR com dados BIM |

---

## 7. ARQUITETURA TÉCNICA

**Pipeline (simplificado):**

```
[Arquivo .dwg Civil 3D]
        ↓
[Extrator de superfícies/alinhamentos]
        ↓
[Parser SICRO → Mapeador de composições]
        ↓
[Calculadora de volumes + Interpolador de preços]
        ↓
[Sensibilidade paramétrica + Gerador de variantes]
        ↓
[Relatório executivo + Alertas de inconsistência]
        ↓
[Feedback loop: mudança no CAD → reprocessamento automático]
```

**Inputs:** Arquivo .dwg (Civil 3D), parâmetros de projeto (região, data-base SICRO, tolerâncias)

**Processing:** Extração de volumes, validação cruzada, cost mapping, análise de sensibilidade

**Outputs:** Planilha Excel estruturada + relatório executivo (PDF) + arquivo de rastreamento de versões

**Gate humano:** Revisor S1 aprova variante eleita antes de lockdown orçamentário

---

## 8. PRÓXIMOS PASSOS

- [ ] Documentar API Autodesk + exemplos de parsing
- [ ] Criar 20 templates SICRO-mapeados (terraplenagem, CBUQ, drenagem, etc.)
- [ ] Validar com 3 projetos piloto S1 (SP, MG, BA)
- [ ] Treinar equipe Manta 05 no novo pipeline
- [ ] Gate: aprovação MN + assinatura de SLA de accuracy (±10% vs realizado)
