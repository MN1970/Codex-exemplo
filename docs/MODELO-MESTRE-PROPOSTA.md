# Modelo Mestre de Proposta — Validação contra MNT-2026-COM-1183_D

Este documento registra a análise solicitada pela Diretoria (MN) sobre se a
proposta técnico-comercial **MNT-2026-COM-1183_D** (Concessão Rota 2 de
Julho — BR-116/324/BA, cliente Nova Infra Invest) pode servir de **modelo
básico/mestre de proposta** do Manta Maestro.

A validação foi feita contra a skill operacional que hoje gera as propostas
comerciais da Manta — `proposta-comercial` (consumida pelo agente
**A7-bd**, ver `CLAUDE.md`) — e não apenas por leitura isolada do PDF.

---

## 1. Padrão canônico vigente (skill `proposta-comercial`)

A skill define uma estrutura fixa de **18 seções + Anexo I**, convenção de
ID `MNT-YYYY-COM-NNNN`, versionamento `REV_00/REV_01/...` e tabela
tarifária padrão (13 perfis, base 176h/mês):

| # | Seção |
|---|---|
| 1 | Introdução |
| 2 | Objeto |
| 3 | Escopo dos Serviços |
| 4 | Documentação a ser Disponibilizada |
| 5 | Entregáveis |
| 6 | Fora do Escopo |
| 7 | Prazo |
| 8 | Dos Casos Omissos |
| 9 | Benefícios e Valor |
| 10 | Equipe |
| 11 | Modalidade Contratual |
| 12 | Preço |
| 13 | Medição e Pagamento |
| 14 | Não Aliciamento e Confidencialidade |
| 15 | Validade da Proposta |
| 16 | Contato Comercial e Dados da Empresa |
| 17 | Limitação de Responsabilidade |
| 18 | Disclaimer |
| Anexo I | Apresentação da Empresa |

## 2. Estrutura do documento de referência (MNT-2026-COM-1183_D)

O documento usa **13 seções em 4 Partes**, com controle de revisão por
letra (`_A`.._D`) e ficha técnica de fechamento:

| Parte | Seções |
|---|---|
| I — Técnico-Comercial | 01 Contexto e Objetivo · 02 A Concessão (dados oficiais e escopo físico) · 03 Objeto e Cenários · 04 Trabalho Base (+ método do paramétrico) · 05 Módulo Adicional (Engenharia de Valor) · 06 Entregáveis por Cenário · 07 Equipe (+ 07.1 CVs) · 08 Prazo e Cronograma · 09 Benefícios e Valor |
| II — Comercial | 10 Preço e Modalidade (+ 10.1 Success Fee) · 11 Infraestrutura e Ferramentas Incluídas · 12 Medição e Pagamento · 13 Propriedade Intelectual e Cláusulas Finais |
| III — Portal Manta | Exemplos de interface (não numerado) |
| IV — Institucional | Documento em apartado (não embutido no PTC) |

## 3. Mapeamento seção a seção

| Skill (18 seções) | Documento de referência | Observação |
|---|---|---|
| 1 Introdução | 01 Contexto e Objetivo | Equivalente, mais focado no BP do cliente |
| 2 Objeto | 03 Objeto | Expandido em **Cenários** (base + módulo opcional) — não existe no padrão atual |
| 3 Escopo dos Serviços | 04 Trabalho Base | Muito mais detalhado: inclui método em 5 etapas, banco de custos, 3 exemplos numéricos reais |
| 4 Documentação a Disponibilizar | — (implícito) | Não é seção própria; citado via fontes da Audiência Pública |
| 5 Entregáveis | 06 Entregáveis por Cenário | Equivalente, com marcos (D+20/D+30/D+60/D+90) |
| 6 Fora do Escopo | 13 (linha de tabela) | Fundido em "Cláusulas Finais", não é seção própria |
| 7 Prazo | 08 Prazo e Cronograma | Equivalente, com Gantt textual e regra de ancoragem ao leilão |
| 8 Casos Omissos | 13 (linha de tabela) | Fundido |
| 9 Benefícios e Valor | 09 Benefícios e Valor | **Mesma numeração e mesmo conteúdo-tipo** da skill |
| 10 Equipe | 07 Equipe Técnica | Equivalente, com currículos resumidos (07.1) — vai além do padrão |
| 11 Modalidade Contratual | 10 Preço e Modalidade | Fundido com Preço |
| 12 Preço | 10 Preço e Modalidade | Fundido; inclui inovação: **success fee segregado em módulo opcional (10.1)** |
| 13 Medição e Pagamento | 12 Medição e Pagamento | Equivalente |
| 14 Não Aliciamento | 13 (linha de tabela) | Fundido |
| 15 Validade | 13 + Ficha Técnica | Fundido |
| 16 Contato/Dados da Empresa | 13 + Ficha Técnica | Fundido, mas com Ficha Técnica mais completa que o padrão |
| 17 Limitação de Responsabilidade | 13 (linha de tabela) | Fundido |
| 18 Disclaimer | 13 (linha de tabela) | Fundido |
| Anexo I | Parte IV | Mantido **fora** do PTC como documento separado — boa prática, evita inflar o corpo comercial |

Não há nenhuma seção do padrão canônico **ausente de conteúdo** no
documento — 6/18 seções (Fora do Escopo, Casos Omissos, Validade, Contato,
Limitação, Disclaimer) foram condensadas em uma única seção de
"Cláusulas Finais" em formato de tabela, em vez de manter numeração
individual.

## 4. O que o documento acrescenta ao padrão

Elementos que **não existem** na skill `proposta-comercial` hoje e que
valeram a pena reter:

1. **Seção de dados oficiais do empreendimento** (02) — quadro físico
   extraído de fonte primária (PER, Audiência Pública) com rastreabilidade
   número-a-número. Essencial em propostas de concessão/infraestrutura de
   grande porte, onde o cliente decide investimento a partir desses dados.
2. **Cenários de contratação** — separação explícita entre escopo-base de
   preço fixo e módulo opcional remunerado por success fee, com cláusula
   de "sem acordo, sem success fee". Resolve um caso comum (cliente quer
   opcionalidade sem comprometer o preço fechado) que o padrão atual não
   modela.
3. **Método do paramétrico exposto em 5 etapas + exemplos numéricos reais**
   (insumos, curva ABC, desvio vs. tabela oficial) — eleva a credibilidade
   técnica além do texto genérico de "Benefícios e Valor".
4. **Seção de Infraestrutura e Ferramentas Incluídas** — itemiza o que está
   incluso (plataformas de IA, tokens, AutoCAD, Civil 3D, SharePoint,
   O365), hoje disperso implicitamente no padrão.
5. **Controle de Revisão** no topo do documento (o que mudou de uma
   revisão para a outra) e **Ficha Técnica** de fechamento — praticamente
   ausentes do padrão atual, que trata isso apenas via nome do arquivo/ID.

## 5. Pontos a reconciliar antes de tornar mestre

- **Versionamento**: o documento usa sufixo de letra (`_A`, `_B`, `_C`,
  `_D`):  a skill define `REV_00/REV_01/...`. Escolher um padrão único ou
  documentar quando usar cada um (ex.: letra para propostas de concessão
  em resposta a processo regulatório público, `REV_NN` para o restante).
- **Numeração**: se a fusão das seções 6/8/14-18 em uma única "Cláusulas
  Finais" for adotada como novo padrão, a skill precisa ser atualizada
  para não quebrar referências cruzadas em propostas já emitidas com a
  numeração de 18 seções.
- **Fonte de verdade**: a skill `proposta-comercial` vive centralizada
  (`Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/02-sub-skills/
  skill-proposta-comercial-SKILL.md` no SharePoint) e é sincronizada para
  o runtime — este repositório (`Codex-exemplo`) **não** é a fonte da
  skill, apenas o registro canônico do mapa de agentes/routing. Qualquer
  mudança na skill em si precisa ser feita e aprovada por esse caminho,
  não aqui.

## 6. Recomendação

**Sim, mas como variante especializada, não substituição.** Recomenda-se:

- Adotar MNT-2026-COM-1183_D como **modelo de referência para o perfil
  "PTC-Infraestrutura/Concessão de grande porte"** dentro da skill
  `proposta-comercial` (agente **A7-bd**) — ao lado do modo M1 genérico
  já existente, não no lugar dele.
- Incorporar ao padrão os 5 itens da Seção 4 acima como blocos
  reutilizáveis (dados oficiais rastreáveis, cenários com success fee
  opcional, método do paramétrico em etapas, infraestrutura incluída,
  controle de revisão + ficha técnica).
- Manter a Parte IV (apresentação institucional) como anexo separado, não
  embutido — já é a prática correta do documento de referência.
- Submeter a atualização da `skill-proposta-comercial-SKILL.md` no
  SharePoint ao **gate humano MN** antes de propagar para produção,
  conforme checklist de deploy do Manta Maestro.

O bloco de texto pronto para colar na skill de produção — variante **M6**,
com os 5 itens acima já redigidos — está em
`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`. Falta apenas o passo manual de
publicação no SharePoint (esta sessão não tem acesso de escrita àquele
conector).

---

*Análise feita a partir da leitura integral do PDF `MNT-2026-COM-1183_D`
(27 páginas) e da skill `proposta-comercial` v. carregada em 2026-09-01.
Este arquivo é apenas registro/recomendação — não altera a skill em
produção.*
