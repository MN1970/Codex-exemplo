# Rodovias — Checklist SAP padrao (A2 Levantamento de Quantidades)

Referencia: SICRO/DNIT OUT/2024 + DER-SP TPU 09/2024 + NBR 15140/12949.
Aplicado ao intake A2 de projetos S1 (Rodovias). Consumido por
`BriefingGenerator._load_checklist_items("rodovia")`.

## Lista base (30 itens)

| SAP        | Descricao                                      | Unidade | Faixa tipica              | Flag se ausente | Norma           |
|------------|------------------------------------------------|---------|---------------------------|-----------------|-----------------|
| SICRO4013116 | CBUQ faixa C 3.5 cm                          | m3      | 0.035 m x area pista      | esperado        | DNIT ES-031/06  |
| SICRO4013118 | CBUQ faixa C binder 4-6 cm                   | m3      | 0.05 m x area pista       | opcional        | DNIT ES-031/06  |
| SICRO4013120 | BGS base 15-20 cm                            | m3      | 0.20 m x area pista       | esperado        | DNIT ES-141/10  |
| SICRO4013122 | BGTC base tratada cimento 20 cm              | m3      | 0.20 m x area pista       | opcional        | DNIT ES-142/10  |
| SICRO4013124 | Sub-base BGS 20 cm                           | m3      | 0.20 m x largura sub-base | esperado        | DNIT ES-139/10  |
| SICRO4013130 | Imprimadura ligante RM-1C                    | m2      | area pista total          | esperado        | DNIT ES-306/97  |
| SICRO4013132 | Pintura de ligacao RR-1C                     | m2      | area entre camadas        | esperado        | DNIT ES-307/97  |
| SICRO4013160 | Reciclagem in-situ com cimento               | m3      | so em reforco             | opcional        | DNIT ES-405/10  |
| SICRO4014115 | Regularizacao subleito                       | m2      | 20 cm x area pista        | esperado        | DNIT ES-137/10  |
| SICRO4014120 | Aterro compactado a >= 100% PN               | m3      | volume greide x plataforma| esperado        | DNIT ES-108/09  |
| SICRO4014122 | Aterro em jazida                             | m3      | volume complementar       | opcional        | DNIT ES-108/09  |
| SICRO4014130 | Escavacao 1a categoria mec.                  | m3      | corte solo                | esperado        | DNIT ES-107/09  |
| SICRO4014131 | Escavacao 2a categoria                       | m3      | rocha alterada            | condicional     | DNIT ES-107/09  |
| SICRO4014132 | Escavacao 3a categoria                       | m3      | rocha sa                  | condicional     | DNIT ES-107/09  |
| SICRO4014135 | Escavacao carga transporte 1 km              | m3.km   | vol x DMT nominal 1km     | esperado        | SICRO 2024      |
| SICRO4014136 | Transporte comercial DMT excedente           | m3.km   | vol x (DMT-1)             | esperado        | SICRO 2024      |
| SICRO4014140 | Bota-fora ou deposito de material excedente  | m3      | residual fill/BF Bruckner | condicional     | DNIT ES-108/09  |
| SICRO4014142 | Emprestimo em jazida licenciada              | m3      | residual cut/EXP Bruckner | condicional     | DNIT ES-108/09  |
| SICRO4014150 | Capina/desmatamento em faixa                 | m2      | area do canteiro          | esperado        | DNIT ES-101/09  |
| SICRO4014152 | Rocada mecanica                              | m2      | area do canteiro fase O&M | opcional        | DNIT ES-101/09  |
| SICRO4014180 | Sinalizacao horizontal termoplastica         | m2      | ext x largura faixa       | esperado        | NBR 6971        |
| SICRO4014182 | Sinalizacao horizontal tinta acrilica        | m2      | ext x largura faixa       | opcional        | NBR 11862       |
| SICRO4014184 | Tachao refletivo bi-direcional               | un      | 1 a cada 8m longitudinal  | esperado        | NBR 14636       |
| SICRO4014186 | Tacha refletiva                              | un      | 1 a cada 4m               | esperado        | NBR 14636       |
| SICRO4014200 | Barreira de concreto New Jersey simples      | m       | canteiro central + bordas | opcional        | NBR 15486       |
| SICRO4014210 | Defensa metalica simples W-beam              | m       | pontos de risco           | esperado        | NBR 6971        |
| SICRO4014212 | Terminal absorcao energia                    | un      | 2 por defensa             | esperado        | NBR 6971        |
| SICRO4014220 | Meio-fio pre-moldado MFC-01                  | m       | borda pista/canteiro      | esperado        | DER-SP IP-DE-D00 |
| SICRO4014230 | Sarjeta STC concreto (revest. primario)      | m       | ext x borda pista         | opcional        | DNIT ES-018/06  |
| SICRO4014240 | Passeio calcada concreto e=6cm               | m2      | so em travessia urbana    | condicional     | NBR 9050        |

## Regras de consistencia (consist-guard)

- espessura_CBUQ: 3-12 cm total (warn fora)
- V_corte + V_aterro devem fechar com Bruckner ±5% (residuais dao emprestimo/BF)
- categoria da escavacao coerente com sondagem (1a >= 60%, 2a 20-30%, 3a <20% em geral)
- imprimadura_area >= area_CBUQ (error se contrario)
- pintura_ligacao_area >= area_binder + area_capa (error se contrario)
- se area_CBUQ_capa > 0 e area_binder == 0: warn (unica-capa nao comum em federal)
- se BF > 20% do corte total: warn (Bruckner mal distribuido)
- se EXP > 20% do aterro total: warn (falta compensacao)

## Discovery hints

- Layers de pavimento no padrao DER-SP: `F-HZ-HATCH-*`
- Perfil longitudinal: `F-VT-MALHA` (quadros no formato Balanco de Massa)
- MDT terreno natural: `MDT_Terreno_*` ou `MDT_TN_*`
- Alignments Civil3D: prefixo do ramo (`BR-XXX_EIXO_*`)
- SICRO estado + data-base: **CRITICO** — MN confirma antes do EXECUTE.
  Default v4.7: SP + OUT/2024.

## Ver tambem

- `rodovias-checklist-sap.md` alimenta `BriefingGenerator._load_checklist_items("rodovia")`
- Backend: `backends/balanco`, `backends/pavimentacao`, `backends/landxml`
- Motor de cenarios: `manta_shared/cenario.py`
- SKILL.md master §14.2.1
