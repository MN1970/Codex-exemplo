# Fontes de Receita Setorial — Consumo de Mão de Obra, Equipamento, Aço e Cimento

Catálogo de fontes (Brasil + exterior) para calcular, a partir da **RECEITA**
dos projetos/operadores (e não do CAPEX de investimento), quanto é consumido
em mão de obra, equipamento, aço e cimento/concreto — por segmento de
infraestrutura. Complementa o modelo já existente no "Livro Azul" (que usa
CAPEX + SICRO/SICFER/SINAPI/CUB + Matriz de Insumo-Produto do IBGE).

**Gerado em**: 2026-08-22 · **Escopo**: Rodovias, Ferrovias, Portos,
Aeroportos, Saneamento, Metrôs, Energia (transmissão), Barragens.

---

## ⚠️ Ressalva metodológica que se aplica a TODO o catálogo

Esta pesquisa foi feita em um ambiente onde o **WebFetch (leitura direta de
PDF/página) esteve bloqueado pelo proxy de rede para praticamente todos os
domínios testados** (gov.br, cvm.gov.br, sec.gov, ferc.gov, sites de RI de
empresas, e até Wikipedia). Todos os 8 agentes de pesquisa relataram o mesmo
bloqueio de forma independente. Isso significa:

- As **URLs listadas são reais** (localizadas via WebSearch, não inventadas).
- Os **números citados vêm de trechos indexados pela busca**, não de leitura
  linha a linha do documento primário.
- **Antes de usar qualquer número deste catálogo em laudo, orçamento ou
  parecer Manta, é obrigatório abrir a fonte manualmente (navegador humano,
  ou ambiente sem esse bloqueio) e confirmar o valor — rodar `aluci-guard`
  no texto final.**

---

## 🔑 Achado estrutural mais importante (afeta a metodologia, não só uma fonte)

**Nenhuma fonte baseada em receita — nem no Brasil, nem no exterior —
desagrega despesa especificamente em "aço" e "cimento/concreto".** Isso se
repetiu nos 8 segmentos e não é falha de busca: é estrutural. Demonstrações
financeiras e sistemas contábeis regulatórios (ANEEL/MCSE-PMSO, SNIS,
FERC Form 1, NTD/APTA, 10-Ks) classificam despesa por **natureza contábil de
OPEX** — Pessoal, Material/Serviços de Terceiros, Depreciação, Energia — e
tratam aço/cimento como **insumo de CAPEX** (obra nova/reforço), nunca como
linha de OPEX recorrente.

**Consequência para a metodologia**: o catálogo abaixo serve para calibrar
coeficientes de **mão de obra, equipamento e serviços/material genérico**
como % da RECEITA operacional. Para **aço e cimento**, a fonte correta
continua sendo o lado CAPEX já usado no Livro Azul (Matriz de Insumo-Produto
do IBGE, aplicada sobre o investimento/reinvestimento, não sobre a receita).
Um modelo híbrido — não um substituto — é a recomendação técnica correta.

---

## Ranking por segmento — melhor fonte Brasil × melhor fonte exterior

| Segmento | Melhor fonte BRASIL | Melhor fonte EXTERIOR | Observação |
|---|---|---|---|
| **Rodovias** | ANTT — Demonstrações Financeiras das concessionárias + Plano de Contas/Manual de Contabilidade + datasets abertos "Receita de Pedágio"/"Custos Operacionais" (dados.antt.gov.br). **Par fechado**: Autoban 2024 — mão de obra+terceiros+material ≈ 8,7% da receita de pedágio | **Autostrade per l'Italia (ASPI)** — balanço 2023 já traz % pronto (manutenção ≈10,8% da receita, pessoal ≈10,1%) | SICRO sozinho é **insuficiente** (custo de obra, não de receita) |
| **Ferrovias** | CVM/DFP de Rumo, MRS, VLI (VLI com número real: receita R$9,95bi / custo R$6,63bi em 2024) | **SEC EDGAR 10-K — Union Pacific, Norfolk Southern, CSX** (EUA) — "operating expenses" já por natureza (compensation & benefits, purchased services & materials, fuel, equipment rents) | Fonte mais forte de toda a Camada 2 internacional |
| **Portos** | CVM (Santos Brasil, Wilson Sons — receita/EBITDA confirmados) + Resolução ANTAQ 49/2021 (Manual de Contas do Setor Portuário / SICRASP) | *Port Economics, Management and Policy* (livro-texto acadêmico aberto) — % mão de obra sobre OPEX por tipo de terminal (contêiner 25–50%, granel 15–20%, carga geral 40–75%) | Operadores globais (PSA, DP World, Hutchison) **não** desagregam custo por natureza publicamente — achado consistente com as 10 tentativas anteriores do Livro Azul |
| **Aeroportos** | ANAC — Demonstrações Financeiras por concessão (fragmentado, ~15-20 aeroportos, sem painel único) | **Fraport AG** (Alemanha) — "Personnel expenses" vs. "Non-staff costs/cost of materials" explícitos; ICAO "State of Airport Economics" como benchmark agregado gratuito | Confirma achado do Livro Azul: Rodovias e Aeroportos são os setores com melhor evidência internacional |
| **Saneamento** | **SNIS** — receita operacional (FN005) + despesa por natureza: pessoal (FN010), produtos químicos (FN011), energia (FN013), terceiros (FN014), por prestador, desde 1996 | **OFWAT** (Reino Unido) — modelos de "base cost" com drivers power/people/service/materials confirmados (energia ≈11% do custo-base médio do setor) | SNIS é o candidato mais forte de todo o catálogo no lado Brasil — número real já obtido (Sanepar 2024: pessoal ≈13,7% da receita) |
| **Metrôs** | Metrô-SP/CMSP (DFs — receita R$3,02bi em 2024, pessoal R$1.872mi) + diagnóstico econômico-financeiro da MetrôRio (SETRAM-RJ) | **NTD/APTA (National Transit Database, EUA)** — API pública com despesa operacional por natureza (labor, fringe benefits, materials & supplies) por agência de "heavy rail", cruzável com receita tarifária. **Número real confirmado**: WMATA (Washington Metro) 2021 — labor = 67,7% do OPEX; materials & supplies = 6,0% | **Melhor fonte de todo o catálogo** — única com API pública nativa e granularidade completa |
| **Energia (transmissão)** | ANEEL — CIEFSE/DCR (plano de contas MCSE, PMSO obrigatório para todas as transmissoras) + RI Taesa/ISA CTEEP/Alupar (RAP e PMSO no mesmo release — **números reais já calculados**: Taesa 2025 PMSO/receita regulatória ≈16,4%; Alupar 2024 custos operacionais/receita líquida ≈16,3%) | **FERC Form 1** (EUA) — contas regulatórias (Uniform System of Accounts) que isolam labor/materials/contract services, série desde 1994, já parseada (PUDL/OpenEI) | RTP/PRORET de transmissão é metodologia de WACC, **não** decomposição de custo — não confundir |
| **Barragens** | Demonstrações financeiras de Vale/Samarco (custo de descaracterização, ex. Vale ≈1,4% da receita líquida em 2024) + relatórios trimestrais ANM de descaracterização | ICMM/GISTM Tailings Progress Report + literatura acadêmica (Carneiro et al., Resources Policy 2022 — US$/tonelada de rejeito) | **Não existe receita de barragem isolada** — usar % da receita da mineradora operadora é a única abordagem defensável, com ressalva metodológica explícita |

---

## Agências reguladoras — lista consolidada

As tabelas por segmento acima citam várias agências espalhadas; esta seção
reúne todas num só lugar, com o que cada uma publica e por que ela é (ou
não) uma boa fonte para o objetivo deste catálogo (receita × consumo por
natureza).

### Brasil

| Agência | Segmento | O que publica (relevante a este catálogo) | URL |
|---|---|---|---|
| **ANTT** — Agência Nacional de Transportes Terrestres | Rodovias, Ferrovias | Demonstrações financeiras por concessionária, Plano de Contas/Manual de Contabilidade (padrão obrigatório, com CVM/ARTESP), datasets abertos "Receita de Pedágio" e "Custos Operacionais", Relatório de Acompanhamento das Concessões Ferroviárias (SAFF) | gov.br/antt · dados.antt.gov.br |
| **ANEEL** — Agência Nacional de Energia Elétrica | Energia (transmissão/distribuição/geração) | CIEFSE/DCR (Demonstrações Contábeis Regulatórias, plano de contas MCSE com PMSO — Pessoal/Material/Serviço de Terceiros/Outros — obrigatório para todas as concessionárias, não só as listadas), RAP por instalação, PRORET (metodologia, não dado bruto) | gov.br/aneel |
| **ANAC** — Agência Nacional de Aviação Civil | Aeroportos | Demonstrações financeiras auditadas por concessão/bloco (receita tarifária + não tarifária); atenção: o "Painel de Indicadores" da ANAC é de **qualidade de serviço**, não financeiro — não confundir os dois | gov.br/anac |
| **ANTAQ** — Agência Nacional de Transportes Aquaviários | Portos | Anuário Estatístico Portuário (operacional, não financeiro) + Resolução nº 49/2021 (Manual de Contas do Setor Portuário / SICRASP — plano de contas padronizado para administrações portuárias **e arrendatários**) | gov.br/antaq |
| **ANM** — Agência Nacional de Mineração | Barragens | Boletim de Barragens de Mineração, relatórios trimestrais de descaracterização (a montante), SIGBM, CFEM — dado de status/royalty, não custo direto de gestão de barragem | gov.br/anm |
| **Ministério das Cidades (SNIS)** | Saneamento | Sistema Nacional de Informações sobre Saneamento — receita operacional total (FN005) e despesa por natureza (pessoal FN010, produtos químicos FN011, energia FN013, terceiros FN014) por prestador, desde 1996 — **fonte mais forte de todo o catálogo no lado Brasil** | app4.mdr.gov.br/serieHistorica |

Agências citadas nas tabelas por segmento mas de uso mais limitado para
este objetivo específico (bom para contexto normativo/técnico, não para
custo por natureza): **ANA** (recursos hídricos, cross-check de barragens
de água), reguladores estaduais como **ARTESP** (SP), **AGERGS** (RS) —
fiscalizam concessões rodoviárias estaduais mas não têm painel aberto de
custo por natureza equivalente ao da ANTT.

### Exterior

| Agência/Órgão | País | Segmento | Por que é forte | URL |
|---|---|---|---|---|
| **FERC** (Federal Energy Regulatory Commission) — Form 1 | EUA | Energia (transmissão) | Contas regulatórias (Uniform System of Accounts) que isolam labor/materials/contract services por utility, série desde 1994, já parseada (PUDL/OpenEI) — **padrão-ouro internacional** | ferc.gov |
| **FTA/NTD** (Federal Transit Administration — National Transit Database), operado com dados da **APTA** | EUA | Metrôs | Despesa operacional por natureza (labor, fringe benefits, materials & supplies) por agência de "heavy rail", com API pública, cruzável com receita tarifária — **padrão-ouro internacional** | transit.dot.gov/ntd |
| **OFWAT** (Water Services Regulation Authority) | Reino Unido | Saneamento | Modelos de "base cost" com drivers power/people/service/materials, benchmarking financeiro do setor de água mais granular do mundo | ofwat.gov.uk |
| **FHWA** (Federal Highway Administration) — Highway Statistics | EUA | Rodovias | Despesa de manutenção rodoviária por "object class"; cobre rodovia pública financiada por imposto, não concessão pedagiada privada | fhwa.dot.gov |

---

## Proposta de padronização

**Não existe uma única fonte que sirva a todos os 8 segmentos** — diferente
do que ocorre no lado CAPEX (onde a Matriz de Insumo-Produto do IBGE serve
igual para todos, porque o IBGE trata "Construção" como atividade única).
Do lado receita, cada setor tem um regime contábil-regulatório próprio, e
forçar uma fonte genérica onde ela não é tecnicamente aplicável produziria
número errado. A padronização correta não é "mesma fonte", é **mesmo tipo
de fonte, na mesma ordem de prioridade**, em cada país:

**Padrão Brasil (nesta ordem de prioridade):**
1. **Sistema contábil-regulatório oficial do setor**, quando existir plano
   de contas obrigatório que já segrega por natureza (Pessoal/Material/
   Serviço de Terceiros) — ANEEL/MCSE-PMSO (energia), SNIS (saneamento),
   ANTT/Plano de Contas (rodovias/ferrovias), ANTAQ/Res. 49-2021 (portos),
   ANAC (aeroportos). Esta camada é auditável, cobre TODOS os operadores
   (não só os listados em bolsa), e é o padrão-ouro.
2. **CVM (DFP/ITR)** das empresas de capital aberto do setor, como
   cross-check numérico real e fonte de série auditada — usar quando (1)
   não existir ou não for suficientemente granular.
3. Para setores sem receita própria atribuível ao ativo de infraestrutura
   (Barragens): usar a receita da empresa operadora associada (mineradora),
   com ressalva metodológica explícita de que é proxy, não medida direta.

**Padrão exterior (nesta ordem de prioridade):**
1. **Formulário regulatório público e obrigatório**, quando existir — FERC
   Form 1 (energia, EUA) e NTD/APTA (transporte sobre trilhos, EUA) são o
   padrão-ouro mundial: dados granulares, auditáveis, com API/download
   público. Priorizar sempre que o setor tiver equivalente.
2. **Divulgação financeira obrigatória de operador privado listado**,
   quando não houver formulário regulatório aberto — SEC 10-K (ferrovias
   dos EUA), Fraport/AENA/ADP (aeroportos europeus), ASPI (rodovias
   pedagiadas).
3. **Referência acadêmica/institucional**, só quando as duas camadas
   acima genuinamente não existirem — *Port Economics, Management and
   Policy* (portos) e ICMM/GISTM + literatura acadêmica (barragens). Usar
   com identificação clara de que é benchmark de dois estágios (coeficiente
   sobre OPEX, não sobre receita diretamente), não dado bruto de balanço.

---

## Rodada 2 — números adicionais confirmados via WebSearch

Após o catálogo inicial, uma segunda rodada de pesquisa (só WebSearch —
WebFetch confirmado bloqueado por política de rede desta sessão, ver
ressalva no topo) aprofundou lacunas específicas de cada segmento. Alguns
números novos e concretos:

| Segmento | Achado novo | Fonte |
|---|---|---|
| Rodovias | **Autoban (Motiva) 2024, real**: pessoal R$165,2mi (+2,5%); serviços de terceiros (inclui conservação) R$127,7mi (+41,8%); material/equipamento/veículos R$30,0mi (+4,7%). Receita não encontrada nesta rodada, então % sobre receita ainda pendente. | DF Autoban 2024 (rodovias.motiva.com.br) |
| Rodovias | SEINFRA-CE confirmado **sem aplicação**: Ceará não tem rodovia concedida à iniciativa privada — a "Tabela de Custos SEINFRA" é só tabela de insumos de engenharia, não dado financeiro de concessão | Diário do Nordeste |
| Ferrovias | **Union Pacific**: compensation & benefits/receita operacional = 20,2% (2024) e 19,97% (2025) | 10-K UNP FY2025, SEC EDGAR |
| Ferrovias | **CSX** 2024: labor & fringe benefits (segmento Rail)/receita total ≈ 20,4% | 10-K CSX FY2024, SEC EDGAR |
| Ferrovias | VLI **Multimodal** (subsidiária, não o consolidado VLI S.A.) 2024: custo dos serviços prestados R$2.486.652mil; materiais/energia/serviços terceiros/outros R$2.750.608mil — usar com ressalva de escopo | DF VLI Multimodal 2024 |
| Portos | Resolução ANTAQ **121/2024** atualizou o Manual de Contas do Setor Portuário (aplicando ICPC 01) — mas ainda **sem painel público agregado** de custo por natureza dos arrendatários | ANTAQ/Kincaid |
| Aeroportos | **Fraport** 9M2025: Personnel expenses €959,1mi; Non-staff costs €1.301,7mi | Fraport Interim Report Q3 9M 2025 |
| Aeroportos | **Groupe ADP** 2024: Charges de personnel €1.259mi (+19,3%); Charges courantes totais do grupo €4.210mi (+17,0%) | Comptes consolidés Groupe ADP 2024 |
| Aeroportos | AENA 2024: números de "gastos de personal"/aprovisionamentos **inconsistentes entre fontes de imprensa** (escopo individual vs. grupo) — não reconciliado, requer leitura direta das Cuentas Anuales | aena.es / imprensa |
| Saneamento | Sabesp (pré-corte): folha ≈R$3bi/ano; energia ≈R$1,5bi/ano — **estimativas de imprensa/CEO**, não valores formais do release/DFP | Bloomberg Línea, InfoMoney |
| Saneamento | Copasa: energia elétrica ≈R$611mi em 2023 (978 GWh) | news.copasa.com.br |
| Saneamento | Ofwat "Water Company Performance Report 2024-25" confirmado publicado (23/10/2025) — números por empresa **não extraíveis via WebSearch** (tabelas dentro do PDF) | ofwat.gov.uk |
| Metrôs | **WMATA (Washington Metro), heavy rail, 2021**: labor = US$1.426.924.660 (**67,7% do OPEX**); materials & supplies = US$127.367.307 (6,0%) — dado real e granular, reforça NTD/APTA como melhor fonte internacional | NTD/FTA Transit Agency Profile |
| Metrôs | SETRAM-RJ (MetrôRio): saldo médio de tesouraria 2022-2023 ≈ R$338mi positivo — dado de caixa, não de receita/custo por natureza | Relatório de Diagnóstico SETRAM-RJ (FIPE) |
| Energia | **Taesa** 2025: PMSO (R$408,9mi) / receita regulatória líquida (R$2,5bi) ≈ **16,4%**; PMSO / RAP operacional (R$4,1bi) ≈ 10,0% | Release 4T25 Taesa |
| Energia | **Alupar** 2024: custos e despesas operacionais (R$652mi) / receita líquida consolidada (R$4,0bi) ≈ **16,3%** | Releases Alupar 4T24 |
| Energia | FERC Form 1 — estrutura confirmada com referência exata: págs. 320-323, contas 561.1-561.8 (Load Dispatching) e 562 (Station Expenses) para O&M de transmissão; exemplo de utility real (AEP/ITC/ATC) **não extraído** via WebSearch | ATC 2023 FERC Form 1; OpenEI/PUDL |
| Barragens | Vale 2025: ≈US$378mi em pagamentos de descaracterização (tentativo — há divergência entre trimestres somados e o total anual citado; não confirmar sem abrir o 20-F/6-K) — **não confundir** com o agregado maior "mandatory cash disbursements" (Brumadinho+Samarco+descaracterização) de US$4,2bi em 2025, que é uma métrica mais ampla | Release Vale 4T25/BrasilMineral |
| Barragens | Samarco: sem número novo de 2025 (permanece ~R$2,8bi acumulado desde 2019); descaracterização de Germano 88% concluída, previsão 2026/2027 (antecipando prazo legal de 2029) | Diário do Comércio |

**Conclusão da rodada 2**: WebSearch consegue confirmar números que já aparecem
resumidos em press release/notícia (Taesa, Alupar, UP, CSX, Fraport, ADP,
WMATA, Autoban), mas **não consegue extrair tabelas internas de PDFs** que só
têm a nota completa dentro do documento (ANTT dataset, DFs ANAC por
concessão, nota completa da Metrô-SP/ViaQuatro, Ofwat WCPR por empresa,
FERC Form 1 por utility, Sabesp/Copasa DFP). Esses casos específicos
permanecem como pendência de validação manual (fora desta sessão).

---

## Rodada 3 — pares receita↔custo por projeto

Uma terceira rodada (8 agentes, alvos cirúrgicos por segmento, só WebSearch)
mirou em fechar o par **receita + custo do MESMO projeto/ano** — a rodada 2
tinha, na maioria dos casos, só um lado do par. Resultado: **2 pares
fechados/confirmados, 1 achado parcial novo, 5 seguem bloqueados** por
exigirem leitura direta de PDF (WebFetch, indisponível nesta sessão).

| Segmento | Resultado | Cálculo |
|---|---|---|
| Rodovias | **Par fechado** — Autoban 2024: receita de pedágio R$3.695.634mil (fonte: relatório de crédito Moody's Local, citando as DFs) | Custos (pessoal+terceiros+material = R$322.911mil) / receita ≈ **8,7%** |
| Barragens | **Confirmado** — Vale 2025: pagamento de descaracterização de barragens US$378mi no ano cheio, separado de Brumadinho (US$299mi) — release oficial "Desempenho da Vale no 4T25 e 2025" | Sobre receita líquida 2025 da Vale — cálculo pendente do valor de receita 2025 (não coletado nesta rodada) |
| Metrôs | **Achado parcial novo** — Metrô-SP 2024: energia de tração R$165,1mi (-12,6% a/a) | Sobre ROL R$3,02bi ≈ **5,5%** — soma-se a pessoal (61,9% já conhecido); material e serviços de terceiros continuam sem valor aberto |
| Ferrovias | Bloqueado — Rumo e MRS só têm texto qualitativo ("custos subiram por mão de obra/manutenção"), sem tabela de valores | requer WebFetch |
| Portos | Bloqueado — Santos Brasil e Wilson Sons: só lucro líquido/EBITDA, nota de custo por natureza não indexada | requer WebFetch |
| Aeroportos | Bloqueado — DF da ANAC (Guarulhos) localizada mas conteúdo não indexado | requer WebFetch |
| Saneamento | Bloqueado — Copasa 2024 tem receita (R$6,97bi) e custo total (R$4,8bi ≈68,9%) mas não a quebra por natureza; Sabesp só texto qualitativo | requer WebFetch |
| Energia | Bloqueado — AEP/ITC/ALLETE só têm variação % ano a ano, não valor absoluto pareado com receita | requer WebFetch |

**Conclusão da rodada 3**: confirma de forma definitiva (3ª vez) que o
WebSearch, sem WebFetch, não consegue abrir a tabela interna de um PDF de
demonstração financeira — só recupera o que já foi resumido em texto
corrido por imprensa/corretora. Os 5 pares pendentes acima são a lista
priorizada para validação manual fora desta sessão (baixar e ler os PDFs
já localizados e linkados nas rodadas 1-3).

---

## Detalhe completo por segmento

As tabelas completas (todas as fontes candidatas pesquisadas em cada
camada — composição de custo / estatística oficial / consultoria — com
URL, se publica receita, se publica breakdown por natureza, e nota de
confiabilidade) estão registradas nos relatórios brutos dos 8 agentes de
pesquisa desta sessão. Recomenda-se, no próximo passo, consolidar esse
detalhe em planilha (uma linha por fonte) quando o time decidir o formato
final — Excel, JSON ou tabela Supabase — conforme previsto no plano original.

## MEF por segmento (Modelo Econômico-Financeiro)

Os coeficientes confirmados nas rodadas 1-3 foram estruturados em um
workbook Excel com 1 aba por segmento — receita do projeto (input) →
coeficientes confirmados/benchmark → consumo estimado (R$) de mão de
obra, material e serviços. Cada célula de coeficiente cita a fonte e o
selo de confiança (Confirmado BR / Confirmado internacional / Parcial /
Pendente). Aço e cimento seguem fora do MEF — ponte explícita para o
modelo CAPEX × IBGE-MIP do Livro Azul. Arquivo: `MEF_Receita_Setorial.xlsx`.

## Próximos passos

1. Validação manual (fora deste ambiente com WebFetch bloqueado) das URLs
   e números citados neste catálogo, com prioridade nas fontes de "melhor
   fonte" da tabela de ranking.
2. Rodar `aluci-guard` sobre este documento antes de qualquer uso em laudo/
   proposta Manta.
3. Decidir formato final do catálogo estruturado (planilha vs. JSON vs.
   Supabase) e migrar este conteúdo para lá.
4. Só depois disso: desenhar o cálculo do coeficiente receita→consumo
   (etapa de implementação, fora do escopo desta pesquisa).

---

_Nota de versão: este catálogo foi originalmente registrado como v4.3 no
CLAUDE.md master; durante o merge com `main`, o registry já havia avançado
para v5.1 (Design Agents ESG), então esta contribuição foi renumerada
para **v5.2** para manter a sequência única de versões._
