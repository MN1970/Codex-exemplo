# D03 — Geotecnia: o que precisa ter para aplicar nos projetos da Manta

**Status:** guia prático, baseado em leitura AO VIVO da fonte real de
produção (SharePoint `04_IA/Manta-Maestro/04-disciplinas/D03-geotecnia/
SKILL.md`, v2.0.0, lida via MCP `SharePoint_Manta` em 2026-09-11). Não é
uma proposta nova — **geotecnia já existe e já está madura** como
Disciplina (Eixo D) do Manta Maestro real. Este documento traduz esse
conteúdo real em termos de aplicação prática nos projetos da Manta, e
identifica as lacunas concretas que faltam fechar.

---

## 1. O que já existe (não precisa criar do zero)

A disciplina **D03-Geotecnia** já cobre, em produção:

- **Investigação de subsolo**: SPT (NBR 6484), sondagem mista e
  rotativa (RQD/TCR), CPT/CPTu, ensaios geofísicos (sísmica de
  refração, MASW, GPR, resistividade), palheta, pressiômetro,
  dilatômetro.
- **Caracterização de solos**: granulometria (NBR 7181), limites de
  Atterberg (NBR 7180), Proctor (NBR 7182), ISC/CBR (NBR 9895),
  cisalhamento direto e triaxial, adensamento oedométrico (NBR 12007).
- **Caracterização de maciço rochoso**: RQD, RMR de Bieniawski, Q de
  Barton, GSI de Hoek — com fórmulas e classes já formalizadas.
- **Estabilidade de taludes**: Fellenius, Bishop, Janbu, Spencer,
  Morgenstern-Price, elementos finitos (PLAXIS, Slide), análise
  probabilística e regressiva.
- **Correlações NSPT**: N60 corrigido, correlações com φ, Cu, E e
  capacidade de carga (Aoki-Velloso, Décourt-Quaresma) — com "red
  flags" de verificação de sanidade já definidos (ex.: FS < 1,3 em
  talude permanente → obrigatório retaludar ou drenar).
- **Normas-chave já mapeadas**: NBR 6484, 6502, 8036, 9820, 7180/7181/
  7182, 9895, 12007, 6458, DNIT DPT PRO 004, ISRM Suggested Methods,
  ASTM D1586, Eurocode 7.
- **Handoffs formais** para D04 (Fundações), D05 (Terraplenagem), D06
  (Pavimentação), D08 (Estrutural OAE), D09 (Contenção), D07
  (Hidrologia), D13 (Meio Ambiente) e A7 (Claims) — com formato de
  entrega especificado para cada um.
- **Skills L1 que a consomem**: `manta-core:extrator-sondagem` (Manta
  22, extrai boletim SPT de PDF), `manta-core:geotech-adapter`
  (persistência em pgvector), `manta-core:rodovias-geotecnia` (perfil
  longitudinal geotécnico), `manta-core:cross-check-tripla` (SPT
  contratado × executado, base de claim).

Segmentos-clientes já mapeados (aplicabilidade real, direto do
SKILL.md): **S1 (Rodovias), S2 (OAE), S3 (Ferrovia), S4 (Metrô), S7
(Portos), S11 (Barragens)** — com peso "Pesado" em terraplenagem (S1),
fundações, contenção, NATM (S4) e barragens (S11).

**Conclusão prática**: se você (ou um agente vertical) precisa de
geotecnia para rodovia, OAE, ferrovia, metrô, porto ou barragem, o
conteúdo técnico já existe e é sólido — o que falta é só *acioná-lo* no
lugar certo (ver seção 3).

---

## 2. O que falta (gap real, verificado)

1. **S12-Túneis não está na lista de segmentos-clientes de D03** — apesar
   de qualquer túnel NATM depender diretamente de RMR/Q/GSI para
   classificar o maciço e definir a classe de suporte. Isso é uma
   lacuna real na fonte oficial, não uma suposição: o SKILL.md de D03
   lista S1/S2/S3/S4/S7/S11 e não lista S12. Como S12 (Túneis) hoje só
   existe como pasta vazia no SharePoint ("a confirmar"), a lacuna em
   D03 provavelmente é só um reflexo de S12 ainda não ter sido escrito
   — ver `docs/S12-TUNEIS-SKILL.md` (deste PR) para a proposta de
   conteúdo de S12, que já assume D03 como dependência principal.
2. **S6 (Edificações) e S9 (Saneamento) não aparecem em D03** apesar de
   fundações de edificações e ETAs/ETEs dependerem de geotecnia —
   provavelmente porque essas disciplinas tratam a parte geotécnica
   dentro de D04 (Fundações) sem retroalimentar D03 explicitamente.
   Não é necessariamente um erro (pode ser intencional — D04 já cobre a
   interface), mas vale confirmação humana.
3. **Nenhum caso-âncora de S12/Túneis** está listado em D03 (os casos
   citados — Ponta Grossa, Metrô L5, Tocantins L2040 — cobrem S1/S4,
   não um túnel isolado como S12 pretende ser).

---

## 3. Como aplicar D03 nos projetos da Manta (guia de uso)

Para qualquer agente vertical (S1, S2, S3, S4, S7, S11 — e S12 quando
formalizado) que precise de geotecnia:

1. **Não reimplemente** classificação de solo/rocha, fórmulas de
   estabilidade ou correlações NSPT dentro do agente vertical — consuma
   D03 via handoff, como já formalizado no SKILL.md real (tabela
   "Handoffs" — ex.: D03 entrega a D04 "Perfil SPT + N60 + parâmetros
   por camada (c, φ, γ, E)").
2. **Use os red flags já definidos** como gate de qualidade antes de
   aceitar um resultado como final — ex.: "NSPT em argila > 20 → provável
   pedregulho ou lente arenosa" e "FS < 1,3 em talude permanente →
   obrigatório retaludar ou drenar". Esses red flags existem
   precisamente para pegar erro de leitura/transcrição de sondagem
   antes que vire proposta ou claim.
3. **Para claims (Manta 01 / A7)**: D03 já formaliza o cruzamento "SPT
   de execução × SPT de contrato — base de variação" como
   `S1.A7.D03` — é o caminho correto para sustentar um pleito de
   variação de categoria de material ou condição geológica imprevista,
   em vez de reconstruir a análise do zero.
4. **Para orçamento (Manta 05)**: a classificação de material de
   1ª/2ª/3ª categoria entregue por D03 a D05 (Terraplenagem) é o insumo
   correto para precificar terraplenagem — não estimar a categoria
   dentro do orçamento sem essa base.
5. **Ao expandir para S12-Túneis**: usar D03 para toda a investigação e
   parâmetros de maciço (RMR/Q/GSI), e a nova disciplina proposta
   **D22-Túneis** (`docs/D22-TUNEIS-SKILL.md`, deste PR) para o método
   construtivo e dimensionamento de suporte propriamente dito — D03 não
   deve ser duplicada dentro de D22, só consumida por ela.

---

## 4. Recomendação

- **Não criar um agente novo para geotecnia** — confirma a decisão já
  tomada nesta sessão (ver PR anterior, fechado): D03 já cobre essa
  necessidade como disciplina transversal madura.
- **Ação concreta e pequena, quando aprovada por MN**: adicionar
  "S12" à lista de segmentos-clientes de D03 no SharePoint real
  (`04-disciplinas/D03-geotecnia/SKILL.md`, campo "Segmentos onde D03
  aparece"), assim que S12-Túneis for formalizado — isso é uma edição
  de uma linha na fonte real, não uma proposta de arquitetura nova.
- **Reaproveitar D03 como template**: os 6 briefs de disciplina/segmento
  novos deste PR (S12, S13, S14, D21, D22) foram escritos espelhando a
  estrutura e o nível de precisão técnica de D03 v2.0.0 — deve
  facilitar a revisão humana por já seguir o padrão real.
