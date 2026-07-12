# Edificacoes — Checklist SAP padrao (A2 Levantamento de Quantitativos)

Referencia: NBR 15575 (desempenho) + NBR 6118/6122/8800/6120 + SINAPI SP
09/2024 + IT-CBMESP + LEED v4.1. Aplicado ao intake A2 de projetos S13
(Edificacoes — vertical residencial/comercial + galpao industrial leve
+ institucional). Consumido por `BriefingGenerator._load_checklist_items("edificacao")`.

Backend de extracao: `backends/ifc/` (leitura nativa QTO do IFC 4).

## Lista base (20 itens)

| SAP           | Descricao                                       | Unidade | Faixa tipica              | Flag se ausente | Norma           |
|---------------|-------------------------------------------------|---------|---------------------------|-----------------|-----------------|
| SINAPI96524   | Estaca helice continua Ø 40 cm ate 20 m          | m       | conforme sondagem         | esperado        | NBR 6122        |
| SINAPI96527   | Sapata isolada C25 armada                       | m3      | area x altura sapata      | condicional     | NBR 6122        |
| SINAPI87905   | Laje protendida macica 12 cm                    | m2      | area piso                 | esperado        | NBR 6118        |
| SINAPI87906   | Laje nervurada polipropileno 25 cm              | m2      | so em vao > 8m            | opcional        | NBR 6118        |
| SINAPI87372   | Alvenaria estrutural bloco 14x19x39             | m2      | vedacao + estrutural      | condicional     | NBR 15961       |
| SINAPI87373   | Alvenaria vedacao bloco ceramico 9 cm           | m2      | vedacao interna           | esperado        | NBR 15270       |
| SINAPI92782   | Pilar concreto C30 20x30 cm                     | m3      | area x altura             | esperado        | NBR 6118        |
| SINAPI92784   | Viga concreto C30 15x50 cm                      | m3      | comp x secao              | esperado        | NBR 6118        |
| SINAPI91940   | Esquadria aluminio linha 25 (janela)            | m2      | area vao                  | esperado        | NBR 10821       |
| SINAPI91942   | Esquadria aluminio linha 50 (porta)             | m2      | area vao                  | esperado        | NBR 10821       |
| SINAPI87881   | Revestimento ceramico piso PEI 4                | m2      | area piso molhavel        | esperado        | NBR 13818       |
| SINAPI88489   | Pintura acrilica interna latex                  | m2      | 2 demaos parede interior  | esperado        | NBR 15494       |
| SINAPI88490   | Pintura acrilica externa (fachada)              | m2      | 2 demaos + primer         | esperado        | NBR 13245       |
| SINAPI87495   | Forro em gesso acartonado                       | m2      | area forro                | esperado        | NBR 14715       |
| SINAPI98459   | Impermeabilizacao cristalizante laje cobertura  | m2      | area cobertura            | esperado        | NBR 9575        |
| SINAPI98460   | Impermeabilizacao manta asfaltica banheiro      | m2      | area piso molhavel        | esperado        | NBR 9575        |
| SINAPI97622   | Sprinkler cabeca padrao K5.6                    | un      | 1 a cada 12 m2 (leve)     | esperado        | IT-CBMESP 23    |
| SINAPI97623   | Tubulacao sprinkler aco preto Ø 25 mm           | m       | comp trecho               | esperado        | NFPA 13         |
| SINAPI91996   | Elevador social 8 paradas 630 kg                | un      | 1 por bloco (habitacional)| condicional     | NBR NM 267      |
| SINAPI92798   | Escada emergencia enclausurada pressurizada     | un      | 1 por bloco > 30m altura  | esperado        | IT-CBMESP 11    |

## Regras de consistencia (consist-guard)

- area_laje_total ≈ area_planta_pavimento x qtd_pavimentos (±3%)
- consumo_forma coerente com area (laje ~1.1x, pilar ~2x, viga ~2.5x)
- consumo_aco: laje 60-80 kg/m3, pilar 100-150 kg/m3, viga 90-120 kg/m3 (warn fora)
- taxa_area_esquadria: 15-25% da area de fachada (warn fora)
- taxa_area_impermeabilizacao_laje: >= area_cobertura (error se contrario)
- alvenaria_estrutural + vedacao ≈ area_paredes_projetadas (±5%)
- sprinkler_qtd >= area_util / 12 m2 (galpao leve) ou 9 m2 (residencial)
  — IT-CBMESP 23
- se altura_ediflicio > 30 m: escada enclausurada pressurizada obrigatoria
- LEED: se declarado, checa consumo agua (aeradores) + energia (envoltoria)

## Discovery hints

- Fonte primaria: **IFC 4** (BIM ISO 16739) — `backends/ifc/` extrai
  QTO nativos via `IfcElementQuantity`. 22 IfcClass mapeadas em PT-BR:
  - `IfcWall` — vedacao/alvenaria
  - `IfcSlab` — laje
  - `IfcBeam` — viga
  - `IfcColumn` — pilar
  - `IfcDoor` — porta
  - `IfcWindow` — janela
  - `IfcSpace` — ambiente
  - `IfcCovering` — revestimento
  - `IfcRailing` — corrimao
  - `IfcStair` — escada
  - `IfcFurnishingElement` — mobiliario (opcional)
- Fallback DXF/DWG (arquitetonico 2D) — tags de layer:
  - `A-WALL-*`, `A-DOOR-*`, `A-WINDOW-*` (AIA CAD Layer Guidelines)
  - `S-COLS-*`, `S-BEAM-*`, `S-SLAB-*` (estrutural)
  - `M-PIPE-SPRK-*` (sprinkler)
- Padroes de nomenclatura brasileira: `EST-PIL-*`, `EST-VIG-*`, `EST-LAJ-*`
- Rebar tag inline: usar mesmo regex do OAE (`(MULTx) N.M ...`)

## Escopo excluido (bloco 5b do briefing)

- MEP detalhado (hidraulica, eletrica, climatizacao) — encaminha para
  agente especializado se necessario
- Fundacao profunda especial (radier estaqueado, tirante) — verifica
  se necessita S13 detalhado
- Reformas complexas com demolicao seletiva — abordagem A5 (advisory)

## Ver tambem

- `edificacoes-checklist-sap.md` alimenta `BriefingGenerator._load_checklist_items("edificacao")`
- Backend: `backends/ifc/app/` (Phase 1 QTO textual)
- SKILL.md master §14.2.1
