# OAE — Checklist SAP padrao (A2 Levantamento de Quantidades)

Referencia: SICRO/DNIT + PRL/RioSP + NBR 6118/7187/7480/15805.
Aplicado ao intake A2 de qualquer projeto S2 (OAE) via `BriefingGenerator`
(v4.7). Cada linha vira 1 item do bloco 6 do briefing pre-extracao.

Fonte do catalogo SAP: `backends/oae/app/aggregator/sap_mapper.py` (16
codigos base + 9 derivados, validado em OAE 622 — Rio Queluz).

## Lista base (22 itens)

| SAP    | Descricao                         | Unidade | Faixa tipica              | Flag se ausente | Norma           |
|--------|-----------------------------------|---------|---------------------------|-----------------|-----------------|
| F3002  | Aco CA-50 estrutural              | kg      | 100-180 kg/m3 concreto    | esperado        | NBR 7480        |
| F2015  | Concreto C30 bloco/travessa       | m3      | 2-8 m3/pilar              | esperado        | NBR 6118        |
| F2018  | Concreto C40 longarina/laje       | m3      | 15-30 m3/longarina        | esperado        | NBR 6118        |
| F1001  | Forma comum madeira               | m2      | perimetro x altura        | esperado        | NBR 14931       |
| F1002  | Forma plana viga/laje             | m2      | area lateral longarina    | esperado        | NBR 14931       |
| O1044  | Aparelho de apoio neoprene        | dm3     | {2,4,8,12,16} unidades    | anomalia se != | NBR 15805       |
| O1632  | Estaca raiz em solo               | m       | 4-30 m por estaca         | esperado        | NBR 6122        |
| O1451  | Estaca raiz em rocha              | m       | 0-10 m por estaca         | opcional        | NBR 6122        |
| O1193  | Arrasamento de estaca             | un      | = qtd estacas             | esperado        | NBR 6122        |
| D5054  | Concreto magro lastro             | m3      | area bloco x 0.05 m       | esperado        | NBR 6118        |
| O2141  | Gradil metalico OAE               | m       | comp ponte x 2 lados      | esperado        | DNIT IPR-698    |
| O2146  | Grout apoio                       | m3      | area apoio x 0.05         | opcional        | NBR 15805       |
| C5001  | Escavacao mecanica sub-obra       | m3      | bloco x 1.5               | esperado        | NBR 5681        |
| T3017  | Reaterro compactado apiloado      | m3      | escav - bloco - magro     | esperado        | NBR 5681        |
| O1174  | Cimbramento metalico              | un      | V_long x 8                | esperado        | NBR 14762       |
| O2021  | Andaime tubular fachada           | m2      | area F1002 espelhada      | opcional        | NBR 6494        |
| O1443  | Estaca metalica cravada           | m       | so se aplicavel           | opcional        | NBR 6122        |
| O1401  | Solo-cimento bloco                | m3      | so se especificado        | opcional        | NBR 12253       |
| O1522  | Barra de transferencia laje       | kg      | conforme detalhe          | opcional        | NBR 6118        |
| O1541  | Junta de dilatacao                | m       | por vao de vigamento      | esperado        | DNIT IPR-698    |
| O2701  | Pintura anticorrosiva metalica    | m2      | so em gradil/apoio        | opcional        | NBR 8095        |
| F2020  | Concreto C50 protendido           | m3      | so em vigamento prot.     | opcional        | NBR 6118        |

## Regras de consistencia (consist-guard)

- taxa_armadura_longarina: 100-180 kg/m3 (warn fora, error se <50 ou >250)
- diametro_cage_vs_furo: cage < furo (error se contrario)
- fck_longarina == 40 MPa (warn se diferente — pode ser projeto especial)
- qtd_neoprene in {2, 4, 8, 12, 16} (anomalia fora — caso raro so com apoio triplo)
- estaca_solo_vs_rocha: soma coerente com sondagem geotecnica ±10%
- fck_bloco == 30 MPa (warn se diferente)
- aco_zero_em_prancha_armacao (error — indica falha de leitura da prancha)
- longarina_sem_extracao_quando_esperada (error se sheet L2-215 presente sem RebarRow)

## Discovery hints (bloco 4 do briefing)

- Sheets tipicas do padrao PRL/RioSP:
  - `-C1-*` topografia
  - `-L2-21x` estrutural (nucleo — sempre olhar aqui)
  - `-L2-215` longarina
  - `-L2-212` bloco/estaca
  - `-L2-214` transversina/aparelho de apoio
- MTEXT patterns (regex do `parse_concrete_notes`):
  - `VOLUME DE CONCRETO:\s*([\d,\.]+)\s*m3`
  - `APARELHOS DE APOIO\s+(\d+)x(\d+)x(\d+)\s*mm\s*\((\d+)x\)`
  - `LASTRO CONCRETO MAGRO\s+e=(\d+)cm`
- Rebar regex universal (`parse_rebar_texts`):
  - `\((\d+)x\)\s*(\d+)\.(\d+)\s*(\d+)([Aa])(\d+)\s*(Ø|%%C)(\d+(?:[\.,]\d+)?)\s*[C|S]?\s*(\d+)(?:cm)?=([\d,\.]+)m?`
- Multiplicadores default: longarina x 2, bloco x 2, estaca x 6 (validar
  no discovery — Phase 2 deriva do sheet count)

## Ver tambem

- `oae-checklist-sap.md` alimenta `BriefingGenerator._load_checklist_items("oae")`
- Backend: `backends/oae/app/aggregator/sap_mapper.py`
- SKILL.md master §14.2.1 — aplicacao P2 Contract em A2
