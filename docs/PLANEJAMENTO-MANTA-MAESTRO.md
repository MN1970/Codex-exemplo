# Planejamento Manta Maestro — Reconciliação de Conhecimento por Agente/Segmento/Disciplina

**Status:** relatório de reconciliação, baseado em leitura AO VIVO da fonte
real de produção (SharePoint) em 2026-09-11. **Este documento substitui
uma versão anterior** que propunha 6 novos "briefs de conhecimento" para
itens que pareciam vazios — essa premissa era **errada** (ver Seção 2). O
conteúdo aqui é o resultado corrigido.

---

## 1. O que este documento pretendia originalmente (e por que mudou)

A primeira versão deste plano partiu do `INDICE-CANONICAL.md` real (v1.1),
que marca `S12-Túneis`, `S13-Mineração`, `S14-Óleo e Gás`,
`D21-Topografia/Geodésia`, `D22-Túneis` e `A11-Fiscalização` como
**"a confirmar"** — e interpretou isso como "pasta vazia, precisa de
conteúdo novo". Nesse entendimento, 5 agentes de pesquisa produziram
briefs completos para cada item, baseados em pesquisa web de normas
técnicas reais.

**Essa interpretação estava errada.** "A confirmar" no índice significa
"conteúdo não auditado nesta revisão do índice" — não "conteúdo
inexistente". Uma segunda rodada de 8 agentes, lendo o SharePoint real
folder a folder, encontrou o oposto: quase todos esses itens **já têm
conteúdo maduro, versionado e em produção**. Publicar os briefs
originais teria arriscado sombrear ou sugerir a substituição de conteúdo
real por versões sintéticas, inferiores em quase todos os casos.

Os 6 arquivos de brief originais (`S12-TUNEIS-SKILL.md`,
`S13-MINERACAO-SKILL.md`, `S14-OLEOGAS-SKILL.md`,
`D21-TOPOGRAFIA-GEODESIA-SKILL.md`, `D22-TUNEIS-SKILL.md`,
`A11-F9-F10-ESCOPO-PROPOSTO.md`) foram **removidos deste PR**.

---

## 2. O que a auditoria real encontrou, item por item

| Item | Estado real | Ação |
|---|---|---|
| **S12-Túneis** | Real, maduro: `agente-tuneis` v1.0.0 (16 KB), 5 vertentes, 10 disciplinas internas próprias (inclui geotecnia de túneis, NATM, TBM, revestimento, ventilação/SCI), RAG `tun:`, handoffs completos. | Nosso rascunho descartado — redundante e inferior. |
| **S13-Mineração** | Real, maduro: `agente-mineracao` v1.0.0 (~20 KB), 5 vertentes, 12 disciplinas (exploração, lavra, beneficiamento, hidrometalurgia, fechamento etc.), RAG `min:`, normas reais (NRM-01-22, NI 43-101, JORC, CBRR). | Nosso rascunho descartado — redundante e inferior. |
| **S14-Óleo e Gás** | Real, maduro: `agente-oleo-gas` v1.0.0 (~18 KB), 5 vertentes, 12 disciplinas, RAG `ogs:`, normas reais (ANP, API, ASME, NFPA, IEC) mais completas que as do nosso rascunho. | Nosso rascunho descartado — redundante e inferior. |
| **D21-Topografia/Geodésia** | Existe, mas o próprio arquivo real se autodeclara **não ratificado** ("candidato, Gate 2 pendente") — situação diferente dos S12-S14. Conteúdo real e nosso rascunho são **complementares** (real tem parâmetros de transformação de datum, GNSS/LiDAR; nosso rascunho tem NBR 14166, PEC/Decreto 89.817, RBAC 100/2026), mas usam esquemas de numeração incompatíveis (`D21/Manta 51` local vs. numeração deste repositório). | Nenhum dos dois publicado — precisa decisão humana sobre qual taxonomia adotar antes de mesclar. |
| **D22-Túneis** | É um **ponteiro deliberado**, não um espaço para conteúdo: aponta para `S2-oae/tuneis-nato/SKILL.md` (8 KB) e `S4-metro/tuneis-metro/SKILL.md` (9 KB), que já contêm o conteúdo técnico real. | Nosso rascunho descartado — duplicava conteúdo que já vive em outro lugar. |
| **A11-Fiscalização** | Real, quase pronto para produção: skill `fiscalizacao-obras` (19 KB) com checklists numéricos por disciplina, classificação de NC em 3 níveis com prazos, schemas JSON de RDO/medição, handoffs para A5/A7/A3, e **protótipo de interface de campo já implementado** (CSS mobile-first). | Nosso rascunho descartado — muito mais raso que o real. |
| **F9-Meta** | Real: governança interna do próprio Maestro (auditoria de canonical, manutenção de índices, ciclo de release) — confirma a hipótese do nosso rascunho, com mais detalhe operacional. | Nosso rascunho era direcionalmente correto mas raso — descartado em favor do real. |
| **F10-Pesquisa Evolutiva** | Real, mas **conceito totalmente diferente** do nosso rascunho: é sobre triagem/reindexação incremental do próprio pipeline RAG (embeddings, chunks), não sobre vigilância regulatória externa. Não existe "Daily Evolution Engine". | Nosso rascunho estava **errado**, não só redundante — descartado. |

**Achado adicional, fora do escopo original**: `S5-Imobiliário`, que o
`CLAUDE.md` deste repositório trata como "sem vertical dedicado, decisão
MN pendente", **também já existe como vertical real e madura** (v3.0.0,
com 5 sub-agentes: viabilidade, incorporação/patrimônio de afetação,
avaliação, gestão de empreendimento, exit/securitização). A única
lacuna real aqui é que nenhum dos documentos de S5 menciona ou reconcilia
com o Manta 04 (horizontal de negócio imobiliário) — sobreposição de
escopo não resolvida, não ausência de conteúdo.

---

## 3. Achado mais importante: colisão de códigos internos (`manta_code`)

Ao ler os frontmatters reais de S12, S13 e S14, apareceu um padrão
consistente e preocupante — cada arquivo carrega **dois campos de código
de segmento que não batem entre si**, e um deles colide com o código
real de OUTRO segmento:

| Arquivo real | `manta_code` (campo legado) | `sp_operational_segment` (campo atual) | Colisão |
|---|---|---|---|
| `S12-tuneis/SKILL.md` | `Manta 03-S5` | `S12` | — |
| `S13-mineracao/SKILL.md` | `Manta 03-S11` | `S13` | **S11 é o código real de Barragens** |
| `S14-oleogas/SKILL.md` | `Manta 03-S12` | `S14` | **S12 é o código real de Túneis** |

Isso não é um problema cosmético: se qualquer parte do sistema real de
routing ainda ler o campo `manta_code` (em vez de `sp_operational_segment`)
para decidir qual agente ativar, uma pergunta sobre óleo e gás poderia
ser roteada para o agente de túneis, e uma pergunta sobre mineração para
o agente de barragens. Comparação com S9-Saneamento e S11-Barragens
(campo `codigo`, sem `manta_code` legado) confirma que a inconsistência
é **isolada aos 3 segmentos mais recentes** (S12-S14), prováveis
sobras do template `agente-infraestrutura v1.0.0` nunca migrado para o
schema mínimo usado pelos segmentos mais novos.

**✅ Gravidade confirmada em 2026-09-13** — investigação direta no
Supabase real (`ogxxgvgtulrbbppshjie`, MCP `Supabase`), com autorização
explícita do usuário para escrever/consultar produção:

- `manta_agent_capabilities`, `sp_agent_routing`,
  `maestro_routing_keywords` e `rag_collections` **não têm nenhuma
  linha** para `agente-tuneis`, `agente-mineracao` ou `agente-oleo-gas`
  — os três existem apenas como documento no SharePoint, nunca foram
  ativados no backend real.
- As tabelas de routing reais roteiam por `agent_slug`/`agent_id`
  (string), nunca por `manta_code` nem por `sp_operational_segment`.

**Conclusão**: a colisão **não é um bug de misroteamento ativo hoje** —
não há nada em produção lendo o campo errado, porque não há nada lendo
os três agentes ainda. É um **risco latente**: vira bug real no dia em
que alguém registrar um desses três agentes usando `manta_code` como
chave de segmento. Nenhuma escrita foi necessária no Supabase para essa
verificação (só leitura).

**Ação recomendada, ainda pendente**: corrigir o `manta_code` nos 3
arquivos reais (`01-segmentos/S12-tuneis/SKILL.md`,
`S13-mineracao/SKILL.md`, `S14-oleogas/SKILL.md`) para bater com o
`sp_operational_segment` de cada um, antes de qualquer ativação futura
no routing. **Não executado nesta sessão**, apesar da autorização de
escrita: a correção da taxonomia D21 (Seção 4 abaixo), feita na mesma
sessão, exigiu reescrever um arquivo real de ~19 KB inteiro via upload
base64 do MCP `SharePoint_Manta` (que não aceita caminho de arquivo
local, só conteúdo em base64 embutido na própria chamada) — processo
que, na prática, expôs risco real de erro de transcrição em textos
longos (dois caracteres divergentes foram detectados e corrigidos por
diff byte a byte antes do envio bem-sucedido). Repetir esse processo
3 vezes para editar um único valor de frontmatter em arquivos de
16–20 KB cada tem custo/risco desproporcional ao benefício, dado que o
achado já foi rebaixado de "ativo" para "latente". Recomendação: a
correção do `manta_code` deve ser feita por quem edita esses arquivos
diretamente na origem (não via reescrita completa por este canal), ou
revisitada nesta sessão só se o usuário priorizar explicitamente.

---

## 4. Correção ao guia de D03-Geotecnia

A versão anterior deste PR recomendava "adicionar S12 como
segmento-cliente de D03". **Essa recomendação está retratada** — ver
`docs/D03-GEOTECNIA-APLICACAO-PROJETOS-MANTA.md` (atualizado) para o
porquê: D03 escopa geotecnia de túnel só para S4 (NATM em metrô), e
S12-Túneis já tem sua própria sub-disciplina de geotecnia interna
(`disciplines/D01-geotecnia-tuneis.md`, dentro da V5 de 10 disciplinas
do próprio `agente-tuneis`) — não delega para D03. O achado real não é
"falta S12 em D03", é um **risco de duplicação de método**: D03 define
RMR/Q/GSI canonicamente, e o D01 interno de S12 parece reimplementar a
mesma classificação de forma independente. Vale uma verificação humana
de que os dois não divergem silenciosamente ao longo do tempo.

---

## 5. Matriz de conhecimento por agente — segue válida como ferramenta de planejamento

`docs/MATRIZ-CONHECIMENTO-POR-AGENTE.md` (mantida neste PR) não foi
invalidada pela auditoria — ela não afirma que conteúdo está ausente,
apenas descreve o conhecimento essencial esperado de cada agente
operacional e aponta gaps de maturidade prováveis (Saneamento/AySA,
Barragens, Aeroportos). Pode servir de checklist para comparar contra
o conteúdo real quando alguém revisar cada skill em produção — mas não
foi cruzada linha a linha contra os arquivos reais, então deve ser lida
como hipótese a validar, não como fato confirmado.

---

## 6. Recomendações finais

1. ~~**Não publicar nenhum dos 6 briefs originais**~~ — feito, já
   removidos deste PR.
2. ~~**Corrigir `CLAUDE.md`**~~ — feito: a entrada de S5-Imobiliário
   como "sem vertical, decisão MN pendente" foi corrigida. **Decisão MN
   (2026-09-13)**: manter S5 (vertical) e Manta 04 (horizontal)
   coexistindo como estão hoje — sem reconciliação de escopo por
   enquanto.
3. ~~**Levar a colisão de `manta_code`** para quem administra o routing
   real de produção~~ — **investigado diretamente em 2026-09-13** (não
   precisou de intermediário: consulta direta ao Supabase real via MCP
   `Supabase`, com autorização do usuário). Achado: os 3 agentes não
   estão registrados no routing/RAG real hoje, então não é um bug ativo
   — é risco latente (Seção 3). **Ainda pendente**: corrigir o
   `manta_code` nos 3 arquivos reais do SharePoint — não executado
   nesta sessão por custo/risco de transcrição em 3 reescritas de
   arquivo grande (ver justificativa na Seção 3); fica como ação para
   quem edita esses arquivos na origem, ou para retomar aqui se o
   usuário priorizar.
4. ~~**D21**~~ — **decidido pelo MN em 2026-09-13 e aplicado na fonte
   real no mesmo dia**: prevalece a numeração D01-D22 deste
   repositório. O arquivo real (`04-disciplinas/D21-topografia-geodesia/
   SKILL.md`) foi corrigido via MCP `SharePoint_Manta` — nota de
   proveniência e seção 8.2 atualizadas para remover o rótulo "Manta 51"
   e a regra de offset "+30" não ratificados; conteúdo técnico (seções
   1–7) preservado. Upload verificado byte a byte contra a fonte local
   antes do envio e por releitura pós-gravação (19.762 bytes).
5. **D03 × S12**: verificar se a classificação RMR/Q/GSI está de fato
   duplicada/divergente entre a disciplina D03 e o D01 interno do
   `agente-tuneis` — não é urgente, mas é dívida técnica real. **Ainda
   pendente.**

---

*Construído com 13 agentes de pesquisa no total nesta sessão (5 na
primeira rodada, que gerou os briefs depois descartados; 8 na segunda
rodada, que auditou o SharePoint real e corrigiu a análise). O processo
em si é um exemplo do porquê nunca se deve tratar "a confirmar" como
"vazio" sem ler o conteúdo real primeiro.*
