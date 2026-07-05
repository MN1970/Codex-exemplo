# Agent Library — Manta 04 Imobiliário (manta-04)

Agente **Imobiliário** (Sonnet, tier default). Escopo: due diligence
imobiliária, matrículas, gravames, análise dominial, servidões, faixa de
domínio em concessões rodoviárias/ferroviárias.

- **Versão:** v1.0 · piloto WF-AKP-001 · 2026-07-05
- **Status:** stub — **0 KEs no MASTER-CATALOG hoje**. Backlog de teses a
  disparar num WF-AKP-002 focado em direito registral + faixa de domínio DNIT/ANTT.

---

## 1. Pastas SharePoint canônicas

| Rota SP                                                             | Uso                                            |
|---------------------------------------------------------------------|------------------------------------------------|
| `03_Projetos/{segmento}/{obra}/07_Imobiliario/`                     | Matrículas, gravames, DDI — L+E                |
| `03_Projetos/{segmento}/{obra}/07_Imobiliario/Faixa_Dominio/`       | Faixa de domínio, servidões                    |
| `04_IA/Manta-Maestro/Modelos/Imobiliario/`                          | Documentos-modelo — só leitura                 |

## 2. Documentos-modelo (starter kit)

| ID          | Documento                                                | Origem                          |
|-------------|----------------------------------------------------------|---------------------------------|
| IMB-M-001   | DDI (Due Diligence Imobiliária) — template                 | Modelo Manta                    |
| IMB-M-002   | Análise dominial — matrícula + gravames                    | Modelo Manta                    |
| IMB-M-003   | Termo de servidão administrativa                           | Lei 4.132/1962 + DNIT PRO 09    |
| IMB-M-004   | Cadastro de faixa de domínio — obra rodoviária             | DNIT PRO 09/2010                |

## 3. Knowledge Elements

**0 KEs próprios.** Backlog documentado — quando WF-AKP-002 ingerir bloco de
direito imobiliário/registral, atualizar aqui.

## 4. Skills disponíveis

- `imobiliario.ddi` — gera IMB-M-001 a partir de matrículas
- `imobiliario.matricula_parse` — extrai estrutura de matrícula digitalizada
- `imobiliario.faixa_dominio` — cadastro de FD para obra linear

## 5. Padrões de uso

| Gatilho                                             | Rota                              | Saída esperada                                    |
|-----------------------------------------------------|-----------------------------------|---------------------------------------------------|
| DD imobiliária de gleba (novo empreendimento)        | 07_Imobiliario                    | IMB-M-001 preenchida + parecer sobre riscos       |
| Concessão rodoviária — cadastro FD                   | 07_Imobiliario/Faixa_Dominio      | IMB-M-004 por trecho km-a-km                      |
| Desapropriação em obra                               | 07_Imobiliario                    | IMB-M-003 + valor de indenização                  |

Handoff frequente: **02 Contratual** (cláusulas de servidão), **15 Advisory**
(pareceres externos), verticais S1/S3/S9 (obras lineares).
