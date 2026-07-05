# Agent Library — Manta 03-S3 Ferrovia (agente-infraestrutura S3)

Agente vertical **Ferrovia**. Cobre via permanente, superestrutura (trilho,
dormente, lastro, AMV), subestrutura, sinalização ferroviária, operação e
concessões (ANTT).

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog: WF-AKP-002
  focado em ANTT ferrovias, ferrovias norte-americanas (AAR) e NBR 16095.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/Ferrovia/{obra}/02_Projeto/{VP,Sub,Sinalizacao}/`      | Projeto — L+E                                  |
| `03_Projetos/Ferrovia/{obra}/06_Operacao/`                          | Operação/manutenção — L+E                      |
| `04_IA/Manta-Maestro/Modelos/Ferrovia/`                             | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| FRV-M-001   | Superestrutura — dimensionamento trilho + dormente        | NBR 7511 / AAR M-960            |
| FRV-M-002   | AMV — tabela de projeto                                   | NBR 7590                        |
| FRV-M-003   | Subestrutura — plataforma + lastro                        | Modelo Manta                    |
| FRV-M-004   | Análise de acesso ferroviário (ANTT)                      | Regulação ANTT                  |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado.

## 4. Skills disponíveis

- `ferrovia.vp_dim` — dimensiona via permanente
- `ferrovia.amv_project` — projeto de AMV
- `ferrovia.antt_check` — verificação regulatória

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| Projeto de ramal / expansão                          | 02_Projeto/*                      | FRV-M-001..003 + fan-out 05 + 07                  |
| DD de concessão ferroviária                          | 12_Advisory                       | Fan-out S3 + 15 + 06 + 02                         |

Handoff frequente: **S1 Rodovias** (interfaces rodoferroviárias), **04
Imobiliário** (faixa de domínio), **15 Advisory** (regulação ANTT).
