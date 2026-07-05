# Agent Library — Manta 06 Modelagem (manta-06)

Referência canônica de trabalho do agente **Modelagem** (Sonnet/Opus híbrido).
Se o `.claude/agents/agente-modelagem.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** modelagem financeira de concessões (FCM, TIR, VPL), impacto de
aditivos, valuation, análise de sensibilidade. Cobre 2 KEs próprios +
consome do 15 Advisory quando precisa de fundamentação jurídico-econômica.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/06_Modelagem/`                       | Modelos financeiros ativos — leitura+escrita   |
| `03_Projetos/{segmento}/{obra}/06_Modelagem/FCM/`                    | Fluxo de Caixa Marginal por aditivo            |
| `03_Projetos/{segmento}/{obra}/06_Modelagem/Sensibilidade/`         | Análises de cenário (P50/P80/P95)              |
| `04_IA/Manta-Maestro/Modelos/Modelagem/`                            | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B5/`                                     | PDFs originais dos KEs — só leitura            |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| MOD-M-001   | FCM padrão — concessão rodoviária (ANTT)                 | KE-035 + KE-037                 |
| MOD-M-002   | Análise de renegociação — matriz de risco alterada        | FGV EPGE + KE-039               |
| MOD-M-003   | Valuation de concessão — DCF + WACC ajustado              | Modelo Manta                    |
| MOD-M-004   | Sensibilidade tarifa × TIR — Monte Carlo                  | Handoff com 07 Cronograma       |

## 3. Knowledge Elements (2 KEs próprios + KEs adjacentes)

| KE     | Tipo         | Uso operacional                                              |
|--------|--------------|--------------------------------------------------------------|
| KE-037 | metodo       | Procrofe fases I-III — Fluxo de Caixa Marginal                |
| KE-039 | metodo       | Renegociação vs reequilíbrio — teoria FGV/BNDES               |

Retrieval expandido (cross-agent com 01, 02, 15):

```sql
select ke_codigo, descricao from knowledge_extractions
where '06' = any(agentes_destino) or (
      '15' = any(agentes_destino) and tipo in ('metodo','parametro','norma')
   )
order by grader_score desc;
```

Cobertura via 15 Advisory: KE-024, 034-038, 043-047 (marco saneamento, ANTT,
TCE-MG, casos privatização).

## 4. Skills disponíveis

- `modelagem.fcm_calc` — monta FCM a partir de aditivo (usa MOD-M-001)
- `modelagem.tir_delta` — impacto de evento na TIR original vs realinhada
- `modelagem.wacc_ajustado` — WACC por segmento + risco-país
- `modelagem.sensitivity_mc` — Monte Carlo em variáveis-chave (tarifa, volume, custo)

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Aditivo contratual (handoff 02 Contratual)          | 06_Modelagem/FCM                  | MOD-M-001 preenchida + impacto na TIR             |
| Cliente pergunta viabilidade de nova concessão       | 06_Modelagem                       | MOD-M-003 + análise de sensibilidade              |
| Renegociação em curso                                | 06_Modelagem                       | MOD-M-002 + comparativo com matriz atual          |
| Handoff de 05 Orçamento (orçamento definitivo)      | 05_Orcamento + 06_Modelagem       | Modelo alimentado com WBS orçado                  |

Handoff frequente: **02 Contratual** (aditivos), **05 Orçamento** (curva de
investimento), **15 Advisory** (fundamentação de FCM em parecer), **01 Claims**
(quando pleito exige demonstração de desequilíbrio).
