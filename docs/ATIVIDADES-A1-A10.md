# Eixo A — Atividades Horizontais (A1–A10)

**Manta Maestro** — documentação formal do Eixo 1/Eixo A do mapa de
agentes (ver `CLAUDE.md` — "Eixo 1 — Horizontais").

Versão: **v1.0** (2026-07-31) · Status: rascunho para revisão MN —
**gate humano pendente** antes de publicar no SharePoint
(`ARQUITETURA-AGENTES-IA.md`).

## 0. Propósito e escopo

As **10 atividades horizontais (A1–A10)** atravessam todos os
segmentos verticais (S1–S11). Uma atividade horizontal é um **tipo de
entregável/processo**, não um segmento de engenharia — o mesmo A-code
se aplica igualmente a uma proposta de rodovia ou de barragem. Cada
atividade é operada por um agente Manta específico, mas o contrato de
entrada/saída é o mesmo independente do segmento vertical que a
invoca.

### Tabela-resumo

| Código | Atividade | Agente responsável | Status |
|--------|-----------|--------------------|--------|
| A1 | Proposta | Manta 13 (bd) + Manta 14 (apresentações) | ✅ Definida |
| A2 | Quantidades | Manta 03-Sx (vertical) + skills de takeoff | ✅ Definida |
| A3 | Orçamento | Manta 05 (orcamento) | ✅ Definida |
| A4 | Modelagem financeira | Manta 06 (modelagem) | ✅ Definida |
| A5 | Cronograma | Manta 07 (cronograma) | ✅ Definida |
| A6 | Contratual | Manta 02 (contratual) | ✅ Definida |
| A7 | Claims | Manta 01 (claims) | ✅ Definida |
| A8 | Advisory | Manta 15 (advisory) | ✅ Definida |
| A9 | Regulatório | **sem agente dedicado no registry v4.2** | 🔴 **TODO — RUBRICA PENDENTE** |
| A10 | Risco | Manta 15 (advisory) coordena; inputs de A1–A9 e S1–S11 | ⚠️ Sem Manta-code próprio |

> **Gap conhecido (A9 e A10):** o `CLAUDE.md` v4.2 (Eixo 1) não lista
> agente "regulatório" nem "risco" no mapa de 20 agentes. Ambas as
> seções abaixo são tratadas como rascunho/coordenação até decisão e
> registro formal por MN.

Template de cada seção: **Descrição · Quando usar · Quem produz ·
Entradas · Saídas · Critérios de aceitação · Handoffs**.

---

## A1 — Proposta

**Descrição.** Primeira peça formal a cliente/dono de ativo:
entendimento do problema, abordagem técnica, equipe, prazo e
enquadramento comercial (técnica + comercial).

**Quando usar.** Resposta a edital/licitação, prospecção ativa (BD),
renovação/ampliação de escopo em contrato vigente. Gatilhos: "proposta",
"RFP", "edital", "TDR", "escopo de serviços", "manifestação de
interesse".

**Quem produz.** **Manta 13 (bd)** qualifica a oportunidade e define
equipe/pricing macro; **Manta 14 (apresentações)** materializa em
documento no padrão visual Manta. Suporte de Manta 15 (posicionamento)
e do vertical do segmento (conteúdo técnico-normativo). Skills:
`proposta-comercial`, `proposta-tecnica-rod`, `ler-edital`, `mk-manta`.

**Entradas.** Edital/TDR ou briefing; segmento indicado (S1–S11);
restrições comerciais (teto de preço, prazo de resposta, habilitação);
histórico de relacionamento.

**Saídas.** Briefing estruturado (objeto, cliente, prazo, segmento,
riscos preliminares); análise preliminar (enquadramento técnico,
normas aplicáveis, benchmarks); indicação de risco (semáforo,
antecipando o A10 completo); documento final de proposta.

**Rubrica (pesos):** aderência ao edital 30% · clareza da abordagem
técnica 25% · indicação de risco 20% · qualidade de apresentação
(`padrao-manta`) 15% · viabilidade de prazo/equipe 10%.

**Critérios de aceitação.**
- [ ] Objeto citado literalmente, sem paráfrase que mude o sentido.
- [ ] Escopo delimitado por fase do ciclo de vida (Eixo 3: 1–8).
- [ ] Segmento(s) vertical(is) corretos, com handoff explícito se >1.
- [ ] Indicação de risco preliminar presente.
- [ ] Gate humano MN antes de envio externo (efeito comercial vinculante).

**Handoffs.** → A3 (pricing detalhado) · → A5 (cronograma macro) ·
→ A10 (evolução da indicação de risco) · → A6 (minuta pós-adjudicação).

---

## A2 — Quantidades

**Descrição.** Levantamento de quantitativos (extensões, áreas,
volumes, unidades de serviço) a partir de projeto (CAD/BIM/EVTEA) para
alimentar orçamento (A3) e cronograma (A5).

**Quando usar.** Recebimento de projeto básico/executivo (DWG, DXF,
IFC, RVT, PDF); leitura de EVTEA/edital (quantitativos preliminares);
due diligence (conferência declarado × as-built). Gatilhos:
"quantitativo", "takeoff", "volume de corte/aterro", "memória de
cálculo".

**Quem produz.** **Agente vertical do segmento (Manta 03-Sx)** é dono
do conteúdo técnico; camada **autodesk-toolkit** lê DXF/DWG/IFC sem
depender de software proprietário. Skills: `cad-quantifier` (rodovias,
a partir de JSON do `cad-reader`), `evtea-quantifier` (14 disciplinas
a partir de `params.json`), `balanco-rodoviario-orquestrador`
(terraplenagem/pavimentação, Brückner), `cqp-cad-bridge` (ponte de
extração p/ validação de conformidade).

**Metodologia.** (1) Ingestão do arquivo fonte; (2) classificação
automática do tipo de desenho/disciplina; (3) takeoff — extensões,
raios, larguras, áreas (m²), volumes (m³, médias ou Brückner);
(4) validação cruzada contra memorial e faixas de plausibilidade;
(5) vinculação a código SICRO/SINAPI sugerido (handoff para A3);
(6) emissão de XLSX por disciplina com memória de cálculo auditável.

**Entradas.** Projeto CAD/BIM ou PDF; memorial descritivo (quando
houver); seções típicas/perfil longitudinal ou peça técnica
equivalente por segmento (batimetria, PCN, plantas de forma etc.).

**Saídas.** Planilha XLSX de quantitativos com memória de cálculo;
JSON estruturado para consumo por A3; lista de pendências/premissas
assumidas.

**Critérios de aceitação.**
- [ ] Todo item rastreável ao desenho/folha de origem.
- [ ] Unidades consistentes com a disciplina.
- [ ] Volumes conferem com método declarado e diagrama de massa.
- [ ] Nenhum item inventado — pendências marcadas explicitamente.
- [ ] `aluci-guard` rodado quando alimenta laudo/claim/orçamento formal.

**Handoffs.** → A3 (JSON de quantidades) · → A5 (produtividade × prazo)
· → A7 (base de comparação contratado × executado) · ← A1 (precisão
menor em fase de estudo prévio, sinalizada como tal).

---

## A3 — Orçamento

**Descrição.** Precificação dos quantitativos (A2) por composição de
custo unitário (CCU) — SICRO/SINAPI ou referência de mercado — e
consolidação em planilha orçamentária por disciplina, com BDI e
encargos sociais.

**Quando usar.** Sempre que houver quantitativo fechado ou preliminar;
elaboração de proposta comercial (A1); conferência de orçamento de
edital; suporte a claims (A7). Gatilhos: "orçamento", "SICRO",
"SINAPI", "BDI", "custo unitário".

**Quem produz.** **Manta 05 (orcamento)**. Skills: `sicro-completo`,
`sicro-composicoes`, `sicro-similaridade` (matching semântico
vetorial para serviço não tabelado).

**Integração SICRO/SINAPI.** SICRO (DNIT) é fonte primária para
rodovias/OAE/ferrovia federal, com composições regionais por UF.
SINAPI (Caixa/IBGE) cobre edificações, saneamento urbano e obras não
cobertas pelo SICRO. Serviços sem correspondência oficial (obra
portuária, aeroportuária específica, barragem CFRD) usam **CCU
própria** fundamentada em cotação de mercado, sinalizada como
não-oficial. `sicro-similaridade` sugere o código mais próximo via
busca vetorial (pgvector/Supabase) quando não há match 1:1.

**Estrutura de orçamento.** Capa (objeto, data-base, fonte de preços)
→ planilha por disciplina (item, código, descrição, unidade,
quantidade, custo unitário, total) → BDI discriminado (impostos,
administração central, lucro, riscos, garantias) → encargos sociais →
resumo executivo por disciplina → curva ABC.

**Entradas.** JSON/planilha de quantidades (A2); data-base de preços;
BDI e encargos aplicáveis.

**Saídas.** Planilha orçamentária completa + resumo; curva ABC;
memória de cálculo de BDI/encargos; relatório de itens sem
correspondência oficial.

**Critérios de aceitação.**
- [ ] Toda linha rastreável a um item de A2 — nenhum valor solto.
- [ ] Código SICRO/SINAPI citado existe na base vigente (`aluci-guard`
  audita especificamente códigos SICRO fabricados).
- [ ] BDI discriminado, não percentual único sem abertura.
- [ ] Data-base explicitada (mês/ano).
- [ ] Itens sem base oficial sinalizados como CCU própria.

**Handoffs.** ← A2 · → A4 (fluxo de custos) · → A5 (curva S) · → A7
(orçado × incorrido, núcleo de qualquer reequilíbrio).

---

## A4 — Modelagem financeira

**Descrição.** Fluxo de caixa projetado, indicadores de retorno (VPL,
TIR, payback) e análise de cenários/sensibilidade — para decisão de
investimento ou acompanhamento de reequilíbrio.

**Quando usar.** EVTE/viabilidade; modelagem de proposta em leilão
(ANEEL/ANTT/ANTAQ/ANAC); reequilíbrio econômico-financeiro (suporte a
A7); due diligence de M&A. Gatilhos: "modelagem financeira", "fluxo de
caixa", "VPL", "TIR", "payback", "cenário", "WACC".

**Quem produz.** **Manta 06 (modelagem)**, tier Sonnet/Opus (Opus para
modelos complexos — múltiplos cenários, concessão longa, M&A). Suporte
de A3 (fluxo de custos) e A5 (faseamento temporal).

**Componentes.** Fluxo de caixa (receitas — tarifa/RAP/contraprestação
/subsídio — e custos CAPEX/OPEX faseados) · VPL descontado a WACC/TMA
· TIR comparada ao WACC/TMA · payback simples e descontado · cenários
(base/otimista/pessimista + riscos regulatórios/mercado) · análise de
sensibilidade (tornado chart).

**Entradas.** Orçamento consolidado (A3); cronograma/faseamento (A5);
premissas macroeconômicas (inflação, câmbio, taxa de desconto);
estrutura de receita do segmento.

**Saídas.** Modelo financeiro (premissas, fluxo de caixa, resultados,
cenários); memorando executivo; tornado chart.

**Critérios de aceitação.**
- [ ] Toda premissa macro/regulatória datada e com fonte.
- [ ] Taxa de desconto justificada, não arbitrária.
- [ ] Ao menos 3 cenários presentes.
- [ ] Sensibilidade cobre as variáveis de maior materialidade.
- [ ] CAPEX/OPEX rastreável a A3; faseamento rastreável a A5.

**Handoffs.** ← A3, A5 · → A1 (suporte a proposta/leilão) · → A8
(recomendação estratégica) · → A10 (cenários pessimistas alimentam
risco financeiro).

---

## A5 — Cronograma

**Descrição.** Sequenciamento de atividades, dependências, alocação de
recursos, nivelamento e caminho crítico. Ferramenta primária: MS
Project (também Primavera P6 via `cronograma-toolkit`).

**Quando usar.** Cronograma macro para proposta (A1); detalhamento
executivo pós-contrato; replanejamento após atraso/aditivo; análise de
atraso para claims (A7). Gatilhos: "cronograma", "MS Project",
"Primavera", "XER", "Gantt", "caminho crítico", "baseline".

**Quem produz.** **Manta 07 (cronograma)**. Skills:
`cronograma-toolkit` (leitura/conversão/clone XER ↔ MSP XML, Gantt
HTML), `xer-msp-toolkit`, `xer-p6-analytics` (atrasos, folgas, marcos).

**Metodologia.** EAP/WBS alinhada a A2/A3 → sequenciamento
FS/SS/FF/SF com lags justificados → duração = produtividade ×
quantidade → alocação de recursos com checagem de superalocação →
nivelamento sem violar prazo contratual → caminho crítico monitorado
continuamente → linha de base congelada → curva S física e financeira
(cruzada com A3/A4).

**Entradas.** Quantitativos (A2) e orçamento (A3); restrições
contratuais de prazo; produtividade de referência; recursos
disponíveis.

**Saídas.** Cronograma detalhado (MPP/XER) com EAP, dependências,
recursos e baseline; Gantt visual; relatório de caminho crítico;
curva S física e financeira.

**Critérios de aceitação.**
- [ ] Duração de toda atividade justificada (produtividade ×
  quantidade), não estimada arbitrariamente.
- [ ] Dependências logicamente consistentes (sem loops).
- [ ] Caminho crítico identificado e explicitado.
- [ ] Recursos nivelados sem superalocação não resolvida.
- [ ] Linha de base preservada; alterações via change control.

**Handoffs.** ← A2, A3 · → A4 (faseamento do fluxo de caixa) · → A7
(peça técnica central de claims de atraso — ver `conclusao-janelas`) ·
→ A10 (atrasos no caminho crítico são risco materializado).

---

## A6 — Contratual

**Descrição.** Elaboração/revisão de peças jurídico-contratuais:
minutas de contrato, termos aditivos, TDP e cláusulas específicas
(reajuste, garantias, matriz de risco, condições suspensivas).

**Quando usar.** Elaboração de minuta de contrato/edital; negociação
de termo aditivo; revisão de cláusulas de risco/reajuste/garantia;
suporte jurídico a claims. Gatilhos: "contrato", "aditivo", "TDP",
"cláusula", "minuta", "condição suspensiva".

**Quem produz.** **Manta 02 (contratual)** — assessora, não substitui
jurídico constituído nas peças que exigem assinatura profissional.

**Peças cobertas.** Contrato (objeto, prazo, valor, obrigações, matriz
de risco, garantias, penalidades, rescisão) · aditivos (prazo, valor/
reequilíbrio, escopo — referenciando Lei 8.666/93, Lei 14.133/2021 ou
regulamento próprio, e a cláusula-base alterada) · TDP (ajustes
simplificados) · cláusulas específicas (reajuste, garantia, força
maior, matriz de risco RDC/PPP/concessão, condições precedentes).

**Entradas.** Objeto/escopo (via A1 ou já contratado); regime legal
aplicável; para aditivos: cláusula-base, justificativa técnica (A2/A3/
A5), limite legal de alteração.

**Saídas.** Minuta de contrato/aditivo com cláusulas numeradas e
referenciadas ao regime legal; parecer de enquadramento do
instrumento; matriz de risco contratual (insumo direto de A10).

**Critérios de aceitação.**
- [ ] Toda cláusula referenciada a dispositivo legal real
  (`aluci-guard` obrigatório).
- [ ] Limite legal de aditivo verificado explicitamente quando
  aplicável.
- [ ] Matriz de risco contratual explícita.
- [ ] Revisão por jurídico habilitado antes de assinatura.
- [ ] Gate humano (MN/jurídico do cliente) antes de envio/assinatura.

**Handoffs.** ← A1 (pós-adjudicação) · ← A2/A3/A5 (justificativa de
aditivos) · → A7 (cláusula é ponto de partida de todo pleito) · → A9
(licença como condição suspensiva) · → A10 (matriz de risco
contratual).

---

## A7 — Claims

**Descrição.** Estruturação e sustentação técnico-financeira de
pleitos (reequilíbrio, revisão de prazo, indenização), cobrindo as
variantes por tipo de causa: extra/adicional, atraso/disrupção, força
maior/fato do príncipe.

**Quando usar.** Evento que rompe premissas de proposta/contrato
(ver `conclusao-janelas` — "quebra das premissas" como um dos três
eixos de conclusão); serviço extra não previsto; atraso não imputável
à contratada; evento de força maior. Gatilhos: "claim", "pleito",
"reequilíbrio", "atraso", "disrupção", "força maior",
"improdutividade".

**Quem produz.** **Manta 01 (claims)**, tier **Opus** por padrão
(maior exigência analítica e risco reputacional/financeiro). Suporte
intenso de A2 e A5 — claim sem lastro quantitativo/cronológico não se
sustenta. Skill `conclusao-janelas` para a conclusão narrativa por
grupo de serviço (três eixos: improdutividade como consequência,
cascata de disrupção, quebra de premissas).

**Variantes.**
- **Extra/adicional** — comparação contratado (A3) × executado (A2),
  com memória de cálculo do adicional.
- **Atraso** — linha de base (A5) × realizado, caminho crítico
  afetado, cascata de disrupção.
- **Força maior/fato do príncipe** — nexo causal entre evento externo
  e impacto medido, com evidência documental (boletim meteorológico,
  decreto, ato normativo).

**Entradas.** Contrato/cláusula aplicável (A6); quantitativo
contratado × executado (A2/A3); cronograma linha de base × realizado
(A5); evidências do evento gerador (RDO, correspondência, laudo).

**Saídas.** Dossiê de claim (narrativa, quantum, memória de cálculo,
cronologia, conclusão por grupo de serviço) + anexos técnicos.

**Critérios de aceitação.**
- [ ] Nexo causal explícito entre evento e impacto — não apenas
  correlação temporal.
- [ ] Quantum sustentado por memória de cálculo rastreável a A2/A3.
- [ ] Cronologia consistente — checagem `consist-guard` obrigatória.
- [ ] Toda norma/lei/cláusula citada verificada via `aluci-guard`.
- [ ] Conclusão nos três eixos obrigatórios (padrão GR), sem inverter
  causa e consequência.
- [ ] Gate humano MN antes de protocolo formal.

**Handoffs.** ← A2, A3, A5, A6 · → A4 (quantum relevante impacta o
modelo financeiro) · → A8 (posicionamento estratégico em negociação/
arbitragem) · → A10 (claim materializado é risco que deveria estar na
matriz).

---

## A8 — Advisory

**Descrição.** Aconselhamento técnico-estratégico de alto nível:
parecer técnico formal, análise de posicionamento (aceitar/recusar
oportunidade, M&A), suporte a decisões de investimento.

**Quando usar.** Parecer técnico formal necessário; decisão
estratégica de negócio; negociação de alto valor. Gatilhos: "parecer",
"advisory", "análise estratégica", "recomendação", "due diligence",
"M&A".

**Quem produz.** **Manta 15 (advisory)**, tier Sonnet/Opus (Opus para
M&A e pareceres de alto risco). Consome outputs de praticamente todos
os demais A-codes/S-codes (advisory é atividade de síntese). Skill
`mk-manta` como apoio metodológico (raciocínio estilo MBB).

**Entradas.** Pergunta/decisão específica; todo contexto técnico
relevante já produzido; restrições de prazo/sigilo.

**Saídas.** Parecer técnico (pergunta, análise, conclusão,
recomendação rastreável às fontes); análise estratégica (memorando
executivo com opções, trade-offs, recomendação).

**Critérios de aceitação.**
- [ ] Pergunta/decisão explicitada no início — nunca implícita.
- [ ] Toda conclusão rastreável a uma fonte (dado, cálculo, norma).
- [ ] Trade-offs das opções alternativas explicitados.
- [ ] Nível de confiança/incerteza declarado quando relevante.
- [ ] `aluci-guard` quando cita normas/leis/referências técnicas.
- [ ] Gate humano MN antes de entrega a cliente ou uso em investimento.

**Handoffs.** ← A1, A3, A4, A6, A7 e qualquer segmento S1–S11 · → A10
(recomendação deve vir com leitura de risco associada) · → decisão
executiva (fora do escopo dos A-codes).

---

## A9 — Regulatório

> ⚠️ **RUBRICA PENDENTE — TODO.** Esta atividade **não possui agente
> Manta dedicado** no `CLAUDE.md` v4.2. O conteúdo abaixo é um
> **rascunho de enquadramento** produzido para preencher a lacuna
> identificada nesta tarefa e **não deve ser tratado como rubrica
> aprovada** até revisão MN e registro formal no `CLAUDE.md` master
> (novo Manta-code, ou decisão explícita de manter distribuído pelos
> verticais).

**Descrição (rascunho).** Enquadramento legal-regulatório de um
projeto/ativo: licenças e aprovações necessárias, agências
reguladoras competentes, compliance setorial, status de processos em
curso.

**Quando usar (rascunho).** Licenciamento ambiental (LP/LI/LO);
enquadramento em agência setorial (ANEEL, ANTT, ANTAQ, ANAC, ANA,
agências estaduais); enquadramento em marco legal (Lei 14.026, marco
de transmissão ANEEL, RBAC, PNSB); due diligence regulatória.
Gatilhos candidatos: "licença ambiental", "outorga", "enquadramento
regulatório", "compliance setorial", "LP/LI/LO".

**Quem produz (TODO — confirmar com MN).** Hoje, sem agente
horizontal dedicado, o enquadramento regulatório é produzido **de
forma distribuída** dentro de cada vertical (Manta 03-S8/saneamento
cita Lei 14.026/ANA; S9/energia cita ANEEL/ONS/EPE; S6/portos cita
ANTAQ; S7/aeroportos cita ANAC/ICAO; S10/barragens cita PNSB/ANM),
com suporte pontual de Manta 02 (condição suspensiva contratual) e
Manta 15 (quando vira decisão estratégica).

**Recomendação para decisão MN:** avaliar se compensa (a) criar
Manta-code horizontal dedicado, consolidando o conhecimento hoje
espalhado pelos verticais, ou (b) manter distribuído e formalizar esta
seção como guia de referência cruzada. Enquanto não decidido, tratar
A9 como **gap conhecido do registry**, não como atividade descoberta —
o conhecimento existe, só não está consolidado sob um A-code único.

**Entradas (rascunho).** Segmento/vertical (S1–S11); localização
(jurisdição — especialmente relevante para operações fora do Brasil,
ex. AySA/Argentina); fase do ciclo de vida (licenciamento concentra-se
nas fases 1–4).

**Saídas (rascunho).** Checklist de licenças/aprovações com órgão e
status; parecer de enquadramento; cronograma de obtenção de licenças
(interface direta com A5).

**Critérios de aceitação (rascunho, sujeitos a revisão).**
- [ ] Toda licença/norma citada existe de fato (`aluci-guard`).
- [ ] Órgão/agência competente corretamente identificado por
  jurisdição.
- [ ] Status do processo explicitado com data de atualização.
- [ ] **[TODO]** Definir critério de completude mínima — depende de
  decisão MN sobre escopo da atividade.

**Handoffs (rascunho).** ← todos os verticais S1–S11 · → A6 (licença
como condição suspensiva) · → A5 (prazo de licença no caminho
crítico) · → A10 (risco regulatório como categoria própria).

---

## A10 — Risco

**Descrição.** Consolidação de riscos do projeto/contrato em matriz
5×5 (probabilidade × impacto), com planos de mitigação/contingência.
É atividade de **síntese transversal** — recebe insumos de todos os
demais A-codes e verticais S1–S11, sem produzir conteúdo
técnico-primário próprio.

> Nota de gap: como A9, **A10 não tem Manta-code próprio** no
> `CLAUDE.md` v4.2. É tratada como processo de consolidação
> coordenado por Manta 15 — não interpretar como criação de agente
> novo sem aprovação/registro formal.

**Quando usar.** Abertura de projeto/proposta (a partir da indicação
preliminar de A1); revisão periódica em obra (fase 4); antes de
decisão estratégica (A8); após materialização de risco (A7), para
atualizar risco residual. Gatilhos: "matriz de risco", "5x5",
"mitigação", "contingência", "risk register".

**Quem produz.** **Manta 15 (advisory)** coordena a consolidação, mas
**cada risco é originado por quem detém o conhecimento técnico**:
risco técnico → vertical do segmento; risco de prazo → A5; risco
financeiro → A4; risco contratual → A6; risco regulatório → A9 (ver
gap); risco de reequilíbrio → A7.

**Estrutura da matriz 5×5** (probabilidade × impacto):

| Prob. \ Impacto | 1 Insignificante | 2 Menor | 3 Moderado | 4 Maior | 5 Catastrófico |
|---|---|---|---|---|---|
| **5 Quase certo** | Médio | Alto | Alto | Crítico | Crítico |
| **4 Provável** | Médio | Médio | Alto | Alto | Crítico |
| **3 Possível** | Baixo | Médio | Médio | Alto | Alto |
| **2 Improvável** | Baixo | Baixo | Médio | Médio | Alto |
| **1 Raro** | Baixo | Baixo | Baixo | Médio | Médio |

Probabilidade (1–5) idealmente quantitativa (histórico Manta de
projetos similares); impacto (1–5) avaliado em ao menos duas
dimensões — financeira (% do valor do contrato) e de prazo (dias no
caminho crítico). Classificação final (Baixo/Médio/Alto/Crítico)
determina o nível de aprovação exigido — "Crítico" exige plano de
contingência formal e aprovação MN.

**Mitigação vs. contingência.** Mitigação = ação preventiva antes do
risco se materializar; contingência = ação reativa preparada para
quando ele se materializa. Todo risco Alto/Crítico exige ambos; Médio
exige ao menos mitigação; Baixo pode ser só monitorado.

**Entradas.** Indicação de risco preliminar (A1); insumos técnicos de
todos os A-codes/S-codes relevantes; histórico de riscos
materializados (claims anteriores — A7).

**Saídas.** Matriz de risco 5×5 (risco classificado, dono nomeado,
mitigação, contingência); risk register vivo; resumo executivo dos
riscos Alto/Crítico.

**Critérios de aceitação.**
- [ ] Todo risco tem probabilidade E impacto justificados.
- [ ] Risco Alto/Crítico tem mitigação **e** contingência
  documentadas.
- [ ] Todo risco tem dono nomeado.
- [ ] Matriz revisada em cadência definida (mínimo trimestral em obra
  longa, ou por marco contratual).
- [ ] Riscos materializados (viraram claim) movidos para "realizado"
  com link ao dossiê correspondente, nunca apagados silenciosamente.

**Handoffs.** ← A1, A4 (cenários pessimistas), A5 (atrasos), A6
(matriz contratual), A7 (materializados), A9 (regulatório) · → A8
(insumo central de recomendação estratégica) · → decisão executiva MN
para riscos Crítico.

---

## Consolidação — fluxo de dados entre atividades

| De \ Para | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A1** | — | | | X | X | X | | | | X |
| **A2** | | — | X | | X | X | | | | |
| **A3** | | | — | X | X | | X | | | |
| **A4** | X | | | — | | | X | X | | X |
| **A5** | | | | X | — | | X | | X | X |
| **A6** | | | | | | — | X | | X | X |
| **A7** | | | X | X | | | — | X | | X |
| **A8** | | | | | | | | — | | X |
| **A9** (TODO) | | | | | X | X | | | — | X |
| **A10** | | | | | | | | X | | — |

## Pendências para fechamento (gate humano MN)

- [ ] **A9** — decidir Manta-code dedicado vs. distribuído pelos
  verticais; atualizar `CLAUDE.md` master.
- [ ] **A10** — confirmar Manta 15 como coordenador oficial ou definir
  Manta-code próprio; atualizar `CLAUDE.md` master.
- [ ] Validar rubricas de A1–A8 com os donos de cada Manta-code antes
  de publicar como SKILL.md formal no SharePoint.
- [ ] Após aprovação MN, replicar em
  `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`.

## Histórico de versões

- **v1.0** (2026-07-31) — primeira versão formal do Eixo A (A1–A10), a
  partir do mapa de agentes do `CLAUDE.md` v4.2. A9 e A10 documentadas
  com gap explícito de Manta-code — pendente decisão MN.
