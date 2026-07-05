# Agent Library — Manta 02 Contratual (manta-02, contratual)

Referência canônica de trabalho do agente **Contratual** (Sonnet, tier default).
Se o `.claude/agents/agente-contratual.md` é o **como o agente pensa**, este
arquivo é o **com o que o agente trabalha**.

**Escopo:** análise/redação de contratos, aditivos, matriz de riscos,
cláusulas de reequilíbrio. Opera adjacente ao **01 Claims** (mesmos KEs de
reequilíbrio) e ao **15 Advisory** (para pareceres).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                          | Uso                                            |
|------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/03_Contratos/`                    | Contrato-mãe, aditivos — leitura+escrita       |
| `03_Projetos/{segmento}/{obra}/03_Contratos/Matriz_Riscos/`      | Matriz de riscos — leitura+escrita             |
| `03_Projetos/{segmento}/{obra}/04_Correspondencias/`             | Trocas contratuais — leitura                   |
| `04_IA/Manta-Maestro/Modelos/Contratual/`                        | Documentos-modelo — só leitura                 |
| `04_IA/Manta-Maestro/Teses/B5/`                                  | KEs de EEF/reequilíbrio (compartilhados 01)    |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                        | Origem                          |
|-------------|--------------------------------------------------|---------------------------------|
| CTR-M-001   | Aditivo contratual — cláusula de reequilíbrio    | Modelo Manta + KE-035           |
| CTR-M-002   | Matriz de riscos — concessão rodoviária          | FGV EEF-Rodovias + KE-036       |
| CTR-M-003   | Cláusula de suspensão / fato do príncipe          | Lei 8.987/95 + Lei 14.133/2021  |
| CTR-M-004   | Termo de reajuste vs revisão contratual           | TCE-MG 2023 + KE-038            |
| CTR-M-005   | Nota técnica — variação cambial em contrato       | TCE-MG 2023 + KE-038            |

## 3. Knowledge Elements

**0 KEs próprios.** Contratual opera sobre KEs de **01 Claims** (B5
reequilíbrio: KE-034, 035, 036, 037, 038) e de **15 Advisory** (mesmo
conjunto). Retrieval cross-agent:

```sql
select ke_codigo, descricao
from knowledge_extractions
where '01' = any(agentes_destino) or '15' = any(agentes_destino)
  and tipo in ('norma','metodo')
order by grader_score desc;
```

Cobertura implícita: Lei 8.987/95, Lei 14.133/2021, Lei 13.303/16,
Decreto 7.983/2013, Resolução ANTT 5.850/2019, 11 parâmetros TCE-SC.

## 4. Skills disponíveis

- `contratual.review_clause` — analisa cláusula contra base normativa (KE-035..038)
- `contratual.matrix_gen` — gera matriz de riscos a partir de contrato + segmento
- `contratual.reequilibrio_clause` — redige aditivo de reequilíbrio (usa CTR-M-001)
- `contratual.reajuste_vs_revisao` — classifica evento como reajuste ou revisão

## 5. Padrões de uso (quando o agente é acionado)

| Gatilho                                            | Rota                              | Saída esperada                                 |
|----------------------------------------------------|-----------------------------------|------------------------------------------------|
| Cliente envia minuta de contrato para análise      | 03_Contratos                      | Parecer + matriz de riscos preenchida          |
| Evento econômico requer aditivo                    | 03_Contratos                      | CTR-M-001 preenchida + fundamentação legal     |
| Solicitação de esclarecimento sobre cláusula       | 03_Contratos + 04_Correspondencias| Nota técnica com base em CTR-M-004/005         |
| Handoff de 01 Claims (pleito exige revisão)        | 09_Pleitos + 03_Contratos         | Cláusula alterada + memória de negociação      |

Handoff frequente: **01 Claims** (pleitos que geram aditivo), **15 Advisory**
(pareceres para stakeholders), **06 Modelagem** (impacto financeiro do
aditivo no FCM).
