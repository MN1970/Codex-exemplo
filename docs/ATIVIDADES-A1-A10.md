# Eixo A — Atividades Horizontais (A1–A10)

**Manta Maestro** — documentação formal do Eixo 1/Eixo A do mapa de
agentes (ver `CLAUDE.md` — "Eixo 1 — Horizontais").

Versão: **v1.0** (2026-07-31)
Autor: bootstrap via sessão Claude Code (Sonnet)
Status: rascunho para revisão MN — **gate humano pendente antes de
publicar no SharePoint** (`ARQUITETURA-AGENTES-IA.md`).

---

## 0. Propósito e escopo

Este documento formaliza as **10 atividades horizontais (A1–A10)** que
atravessam todos os segmentos verticais (S1–S11: Rodovias, OAE,
Ferrovia, Metrô, Túneis, Portos, Aeroportos, Saneamento, Energia,
Barragens, Edificações). Uma atividade horizontal é um **tipo de
entregável/processo**, não um segmento de engenharia — por isso o
mesmo A-code se aplica igualmente a uma proposta de rodovia ou a uma
proposta de barragem.

Cada atividade é operada por um agente Manta específico (ou por um
conjunto de agentes em handoff), mas o **contrato de entrada/saída é o
mesmo independentemente do segmento vertical** que a invoca.

### 0.1 Tabela-resumo

| Código | Atividade | Agente responsável | Status da rubrica |
|--------|-----------|--------------------|--------------------|
| A1 | Proposta | Manta 13 (bd) + Manta 14 (apresentações) | ✅ Definida |
| A2 | Quantidades | Manta 03-Sx (vertical) + skills de takeoff | ✅ Definida |
| A3 | Orçamento | Manta 05 (orcamento) | ✅ Definida |
| A4 | Modelagem financeira | Manta 06 (modelagem) | ✅ Definida |
| A5 | Cronograma | Manta 07 (cronograma) | ✅ Definida |
| A6 | Contratual | Manta 02 (contratual) | ✅ Definida |
| A7 | Claims | Manta 01 (claims) | ✅ Definida |
| A8 | Advisory | Manta 15 (advisory) | ✅ Definida |
| A9 | Regulatório | **sem agente dedicado no registry v4.2** | 🔴 **TODO — RUBRICA PENDENTE** |
| A10 | Risco | Manta 15 (advisory) coordena; inputs de A1–A9 e S1–S11 | ⚠️ Definida como processo transversal (sem Manta-code próprio no `CLAUDE.md` atual) |

> **Nota de gap (A9 e A10):** o `CLAUDE.md` v4.2 (Eixo 1) não lista um
> agente "Manta XX — regulatório" nem "Manta XX — risco" no mapa de 20
> agentes. A9 é tratada abaixo com rubrica **provisória/TODO** e deve
> ser confirmada com MN antes de virar SKILL.md oficial. A10 é
> documentada como processo transversal de consolidação (matriz 5×5),
> sem produção própria de conteúdo técnico — **não deve ser lida como
> confirmação de que existe um "Manta 17 — risco"** enquanto isso não
> for registrado no `CLAUDE.md` master.

### 0.2 Como ler cada seção

Cada atividade segue o mesmo template:

1. **Descrição** — o que é, por que existe.
2. **Quando usar** — gatilhos/palavras-chave que disparam a atividade.
3. **Quem produz** — agente Manta responsável + skills/ferramentas.
4. **Entradas** — o que precisa existir antes de iniciar.
5. **Saídas** — entregáveis formais.
6. **Critérios de aceitação** — checklist objetivo de "pronto".
7. **Metodologia/rubrica** — como o conteúdo é avaliado internamente.
8. **Handoffs** — para quais outras atividades/agentes este entregável
   alimenta ou depende.

---

## A1 — Proposta

### Descrição

Primeira peça formal entregue a um cliente ou dono de ativo,
consolidando entendimento do problema, abordagem técnica proposta,
equipe, prazo e enquadramento comercial. Cobre tanto **proposta
técnica** (escopo, metodologia, equipe-chave, cronograma macro) quanto
**proposta comercial** (preço, condições, forma de pagamento).

### Quando usar

- Resposta a edital de licitação (DNIT, DER, concessionária, agência
  reguladora).
- Prospecção ativa (BD) para cliente privado ou público.
- Renovação/ampliação de escopo em contrato já em curso.
- Palavras-chave de roteamento: "proposta", "RFP", "edital", "TDR",
  "escopo de serviços", "carta-convite", "manifestação de interesse".

### Quem produz

- **Manta 13 (bd / business-dev)** — dono do processo, qualifica a
  oportunidade, define equipe e pricing macro.
- **Manta 14 (apresentacoes)** — materializa a proposta em documento
  formatado (PPTX/DOCX) no padrão visual Manta.
- Suporte pontual de **Manta 15 (advisory)** para posicionamento
  estratégico e de **agente-infraestrutura Sx** (ou vertical
  correspondente) para o conteúdo técnico-normativo do segmento.
- Skills envolvidas: `proposta-comercial`, `proposta-tecnica-rod`,
  `ler-edital` (quando a origem é um edital público), `mk-manta`
  (estruturação estratégica do argumento).

### Entradas

- Edital/TDR ou briefing de oportunidade (reunião, e-mail, RFP).
- Indicação preliminar de escopo e segmento (S1–S11).
- Restrições comerciais conhecidas (teto de preço, prazo de resposta,
  exigências de habilitação).
- Histórico de relacionamento com o cliente (se houver).

### Saídas

- **Briefing estruturado** (1–2 páginas): objeto, cliente, prazo,
  segmento, riscos preliminares de qualificação.
- **Análise preliminar**: enquadramento técnico, referências
  normativas aplicáveis, benchmarks de projetos similares.
- **Indicação de risco** (semáforo simplificado, antecipando o A10
  completo): comercial, técnico, prazo, regulatório.
- Documento de proposta final (técnica + comercial) pronto para
  assinatura/envio.

### Critérios de aceitação

- [ ] Objeto do contrato/edital citado literalmente (sem paráfrase que
  mude o sentido).
- [ ] Escopo delimitado por fase do ciclo de vida (Eixo 3: 1–8).
- [ ] Segmento(s) vertical(is) corretamente identificado(s) — se mais
  de um (ex.: porto + ferrovia de acesso), ambos citados com handoff
  explícito.
- [ ] Indicação de risco preliminar presente (mesmo que qualitativa).
- [ ] Prazo de resposta e forma de entrega confirmados.
- [ ] Revisão MN antes de envio externo (gate humano obrigatório —
  proposta é documento com efeito comercial vinculante).

### Metodologia / rubrica

| Critério | Peso | O que avalia |
|----------|------|---------------|
| Aderência ao edital/briefing | 30% | Todo requisito obrigatório do TDR foi endereçado |
| Clareza da abordagem técnica | 25% | Metodologia proposta é específica ao segmento, não genérica |
| Indicação de risco | 20% | Riscos relevantes antecipados, mesmo que qualitativamente |
| Qualidade de apresentação | 15% | Segue `padrao-manta` (visual, rastreabilidade) |
| Viabilidade de prazo/equipe | 10% | Equipe e cronograma macro são realistas |

### Handoffs

- → **A3 (orçamento)** quando a proposta exige pricing detalhado.
- → **A5 (cronograma)** para o cronograma macro embutido na proposta.
- → **A10 (risco)** quando a indicação de risco preliminar deve
  evoluir para matriz 5×5 completa (proposta vencedora / contrato
  assinado).
- → **A6 (contratual)** após adjudicação, para minuta de contrato.

---

## A2 — Quantidades

### Descrição

Levantamento de quantitativos de engenharia (extensões, áreas,
volumes, unidades de serviço) a partir de projeto (CAD, BIM, EVTEA,
planilha de referência) para alimentar orçamento (A3) e cronograma
(A5). É a atividade que traduz "o projeto" em "quanto tem de cada
serviço".

### Quando usar

- Após recebimento de projeto básico/executivo (DWG, DXF, IFC, RVT,
  PDF de plantas).
- Na leitura de EVTEA/edital, para estruturar quantitativos
  preliminares (fase de estudo prévio).
- Em due diligence (fase 7 do ciclo de vida), para conferência de
  quantitativos declarados vs. as-built.
- Palavras-chave: "quantitativo", "takeoff", "levantamento de
  quantidades", "volume de corte/aterro", "área de pavimento",
  "memória de cálculo".

### Quem produz

- **Agente vertical do segmento (Manta 03-Sx)** — dono do conteúdo
  técnico (o que é "certo" para aquele tipo de obra).
- Camada compartilhada **autodesk-toolkit** — leitura de DXF/DWG/IFC
  sem depender de AutoCAD/Civil3D/Revit instalados.
- Skills especializadas por contexto: `cad-quantifier` (rodoviário, a
  partir do JSON canônico do `cad-reader`), `evtea-quantifier`
  (14 disciplinas rodoviárias a partir de `params.json`),
  `balanco-rodoviario-orquestrador` (terraplenagem/pavimentação —
  Brückner), `cqp-cad-bridge` (ponte de extração para validação de
  conformidade).

### Metodologia (takeoff / BIM / CAD parsing / validação)

1. **Ingestão** — leitura do arquivo fonte (DXF/DWG via
   `autodesk-toolkit`, IFC/RVT para BIM, PDF vetorial ou raster com
   OCR quando necessário).
2. **Classificação automática** — identifica tipo de desenho (planta,
   perfil longitudinal, seção típica, planta de drenagem) e disciplina
   envolvida.
3. **Extração (takeoff)** — aplica heurísticas de domínio por
   disciplina: extensões de eixo, raios de curva, larguras de
   plataforma, áreas de pavimento (m²), volumes de corte/aterro/
   empréstimo/bota-fora (m³ via método das médias ou Brückner).
4. **Validação cruzada** — compara quantitativo extraído contra:
   (a) memorial descritivo do projeto, quando existir; (b) faixas de
   plausibilidade por tipo de obra (ex.: espessura de CBUQ entre 4–15
   cm); (c) consistência dimensional (m vs m² vs m³ coerentes com a
   disciplina).
5. **Vinculação a código de serviço** — sugestão de código SICRO/
   SINAPI correspondente a cada item quantificado (handoff direto para
   A3).
6. **Emissão** — planilha XLSX no padrão Manta, uma aba por
   disciplina, com memória de cálculo auditável (fórmula + referência
   à folha/desenho de origem).

### Entradas

- Projeto em CAD/BIM (DWG, DXF, IFC, RVT) ou PDF de projeto.
- Memorial descritivo (quando existir).
- Seções típicas e perfil longitudinal, no mínimo, para rodovias/
  ferrovias; plantas de forma para OAE/edificações; peça técnica
  equivalente por segmento (batimetria para portos, PCN para
  aeroportos etc.).

### Saídas

- Planilha XLSX de quantitativos por disciplina, com memória de
  cálculo.
- JSON de quantidades estruturado (para consumo automatizado pela A3 —
  orçamento).
- Lista de pendências/premissas assumidas (ex.: "seção tipo aplicada
  uniformemente por falta de seções específicas no trecho X").

### Critérios de aceitação

- [ ] Todo item quantificado rastreável até o desenho/folha de origem.
- [ ] Unidades consistentes com a disciplina (m, m², m³, un, kg).
- [ ] Volumes de terraplenagem conferem com método declarado
  (médias/Brückner) e diagrama de massa, quando aplicável.
- [ ] Nenhum item "inventado" sem base no projeto — pendências e
  premissas explicitamente marcadas, nunca silenciosamente assumidas.
- [ ] Validado por `aluci-guard` quando o quantitativo alimentar laudo/
  claim/orçamento formal (checagem de normas/códigos citados).

### Handoffs

- → **A3 (orçamento)** — entrega direta do JSON de quantidades.
- → **A5 (cronograma)** — quantidades alimentam produtividade × prazo.
- → **A7 (claims)** — quantitativo é a base de comparação
  contratado × executado em pleitos de reequilíbrio.
- ← **A1 (proposta)** — quando o quantitativo é preliminar (fase de
  estudo prévio), a precisão exigida é menor e deve ser sinalizada
  como tal.

---

## A3 — Orçamento

### Descrição

Estruturação do orçamento de obra/serviço a partir dos quantitativos
(A2), com precificação por composição de custo unitário (CCU) —
oficial (SICRO/SINAPI) ou de referência de mercado/regional — e
consolidação em planilha orçamentária por disciplina, com BDI, encargos
sociais e demais rubricas.

### Quando usar

- Sempre que houver quantitativo (A2) fechado ou preliminar precisando
  de precificação.
- Elaboração de proposta comercial (handoff de A1).
- Conferência de orçamento de edital (dado vs. mercado).
- Suporte a claims (A7) — orçamento contratado vs. custo incorrido.
- Palavras-chave: "orçamento", "SICRO", "SINAPI", "composição de
  custo", "BDI", "planilha orçamentária", "custo unitário".

### Quem produz

- **Manta 05 (orcamento)** — dono do processo de precificação.
- Skills de suporte: `sicro-completo`, `sicro-composicoes`,
  `sicro-similaridade` (matching semântico de serviço não tabelado
  para código SICRO mais próximo).

### Integração SICRO/SINAPI

- **SICRO** (Sistema de Custos Referenciais de Obras — DNIT): fonte
  primária para rodovias, OAE, ferrovias federais. Composições
  regionais por UF, atualizadas periodicamente pelo DNIT.
- **SINAPI** (Sistema Nacional de Pesquisa de Custos e Índices da
  Construção Civil — Caixa/IBGE): fonte primária para edificações,
  saneamento urbano, obras não cobertas pelo SICRO.
- Quando o serviço quantificado não tem correspondência direta em
  nenhuma tabela oficial (ex.: obra marítima portuária, obra
  aeroportuária específica, barragem CFRD), aplica-se **composição
  própria** (CCU Manta) fundamentada em cotação de mercado e memória
  de cálculo, sinalizada explicitamente como não-oficial.
- `sicro-similaridade` roda busca vetorial (pgvector/Supabase) sobre a
  base de composições para sugerir o código mais próximo quando o
  quantitativo não bate 1:1 com item tabelado.

### Estrutura de orçamento (padrão Manta)

1. **Capa** — objeto, cliente, data-base, fonte de preços (SICRO mês/
   ano, SINAPI mês/ano, ou CCU própria).
2. **Planilha orçamentária** — por disciplina (uma aba cada),
   colunas: item, código de referência, descrição, unidade,
   quantidade (vinda de A2), custo unitário, custo total.
3. **BDI** — Bonificação e Despesas Indiretas, discriminado (impostos,
   administração central, lucro, riscos, garantias) — nunca aplicado
   como percentual único sem abertura, salvo exigência do edital.
4. **Encargos sociais** — sobre mão de obra, por regime (horista/
   mensalista), conforme convenção coletiva aplicável.
5. **Resumo por disciplina** — consolidação em página única para
   leitura executiva.
6. **Curva ABC** — identificação dos itens de maior peso financeiro,
   para priorização de auditoria/negociação.

### Entradas

- JSON/planilha de quantidades (A2).
- Data-base de preços a adotar (mês/ano SICRO ou SINAPI, ou cotações
  próprias).
- BDI e encargos sociais aplicáveis (contratuais ou de referência de
  mercado).

### Saídas

- Planilha orçamentária completa (XLSX), por disciplina + resumo.
- Curva ABC.
- Memória de cálculo do BDI e dos encargos.
- Relatório de itens sem correspondência oficial (CCU própria),
  com justificativa.

### Critérios de aceitação

- [ ] Toda linha de orçamento rastreável a um item de quantitativo
  (A2) — nenhum valor "solto".
- [ ] Código SICRO/SINAPI citado existe de fato na base vigente
  (checagem obrigatória via `aluci-guard` — código SICRO fabricado é
  um dos padrões que a skill audita especificamente).
- [ ] BDI discriminado, não apenas um percentual aplicado sem abertura.
- [ ] Data-base de preços explicitada (mês/ano).
- [ ] Itens sem base oficial claramente sinalizados como CCU própria.

### Handoffs

- ← **A2 (quantidades)** — insumo direto.
- → **A4 (modelagem financeira)** — orçamento é a base do fluxo de
  custos do modelo financeiro.
- → **A5 (cronograma)** — orçamento por período alimenta a curva S.
- → **A7 (claims)** — comparação orçado × incorrido é o núcleo de
  qualquer pleito de reequilíbrio econômico-financeiro.

---

## A4 — Modelagem financeira

### Descrição

Construção do modelo financeiro do projeto/contrato: fluxo de caixa
projetado, indicadores de retorno (VPL, TIR, payback) e análise de
sensibilidade/cenários. Usado tanto para decisão de investimento
(estudo de viabilidade, leilão de concessão) quanto para
acompanhamento de reequilíbrio contratual.

### Quando usar

- EVTE/viabilidade econômica de novo projeto ou concessão.
- Modelagem de proposta em leilão (ANEEL, ANTT, ANTAQ, ANAC, estadual).
- Reequilíbrio econômico-financeiro de contrato em curso (suporte a
  claims — A7).
- Due diligence de M&A (fase 7 do ciclo de vida) — validação do modelo
  do vendedor/comprador.
- Palavras-chave: "modelagem financeira", "fluxo de caixa", "VPL",
  "TIR", "payback", "cenário", "sensibilidade", "reequilíbrio",
  "EBITDA", "WACC".

### Quem produz

- **Manta 06 (modelagem)** — dono do modelo financeiro.
- Suporte de **Manta 05 (orcamento)** para o fluxo de custos e
  **Manta 07 (cronograma)** para o faseamento temporal dos
  desembolsos/receitas.
- Escalação para tier **Opus** em modelos complexos (múltiplos
  cenários, contratos de concessão de longo prazo, M&A) — ver
  `CLAUDE.md`, coluna "Tier default" de Manta 06.

### Componentes do modelo

1. **Fluxo de caixa projetado** — receitas (tarifa, RAP, contraprestação,
   subsídio) e custos (CAPEX faseado por A3+A5, OPEX, manutenção
   periódica) período a período, ao longo do horizonte contratual.
2. **VPL (Valor Presente Líquido)** — descontado à taxa de referência
   (WACC do setor, TMA definida pelo cliente, ou taxa do edital).
3. **TIR (Taxa Interna de Retorno)** — comparada ao WACC/TMA para
   julgamento de atratividade.
4. **Payback** — simples e descontado.
5. **Cenários** — base, otimista, pessimista, e cenários específicos
   de risco regulatório/mercado (ex.: variação de tráfego, RAP menor
   que o teto, atraso de obra).
6. **Análise de sensibilidade** — variação de uma variável por vez
   (tornado chart) para identificar os drivers de maior impacto no
   VPL/TIR.

### Entradas

- Orçamento consolidado (A3) — CAPEX e OPEX.
- Cronograma (A5) — faseamento temporal de desembolsos.
- Premissas macroeconômicas (inflação, câmbio quando aplicável, taxa
  de desconto).
- Estrutura de receita do segmento (tarifa, RAP, pedágio, contrato de
  disponibilidade etc. conforme S1–S11).

### Saídas

- Modelo financeiro (planilha/ferramenta de modelagem) com abas de
  premissas, fluxo de caixa, resultados (VPL/TIR/payback) e cenários.
- Memorando executivo com os principais resultados e recomendação.
- Tornado chart / matriz de sensibilidade.

### Critérios de aceitação

- [ ] Toda premissa macroeconômica e regulatória explicitada e
  datada (fonte e data de captura).
- [ ] VPL/TIR calculados com taxa de desconto justificada (não
  arbitrária).
- [ ] Ao menos 3 cenários (base/otimista/pessimista) presentes.
- [ ] Sensibilidade cobre as variáveis de maior materialidade
  (identificadas, não escolhidas arbitrariamente).
- [ ] Rastreabilidade do CAPEX/OPEX até A3 e do faseamento até A5.

### Handoffs

- ← **A3 (orçamento)**, ← **A5 (cronograma)** — insumos diretos.
- → **A1 (proposta)** — quando o modelo suporta uma proposta comercial/
  leilão.
- → **A8 (advisory)** — quando o resultado do modelo demanda
  recomendação estratégica (ex.: "aceitar ou não a oportunidade").
- → **A10 (risco)** — cenários pessimistas do modelo alimentam a
  matriz de risco financeiro.

---

## A5 — Cronograma

### Descrição

Planejamento e controle do tempo de execução do projeto/obra:
sequenciamento de atividades, dependências, alocação de recursos,
nivelamento e acompanhamento de caminho crítico. Ferramenta primária:
MS Project (também Primavera P6 via `cronograma-toolkit`/
`xer-p6-analytics`).

### Quando usar

- Elaboração de cronograma macro para proposta (A1).
- Detalhamento de cronograma executivo pós-contrato.
- Replanejamento após atraso, aditivo ou mudança de escopo.
- Análise de atraso para suporte a claims (A7) — cronograma
  contratual vs. realizado, identificação de caminho crítico afetado.
- Palavras-chave: "cronograma", "MS Project", "Primavera", "XER",
  "Gantt", "caminho crítico", "curva S", "nivelamento de recursos",
  "linha de base", "baseline".

### Quem produz

- **Manta 07 (cronograma)** — dono do processo.
- Skills/ferramentas: `cronograma-toolkit` (leitura/conversão/clone
  bidirecional entre XER e MSP XML, geração de Gantt HTML interativo),
  `xer-msp-toolkit`, `xer-p6-analytics` (análise de métricas P6:
  atrasos, folgas, marcos).

### Metodologia (MS Project, Gantt, dependências, recursos,
nivelamento)

1. **EAP/WBS** — estrutura analítica do projeto alinhada à estrutura
   de quantidades (A2) e orçamento (A3) por disciplina.
2. **Sequenciamento** — dependências FS/SS/FF/SF entre atividades,
   com lags/leads justificados tecnicamente (não arbitrários).
3. **Duração** — estimada a partir de produtividade (histórico Manta,
   SICRO quando aplicável) × quantidade (A2).
4. **Recursos** — alocação de equipes/equipamentos, com verificação de
   superalocação.
5. **Nivelamento** — resolução de conflitos de recursos sem violar
   restrições de prazo contratual, priorizando o caminho crítico.
6. **Caminho crítico** — identificação e monitoramento contínuo;
   qualquer atividade no caminho crítico que atrase implica atraso
   direto no prazo final (insumo central para A7 — claims de atraso).
7. **Linha de base (baseline)** — congelada no início da execução,
   usada como referência de comparação (Planejado × Realizado) ao
   longo de toda a obra.
8. **Curva S** — físico (avanço de quantidades) e financeiro (avanço
   de desembolso), cruzado com A3/A4.

### Entradas

- Quantitativos (A2) e orçamento (A3) por disciplina.
- Restrições contratuais de prazo (marcos, multas por atraso).
- Produtividade de referência (histórico Manta, SICRO, ou dados do
  edital).
- Recursos disponíveis (equipes, equipamentos, frentes de obra).

### Saídas

- Cronograma detalhado (MPP/XER) com EAP, dependências, recursos e
  linha de base.
- Gantt visual (HTML interativo ou nativo da ferramenta).
- Relatório de caminho crítico e folgas.
- Curva S física e financeira.

### Critérios de aceitação

- [ ] Toda atividade tem duração justificada (produtividade ×
  quantidade), não estimada "no olho".
- [ ] Dependências logicamente consistentes (sem loops, sem
  sucessoras iniciando antes de predecessoras obrigatórias).
- [ ] Caminho crítico identificado e explicitado no relatório.
- [ ] Recursos nivelados sem superalocação não resolvida.
- [ ] Linha de base registrada e preservada (alterações via change
  control, nunca sobrescrita silenciosamente).

### Handoffs

- ← **A2 (quantidades)**, ← **A3 (orçamento)** — insumos diretos.
- → **A4 (modelagem financeira)** — faseamento temporal do fluxo de
  caixa.
- → **A7 (claims)** — cronograma é a peça técnica central de qualquer
  pleito de atraso/disrupção (ver também skill `conclusao-janelas`
  para a lógica de cascata cronológica usada em claims de OAE).
- → **A10 (risco)** — atrasos no caminho crítico são risco
  materializado, retroalimentam a matriz.

---

## A6 — Contratual

### Descrição

Elaboração, revisão e gestão de peças jurídico-contratuais: minutas de
contrato, termos aditivos, termos de dispensa/pactuação (TDP), e
cláusulas específicas (reajuste, garantias, matriz de risco
contratual, condições suspensivas). Cobre tanto a fase de formação do
contrato quanto sua vida útil (aditivos, repactuações).

### Quando usar

- Elaboração de minuta de contrato ou edital (fase de licitação).
- Negociação e redação de termo aditivo (mudança de escopo, prazo ou
  valor).
- Revisão de cláusulas de risco, reajuste, garantia, rescisão.
- Suporte jurídico a claims (interpretação de cláusula aplicável).
- Palavras-chave: "contrato", "aditivo", "TDP", "cláusula",
  "minuta", "termo de referência", "condição suspensiva", "garantia
  contratual", "matriz de risco contratual".

### Quem produz

- **Manta 02 (contratual)** — dono do processo, produz e revisa peças
  jurídicas.
- Handoff obrigatório para jurídico externo/interno do cliente para
  validação final — Manta 02 **assessora**, não substitui advogado
  constituído nas peças que exigem assinatura profissional.

### Peças jurídicas cobertas

1. **Contrato** — objeto, prazo, valor, forma de pagamento, obrigações
   das partes, matriz de risco, garantias, penalidades, condições de
   rescisão.
2. **Aditivos** — de prazo, de valor (reequilíbrio), de escopo
   (supressão/acréscimo dentro ou fora dos limites legais — Lei
   8.666/93, Lei 14.133/2021, ou regulamento próprio do
   contratante), sempre referenciando a cláusula-base alterada.
3. **TDP (Termo de Dispensa/Pactuação)** — instrumento simplificado
   para ajustes de menor complexidade, quando o regime contratual
   permite.
4. **Cláusulas específicas** — reajuste (índice, periodicidade),
   garantia (seguro-garantia, fiança, caução), força maior/caso
   fortuito, matriz de risco (RDC, PPP, concessão), condições
   suspensivas e precedentes.

### Entradas

- Objeto/escopo definido (via A1 ou já contratado).
- Regime legal aplicável (Lei 8.666/93, Lei 14.133/2021, Lei das
  PPPs, Lei das Concessões, regulamento próprio do órgão/empresa).
- Para aditivos: cláusula-base, justificativa técnica (normalmente
  vinda de A2/A3/A5), e limite legal de alteração (ex.: 25%/50% do
  valor contratual conforme regime).

### Saídas

- Minuta de contrato ou aditivo, com cláusulas numeradas e
  referenciadas ao regime legal aplicável.
- Parecer de enquadramento legal do instrumento (contrato vs. aditivo
  vs. TDP).
- Matriz de risco contratual (alocação de risco entre as partes —
  insumo direto para A10).

### Critérios de aceitação

- [ ] Toda cláusula referenciada a dispositivo legal real (checagem
  `aluci-guard` obrigatória — lei/norma fabricada é um dos padrões
  auditados).
- [ ] Limite legal de aditivo (percentual) verificado explicitamente
  quando aplicável.
- [ ] Matriz de risco contratual explícita (quem assume o quê).
- [ ] Revisão por jurídico habilitado antes de assinatura — Manta 02
  não assina, apenas instrui a minuta.
- [ ] Gate humano (MN ou jurídico do cliente) antes de qualquer envio
  externo ou assinatura.

### Handoffs

- ← **A1 (proposta)** — pós-adjudicação, vira minuta de contrato.
- ← **A2/A3/A5** — fundamentam justificativa técnica de aditivos.
- → **A7 (claims)** — cláusula contratual é sempre o ponto de partida
  de qualquer pleito.
- → **A9 (regulatório)** — quando a peça contratual depende de
  licença/aprovação regulatória como condição suspensiva.
- → **A10 (risco)** — matriz de risco contratual alimenta a matriz de
  risco 5×5 consolidada.

---

## A7 — Claims

### Descrição

Estruturação e sustentação técnico-financeira de pleitos contratuais
(reequilíbrio econômico-financeiro, revisão de prazo, indenização),
cobrindo as variantes por tipo de causa: serviço extra/adicional,
atraso/disrupção, e força maior/fato do príncipe.

### Quando usar

- Identificação de evento que rompe premissas de proposta/contrato
  (ver skill `conclusao-janelas` — "quebra das premissas de
  proposta" como um dos três eixos obrigatórios de conclusão).
- Necessidade de reequilíbrio por serviço não previsto no orçamento
  original.
- Atraso não imputável à contratada (interferência de terceiros,
  atraso de liberação de frente de serviço, licenciamento).
- Evento de força maior/caso fortuito (clima extremo, pandemia, ato de
  autoridade).
- Palavras-chave: "claim", "pleito", "reequilíbrio", "extra
  contratual", "atraso", "disrupção", "força maior", "fato do
  príncipe", "improdutividade".

### Quem produz

- **Manta 01 (claims)** — dono do processo, tier **Opus** por padrão
  (maior exigência analítica e de risco reputacional/financeiro do
  entregável).
- Suporte intenso de **A2 (quantidades)** e **A5 (cronograma)** —
  claim sem lastro quantitativo/cronológico não se sustenta.
- Skill `conclusao-janelas` para a redação da conclusão narrativa por
  grupo de serviço (GR), com os três eixos: improdutividade como
  consequência, disrupção/cascata cronológica, quebra de premissas.

### Variantes por tipo de causa

1. **Extra/adicional** — serviço não previsto no orçamento contratado,
   executado por necessidade técnica ou determinação do contratante.
   Sustentação: comparação quantitativo contratado (A3) × executado
   (A2), com memória de cálculo do adicional.
2. **Atraso** — impacto no prazo contratual por causa não imputável à
   contratada. Sustentação: cronograma linha de base (A5) × realizado,
   identificação do caminho crítico afetado, cascata de disrupção
   (efeito de um atraso pontual sobre atividades subsequentes).
3. **Força maior / fato do príncipe** — evento externo, imprevisível
   ou de efeitos incalculáveis, que impede ou onera a execução.
   Sustentação: nexo causal entre o evento e o impacto medido (custo
   e/ou prazo), com evidência documental do evento (boletim
   meteorológico, ato normativo, decreto).

### Entradas

- Contrato e cláusula aplicável (A6).
- Quantitativo contratado × executado (A2/A3).
- Cronograma linha de base × realizado (A5).
- Evidências do evento gerador (RDO, correspondência, ato normativo,
  laudo técnico, registro fotográfico).

### Saídas

- Dossiê de claim: narrativa técnica, quantum (valor pleiteado),
  memória de cálculo, cronologia de eventos, conclusão por grupo de
  serviço (quando aplicável — GR-01 a GR-09 no padrão de contratos de
  OAE de grande porte).
- Anexos técnicos de suporte (cronograma comparativo, planilha de
  quantidades, evidências documentais).

### Critérios de aceitação

- [ ] Nexo causal explícito entre evento e impacto (custo/prazo) — não
  apenas correlação temporal.
- [ ] Quantum sustentado por memória de cálculo auditável, rastreável
  a A2/A3.
- [ ] Cronologia consistente (datas em ordem lógica, sem
  sobreposição não explicada) — checagem obrigatória via
  `consist-guard` antes de fechar o documento.
- [ ] Toda norma/lei/cláusula citada verificada via `aluci-guard`.
- [ ] Conclusão redigida nos três eixos obrigatórios (quando aplicável
  ao padrão GR): improdutividade como consequência, cascata de
  disrupção, quebra de premissas — nunca invertendo causa e
  consequência.
- [ ] Gate humano (MN) antes de protocolo formal do pleito.

### Handoffs

- ← **A2, A3, A5, A6** — insumos técnicos e contratuais diretos.
- → **A4 (modelagem financeira)** — quantum de claim relevante impacta
  o modelo financeiro do contrato/concessão.
- → **A8 (advisory)** — quando o claim exige posicionamento
  estratégico (negociação, mediação, arbitragem).
- → **A10 (risco)** — todo claim materializado é, retroativamente, um
  risco que deveria estar (ou já estava) na matriz.

---

## A8 — Advisory

### Descrição

Aconselhamento técnico-estratégico de alto nível: parecer técnico
formal, análise estratégica de posicionamento (aceitar/recusar
oportunidade, entrar/sair de mercado, estrutura de negociação),
suporte a decisões de investimento e M&A.

### Quando usar

- Necessidade de parecer técnico formal sobre questão específica
  (viabilidade, conformidade, adequação de solução).
- Decisão estratégica de negócio (entrar em leilão, aceitar due
  diligence, priorizar oportunidade).
- Suporte executivo em negociação de alto valor (reequilíbrio,
  renovação de concessão, M&A).
- Palavras-chave: "parecer", "advisory", "análise estratégica",
  "recomendação", "due diligence", "M&A", "posicionamento",
  "decisão executiva".

### Quem produz

- **Manta 15 (advisory)** — tier **Sonnet/Opus** conforme
  complexidade (Opus para M&A, pareceres de alto risco reputacional
  ou grandes valores envolvidos).
- Consome outputs de praticamente todos os demais A-codes e S-codes
  como insumo (advisory é, por natureza, uma atividade de síntese).
- Skill `mk-manta` (raciocínio estruturado estilo MBB) como apoio
  metodológico à construção do argumento.

### Entradas

- Pergunta/decisão específica a ser respondida.
- Todo o contexto técnico relevante já produzido (orçamento,
  cronograma, modelo financeiro, quantitativos, situação contratual).
- Restrições de prazo e de sigilo (M&A e negociações sensíveis
  frequentemente exigem tratamento confidencial).

### Saídas

- **Parecer técnico** — documento formal com pergunta, análise,
  conclusão e recomendação, cada uma rastreável às fontes utilizadas.
- **Análise estratégica** — memorando executivo (1–3 páginas) com
  opções, trade-offs e recomendação clara.

### Critérios de aceitação

- [ ] Pergunta/decisão a ser respondida explicitada no início do
  documento (nunca implícita).
- [ ] Toda conclusão rastreável a uma fonte (dado, cálculo, norma) —
  parecer não pode se apoiar em afirmação não sustentada.
- [ ] Trade-offs das opções alternativas explicitados, não apenas a
  opção recomendada.
- [ ] Nível de confiança/incerteza da recomendação declarado quando
  relevante (ex.: "recomendação condicionada à confirmação de X").
- [ ] Checagem `aluci-guard` quando o parecer cita normas, leis ou
  referências técnicas.
- [ ] Gate humano (MN) antes de entrega a cliente ou uso em decisão de
  investimento.

### Handoffs

- ← **A1, A3, A4, A6, A7** e qualquer segmento S1–S11 — advisory
  consome o output de praticamente toda a cadeia.
- → **A10 (risco)** — toda recomendação estratégica deveria vir
  acompanhada de leitura de risco associada.
- → decisão executiva (fora do escopo dos A-codes — decisão humana
  final).

---

## A9 — Regulatório

> ⚠️ **RUBRICA PENDENTE — TODO.** Esta atividade **não possui agente
> Manta dedicado** no `CLAUDE.md` v4.2 (Eixo 1 — Horizontais). O
> conteúdo abaixo é um **rascunho de enquadramento**, produzido para
> preencher a lacuna identificada nesta tarefa, e **não deve ser
> tratado como rubrica aprovada** até revisão e aprovação MN + registro
> formal no `CLAUDE.md` master (inclusão de um Manta-code, ex.
> "Manta XX — regulatório", ou decisão explícita de manter a atividade
> distribuída entre os verticais S1–S11 sem agente horizontal próprio).

### Descrição (rascunho)

Enquadramento legal-regulatório de um projeto/ativo: identificação de
licenças e aprovações necessárias, agências reguladoras competentes,
compliance com marcos setoriais, e acompanhamento do status de
processos regulatórios em curso.

### Quando usar (rascunho)

- Identificação de licenciamento ambiental necessário (LP/LI/LO).
- Enquadramento perante agência setorial (ANEEL, ANTT, ANTAQ, ANAC,
  ANA, agências estaduais de saneamento/energia).
- Devido enquadramento em marco legal (Lei 14.026 saneamento, Lei do
  Gás, marco de transmissão ANEEL, RBAC aeroportuário, PNSB
  barragens).
- Due diligence regulatória (fase 7 do ciclo de vida).
- Palavras-chave candidatas: "licença ambiental", "outorga",
  "enquadramento regulatório", "compliance setorial", "agência
  reguladora", "LP/LI/LO", "autorização", "concessão administrativa".

### Quem produz (rascunho — TODO confirmar com MN)

Hoje, na ausência de um agente horizontal dedicado, o enquadramento
regulatório é produzido **de forma distribuída** dentro de cada
agente vertical (ex.: Manta 03-S8/saneamento cita Lei 14.026/ANA;
Manta 03-S9/energia cita ANEEL/ONS/EPE; Manta 03-S6/portos cita
ANTAQ; Manta 03-S7/aeroportos cita ANAC/ICAO; Manta 03-S10/barragens
cita PNSB/ANM), com suporte pontual de **Manta 02 (contratual)** para
a interface entre licença/aprovação e condição suspensiva contratual,
e de **Manta 15 (advisory)** quando a questão regulatória vira decisão
estratégica.

**Recomendação para decisão MN:** avaliar se compensa (a) criar um
Manta-code horizontal dedicado a A9, consolidando o conhecimento
regulatório hoje espalhado pelos verticais, ou (b) manter distribuído
e apenas formalizar esta seção como "guia de referência cruzada" sem
agente próprio. Enquanto a decisão não for tomada, tratar A9 como
**gap conhecido do registry**, não como atividade não coberta — o
conhecimento existe, só não está consolidado sob um único A-code.

### Entradas (rascunho)

- Segmento/vertical do projeto (S1–S11).
- Localização (município, estado, país — regulação varia por
  jurisdição, especialmente relevante para operações fora do Brasil,
  ex. AySA/Argentina).
- Fase do ciclo de vida (licenciamento tende a concentrar-se nas fases
  1–4).

### Saídas (rascunho)

- Checklist de licenças/aprovações aplicáveis, com órgão responsável
  e status.
- Parecer de enquadramento legal-regulatório.
- Cronograma de obtenção de licenças (interface direta com A5).

### Critérios de aceitação (rascunho — sujeitos a revisão)

- [ ] Toda licença/norma citada existe de fato (checagem
  `aluci-guard` obrigatória).
- [ ] Órgão/agência competente corretamente identificado por
  jurisdição.
- [ ] Status do processo (não iniciado/em análise/deferido/indeferido)
  explicitado, com data de última atualização.
- [ ] **[TODO]** Definir critério de completude mínima (quantas
  licenças cobertas = "pronto") — depende de decisão MN sobre escopo
  da atividade.

### Handoffs (rascunho)

- ← todos os verticais S1–S11 — cada um contribui com seu marco
  regulatório setorial.
- → **A6 (contratual)** — licença como condição suspensiva.
- → **A5 (cronograma)** — prazo de obtenção de licença é atividade do
  caminho crítico em fases iniciais.
- → **A10 (risco)** — risco regulatório é categoria própria na matriz
  5×5.

---

## A10 — Risco

### Descrição

Consolidação e gestão de riscos do projeto/contrato em matriz
padronizada 5×5 (probabilidade × impacto), com planos de mitigação e
contingência associados a cada risco relevante. É a atividade de
**síntese transversal**: recebe insumos de todos os demais A-codes e
de todos os verticais S1–S11, e não produz conteúdo técnico-primário
próprio.

### Quando usar

- Abertura de projeto/proposta (matriz de risco inicial, a partir da
  "indicação de risco" preliminar de A1).
- Revisão periódica ao longo da execução (obra em andamento — fase 4).
- Antes de decisão estratégica relevante (suporte a A8).
- Após materialização de risco (claim — A7), para atualizar
  probabilidade/impacto residual.
- Palavras-chave: "matriz de risco", "5x5", "mitigação",
  "contingência", "probabilidade e impacto", "risk register", "risco
  residual".

### Quem produz

- **Manta 15 (advisory)** coordena a consolidação, mas **não é o
  autor exclusivo do conteúdo** — cada risco listado deve ser
  originado por quem detém o conhecimento técnico da matéria:
  - Risco técnico → agente vertical do segmento (S1–S11).
  - Risco de prazo → **A5 (cronograma)**.
  - Risco financeiro → **A4 (modelagem financeira)**.
  - Risco contratual → **A6 (contratual)**.
  - Risco regulatório → **A9 (regulatório)** — ver ressalva de gap
    acima.
  - Risco de reequilíbrio/claim → **A7 (claims)**.

> Nota de gap: assim como A9, **A10 não tem Manta-code próprio no
> `CLAUDE.md` v4.2**. É tratada aqui como processo de consolidação
> coordenado por Manta 15, não como um agente novo — não interpretar
> esta seção como criação de um "Manta 17" sem aprovação/registro
> formal.

### Estrutura da matriz 5×5

| Probabilidade \ Impacto | 1 – Insignificante | 2 – Menor | 3 – Moderado | 4 – Maior | 5 – Catastrófico |
|---|---|---|---|---|---|
| **5 – Quase certo** | Médio | Alto | Alto | Crítico | Crítico |
| **4 – Provável** | Médio | Médio | Alto | Alto | Crítico |
| **3 – Possível** | Baixo | Médio | Médio | Alto | Alto |
| **2 – Improvável** | Baixo | Baixo | Médio | Médio | Alto |
| **1 – Raro** | Baixo | Baixo | Baixo | Médio | Médio |

- **Probabilidade** (1–5): raro → quase certo, com critério
  quantitativo quando possível (ex.: baseado em histórico Manta de
  projetos similares).
- **Impacto** (1–5): insignificante → catastrófico, avaliado em pelo
  menos duas dimensões — financeira (% do valor do contrato) e de
  prazo (dias de atraso no caminho crítico).
- **Classificação final**: Baixo / Médio / Alto / Crítico — determina
  a obrigatoriedade e o nível de aprovação do plano de mitigação
  (riscos "Crítico" exigem plano de contingência formal e aprovação
  MN).

### Planos de mitigação e contingência

- **Mitigação** — ação preventiva para reduzir probabilidade e/ou
  impacto antes do risco se materializar (ex.: sondagem adicional
  para reduzir risco geotécnico).
- **Contingência** — ação reativa preparada para quando o risco se
  materializa (ex.: reserva de contingência financeira, cronograma
  alternativo, cláusula contratual de reequilíbrio automático).
- Todo risco "Alto" ou "Crítico" deve ter **ambos** documentados;
  riscos "Médio" ao menos mitigação; riscos "Baixo" podem ser apenas
  monitorados (sem plano formal obrigatório).

### Entradas

- Indicação de risco preliminar (A1).
- Insumos técnicos de todos os A-codes/S-codes relevantes ao projeto
  (orçamento, cronograma, modelo financeiro, situação contratual,
  enquadramento regulatório).
- Histórico de riscos materializados em projetos similares (claims
  anteriores — A7).

### Saídas

- **Matriz de risco 5×5** consolidada, com cada risco classificado,
  descrito, com dono nomeado (quem monitora), plano de mitigação e
  plano de contingência.
- **Risk register** (planilha viva, atualizada periodicamente).
- Resumo executivo dos riscos "Alto"/"Crítico" para decisão MN.

### Critérios de aceitação

- [ ] Todo risco tem probabilidade E impacto justificados (não
  atribuídos arbitrariamente).
- [ ] Todo risco "Alto"/"Crítico" tem plano de mitigação **e**
  contingência documentados.
- [ ] Todo risco tem dono nomeado (pessoa ou papel responsável pelo
  monitoramento).
- [ ] Matriz revisada em cadência definida (mínimo: a cada marco
  contratual relevante ou trimestralmente em obra longa).
- [ ] Riscos materializados (viraram claim — A7) são movidos para
  "realizado" com link ao dossiê de claim correspondente, não apenas
  apagados da matriz.

### Handoffs

- ← **A1** (indicação preliminar), **A4** (cenários pessimistas),
  **A5** (atrasos de caminho crítico), **A6** (matriz de risco
  contratual), **A7** (riscos materializados), **A9** (risco
  regulatório) — todos alimentam A10.
- → **A8 (advisory)** — matriz de risco é insumo central de qualquer
  recomendação estratégica.
- → decisão executiva MN para riscos "Crítico".

---

## 1. Consolidação — tabela de entradas/saídas cruzadas

| De \ Para | A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9 | A10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A1** Proposta | — | | | X | X | X | | | | X |
| **A2** Quantidades | | — | X | | X | X | | | | |
| **A3** Orçamento | | | — | X | X | | X | | | |
| **A4** Modelagem financeira | X | | | — | | | X | X | | X |
| **A5** Cronograma | | | | X | — | | X | | X | X |
| **A6** Contratual | | | | | | — | X | | X | X |
| **A7** Claims | | | X | X | | | — | X | | X |
| **A8** Advisory | | | | | | | | — | | X |
| **A9** Regulatório (TODO) | | | | | X | X | | | — | X |
| **A10** Risco | | | | | | | | X | | — |

*(X = existe fluxo de dados relevante do agente da linha para o
agente da coluna, conforme handoffs descritos em cada seção acima.)*

---

## 2. Pendências para fechamento (gate humano MN)

- [ ] **A9 — Regulatório**: decidir se vira Manta-code horizontal
  dedicado ou permanece distribuído pelos verticais; atualizar
  `CLAUDE.md` master de acordo.
- [ ] **A10 — Risco**: confirmar se Manta 15 (advisory) é de fato o
  coordenador oficial da consolidação, ou se cabe um Manta-code
  próprio; atualizar `CLAUDE.md` master de acordo.
- [ ] Validar rubricas de A1–A8 com os donos de cada Manta-code
  (Manta 13/14, Manta 05, Manta 06, Manta 07, Manta 02, Manta 01,
  Manta 15) antes de publicar como SKILL.md formal no SharePoint.
- [ ] Após aprovação MN, replicar este documento (ou seu conteúdo
  consolidado) em `sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`
  conforme checklist de deploy do `CLAUDE.md`.

---

## Histórico de versões

- **v1.0** (2026-07-31) — primeira versão formal do Eixo A (A1–A10),
  produzida a partir do mapa de agentes do `CLAUDE.md` v4.2. A9 e A10
  documentadas com gap explícito de Manta-code — pendente decisão MN.
