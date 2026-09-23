# Relatório de testes funcionais — Manta Maestro (2026-09-23)

Execução do `docs/PLANO-TESTES-MAESTRO-v1.md`, com as decisões de MN de
2026-09-23: **(1)** rodar as 6 camadas; **(2)** custo de API liberado;
**(3)** T5 simulado com os agentes desta sessão; **(4)** corrigir já os
defeitos de baixo risco. Complementa a auditoria de consistência de
2026-09-22 (`docs/auditoria/RELATORIO-AUDITORIA-2026-09-22.md`).

Repositório público (achado P-21): este relatório não traz nome de cliente,
de projeto nem de pessoa. Onde o teste precisou deles, o texto fica só no
banco ou no scratchpad da sessão.

---

## 0. Resumo executivo

| Camada | O que mede | Antes | Depois das correções | Meta | Situação |
|---|---|---|---|---|---|
| T1 Roteamento — referência (`keyword_router.py`) | agente primário certo, 48 prompts | 44/48 (92%) | **48/48** | ≥ 90% | ✅ |
| T1 Roteamento — banco (`maestro_routing_keywords`) | idem | 27/48 (56%) · 6 agentes | **46/48** · 20 agentes | ≥ 90% | ✅ (2 casos ambíguos exigem regra, não palavra) |
| T2 Cobertura de vetor | trechos com embedding | 162/316 (51%) | **316/316** ⁽¹⁾ | 100% | ✅ |
| T2 Busca textual `manta_rag_fts` | acerto@5, 22 perguntas-ouro | **2/22 (9%)** | — (não alterada) | ≥ 70% | 🔴 |
| T2 Busca vetorial `manta_rag_search` | acerto@5 | não medível (51% sem vetor) | **14/22 (64%)** · híbrida chegaria a 19/22 | ≥ 70% | 🟡 |
| T3 R1 (`manta_r1_check`) | 10 sujos / 10 limpos | 4/10 detectados · 3 falsos positivos | **7/10** · **1** falso positivo | 10/10 · ≤ 1 | 🟡 |
| T3 aluci-guard | 5 reais / 5 inventadas | 7/10 | **10/10** (+ 13 testes de regressão) | 10/10 | ✅ |
| T3 consist-guard | 4 defeitos plantados + 1 doc limpo | — | **4/4** + 1 extra · limpo = limpo | 4/4 | ✅ |
| T4 Agentes (30 perguntas) | nota ≥ 4 | **26/30 (87%)** | — | ≥ 80% | ✅ |
| T4 Armadilhas | premissa errada corrigida | **5/6** + 1 parcial | — | 6/6 | 🟡 |
| T4 Referência inventada | aluci nas respostas | **3 inventadas + 1 desatualizada** | — | 0 | 🔴 |
| T5 Ponta a ponta (simulado) | 5 casos S.A.D | 2/5 com rota e handoff certos | **4/5** (E4: slug S1 legado) · notas 4–5 | 4/4 + lacuna E5 | 🟡 |
| T6 SharePoint | índice → arquivo; dry-run da Routine | 5/5 · 6/6 idênticos | — | 5/5 · 0 dif. | ✅ |

⁽¹⁾ Vetores gerados nesta sessão com o mesmo modelo que indexou a base
(validado: cosseno 1,00000 contra vetores já gravados).

**Leitura em uma frase**: os agentes especialistas são bons — raciocinam
certo, pedem dado em vez de inventar número e corrigem premissa perigosa
—, mas a **infraestrutura em volta deles** (busca na base, roteamento no
banco, guardrail R1, registro de normas) estava fraca ou quebrada, e
continua sendo o elo mais fraco do Maestro.

---

## 1. Escopo e método

| Componente | Como foi testado | Fidelidade |
|---|---|---|
| C1 Roteamento | `scripts/test_routing.py` contra o router de referência e contra as palavras-chave do banco (export não versionado) | real |
| C2 RAG | SQL nas funções de produção (`manta_rag_fts`, `manta_rag_search`) | real |
| C3 Guardrails | R1 = função SQL real; aluci-guard = `guardrails/aluci-guard/auditor.py` real; consist-guard = skill de instrução aplicada por um agente Haiku, como o `SKILL.md` prevê | real / simulado |
| C4 Agentes | 6 subagentes (`.claude/agents/*.md`) respondendo às 30 perguntas de `tests/smoke/queries/` + 6 armadilhas | real (agentes do repo) |
| C5 Rubricas | notas 0–5 pelo critério das rubricas de `08-rubricas/` (lidas do SharePoint, somente leitura) | real |
| C6 Skill `manta-maestro` | **simulada**: rota calculada pelo router + agente de destino, com o contexto que o Maestro montaria | simulado — MN pode repetir no chat (§6.2) |

---

## 2. T1 — Roteamento

**Casos**: 36 de `tests/routing/prompts.md` + 12 novos (3 S6, 3 S12–S14, 6
horizontais/ESG), agora parte do arquivo e do CI
(`tests/routing/test_routing_prompts.py`, 49 testes). O
`scripts/test_routing.py` foi reescrito: a versão v4.2 trazia uma terceira
cópia das regras de roteamento, escrita à mão; a nova usa o router de
referência e, opcionalmente, o export do banco.

### 2.1 Antes

- Referência: 44/48. Erros: `dam breach` sem palavra-chave; UHE com
  barragem ia para energia (o CLAUDE.md manda barragens); adutora que
  atravessa barragem ia para barragens (o CLAUDE.md manda saneamento);
  ESG sem agente no router.
- Banco: 27/48. Só conhecia 6 agentes; 0/12 nos casos novos; 7 prompts sem
  nenhuma palavra casada (PIANC, RBAC, PCN, PMSB, ampacidade, SIGBM, dam
  breach); "30 pavimentos" de uma torre residencial ia para **rodovias**
  (casa "pavimento").

### 2.2 Correções aplicadas

- `src/maestro/keyword_router.py`: palavras de barragens (`dam break`,
  `Brumadinho`, `PAEBM`, `alteamento`); `duto` em S14; agente `manta-20-esg`
  (co-agente); **regras de ambiguidade** do CLAUDE.md como código (UHE →
  barragens; adutora + barragem → saneamento); handoffs barragens → energia
  e → óleo e gás; quando o primário é horizontal, o vertical citado entra
  como handoff de contexto.
- Supabase: `supabase/migrations/2026_09_23_testes_t1_routing_keywords.sql`
  — 87 linhas novas, só `INSERT` (61 → 148 linhas; 6 → 20 agentes).
  Horizontais com prioridade 50, abaixo dos verticais.

### 2.3 O que continua aberto

- **O banco não expressa política de ambiguidade** (2 casos ainda erram):
  soma de prioridades não sabe que "ETE + subestação" é saneamento.
  Consumidores do banco deveriam chamar o router, não refazer a regra.
- **Nenhum código consome `maestro_routing_keywords`** (nenhuma função SQL
  a lê; edge functions não existem). Quem usa a tabela é, no máximo, a
  skill no chat — não verificável daqui.
- **Slug legado**: router e banco despacham S1–S4 para
  `agente-infraestrutura`, que só existe em `99-backup/...-legado` no
  SharePoint. Os agentes vivos são `agente-S1-rodovias` … `S4-metro`.
- **Conflito de política**: o CLAUDE.md diz "o segmento decide o dispatch
  primário", mas os testes-ouro (`prompts_golden_40.json`) esperam o
  horizontal quando a atividade domina ("avaliação imobiliária de terreno
  para complexo de energia" → Manta 04). Mantido o comportamento dos
  testes; decisão de MN (§9).
- Índice canônico manda `TBM` para S4-metro e para S12-túneis ao mesmo
  tempo (§12 do índice).

---

## 3. T2 — Base de conhecimento (RAG)

### 3.1 Cobertura de vetor

154 de 316 trechos estavam sem embedding (tipos inteiros: 63 de
`knowledge_base`, 11 de `manual_tecnico`, 12 de `artefato_html` etc.).
Todos gerados nesta sessão com `bge-small-en-v1.5` (384 d) — obtido de
pacote npm que embute os pesos, porque o HuggingFace está bloqueado no
proxy. Validação: vetor recalculado de 2 trechos já indexados deu
cosseno **1,00000** com o gravado; cada lote conferido por md5 do texto e
do vetor. Só `UPDATE ... SET embedding` onde era `NULL`.

### 3.2 Busca textual (`manta_rag_fts`)

22 perguntas-ouro (`tests/rag/golden_queries.yaml`) cobrindo as 11 coleções:

| Variante | Acerto@5 | Perguntas com 0 resultados |
|---|---|---|
| Produção (`plainto_tsquery`, E lógico) | **2/22 (9%)** | 17/22 |
| Mesma busca com OU entre termos | 14/22 (64%) | — |

Causa: `plainto_tsquery` exige que **todas** as palavras da pergunta
estejam no mesmo trecho — pergunta em linguagem natural quase nunca casa.
**Não corrigido** (muda o comportamento de uma função que outros podem
chamar); proposta em §7.

### 3.3 Busca vetorial (`manta_rag_search`)

Com a base 100% vetorizada, gerando o vetor da pergunta com o mesmo
modelo (prefixo de consulta do bge):

| Busca | Acerto@5 | Erra (fora do top 10) |
|---|---|---|
| Vetorial (`manta_rag_search`) | **14/22 (64%)** | aer-1, bar-1, ene-1, ene-2, fer-2, ins-1, ins-2, ins-3 |
| Textual com OU (§3.2) | 14/22 (64%) | — |
| **União das duas** (limite de uma busca híbrida) | **19/22 (86%)** | aer-1, ins-2, ins-3 |

As duas erram perguntas **diferentes** — a vetorial perde as que dependem
de termo exato ("Lei 14.066", "IEEE 738", "NBR 5422"); a textual perde as
de sinônimo ("pavimento flexível" × "pavimentação"). É o argumento
quantitativo para a busca híbrida (§7). Um vetor (trecho 184) ficou com 1
de 384 componentes arredondado diferente (cosseno 0,999999998 com o
correto) — irrelevante para a busca.

### 3.4 Achados estruturais

1. **As 11 coleções de `rag_collections` não se ligam a nenhum
   documento**: `manta_rag_documents` não tem campo de coleção, e o campo
   `projeto` é quase todo de um único projeto (72 de 126). Não há como
   filtrar "busque só em saneamento" — a métrica "coleção certa no 1º
   resultado" do plano é impossível de medir.
2. **Embedder em inglês para base em português** — `bge-small-en-v1.5` é
   monolíngue; a decisão G010 (rejeitar `bge-m3`, multilíngue) merece ser
   revista com os números de §3.3.
3. **Leitura anônima liberada** em `manta_rag_chunks` e
   `manta_rag_documents` (policy `anon SELECT`): quem tiver a chave
   publicável — que vai embutida em qualquer front-end — lê a base inteira.
   R1 passada sobre a base: 4 trechos com nome da lista de clientes, 0 com
   dado pessoal. Não alterado (pode haver portal dependendo disso); decisão
   de MN.
4. Coluna `embedding_m3` vazia em 316/316 (resto da avaliação de bge-m3).

---

## 4. T3 — Guardrails

### 4.1 R1 (`manta_r1_check` / `_sanitize` / `_violations`)

Era uma regex com lista fixa de nomes, por **substring**: "consagrado",
"motivação" e "CCR" (concreto compactado com rolo) viravam violação, e o
`sanitize` corrompia palavras ("Método [CONCESS.]rado"). Não detectava
CNPJ, CPF, telefone, e-mail.

Corrigido no banco (migração `2026_09_23_testes_t3_r1_fronteira_pii`,
**não versionada no repositório** porque a função contém a lista de
clientes): palavra inteira + padrões de CNPJ, CPF, telefone e e-mail.
Assinaturas e rótulos mantidos. Resultado: 7/10 sujos, 1/10 falso
positivo.

Ainda não pega: **nome de pessoa** e **cliente fora da lista** — regex não
resolve; precisa de classificador (ex.: o próprio modelo, no gate
DELIVER). "CCR" é ambíguo (sigla técnica e nome de cliente): decisão de MN.

### 4.2 aluci-guard (`guardrails/aluci-guard/`)

O **registro de referência do guardrail tinha erros** — conferidos na
internet:

| Entrada | Registro dizia | Correto |
|---|---|---|
| NBR 7590 | Cordoalha para protendido | Trilho Vignole (cordoalha é NBR 7483) |
| NBR 12212 / 12214 / 12215 / 12217 | adutora / reservatório / elevatória / ETA (repetida) | poço tubular / bombeamento / adutora / reservatório |
| NBR 5356 | Transformadores para instrumentos | Transformadores de potência |
| "NBR 60076" | norma ABNT válida | **não existe** (IEC 60076 é adotada como série NBR 5356) |
| NBR 15749 | Eletrodos de aterramento | Medição de resistência de aterramento |
| NBR 12266 | Assentamento de tubos de concreto | Valas para assentamento de tubulação |
| NBR 6118 / 6122 | edições 2014 / 2010 | 2023 / 2019 |

Ou seja: o guardrail anti-alucinação **certificava uma norma inexistente**
e reprovava normas reais fora da lista (NBR 15575, NBR 17505). Corrigido
(v0.2 do registro, +22 normas e +5 leis de uso comum; parte/faixa de
norma validada pelo número-base). 10/10 e 13 testes de regressão em
`tests/test_aluci_guard_registry.py`.

Limite que continua: o registro é uma lista curta e manual; não confere
**edição** (NBR 6118:2014 passa como válida) nem ICOLD, PIANC, resoluções
de agência — foi justamente aí que os agentes erraram (§5.2).

### 4.3 consist-guard

É skill de instrução (sem código). Aplicado por um agente Haiku a 2
pareceres HTML: encontrou os 4 defeitos plantados (soma 127,0 × 124,0 =
2,4%; Tabela 5.7 inexistente; entrega 61 dias após o fim do cronograma
financeiro; 45 km × 42 km) e um quinto real que não foi plantado
(custo/km incoerente). Parecer limpo saiu `clean: true`. Por depender do
modelo, não é determinístico: recomendável implementar ao menos
`check_soma_agregado` em código.

---

## 5. T4 — Agentes especialistas

### 5.1 Notas (0–5, critério das rubricas de segmento)

| Agente | Q1 | Q2 | Q3 | Q4 | Q5 | Média | Armadilha |
|---|---|---|---|---|---|---|---|
| portos (S7) | 5 | 5 | 5 | 4 | 5 | 4,8 | ✅ calado ≠ profundidade (UKC, onda, sobredragagem) |
| energia (S10) | 4 | 5 | 5 | 5 | 5 | 4,8 | ✅ faixa de servidão depende da tensão (NBR 5422) |
| saneamento (S9) | 5 | 5 | 3 | 5 | 4 | 4,4 | ✅ exige K1/K2 e vazão de pico |
| aeroportos (S8) | 5 | 5 | 3 | 4 | 5 | 4,4 | 🟡 corrige, mas usa ACN-PCN (substituído por ACR-PCR em 28/11/2024) |
| óleo e gás (S14) | 5 | 5 | 4 | 4 | 4 | 4,4 | ✅ exige contenção (NFPA 30, NR-20) |
| barragens (S11) | 5 | 3 | 3 | 4 | 5 | 4,0 | ✅ recusa alteamento a montante (Lei 14.066/2020) |

26/30 com nota ≥ 4. Pontos fortes consistentes: nenhum agente inventou
**número de projeto** (todos pediram batimetria, VDM, sondagem, data-base
em vez de chutar); todos declararam o que falta; bons handoffs.

### 5.2 Referências erradas nas respostas

| Agente | Citou | Realidade |
|---|---|---|
| barragens | "DNPM/ANM 100.001/2019" para dam break | não existe; é a Res. ANM 95/2022 (atualizada pela Res. ANM 220/2025, que o agente desconhece) |
| barragens | "ICOLD Bulletin 164 trata de CFRD" | 164 é erosão interna; CFRD é o Bulletin 141 |
| saneamento | "marco tarifário PIRHA" de concessionária estrangeira | sigla sem lastro; o regime é a Res. ERAS 30/2026 |
| aeroportos | método ACN-PCN como vigente | ACR-PCR desde 28/11/2024 |
| energia | "S9.A1" para leilão de transmissão; VPL/TIR para Manta 15 | S10.A1; VPL/TIR é Manta 06 |

Padrão: erram **números de documento de nicho** (bulletins, resoluções de
agência, siglas estrangeiras) e **atualizações de 2024–2025** — exatamente
o que o RAG deveria suprir e o aluci-guard deveria pegar, e nenhum dos
dois cobre hoje.

---

## 6. T5 e T6

### 6.1 T5 — Ponta a ponta (simulado)

| # | Célula | Rota | Resultado |
|---|---|---|---|
| E1 | S9.A3.D07 ETE 500 L/s | orçamento + contexto saneamento ⁽²⁾ | 4 — estrutura certa, Acórdão TCU 2622/2013, sem preço inventado; citou concessionárias estaduais pelo nome (R1 leve) |
| E2 | S7.A2.D01 dragagem calado 14 m | portos | 5 — memória de cálculo completa, PIANC 121, zero número inventado |
| E3 | S11.A10.D03 matriz de risco a montante | barragens | 5 — reformula antes da matriz, cita a vedação legal |
| E4 | S1.A1 proposta PRT 60 km | bd (S1 sem agente no repo) | 4 — R1 limpo com placeholders; não usou o template PRT real (está no SharePoint, fora do alcance) |
| E5 | S14 + S11 duto sobre barragem de UHE | barragens + handoffs energia e óleo e gás ⁽²⁾ | 5 — riscos de piping, travessia pelo corpo evitada, handoffs certos |

⁽²⁾ rota só correta depois das correções de §2.2 (antes: E1 perdia o
segmento; E5 não acionava óleo e gás).

### 6.2 Para MN repetir no chat (teste fiel do canal real)

Colar na skill `manta-maestro`, um por conversa, e guardar a resposta:

1. `Orçamento paramétrico de uma ETE de lodos ativados para 500 L/s, com BDI e data-base.`
2. `Volume de dragagem de aprofundamento do canal de acesso para calado de 14 m.`
3. `Monte a matriz de risco da nossa nova barragem de rejeitos com alteamento a montante.`
4. `Proposta técnica PRT para duplicação de rodovia de 60 km.`
5. `Um duto de óleo vai cruzar a barragem de uma UHE: quais cuidados?`

### 6.3 T6 — Integração SharePoint

- Índice → arquivo: 5/5 (S9, A1, F7/consist-guard, D03, 08-rubricas com
  as 41 rubricas declaradas). Ressalva: S9 usa `SKILL-S9-saneamento.md`,
  os demais `SKILL.md` — carregador que procure `SKILL.md` falha em S9.
- Dry-run da Routine de publicação repo → SP: 6/6 arquivos com
  quickXorHash idêntico; nada a publicar.

---

## 7. Avaliação da estratégia do Manta Maestro

**O que está certo e deve ser preservado**

1. **Agentes por segmento com "ordem canônica de raciocínio"** — é o que
   mais funciona. As respostas seguem enquadramento → dados → método →
   lacunas, e isso gerou 6/6 armadilhas tratadas. O ativo da Manta aqui é
   o *método*, e ele está bem codificado.
2. **R2 (não inventar dado) internalizado** — em 36 respostas, nenhum
   número de projeto inventado. Para consultoria de engenharia, é o
   atributo mais valioso.
3. **Composição S.A.D** como modelo mental — orienta handoffs corretos
   (E1, E5) quando o router ajuda.

**O que não funciona e por quê**

1. **Três taxonomias concorrentes.** Repositório (D01 = Hidráulica, Manta
   05 = orçamento), SharePoint (D01 = Tráfego, D06 = Pavimentação, "Manta
   05 CAD, Manta 07 SICRO" no S1) e router (slug legado
   `agente-infraestrutura`). As rubricas seguem o SharePoint. Cada camada
   nova herda uma numeração diferente — é a causa-raiz de metade dos
   achados de ontem e de hoje.
2. **Infraestrutura "declarada" maior que a "funcionando".** Existem 11
   coleções que não filtram nada, uma busca textual que devolve zero em
   77% das perguntas, uma tabela de roteamento que ninguém lê, ML/consenso
   sem implantação (E9). O custo de manter a documentação dessas camadas é
   alto e o retorno é nulo enquanto elas não funcionam.
3. **Guardrails fracos exatamente onde o modelo erra.** O modelo acerta
   engenharia e erra *referência de nicho e atualização recente*; o
   aluci-guard só conhece 52 normas ABNT e 16 leis, e o RAG não cobria
   essas fontes. Os dois precisam mirar esse ponto.
4. **Conhecimento datado sem data.** Nenhuma resposta disse "até onde sei,
   em <data>". ACR-PCR (2024) e Res. ANM 220 (2025) mostram que o risco é
   real em 2026.

**Recomendação estratégica (ordem de valor)**

1. **Uma taxonomia só** — adotar a do SharePoint (já usada nas 41
   rubricas e nos SKILL.md vivos) para D e para os Manta-codes, e
   regenerar repo, router e banco a partir dela. Um arquivo-fonte
   (`taxonomia.yaml`) do qual o resto é gerado.
2. **Fazer o RAG servir aos agentes antes de crescer**: coluna de coleção
   nos documentos; busca híbrida (vetor + textual com OU) como função
   única; perguntas-ouro de `tests/rag/golden_queries.yaml` no CI; reavaliar
   embedder multilíngue com esses números.
3. **Registro de referências como base de dados, não lista em código**:
   normas ABNT com edição vigente, bulletins ICOLD/PIANC, resoluções
   ANM/ANA/ANEEL/ANAC, com data de atualização — alimentando tanto o RAG
   quanto o aluci-guard. É o investimento com maior retorno de qualidade.
4. **Cortar ou congelar o que não tem lastro** (camada "Maestro OS v6",
   tabelas vazias) até existir caso de uso; documentar só o que roda.
5. **Manter o posicionamento de 2026-09-10** (equipe primeiro, IA como
   multiplicador): os testes confirmam que o valor está no método da
   equipe codificado nos agentes, e que o elo fraco é a infraestrutura —
   não a engenharia.

---

## 8. Alterações feitas em produção nesta rodada (e como reverter)

| Onde | O quê | Reverter |
|---|---|---|
| Supabase `maestro_routing_keywords` | +87 linhas (INSERT) | `DELETE ... WHERE created_at >= '2026-09-23'` |
| Supabase `manta_rag_chunks.embedding` | 154 vetores onde era NULL | `UPDATE ... SET embedding = NULL WHERE chunk_id IN (...)` (lista nos lotes do scratchpad) |
| Supabase `manta_r1_*` | fronteira de palavra + PII; 2 funções auxiliares novas | definição anterior guardada fora do repo (contém nomes) |
| Repo | router, registro do aluci-guard, testes, perguntas-ouro, script de roteamento | git revert |

Nenhuma escrita no SharePoint.

## 9. Decisões pedidas a MN

1. **Taxonomia única** (§7.1): adotar a do SharePoint? Isso renumera D e
   Manta-codes no repositório.
2. **Política de dispatch** (§2.3): segmento sempre primário (CLAUDE.md) ou
   atividade dominante (testes-ouro)?
3. **`manta_rag_fts`**: trocar por busca híbrida com OU? (muda o resultado
   para quem já chama a função)
4. **Leitura anônima da base RAG**: fechar para `authenticated`?
5. **"CCR"** na R1 (sigla técnica que coincide com um nome da lista): manter
   bloqueada ou exigir o nome composto?
6. **Slug S1–S4**: trocar `agente-infraestrutura` por `agente-S1-rodovias`
   … `S4-metro` no router e no banco?
7. Rodar os 5 prompts de §6.2 no chat para fechar o T5 no canal real.
