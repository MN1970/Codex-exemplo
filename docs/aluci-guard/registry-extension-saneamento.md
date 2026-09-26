# Extensão do registry aluci-guard — Saneamento (Manta 03-S8)

Fonte: `sharepoint/01-agentes-fundamentais/agente-saneamento/SKILL.md` (v1.0.0, 2026-07-05).
Todas as referências abaixo foram extraídas literalmente do texto do SKILL.md — nenhuma
foi inferida ou complementada. Nenhuma verificação externa de vigência/existência foi
feita (fora de escopo desta extração).

## Compatível com schema atual (normas_abnt.py / leis_federais.py)

### normas_abnt.py

- `{"codigo": "NBR 12211-12218", "descricao": "Concepção de sistemas de abastecimento de água (estudos de concepção, ETA) — citada no SKILL.md como faixa de normas ABNT, sem detalhamento individual por número dentro da faixa", "status": "a confirmar"}`
- `{"codigo": "NBR 9648-9651", "descricao": "Sistemas de esgoto sanitário (concepção/projeto) — citada no SKILL.md como faixa de normas ABNT, sem detalhamento individual por número dentro da faixa", "status": "a confirmar"}`

Observação: o SKILL.md cita ambas as faixas apenas como intervalos ("NBR 12211-12218",
"NBR 9648-9651"), sem listar os códigos individuais (ex.: NBR 12211, NBR 12212, ...).
Antes de popular o registry linha a linha, será necessário decompor cada faixa nos
códigos ABNT individuais reais — o que exige consulta à base oficial ABNT (fora de
escopo desta extração).

### leis_federais.py

- `{"codigo": "Lei 14.026/2020", "descricao": "Marco legal do saneamento básico no Brasil (novo marco regulatório, citado no SKILL.md como base do eixo BR e da Q3 do intake)", "status": "a confirmar"}`

## Fora do schema atual (requer nova categoria de registry)

Requer categoria nova — sugestões conforme o pedido: `normas_setoriais.py` (normas/
resoluções de agências reguladoras e órgãos ambientais brasileiros), `normas_internacionais.py`
(normas/guias internacionais) e `normas_argentina.py` (marco regulatório argentino,
prioridade AySA).

### Candidatas a `normas_setoriais.py` (BR — agências/resoluções)

- **SNIS** — Sistema Nacional de Informações sobre Saneamento (citado como fonte de
  indicadores/diagnósticos anuais; também na regra R2 "não inventar SNIS/ERAS/norma").
- **PRC 05/2017** — Portaria de Consolidação nº 5/2017, citada como norma de potabilidade
  BR (referenciada em "resultados analíticos (PRC 05/2017)" e em "san-doc-analitico.md").
- **CONAMA 357/430** — Resoluções CONAMA citadas juntas como norma de lançamento de
  efluentes ("PRC 05/2017 (potabilidade BR), CONAMA 357/430 (lançamento)"). O SKILL.md
  não separa os dois números em entradas distintas — citados sempre como par "357/430".
- **ANA** — Agência Nacional de Águas, citada repetidamente como órgão regulador federal
  BR (Q3 do intake, V2 Inteligência Setorial, aba 4 do artefato). É uma agência/instituição,
  não um código de norma isolado — registrar como referência institucional se a categoria
  setorial incluir esse tipo de entidade.
- **ABES** — Associação Brasileira de Engenharia Sanitária e Ambiental, citada em
  `axes/06-academia.md` como fonte de publicações. Também institucional, não norma numerada.

### Candidatas a `normas_internacionais.py`

- **IWA** — International Water Association, citada repetidamente (V2 Inteligência
  Setorial, fontes RAG, regra 6 do aluci-guard: "NBR/AySA/IWA existem e estão vigentes?").
  No SKILL.md aparece associada a duas publicações/diretrizes específicas: "IWA Water
  Sensitive Cities" e "Sanitation Safety Planning" — citadas como títulos, sem número de
  norma formal.

### Candidatas a `normas_argentina.py` (prioridade AySA)

- **AySA** — Agua y Saneamientos Argentinos, empresa/operador argentino, citada em todo
  o documento (frontmatter, Q3, V2, fontes RAG, integrações, regra 6 do aluci-guard).
  Instituição, não norma numerada isoladamente.
- **ERAS** — Ente Regulador de Agua y Saneamiento (Argentina), citado em Q3 ("AySA, ERAS"),
  V2 Inteligência Setorial, fontes RAG e regra R2 ("não inventar SNIS/ERAS/norma").
- **PIRHA** — citado como "Marco Regulatorio PIRHA" (Q3: "AySA, ERAS, PIRHA"; fontes RAG:
  "Marco Regulatorio PIRHA + projetos (Riachuelo, Sistema Norte, Sistema Sur)"). É o marco
  regulatório argentino propriamente dito, o item mais próximo de uma "norma/lei" no eixo AR.

## Observações

- Total de referências normativas/legais/técnicas explicitamente citadas no SKILL.md: **10**
  itens distintos (2 compatíveis com o schema atual; 8 fora dele).
- Duas das referências compatíveis (NBR 12211-12218 e NBR 9648-9651) estão citadas como
  faixas, não como códigos ABNT individuais — decompô-las em entradas unitárias exigirá
  consulta à tabela oficial ABNT, o que está fora do escopo desta extração.
- CONAMA 357/430 foi mantida como uma única referência combinada porque é assim que o
  SKILL.md a cita (par inseparável no texto), embora sejam duas resoluções distintas na
  prática.
- ANA, ABES, AySA e ERAS são instituições/agências, não normas numeradas — foram incluídas
  porque o SKILL.md as trata como referências a validar (ex.: regra 6 do aluci-guard cita
  "NBR/AySA/IWA existem e estão vigentes?"; regra R2 cita "não inventar SNIS/ERAS/norma").
  Uma categoria setorial/institucional pode precisar de um formato de entrada diferente do
  par (código, descrição, status, ano) usado para normas técnicas e leis.
- Não foram encontradas no SKILL.md menções a códigos SICRO/DNIT, portanto nenhuma entrada
  foi proposta para `sicro.py`.
- Nenhuma norma foi inventada ou inferida além do que está literalmente escrito no
  SKILL.md; nenhuma verificação de vigência foi realizada (todos os itens marcados
  "status a confirmar" ou equivalente).
