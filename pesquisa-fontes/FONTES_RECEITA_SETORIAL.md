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
| **Rodovias** | ANTT — Demonstrações Financeiras das concessionárias + Plano de Contas/Manual de Contabilidade + datasets abertos "Receita de Pedágio"/"Custos Operacionais" (dados.antt.gov.br) | **Autostrade per l'Italia (ASPI)** — balanço 2023 já traz % pronto (manutenção ≈10,8% da receita, pessoal ≈10,1%) | SICRO sozinho é **insuficiente** (custo de obra, não de receita) |
| **Ferrovias** | CVM/DFP de Rumo, MRS, VLI (VLI com número real: receita R$9,95bi / custo R$6,63bi em 2024) | **SEC EDGAR 10-K — Union Pacific, Norfolk Southern, CSX** (EUA) — "operating expenses" já por natureza (compensation & benefits, purchased services & materials, fuel, equipment rents) | Fonte mais forte de toda a Camada 2 internacional |
| **Portos** | CVM (Santos Brasil, Wilson Sons — receita/EBITDA confirmados) + Resolução ANTAQ 49/2021 (Manual de Contas do Setor Portuário / SICRASP) | *Port Economics, Management and Policy* (livro-texto acadêmico aberto) — % mão de obra sobre OPEX por tipo de terminal (contêiner 25–50%, granel 15–20%, carga geral 40–75%) | Operadores globais (PSA, DP World, Hutchison) **não** desagregam custo por natureza publicamente — achado consistente com as 10 tentativas anteriores do Livro Azul |
| **Aeroportos** | ANAC — Demonstrações Financeiras por concessão (fragmentado, ~15-20 aeroportos, sem painel único) | **Fraport AG** (Alemanha) — "Personnel expenses" vs. "Non-staff costs/cost of materials" explícitos; ICAO "State of Airport Economics" como benchmark agregado gratuito | Confirma achado do Livro Azul: Rodovias e Aeroportos são os setores com melhor evidência internacional |
| **Saneamento** | **SNIS** — receita operacional (FN005) + despesa por natureza: pessoal (FN010), produtos químicos (FN011), energia (FN013), terceiros (FN014), por prestador, desde 1996 | **OFWAT** (Reino Unido) — modelos de "base cost" com drivers power/people/service/materials confirmados (energia ≈11% do custo-base médio do setor) | SNIS é o candidato mais forte de todo o catálogo no lado Brasil — número real já obtido (Sanepar 2024: pessoal ≈13,7% da receita) |
| **Metrôs** | Metrô-SP/CMSP (DFs — receita R$3,02bi em 2024, pessoal R$1.872mi) + diagnóstico econômico-financeiro da MetrôRio (SETRAM-RJ) | **NTD/APTA (National Transit Database, EUA)** — API pública com despesa operacional por natureza (labor, fringe benefits, materials & supplies) por agência de "heavy rail", cruzável com receita tarifária | **Melhor fonte de todo o catálogo** — única com API pública nativa e granularidade completa |
| **Energia (transmissão)** | ANEEL — CIEFSE/DCR (plano de contas MCSE, PMSO obrigatório para todas as transmissoras) + RI Taesa/ISA CTEEP/Alupar (RAP e PMSO no mesmo release) | **FERC Form 1** (EUA) — contas regulatórias (Uniform System of Accounts) que isolam labor/materials/contract services, série desde 1994, já parseada (PUDL/OpenEI) | RTP/PRORET de transmissão é metodologia de WACC, **não** decomposição de custo — não confundir |
| **Barragens** | Demonstrações financeiras de Vale/Samarco (custo de descaracterização, ex. Vale ≈1,4% da receita líquida em 2024) + relatórios trimestrais ANM de descaracterização | ICMM/GISTM Tailings Progress Report + literatura acadêmica (Carneiro et al., Resources Policy 2022 — US$/tonelada de rejeito) | **Não existe receita de barragem isolada** — usar % da receita da mineradora operadora é a única abordagem defensável, com ressalva metodológica explícita |

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

## Detalhe completo por segmento

As tabelas completas (todas as fontes candidatas pesquisadas em cada
camada — composição de custo / estatística oficial / consultoria — com
URL, se publica receita, se publica breakdown por natureza, e nota de
confiabilidade) estão registradas nos relatórios brutos dos 8 agentes de
pesquisa desta sessão. Recomenda-se, no próximo passo, consolidar esse
detalhe em planilha (uma linha por fonte) quando o time decidir o formato
final — Excel, JSON ou tabela Supabase — conforme previsto no plano original.

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
