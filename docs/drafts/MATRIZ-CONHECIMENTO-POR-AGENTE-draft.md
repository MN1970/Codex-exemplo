# Matriz de Conhecimento por Agente — Manta Maestro

Documento de planejamento (draft). Objetivo: mapear, para cada um dos
agentes operacionais do Manta Maestro, o conhecimento técnico/profissional
mínimo necessário para que o agente seja realmente útil em projetos reais
de consultoria em infraestrutura da Manta Associados (EVTEA, propostas
técnicas, orçamento, cronograma, claims/reequilíbrio, advisory, processos
de licenciamento e licitação).

**Nota metodológica:** normas, leis e frameworks citados abaixo foram
verificados (nome do órgão, existência e função geral da norma/família de
normas). Onde o número exato de uma resolução, edição ou artigo não foi
confirmado nesta pesquisa, o texto usa referência genérica ("família de
normas X", "norma ABNT que trata de Y") em vez de um número específico,
para evitar citação fabricada. Antes de qualquer laudo, claim ou proposta
formal, os textos gerados por estes agentes devem passar por checagem de
citação (ex.: skill `aluci-guard`) e por revisão humana.

---

## Horizontais

### Manta 00 — maestro (router)

**Missão no contexto Manta:** Interpretar a intake do usuário e rotear a
solicitação para o agente vertical/horizontal correto, evitando que um
caso de saneamento seja tratado por um agente de rodovias (ou vice-versa).

**Conhecimento técnico essencial:**
- Vocabulário técnico mínimo de todos os segmentos (termos-gatilho: CBUQ,
  OAE, AMV, NATM, ETA/ETE, RAP/ANEEL, dragagem/berço, RBAC/ICAO, CFRD/CCR)
  suficiente para classificar, não para responder tecnicamente.
- Estrutura do ciclo de vida de projeto de infraestrutura (estudo prévio →
  projeto básico → executivo → obra → O&M → licitação → due diligence →
  descomissionamento), para aplicar a fase correta do intake.
- Modelo de negócio e nomenclatura interna da Manta (códigos de agente,
  aliases, tiers de modelo).
- Noções de custo/latência de modelos LLM (quando escalar de Haiku para
  Sonnet/Opus).

**Fontes de atualização contínua:**
- Registro interno de agentes (este próprio CLAUDE.md e runbooks).
- Feedback de roteamento incorreto reportado pelos usuários internos.

**Gap de maturidade atual:** Suficiente para o volume atual de segmentos;
tende a exigir revisão de regras a cada novo segmento vertical adicionado
(ex.: expansão S6–S11) — risco é regra de roteamento desatualizada, não
falta de profundidade técnica.

---

### Manta 01 — claims

**Missão no contexto Manta:** Sustentar tecnicamente pleitos de
reequilíbrio econômico-financeiro e análises de atraso/improdutividade em
contratos de obra pública e concessões, com nexo causal defensável.

**Conhecimento técnico essencial:**
- Metodologia AACE International RP 29R-03 (Forensic Schedule Analysis) —
  taxonomia de métodos de análise de atraso e apuração de caminho crítico.
- Métodos de quantificação de improdutividade (ex.: measured mile /
  método da milha medida) e distinção entre disrupção e atraso.
- Protocolo SCL (Society of Construction Law Delay and Disruption
  Protocol) como referência complementar em arbitragens internacionais.
- Base legal brasileira de reequilíbrio: Lei 14.133/2021 (Nova Lei de
  Licitações), Lei 8.987/1995 (concessões) e jurisprudência do TCU sobre
  matriz de risco e álea ordinária/extraordinária.
- Conceito de nexo causal e cadeia de causalidade entre evento, impacto no
  cronograma e dano financeiro.
- Interface com cronograma (Primavera P6/CPM) e com orçamento
  (SICRO/SINAPI) para quantificar o quantum do pleito.

**Fontes de atualização contínua:**
- Publicações e Recommended Practices da AACE International.
- Acórdãos do TCU e jurisprudência de tribunais arbitrais sobre
  reequilíbrio e matriz de risco em contratos de infraestrutura.
- Alterações na Lei 14.133/2021 e regulamentação correlata.

**Gap de maturidade atual:** É um dos agentes mais expostos a risco
reputacional (documento vira prova em disputa) — mesmo com metodologia
AACE bem estabelecida, precisa de biblioteca de jurisprudência nacional
atualizada e de checagem de citação mais rígida que os demais agentes.

---

### Manta 02 — contratual

**Missão no contexto Manta:** Apoiar a leitura e redação de cláusulas
contratuais, aditivos e matrizes de risco em contratos de obra pública,
concessão e PPP.

**Conhecimento técnico essencial:**
- Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos) e
  regime de transição da Lei 8.666/1993.
- Lei 8.987/1995 (concessões de serviço público) e Lei 11.079/2004 (PPP).
- Estrutura de matriz de risco contratual (alocação de risco entre poder
  concedente/contratante e concessionária/contratada).
- Tipologia de aditivos contratuais (prazo, valor, escopo, reequilíbrio) e
  limites legais de acréscimo/supressão.
- Jurisprudência do TCU e tribunais de contas estaduais sobre aditivos e
  equilíbrio econômico-financeiro.

**Fontes de atualização contínua:**
- Alterações legislativas (Lei 14.133/2021 e regulamentos), súmulas e
  acórdãos do TCU.
- Editais-padrão de agências reguladoras setoriais (ANTT, ANEEL, ANTAQ,
  ANAC) quando o contrato de referência for uma concessão federal.

**Gap de maturidade atual:** Base legal geral é estável e bem documentada;
o gap real está em manter atualizada a leitura de jurisprudência recente,
que muda com mais frequência que a lei em si.

---

### Manta 04 — imobiliario

**Missão no contexto Manta:** Suportar avaliação imobiliária, estudos de
viabilidade de incorporação e cálculo de VGV para projetos imobiliários e
para componentes fundiários de projetos de infraestrutura (desapropriação,
faixa de domínio).

**Conhecimento técnico essencial:**
- ABNT NBR 14653 (Avaliação de bens), família de 7 partes — Parte 1
  (procedimentos gerais), Parte 2 (imóveis urbanos), Parte 3 (imóveis
  rurais), demais partes conforme o ativo avaliado.
- Métodos comparativo, involutivo, evolutivo e da renda para avaliação.
- Padrões internacionais de referência quando o cliente exigir (RICS Red
  Book / International Valuation Standards; USPAP nos EUA) — usados como
  referência comparativa, não como norma aplicável no Brasil.
- Legislação de incorporação imobiliária (Lei 4.591/1964) e Lei do
  Distrato (Lei 13.786/2018).
- Fundamentos de desapropriação para fins de utilidade pública (relevante
  em faixa de domínio de rodovias, ferrovias e linhas de transmissão).

**Fontes de atualização contínua:**
- Revisões da série ABNT NBR 14653.
- Publicações RICS/IVSC quando o mandato envolver padrão internacional.
- Jurisprudência sobre desapropriação e indenização.

**Gap de maturidade atual:** Núcleo normativo (NBR 14653) é estável e bem
mapeável; maior gap está na conexão entre avaliação imobiliária e a lógica
de desapropriação/faixa de domínio específica de projetos de
infraestrutura linear, que é menos padronizada.

---

### Manta 05 — orcamento

**Missão no contexto Manta:** Elaborar e revisar orçamentos de obra com
base nos sistemas de custos referenciais oficiais, com BDI e CCU
tecnicamente defensáveis perante órgãos de controle.

**Conhecimento técnico essencial:**
- SICRO (Sistema de Custos Referenciais de Obras, mantido pelo DNIT) —
  composições de custo para obras de infraestrutura de transporte,
  atualizado trimestralmente.
- SINAPI (Sistema Nacional de Pesquisa de Custos e Índices da Construção
  Civil, Caixa/IBGE) — usado para edificações e saneamento.
- Metodologia de cálculo de BDI (Benefícios e Despesas Indiretas) e CCU
  (Custo de Compra dos Equipamentos/Custo por Categoria Unitária), incluindo
  faixas de referência discutidas em acórdãos do TCU.
- Lei 14.133/2021 quanto a orçamento estimado, sigilo de orçamento e
  critérios de aceitabilidade de preços.
- Diferenças estruturais entre SICRO (equipamento pesado, produção por
  frente) e SINAPI (edificação/saneamento).

**Fontes de atualização contínua:**
- Publicações trimestrais do DNIT (SICRO) e mensais da Caixa/IBGE
  (SINAPI).
- Acórdãos do TCU sobre limites e composição de BDI.
- Alterações na Lei 14.133/2021 relativas a orçamentação pública.

**Gap de maturidade atual:** Base de dados (SICRO/SINAPI) é pública e
estruturada, favorecendo automação; o gap está em manter a base local
sincronizada com as atualizações trimestrais/mensais e em cobrir estados
específicos (encargos sociais e insumos variam por UF).

---

### Manta 06 — modelagem

**Missão no contexto Manta:** Construir e revisar modelos financeiros de
viabilidade (EVTEA econômico-financeiro, concessões, M&A de ativos de
infraestrutura).

**Conhecimento técnico essencial:**
- Fluxo de caixa descontado (DCF), TIR, VPL, WACC e estrutura de capital
  típica de project finance de infraestrutura.
- Modelagem de concessões (curva de demanda/tarifa, CAPEX/OPEX em fases,
  valor residual, garantias).
- Análise de sensibilidade e simulação de Monte Carlo para variáveis de
  risco (tráfego, custo de obra, taxa de câmbio quando aplicável).
- Tratamento contábil de concessões sob IFRS (ICPC 01/IFRIC 12 —
  ativo financeiro vs. ativo intangível), relevante para due diligence.
- Métricas de bancabilidade usadas por financiadores (DSCR, LLCR) em
  project finance de infraestrutura.

**Fontes de atualização contínua:**
- Práticas de mercado de bancos de desenvolvimento e financiadores
  (BNDES, IFC) em estruturação de project finance.
- Normas contábeis (CPC/IFRS) aplicáveis a concessões.

**Gap de maturidade atual:** Fundamentos de finanças corporativas são
maduros e bem documentados; o gap está na camada de premissas
setoriais específicas (curvas de tráfego, elasticidade tarifária por
segmento), que dependem de dados de projeto e não de norma pública.

---

### Manta 07 — cronograma

**Missão no contexto Manta:** Elaborar, auditar e comparar cronogramas de
obra (linha de base, replanejamento, análise de atraso) em Primavera P6 e
MS Project, servindo de insumo técnico para claims e para acompanhamento
de obra.

**Conhecimento técnico essencial:**
- Método do Caminho Crítico (CPM) e conceitos de folga total/livre,
  sucessor/predecessor, lag/lead.
- Formatos de arquivo Primavera P6 (XER) e Microsoft Project (.mpp / XML
  MSPDI) e suas diferenças estruturais de WBS/calendário/recursos.
- Curva-S e Earned Value Management (EVM: PV, EV, AC, SPI, CPI) para
  acompanhamento físico-financeiro.
- Boas práticas de qualidade de cronograma (guias do PMI/PMBOK e práticas
  recomendadas da AACE sobre scheduling) usadas como referência de
  auditoria de linha de base.
- Interface direta com Manta 01 (claims) para análise forense de atraso.

**Fontes de atualização contínua:**
- Documentação de versão do Primavera P6 e do MS Project (mudanças de
  schema XER/XML entre releases).
- Práticas recomendadas de scheduling da AACE International e do PMI.

**Gap de maturidade atual:** Parsing técnico dos formatos (XER/MSPDI) é
mecânico e bem coberto; o gap está no julgamento de qualidade de
cronograma (identificar más práticas de sequenciamento) em cronogramas de
terceiros, que exige mais contexto de obra do que norma.

---

### Manta 13 — bd (business development)

**Missão no contexto Manta:** Estruturar propostas comerciais e apoiar
inteligência de mercado para captação de novos contratos de consultoria.

**Conhecimento técnico essencial:**
- Estrutura de proposta técnico-comercial (18 seções canônicas da skill
  `proposta-comercial`) e variantes por porte de contrato.
- Calendário de processos competitivos e leilões dos órgãos reguladores
  relevantes (ANTT, ANEEL, ANTAQ, ANAC, agências estaduais) como fonte de
  oportunidades.
- Precificação de serviços de consultoria em função de escopo, prazo e
  risco (relaciona-se com Manta 05/06 para o lastro numérico da proposta).
- Noções básicas de compliance de licitação (habilitação técnica,
  atestados de capacidade técnica) exigidas em editais públicos.

**Fontes de atualização contínua:**
- Portais de editais e leilões das agências reguladoras setoriais.
- Movimentações de mercado (fusões, novos entrantes, resultados de
  leilões) no setor de infraestrutura.

**Gap de maturidade atual:** Estrutura de proposta já está bem
desenvolvida (skill dedicada com 18 seções); o gap é mais de processo
(gate humano MN pendente para publicar variantes novas, como registrado
para o modelo mestre M6) do que de conhecimento técnico em si.

---

### Manta 14 — apresentacoes

**Missão no contexto Manta:** Produzir apresentações executivas (PPTX)
que comuniquem com clareza os resultados técnicos dos demais agentes para
públicos não técnicos (clientes, diretoria, órgãos públicos).

**Conhecimento técnico essencial:**
- Boas práticas de design de apresentação executiva (hierarquia visual,
  storytelling de dados, densidade de informação por slide).
- Convenções visuais e de marca da Manta Associados (identidade
  corporativa) para consistência entre entregáveis.
- Tradução de conteúdo técnico denso (orçamento, cronograma, claims) em
  narrativa executiva sem perder rastreabilidade ao dado-fonte.
- Formato PPTX (estrutura de arquivo, mestres de slide, templates
  reutilizáveis).

**Fontes de atualização contínua:**
- Padrão visual interno da Manta (guia de marca).
- Boas práticas de comunicação executiva de mercado (não é uma área
  normatizada por órgão regulador).

**Gap de maturidade atual:** É o agente com menor necessidade de
profundidade normativa entre os 21 — o conhecimento crítico é de design e
de fidelidade ao dado técnico gerado por outros agentes, não de norma de
engenharia; hoje já deve estar em nível adequado para uso interno.

---

### Manta 15 — advisory

**Missão no contexto Manta:** Elaborar pareceres técnicos, apoiar perícia
judicial/arbitral e due diligence técnica multi-disciplinar em ativos de
infraestrutura.

**Conhecimento técnico essencial:**
- Estrutura de laudo/parecer técnico pericial e requisitos formais de
  perícia no processo civil e em arbitragem no Brasil.
- Conhecimento transversal suficiente de todas as normas ABNT/DNIT/
  agências setoriais citadas pelos agentes verticais, para poder revisar
  criticamente (não substitui a profundidade do agente vertical).
- Metodologia de due diligence técnica de ativos de infraestrutura
  (levantamento de passivos técnicos, contingências, conformidade
  regulatória).
- Interface com Manta 01 (claims) quando o parecer envolver disputa
  contratual.

**Fontes de atualização contínua:**
- Jurisprudência sobre prova pericial e due diligence técnica.
- Atualizações normativas dos agentes verticais que alimentam o parecer.

**Gap de maturidade atual:** Por ser um agente de síntese multi-
disciplinar, seu gap está diretamente ligado à maturidade dos agentes
verticais que ele consome — enquanto S6–S11 ainda estão em consolidação
(criados 2026-07-05), o advisory herda essa mesma imaturidade relativa
nesses segmentos.

---

### Manta 16 — arquiteto-ia

**Missão no contexto Manta:** Projetar e revisar a arquitetura do próprio
sistema de agentes de IA da Manta (skills, hooks, subagentes, integrações
MCP), não a engenharia civil em si.

**Conhecimento técnico essencial:**
- Capacidades e limites da plataforma Claude (Chat, Code, Cowork, API) e
  critérios de escolha entre elas.
- Padrões de design de skills, hooks e subagentes no Claude Code, e
  arquitetura de integrações MCP.
- Model tiering (custo/latência/qualidade por modelo) para dimensionar
  cada agente do Maestro.
- Práticas de mitigação de alucinação e de citação fabricada em sistemas
  de IA aplicados a documentos técnicos sensíveis (diretamente relevante
  dado o histórico de problemas da Manta com citações fabricadas).

**Fontes de atualização contínua:**
- Documentação oficial da Anthropic (Claude, Claude Code, MCP) — muda com
  frequência e é a fonte primária deste agente.
- Práticas internas de outros agentes Manta (retroalimentação do próprio
  ecossistema).

**Gap de maturidade atual:** Domínio é meta (arquitetura de IA, não
engenharia civil) e evolui rápido por natureza da plataforma; exige
processo de atualização contínua mais do que uma biblioteca normativa
estática — risco maior é desatualização de versão de plataforma do que
falta de profundidade conceitual.

---

### Manta 20 — esg

**Missão no contexto Manta:** Apoiar avaliação e reporte de aspectos
ambientais, sociais e de governança em projetos de infraestrutura,
inclusive para financiamento por bancos multilaterais e de
desenvolvimento.

**Conhecimento técnico essencial:**
- Frameworks internacionais de reporte ESG: GRI (Global Reporting
  Initiative), padrões ISSB (que incorporam o legado de SASB e TCFD desde
  2023) e, quando exigido pelo financiador, os Performance Standards da
  IFC e os Equator Principles.
- Licenciamento ambiental brasileiro (competências federal/estadual,
  papel do IBAMA e órgãos estaduais) na medida em que afeta cronograma e
  viabilidade de projetos de infraestrutura.
- Salvaguardas sociais típicas de projetos lineares/grandes obras
  (reassentamento involuntário, populações tradicionais) usadas por
  financiadores multilaterais.
- Indicadores setoriais de governança aplicáveis a concessões públicas.

**Fontes de atualização contínua:**
- Atualizações do GRI e do ISSB (convergência ainda em curso em 2026).
- Diretrizes de salvaguarda de bancos multilaterais (IFC, BID, Banco
  Mundial) quando o projeto envolver financiamento internacional.
- Mudanças na legislação ambiental federal/estadual de licenciamento.

**Gap de maturidade atual:** Este é um agente novo/pouco consolidado no
mapa atual de 21 (não aparece no registro de agentes operacionais do
CLAUDE.md master v4.2.1) — provavelmente o horizontal com maior gap de
maturidade hoje, precisando de biblioteca normativa e de casos de uso
construída desde a base.

---

## Verticais

### Manta 03-S1 — Rodovias

**Missão no contexto Manta:** Suportar EVTEA, projeto e orçamento de obras
rodoviárias (terraplenagem, pavimentação, drenagem, sinalização).

**Conhecimento técnico essencial:**
- Manuais técnicos do DNIT (pavimentação, terraplenagem, drenagem) e
  método nacional de dimensionamento de pavimentos atualmente em uso pelo
  DNIT (sucessor dos métodos DNER anteriores).
- Sistema de custos SICRO (composições por serviço: CBUQ, BGS,
  terraplenagem) — ver também Manta 05.
- Estrutura de EVTEA rodoviário conforme padrão DNIT (estudo de
  alternativas de traçado, tráfego/VMDa, OAEs do projeto).
- Ensaios geotécnicos básicos de referência (ex.: CBR) usados no
  dimensionamento de pavimento.

**Fontes de atualização contínua:**
- Publicações técnicas e manuais do DNIT.
- Atualizações trimestrais do SICRO.

**Gap de maturidade atual:** Segmento mais maduro do portfólio (S1, em
operação desde antes da expansão v4.2) — base normativa e de skills
(evtea-extractor, cad-quantifier, sicro-completo) já é a mais extensa
entre os verticais.

---

### Manta 03-S2 — OAE (pontes, viadutos)

**Missão no contexto Manta:** Apoiar projeto, quantificação e análise de
obras de arte especiais (pontes, viadutos, túneis rodoviários).

**Conhecimento técnico essencial:**
- ABNT NBR 6118 (projeto de estruturas de concreto — geral) e a norma
  ABNT específica de pontes de concreto armado e protendido.
- ABNT NBR 8681 (ações e segurança nas estruturas) para definição de
  cargas e combinações.
- Fundamentos de fadiga e durabilidade de estruturas de concreto expostas
  a tráfego pesado.
- Referências internacionais (ex.: AASHTO LRFD) usadas comparativamente em
  projetos com financiamento ou revisão internacional.

**Fontes de atualização contínua:**
- Revisões da série ABNT NBR de estruturas de concreto e pontes.
- Boletins técnicos de associações de engenharia estrutural.

**Gap de maturidade atual:** Núcleo normativo ABNT é estável e conhecido;
maior atenção necessária em manter as revisões de norma sincronizadas
(normas estruturais passam por atualizações periódicas).

---

### Manta 03-S3 — Ferrovia

**Missão no contexto Manta:** Apoiar projetos de via permanente ferroviária
(superestrutura, geometria, AMV).

**Conhecimento técnico essencial:**
- Normas técnicas ferroviárias da ANTT e regulamentos de via permanente
  aplicáveis a concessões ferroviárias federais.
- Fundamentos de geometria de via (curvas, superelevação, bitola) e
  componentes de superestrutura (trilho, dormente, lastro, AMV).
- Referências internacionais (ex.: práticas AREMA nos EUA) usadas
  comparativamente quando não houver norma nacional específica.

**Fontes de atualização contínua:**
- Regulamentos e resoluções da ANTT sobre operação e segurança
  ferroviária.
- Publicações técnicas de associações ferroviárias internacionais.

**Gap de maturidade atual:** Segmento com base normativa nacional menos
unificada que rodovias (mais fragmentada entre concessionárias); é o
vertical S1-S4 com maior necessidade de aprofundamento documental hoje.

---

### Manta 03-S4 — Metrô

**Missão no contexto Manta:** Apoiar projeto e análise de sistemas
metroviários (túneis urbanos, estações, sistemas).

**Conhecimento técnico essencial:**
- Método NATM (New Austrian Tunneling Method) e diretrizes da ITA-AITES
  (International Tunnelling Association) para projeto e execução de
  túneis urbanos.
- Normas ABNT de segurança contra incêndio e acessibilidade aplicáveis a
  estações e sistemas de transporte de passageiros.
- Padrões técnicos específicos de operadores metroviários (cada empresa —
  ex. Metrô-SP — tem diretrizes próprias de projeto, o que exige
  biblioteca por cliente, não só por norma nacional).

**Fontes de atualização contínua:**
- Publicações da ITA-AITES sobre túneis urbanos.
- Diretrizes técnicas publicadas pelos operadores metroviários estaduais.

**Gap de maturidade atual:** Parcialmente coberto por sobreposição com S2
(estruturas) e por conhecimento genérico de túneis; carece de biblioteca
própria de padrões de operador metroviário, que é fragmentada por estado/
concessionária.

---

### Manta 03-S6 — Edificações

**Missão no contexto Manta:** Apoiar projeto, orçamento e due diligence
técnica de edificações (comerciais, institucionais, residenciais)
associadas a projetos de infraestrutura ou a mandatos imobiliários.

**Conhecimento técnico essencial:**
- ABNT NBR 6118 (estruturas de concreto) e ABNT NBR 6120 (ações para
  cálculo de estruturas).
- ABNT NBR 15575 (desempenho de edificações habitacionais).
- ABNT NBR 9050 (acessibilidade a edificações).
- Códigos de obras municipais (variam por município — não há norma
  federal única) e sistema de custos SINAPI (ver Manta 05).

**Fontes de atualização contínua:**
- Revisões da série ABNT de estruturas e desempenho de edificações.
- Atualizações do SINAPI (Caixa/IBGE).

**Gap de maturidade atual:** Segmento mais recente no mapa vertical
("🆕 Criado 2026-07-05" na nomenclatura interna, embora não listado no
CLAUDE.md master atual como S6) — precisa de biblioteca normativa
construída praticamente do zero, com prioridade menor que os segmentos
com maior exposição regulatória internacional (portos, energia,
barragens).

---

### Manta 03-S7 — Portos

**Missão no contexto Manta:** Apoiar estudos e projetos portuários
(dragagem, calado, berços, terminais).

**Conhecimento técnico essencial:**
- Regulamentação da ANTAQ (Agência Nacional de Transportes Aquaviários)
  sobre arrendamento portuário, dragagem e operação de terminais.
- Diretrizes técnicas internacionais da PIANC (World Association for
  Waterborne Transport Infrastructure) para canais de acesso, dragagem e
  dimensionamento de berços — referência técnica de facto no Brasil, com
  seção nacional PIANC recém-criada para adaptação ao ordenamento
  jurídico brasileiro.
- Normas da Autoridade Marítima (NORMAM, Marinha do Brasil) aplicáveis à
  segurança da navegação em áreas portuárias.
- Licenciamento ambiental específico de dragagem (interface com IBAMA/
  órgãos estaduais).

**Fontes de atualização contínua:**
- Publicações técnicas da PIANC e da seção nacional PIANC Brasil.
- Resoluções e notas técnicas da ANTAQ.
- Normas da Autoridade Marítima (Marinha/NORMAM).

**Gap de maturidade atual:** Segmento altamente regulado e com forte
componente internacional (PIANC); é um dos que exigem biblioteca
normativa mais profunda entre os verticais recém-criados, dado que a
harmonização de normas PIANC ao ordenamento nacional ainda está em
andamento em 2026.

---

### Manta 03-S8 — Aeroportos

**Missão no contexto Manta:** Apoiar estudos e projetos aeroportuários
(pista, pátio, terminal de passageiros/carga, balizamento).

**Conhecimento técnico essencial:**
- Regulamentos Brasileiros da Aviação Civil (RBAC) da ANAC, em especial os
  regulamentos de infraestrutura e operação de aeródromos (série que trata
  de projeto de aeródromo e de operação/manutenção).
- ICAO Annex 14 (Aerodromes) — os RBAC de aeródromo são a tradução
  brasileira dos padrões e práticas recomendadas deste anexo, com
  atualizações periódicas por emenda.
- Métodos de dimensionamento de pavimento aeroportuário e classificação
  de capacidade de pavimento (sistemas do tipo PCN/ACN) usados
  internacionalmente.
- Circulares consultivas da FAA (Advisory Circulars) como referência
  comparativa em ausência de detalhamento nacional específico.

**Fontes de atualização contínua:**
- Emendas ao ICAO Annex 14 e correspondentes atualizações dos RBAC pela
  ANAC (o processo de alinhamento entre emenda ICAO e RBAC leva tempo e
  precisa ser rastreado).
- Resoluções da ANAC sobre infraestrutura aeroportuária.

**Gap de maturidade atual:** Segmento tecnicamente denso e de rastreio
duplo (norma internacional ICAO + tradução nacional RBAC, com defasagem
entre as duas) — hoje provavelmente o vertical com maior necessidade de
biblioteca normativa detalhada entre os novos segmentos S6-S11.

---

### Manta 03-S9 — Saneamento (prioridade AySA)

**Missão no contexto Manta:** Apoiar estudos e projetos de sistemas de
água e esgoto (ETA/ETE, adutoras, redes), com prioridade declarada para
mandatos ligados à AySA (companhia estatal de água e saneamento da região
metropolitana de Buenos Aires, Argentina).

**Conhecimento técnico essencial:**
- Lei 14.026/2020 (novo marco legal do saneamento básico brasileiro) e o
  papel ampliado da ANA — desde 2020 renomeada Agência Nacional de Águas e
  Saneamento Básico — na edição de normas de referência regulatória do
  setor.
- Transição do sistema de indicadores do setor: o SNIS (Sistema Nacional
  de Informações sobre Saneamento) encerrou suas atividades em 2023,
  sendo sucedido pelo SINISA a partir de 2024 — qualquer análise histórica
  precisa considerar essa descontinuidade de série.
- Família de normas ABNT aplicáveis a projeto de sistemas de água e
  esgoto (a Manta deve validar o número exato de cada norma por disciplina
  no momento do uso, em vez de fixar números aqui sem confirmação).
- Para o componente AySA/Argentina: regulação local específica da
  prestação de serviços de água e saneamento na área metropolitana de
  Buenos Aires — deve ser tratada como conhecimento à parte do arcabouço
  brasileiro, não uma extensão dele.
- Referências internacionais de benchmarking operacional (ex.: IWA —
  International Water Association) para eficiência e perdas.

**Fontes de atualização contínua:**
- Normas de referência publicadas pela ANA (Agência Nacional de Águas e
  Saneamento Básico).
- Dados e metodologia do SINISA (sucessor do SNIS).
- Regulação e dados operacionais específicos da AySA/Argentina, quando
  aplicável ao mandato.

**Gap de maturidade atual:** Gap alto e duplo: (1) o marco regulatório
brasileiro mudou de forma relativamente recente (2020) e a própria base
de indicadores do setor trocou de sistema (SNIS→SINISA) em 2024, o que
torna fácil citar uma fonte descontinuada sem perceber; (2) o componente
AySA/Argentina exige um corpo de conhecimento regulatório totalmente
distinto do brasileiro que ainda não está claramente segregado na
descrição do agente.

---

### Manta 03-S10 — Energia (transmissão, ANEEL)

**Missão no contexto Manta:** Apoiar análise de editais de leilão de
transmissão de energia elétrica e estudos técnicos associados (RAP,
lotes/sublotes).

**Conhecimento técnico essencial:**
- Regulamentação da ANEEL para leilões de transmissão, com a RAP (Receita
  Anual Permitida) como variável central de disputa no leilão (o
  vencedor é quem aceita operar com a menor RAP).
- Papel do ONS (Operador Nacional do Sistema Elétrico) na operação da
  rede básica e da EPE (Empresa de Pesquisa Energética) nos estudos de
  planejamento que originam os lotes licitados (relatórios de estudo
  técnico que antecedem o edital).
- ABNT NBR 5422 (projeto de linhas aéreas de energia elétrica — critérios
  técnicos), norma revisada e em vigor desde 2024, referência central para
  dimensionamento eletromecânico de linhas de transmissão.
- Estrutura de um edital ANEEL de transmissão (edital principal, anexos
  técnicos por lote/sublote, minuta de contrato de concessão).

**Fontes de atualização contínua:**
- Editais publicados pela ANEEL para cada leilão de transmissão.
- Estudos de planejamento da EPE (ciclo de relatórios que fundamenta cada
  leilão).
- Revisões da ABNT NBR 5422 e normas correlatas de subestações.

**Gap de maturidade atual:** Segmento com fonte primária de alta
qualidade e bem estruturada (editais ANEEL são públicos e padronizados),
mas o conhecimento precisa ser reconstruído a cada novo leilão (RAP e
lotes mudam por edital) — gap está em manter o pipeline de ingestão de
editais atualizado, não na compreensão do mecanismo regulatório em si.

---

### Manta 03-S11 — Barragens

**Missão no contexto Manta:** Apoiar análise de segurança, classificação
de risco e devida diligência técnica de barragens (acumulação de água e
disposição de rejeitos de mineração).

**Conhecimento técnico essencial:**
- Lei 12.334/2010 — Política Nacional de Segurança de Barragens (PNSB) —
  e o Sistema Nacional de Informações sobre Segurança de Barragens
  (SNISB), com competências repartidas entre ANA, ANEEL, IBAMA e ANM
  conforme a finalidade da barragem.
- Regulamentação específica da ANM (Agência Nacional de Mineração) para
  barragens de rejeitos de mineração — o arcabouço foi revisado
  significativamente nos últimos anos (ex.: resoluções sobre Plano de
  Ação de Emergência para Barragens de Mineração — PAEBM, classificação de
  risco e critérios de projeto como fator de segurança e borda livre).
- Diretrizes técnicas do ICOLD (International Commission on Large Dams) e
  do CBDB (Comitê Brasileiro de Barragens) sobre segurança estrutural e
  operacional de barragens de grande porte.
- Tipologias construtivas relevantes (CFRD — Concrete Face Rockfill Dam,
  CCR — Concreto Compactado a Rolo) e seus critérios de projeto
  específicos.
- Instrumentos da PNSB: Plano de Segurança da Barragem (PSB), Plano de
  Ação de Emergência (PAE) e classificação por categoria de risco e dano
  potencial associado.

**Fontes de atualização contínua:**
- Resoluções da ANM sobre segurança de barragens de mineração (arcabouço
  em revisão ativa nos últimos anos, inclusive com participação de
  Ministério Público em consultas recentes).
- Boletins técnicos do ICOLD e publicações do CBDB.
- Atualizações do SNISB (ANA) sobre cadastro e classificação de barragens.

**Gap de maturidade atual:** Um dos segmentos de maior exposição
reputacional e regulatória do portfólio (rompimentos de barragem de
rejeitos geraram revisão normativa recorrente no Brasil) — exige a
biblioteca normativa mais robusta e mais frequentemente revisada entre
todos os 21 agentes, com verificação redobrada de qualquer número de
resolução ANM citado, dado o ritmo de revisão do arcabouço.

---

## Síntese — maiores gaps de maturidade (visão do documento)

Em ordem decrescente de gap percebido:

1. **S9 — Saneamento (prioridade AySA):** combina uma mudança recente de
   marco legal e de sistema de indicadores (SNIS→SINISA) com a exigência
   de um corpo de conhecimento regulatório argentino (AySA) que hoje não
   está claramente segregado do arcabouço brasileiro.
2. **S11 — Barragens:** arcabouço normativo (especialmente ANM) em
   revisão ativa e de altíssima exposição reputacional; qualquer citação
   desatualizada tem consequência prática severa.
3. **S8 — Aeroportos:** depende de rastrear duas camadas normativas em
   paralelo (emendas ICAO Annex 14 e a tradução/atualização correspondente
   nos RBAC da ANAC), com defasagem natural entre as duas.

Estes três, junto com Manta 20 — esg (agente horizontal aparentemente
ainda não consolidado no registro operacional), são os candidatos
prioritários para investimento de curadoria normativa no próximo ciclo.
