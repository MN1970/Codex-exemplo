# Proposta de Escopo — A11 (Fiscalização), F9 (Meta) e F10 (Pesquisa Evolutiva)

**Status:** PROPOSTA — pendente de validação humana (gate MN). Nenhum destes
três itens está implementado; este documento apenas propõe uma definição de
escopo para as pastas hoje marcadas "a confirmar" no SharePoint da Manta
Associados.

**Autor da proposta:** rascunho gerado por agente Claude Code, a pedido de
mneves@mantaassociados.com, para revisão humana antes de qualquer publicação
no SharePoint ou registro de agente/skill.

**Metodologia:** para A11, os pontos de embasamento normativo foram checados
via busca na web (fontes listadas na seção de referências abaixo); onde não
foi possível confirmar um número de norma específico, o campo foi marcado
explicitamente como "a confirmar" em vez de inventado. Para F9 e F10 — que
descrevem funções internas do próprio sistema Manta Maestro, não práticas de
engenharia externas — não há norma técnica a citar; o texto é uma proposta de
organização interna, também sujeita a aprovação.

---

## A11 — Fiscalização

**Proposta de escopo:**

A11-Fiscalização é a atividade horizontal responsável pelo acompanhamento da
execução contratual de obras e serviços de engenharia — verificação de
conformidade entre o que está sendo executado em campo e o que foi
contratado (projeto, especificações, cronograma e orçamento), com registro
formal apto a servir de prova em processos administrativos, medições,
reequilíbrios e eventuais claims. Diferentemente das demais atividades do
Eixo 1, que operam predominantemente sobre documentos (propostas,
orçamentos, modelos, cronogramas), A11 tem como insumo primário registros de
campo — diário de obra / RDO, boletins de medição, relatórios fotográficos,
fichas de verificação de serviço (FVS) — e como função central transformar
esses registros brutos em pareceres estruturados de conformidade.

A11 não substitui a fiscalização contratual exercida pelo profissional
formalmente designado pelo contratante (com ART/RRT, nos termos da
legislação de licitações) — ela apoia esse profissional e as equipes da
Manta na consolidação, análise e cruzamento desses registros, sinalizando
desvios, atrasos, não conformidades e inconsistências que podem gerar
reequilíbrio contratual (via A6) ou fundamentar reivindicação (via A7).

**Quando invocar:**
- Ao receber diários de obra / RDO (Relatório Diário de Obra) para
  consolidação periódica (semanal, mensal) ou para verificação de um evento
  específico (chuva, embargo, atraso de terceiros).
- Ao processar boletins de medição para conferência de quantidades
  executadas x quantidades contratadas/planejadas, antes do envio a A3
  (orçamento) ou A6 (contratual).
- Quando houver menção a: fiscalização, medição, diário de obra, RDO, livro
  de ordem, FVS (ficha de verificação de serviço), conformidade contratual,
  auto de recebimento, boletim de medição, glosa, paralisação de obra.
- Quando A7 (claims) ou A6 (contratual) precisarem de lastro factual de
  campo (datas, ocorrências, fotos, ordens de serviço) para fundamentar uma
  análise de reequilíbrio ou disputa.
- Em due diligence técnica (fase 7 do ciclo de vida), para checar o histórico
  de conformidade de uma obra antes de uma transação.

**Entregáveis típicos:**
- Relatório de fiscalização (síntese periódica de conformidade, não
  conformidades abertas/fechadas, status físico x planejado).
- Planilha de consolidação de medições (comparativo executado x contratado,
  saldo contratual).
- Registro estruturado de ocorrências extraídas do diário de obra (datas,
  responsáveis, natureza do evento, evidência fotográfica associada).
- Lista de não conformidades com prazo e responsável pela correção.
- Linha do tempo de eventos de campo relevante para reequilíbrio ou disputa
  (insumo direto para A6/A7).

**Handoffs:**

| Para | Quando | Formato |
|------|--------|---------|
| A6 — Contratual | Identificada não conformidade, atraso ou evento com potencial efeito no equilíbrio econômico-financeiro do contrato | Relatório de fiscalização + linha do tempo de ocorrências + evidências (fotos, RDO) |
| A7 — Claims | Evento de campo com indício de causa imputável a terceiros/contratante, ou padrão recorrente de disrupção | Dossiê de ocorrências consolidado (datas, nexo causal preliminar, evidência documental) — sem elaborar o quantum, que é atribuição de A7 |
| A3 — Orçamento | Divergência entre quantidade medida e quantidade orçada | Planilha de medição consolidada com apontamento de divergência |
| A5 — Cronograma | Atraso de campo identificado que impacta o caminho crítico | Registro de ocorrência com data e duração do impacto |

**Normas/referências aplicáveis:**
- Lei nº 8.666/1993, art. 67 — designação de representante da Administração
  para acompanhar e fiscalizar a execução do contrato (norma legal, não uma
  norma técnica ABNT; aplicável a contratos anteriores à Lei 14.133 ou ainda
  regidos por ela).
- Lei nº 14.133/2021 (Nova Lei de Licitações), art. 117 — fiscalização e
  gestão de contratos administrativos.
- Resolução Confea nº 1.024 — referida em fontes consultadas como base para
  a formalização de diário de obra/registro de ocorrências por profissional
  habilitado; **o teor exato e o número desta resolução devem ser
  reconfirmados diretamente na fonte do Confea antes de citação em documento
  formal** — não foi possível validar o texto integral nesta pesquisa.
  a confirmar.
- Manuais de fiscalização e gestão de contratos do DNIT (versão pública
  disponível em gov.br/dnit) — referência de boas práticas para boletim de
  medição, FVS e relatório de não conformidade; não é norma cogente para
  contratos privados ou de outros órgãos, usar como benchmark metodológico.
  a confirmar aplicabilidade caso a caso.
- Exigência de ART (engenheiro civil, CREA) ou RRT (arquiteto, CAU) para o
  profissional responsável pela fiscalização — prática consolidada, sem
  número de norma específico verificado nesta pesquisa. a confirmar.
- Normas de medição específicas por contratante (CAIXA, órgãos estaduais,
  concessionárias) variam por edital — **não citar número de norma
  específica sem confirmação contrato a contrato**. a confirmar.

**Palavras-chave de roteamento:** fiscalização, diário de obra, RDO,
relatório diário de obra, livro de ordem, medição, boletim de medição, FVS,
ficha de verificação de serviço, conformidade contratual, não conformidade,
auto de recebimento, glosa, paralisação, ordem de serviço, ART, RRT,
acompanhamento de obra.

---

## F9 — Meta

**Proposta de escopo:**

F9-Meta é a funcional transversal proposta para concentrar a
autogestão do próprio sistema Manta Maestro — isto é, atividades cujo
"cliente" é o próprio ecossistema de agentes, e não um projeto de engenharia
de um cliente externo. Isso inclui manter atualizado o registro mestre de
agentes (este CLAUDE.md e equivalentes), controlar versionamento de skills e
agentes (o que mudou, quando, por que), coordenar a criação/aposentadoria de
agentes verticais e horizontais, e servir de ponto único de referência para
"o que existe, onde vive e em que versão está" dentro do Maestro.

A hipótese de trabalho, a confirmar com o time, é que F9 absorve — ou
convive de forma claramente delimitada com — a pasta `99-meta/
agente-projeto-claude/` mencionada no índice do SharePoint. Antes de definir
o escopo final, recomenda-se decisão humana explícita sobre uma das duas
opções: (a) `99-meta/agente-projeto-claude/` é o mesmo escopo de F9 e deve
ser unificado/redirecionado para `03-funcionais/F9-meta/`, ou (b) as duas
pastas têm propósitos distintos (por exemplo, F9 cuida do registro de
agentes/skills enquanto `agente-projeto-claude` cuida da gestão do projeto
Claude Code em si — configuração de ambiente, permissões, hooks) e devem
permanecer separadas com um documento curto de distinção entre elas. Este
rascunho não assume nenhuma das duas hipóteses como decidida.

**Quando invocar:**
- Ao criar, versionar ou aposentar um agente (horizontal ou vertical) ou uma
  skill do catálogo Manta.
- Ao atualizar o CLAUDE.md master ou qualquer registro equivalente de
  routing/mapa de agentes.
- Ao revisar a consistência entre o que está documentado (SharePoint,
  CLAUDE.md) e o que está de fato implantado (`.claude/agents/`, skills
  registradas).
- Quando houver dúvida sobre "isso é um agente novo ou uma versão de um
  agente existente?" — decisão que hoje não tem dono claro no mapa de 20
  agentes.
- Antes de um merge/deploy que altere a estrutura de agentes (ex.: os itens
  ainda pendentes no DEPLOY CHECKLIST v4.2 deste repositório).

**Entregáveis típicos:**
- Changelog/histórico de versões de agentes e skills (o que já existe de
  forma embrionária na seção "Histórico de versões" deste CLAUDE.md).
- Registro de decisões de arquitetura de agentes (por que um agente foi
  criado, desativado ou fundido com outro).
- Checklist de deploy de novos agentes/skills (também já esboçado neste
  arquivo, na seção "DEPLOY CHECKLIST").
- Relatório periódico de divergência entre documentação e implementação.

**Handoffs:**

| Para | Quando | Formato |
|------|--------|---------|
| Manta 00 — Maestro (router) | Novo agente/alias precisa ser incluído nas regras de roteamento | Trecho de regra de roteamento proposto + palavras-chave |
| Manta 16 — Arquiteto-IA | Mudança estrutural relevante (novo eixo, nova camada) que exige revisão arquitetural | Proposta de mudança documentada, para avaliação antes de implementação |
| Gate humano (MN) | Qualquer alteração em registro mestre, criação/aposentadoria de agente, ou merge de skill | Documento de proposta + diff do CLAUDE.md/skill, para aprovação explícita antes de publicação |

**Normas/referências aplicáveis:** não se aplica — F9 é uma função de
governança interna do sistema de agentes da Manta, não uma prática de
engenharia civil regida por norma técnica externa. a confirmar apenas no
sentido de que o formato final do processo de versionamento (ex.: semver,
changelog) deve ser decidido pelo time, não pressuposto aqui.

**Palavras-chave de roteamento:** meta, registro de agentes, versionamento
de skill, changelog de agente, governança do Maestro, agente-projeto-claude,
deploy checklist, catálogo de skills, ciclo de vida do agente.

---

## F10 — Pesquisa Evolutiva

**Proposta de escopo:**

F10-Pesquisa Evolutiva é a funcional transversal proposta para
concentrar a vigilância contínua de fontes externas relevantes ao negócio da
Manta — atualizações de normas técnicas de engenharia, mudanças
regulatórias por segmento (ANEEL, ANTAQ, ANAC, ANTT, DNIT etc.), inteligência
de mercado (editais, concorrência, tendências do setor de infraestrutura) —
e alimentar essas atualizações de volta para os agentes verticais e
horizontais pertinentes. É uma função de "pesquisa e vigilância", não de
entrega a cliente: o produto de F10 é conhecimento estruturado que outros
agentes (A9-Regulatório, os agentes verticais S1-S10, A13-BD) consomem, não
um relatório entregue diretamente a um cliente externo da Manta.

A menção a um "Daily Evolution Engine" em outras skills do ecossistema
sugere a intenção de que essa vigilância rode em cadência diária ou
periódica regular, mas este documento não assume nenhuma ferramenta,
fornecedor, dataset ou mecanismo específico como já existente — isso deve
ser especificado e aprovado separadamente pelo time técnico. O escopo aqui
proposto é apenas funcional (o que a função faz e para quem), não uma
descrição de implementação.

**Quando invocar:**
- Em rotina periódica (cadência a definir — diária, semanal) para varredura
  de atualizações normativas e regulatórias por segmento.
- Quando um agente vertical (S1-S10) ou A9-Regulatório sinalizar
  desatualização de uma referência normativa usada em suas skills.
- Ao preparar uma proposta ou parecer que dependa de estar alinhado com a
  versão mais recente de uma norma, edital-modelo ou prática de mercado.
- Quando houver menção a: atualização normativa, nova versão de norma,
  vigilância regulatória, inteligência de mercado, benchmarking setorial,
  monitoramento de editais, radar regulatório.

**Entregáveis típicos:**
- Boletim periódico de atualizações normativas/regulatórias por segmento,
  com indicação de quais agentes/skills são potencialmente afetados.
- Alerta pontual quando uma norma citada em uma coleção RAG (Supabase) for
  identificada como desatualizada ou revogada.
- Nota de inteligência de mercado (mudanças em editais-modelo, práticas de
  concorrentes, tendências de segmento) para uso por A13-BD e A15-Advisory.
- Recomendação de atualização de coleção RAG ou de skill, encaminhada para
  aprovação humana antes de qualquer alteração de conteúdo em produção.

**Handoffs:**

| Para | Quando | Formato |
|------|--------|---------|
| A9 — Regulatório | Mudança regulatória identificada em segmento coberto por A9 | Nota de atualização regulatória com fonte e data |
| Agentes verticais S1-S10 | Norma técnica do segmento (ex.: ABNT, ANEEL, ANTAQ) atualizada ou revogada | Alerta de atualização normativa, referenciando a coleção RAG afetada |
| F9 — Meta | Atualização implica mudança em skill/agente/registro mestre | Recomendação de mudança, para entrar no fluxo de versionamento de F9 |
| Gate humano (MN) | Antes de qualquer atualização efetiva de conteúdo normativo em coleção RAG de produção | Boletim/nota + fonte primária citável, para validação antes de ingestão |

**Normas/referências aplicáveis:** não se aplica diretamente — F10 é uma
função de vigilância/pesquisa sobre normas de terceiros (ABNT, ANEEL, ANTAQ,
ANAC, ICOLD etc.), não uma prática normatizada em si. O processo de
vigilância (fontes oficiais a monitorar, cadência, critério de relevância)
deve ser definido e documentado pelo time antes de operacionalização. a
confirmar.

**Palavras-chave de roteamento:** pesquisa evolutiva, vigilância normativa,
radar regulatório, atualização de norma, inteligência de mercado,
monitoramento de editais, benchmarking, daily evolution, atualização RAG.

---

## Observações finais / pontos de incerteza sinalizados

1. **A11**: a existência e o número exato da Resolução Confea citada em
   fontes de terceiros como base para obrigatoriedade de diário de
   obra/registro não foram confirmados no texto integral durante esta
   pesquisa — recomenda-se checagem direta no site do Confea antes de
   citar em qualquer documento formal ou parecer.
2. **A11**: normas de medição variam por contratante (DNIT, CAIXA, estados,
   concessionárias); este documento não cita número de norma específica de
   medição por não ter sido possível confirmar uma única referência
   universal aplicável a todos os contratos da carteira Manta.
3. **F9**: a relação entre `03-funcionais/F9-meta/` e
   `99-meta/agente-projeto-claude/` é uma hipótese, não um fato verificado —
   nenhuma das duas pastas foi inspecionada diretamente nesta tarefa (esta
   sessão não tem acesso de leitura ao SharePoint real); a decisão de
   unificar ou manter separado depende de revisão humana do conteúdo real
   dessas pastas.
4. **F10**: o "Daily Evolution Engine" é tratado aqui apenas como um nome
   mencionado em outras skills do ecossistema — este documento não afirma
   que tal mecanismo existe, funciona ou está implementado, apenas propõe o
   escopo funcional que uma função de pesquisa evolutiva deveria cobrir.
5. Nenhum dos três escopos aqui propostos deve ser publicado no SharePoint,
   registrado como skill/agente ou tratado como definição oficial sem
   aprovação humana explícita (gate MN), conforme prática já registrada
   neste repositório para mudanças de escopo de agente.

## Fontes consultadas (busca web, 2026-09-11)

- [Fiscalização de Obras: como funciona no Brasil? - Sienge](https://sienge.com.br/blog/fiscalizacao-de-obras/)
- [Diário de Obra: o que é, o que deve conter, como fazer e modelo grátis - Sienge](https://sienge.com.br/blog/diario-de-obra/)
- [Fiscalização de Obras: como estruturar e o que documentar - OrçaFascio](https://www.orcafascio.com/papodeengenheiro/fiscalizacao-de-obras)
- [TCU — Obras Públicas: Recomendações Básicas para a Contratação e Fiscalização](https://portal.tcu.gov.br/data/files/2E/67/31/ED/63DEF610F5680BF6F18818A8/Obras_publicas_recomendacoes_basicas_contratacao_fiscalizacao_obras_edificacoes_publicas_2_edicao.PDF)
- [Controle de Obras Públicas — Diário de Obra / Livro de Ordem](https://sites.google.com/site/controledeobraspublicas/contratos/fiscaliza%C3%A7%C3%A3o/di%C3%A1rio-de-obra-livro-de-ordem)
- [Guia de Fiscalização de Obras — IFRS](https://ifrs.edu.br/wp-content/uploads/2021/01/Guia-de-Fiscalizacao-de-Obras-do-IFRS.pdf)
- [Manual de Fiscalização de Contratos de Obras e/ou Serviços de Engenharia — DNOCS](https://www.gov.br/dnocs/pt-br/centrais-de-conteudo/documentos/nugov/manuais/manual-de-fiscalizacao-de-contratos-de-obras-e-ou-servicos-de-engenharia/manual_de_fiscalizacao_de_contratos_de_obras_e_servicos_de_engenharia____rev_1-1.pdf)
- [Normas Sobre Medição de Obras — Superintendência de Obras Públicas (SOP-CE)](https://www.sop.ce.gov.br/edificacoes/normas-sobre-medicao-de-obras/)
- [Controle de Obras Públicas — Medição](https://sites.google.com/site/controledeobraspublicas/contratos/fiscaliza%C3%A7%C3%A3o/medi%C3%A7%C3%A3o)
- [Manual de fiscalização de contratos – DNIT](https://egov.df.gov.br/wp-content/uploads/2023/02/Manual-de-fiscalizacao-de-contratos-%E2%80%93-DNIT.pdf)
- [RDO digital para obras públicas: o que muda e o que registrar — Obra Prima](https://blog.obraprima.eng.br/rdo-digital-para-obras-publicas/)
- [Manual de Gestão e Fiscalização de Contratos Administrativos — TRT2](https://ww2.trt2.jus.br/fileadmin/licitacoes/manuais/Manual_Gestao_Fiscalizacao.pdf)
- [Manual Orientativo de Fiscalização de Obras e Serviços de Engenharia — CGE-PB](https://cge.pb.gov.br/gea/downloads/arquivos/ManualObras/manual/MANUAL%20DE%20FISCALIZA%C3%87%C3%83O%20DE%20OBRAS%20v1.pdf)
- [Manual de Fiscalização e Gestão de Contratos — DNIT (aquaviário)](https://www.gov.br/dnit/pt-br/assuntos/aquaviario/manuais-daq/manual_gestao_e_fiscalizacao_de_contratos_2021.pdf)
