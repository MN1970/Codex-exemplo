-- Migration: RAG Collection — Pavimentação (rod:pav:*)
-- Date: 2026-08-04 (FIXED schema)
-- Status: Fase II consolidation
-- Source: .claude/knowledge/rodovias/pavimentacao/08-pavimentacao-especializacoes.md
-- Chunks: 20 entries covering 20 specializations

BEGIN TRANSACTION;

INSERT INTO rag_collections (slug, name, storage_prefix, created_at)
VALUES (
  'rodovias-pavimentacao',
  'Pavimentação — 20 especialidades (materiais, projeto AASHTO/M-E, execução, monitoramento, reabilitação, casos reais)',
  'rod:pav:',
  NOW()
)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO manta_rag_chunks (collection, prefix, content, tokens, created_at)
SELECT
  'rodovias-pavimentacao',
  'rod:pav:' || category,
  content,
  CEIL(LENGTH(content) / 4)::int,
  NOW()
FROM (
  SELECT 'materiais' as category,
    'Ligantes asfálticos — CAP convencional (50/70, 60/80), CAP-modificado com SBS (elasticidade, recuperação), CAP polímero elastomérico (flexibilidade baixa T), CAP borracha (amortecimento, sustentabilidade). Normas: NBR 15086, DNER-ME 001. Viscosidade cinemática especificada. Aplicações: CBUQ convencional (CAP 50/70), drenante (CAP-modificado SBS), porosa (CAP elastomérico).' as content
  UNION ALL
  SELECT 'agregados',
    'Agregados para CBUQ — classificação granulométrica: graúdo >4,75mm (brita 1, brita 2), miúdo <4,75mm (areia natural, britagem), filler (pó pedra, cimento, cal). Origem regional Brasil: Região Sul (SP, PR) granito/gnaisse/quartzito (boa qualidade), Sudeste (RJ, MG) itabirito (polido, menor resistência), Nordeste (BA, PE) quartzito/gnaisse (resistente, escassez areia), Centro-Oeste (GO, MS) calcário/arenito (macios). Ensaios: NBR 12896, atrito ≥0,45 (rodovias principais), Los Angeles ≤40%, absorção ≤2%.' as content
  UNION ALL
  SELECT 'reciclagem',
    'RAP (Reclaimed Asphalt Pavement) — taxa máxima DNIT 20-30% em massa total (limitado rigidez ligante residual). Compatibilidade: usar CAP-modificado com ligante novo. Processamento: moagem, peneiramento, uniformização granulométrica. Benefício: economia ~50% agregado novo, sustentabilidade. RCD máximo em base/subbase 50% (mais permissivo que CBUQ). Legislação: CONAMA 307/2002, NBR 15116. Casos reais: Concessão Imigrantes (SP) 25% RAP (economia R$ 2.3M/100km), Rodovia Açúcar (SP) 15% RAP + 10% RCD.' as content
  UNION ALL
  SELECT 'misturas_especiais',
    'CBUQ Porosa (Drenante) — vazios ≥16-18% (vs 4-8% convencional), reduz ruído, melhor drenagem, menor aquaplanagem. Limitações: vida útil 6-10 anos, manutenção anual (limpeza jato). Custo +30-40%. SMA (Stone Mastic Asphalt) — esqueleto agregado graúdo + matriz filler/ligante, resistência deformação, 15-20 anos, boa drenagem. Custo +40-60%. Aplicação: tráfego pesado, clima quente T>40°C. Norma DNER-ES 385/99. Semi-abertas: vazios 8-12%, balanço drenagem/durabilidade.' as content
  UNION ALL
  SELECT 'concreto_portland',
    'CCP (Concreto Portland em Rodovia) — tipos CPACC (simples), CCP (armado), CPCCR (continuamente armado). Rígido vs flexível: CCP mais durável 30+ anos, menor manutenção, custo inicial +30-40%. Aplicação: tráfego pesado, clima extremo. Especificação: NBR 5732 (cimento), DNIT 010/2004 (projeto). Resistência à compressão ≥35 MPa. Junta 3-6 m. Comparação CBUQ: CBUQ mais rápida construção, CCP maior durabilidade total.' as content
  UNION ALL
  SELECT 'aashto_1993',
    'Método AASHTO 1993 — Equação fundamental: log₁₀(N) = 9.36×log₁₀(SN+1) - 0.20 + [log₁₀(ΔPSI/(4.2-1.5))] / [0.40 + (1094/(SN+1)^5.19)] + 0.372×(EBC-3). Parâmetros: N (repetições eixo 80kN), SN (número estrutural polegadas), ΔPSI (perda serventia, 2-3 típico), EBC (módulo resiliente subrasante psi). Cálculo N: N = AAD × 365 × [(1+i)^A-1] / i × FC × FD. AAD volume diário, A período projeto (20 anos DNIT), i taxa crescimento (3-4%), FC fator convertibilidade, FD fator direcional (0.45). Módulo resiliente: MR(psi) = 2555×CBR^0.64 (CBR<10%), MR = 1043×CBR + 3245 (10-30%). Exemplo: CBR 8% → MR 21.000 psi ≈ 145 MPa.' as content
  UNION ALL
  SELECT 'mecanistico_empirico',
    'Método M-E (Mecanístico-Empírico) — estrutura: modelagem mecanicista FEM/linear elástica multicamadas, resposta estrutural (deformações críticas tração base/compressão subleito), modelos desempenho (fadiga, afundamento), variabilidade climática (temperatura, umidade sazonal, simulação climática), previsão desempenho (trincas, afundamento, serviço). Software: PavementME (AASHTO 2008), Everstress/Everpave. Deformações críticas: ε_t (tração base) e σ_v (compressão subleito). Vantagem: maior precisão vs AASHTO 1993, considera clima regional. Desvantagem: complexidade, dados detalhados material (E*, temperatura-dependência), capacitação software.' as content
  UNION ALL
  SELECT 'fadiga_deformacao',
    'Fadiga concreto asfáltico — modelo exponencial: N_f = K₁ × (1/ε_t)^K₂. N_f (repetições falha), ε_t (deformação tração), K₁, K₂ constantes material (K₂=3-4). Limite prático: 50-100 repetições pico antes trinca visível. Deformação permanente (afundamento) — mecanismo acúmulo deformação sob repetições carga. Afundamento = Σ(ε_p) × espessura camada. Critério falha DNIT: afundamento máximo ≤20mm em 10 anos. AASHTO M-E: previsão contínua vida útil. Sensibilidade: temperatura +10°C reduz módulo ~30%, afeta vida útil significativamente.' as content
  UNION ALL
  SELECT 'modulo_dinamico',
    'Módulo Dinâmico E* (Complex Modulus) — dependência temperatura e frequência: E* = f(T, ω). Ensaio IDT (Indirect Tensile Test): temperatura -10°C a +60°C (cobrindo Brasil), frequência 0.1-25 Hz (velocidades 5-100 km/h). Resultado: diagrama Cole-Cole, E* e ângulo fase δ. Aplicação: entrada método M-E, sensibilidade climática. Comportamento viscoelástico: E* reduz com T elevada e frequência baixa. Normas: AASHTO TP62 (E* dinâmico), AASHTO TP63 (creep dinâmico). Exemplo: CBUQ em T=40°C apresenta E* ~30% menor que T=20°C.' as content
  UNION ALL
  SELECT 'drenagem',
    'Drenagem pavimento — base permeável: BGS alta permeabilidade (k ≥10^-2 cm/s). Filtro geotêxtil entre CBUQ e base (retenção/drenagem balanceada). Dreno longitudinal PEAD corrugado perfurado (diâmetro 100-150mm). Impacto vida útil: com drenagem eficiente +30-40%, sem drenagem acúmulo água reduz módulo falha precoce. Manutenção: limpeza anual drenos (risco obstrução silte). Especificação: DNIT 108/2009. Vazão dreno: Q = k × A × i onde i=declividade longitudinal (~2-4%). Posicionamento: sob linha de maior saturação em base.' as content
  UNION ALL
  SELECT 'compactacao',
    'Grau Compactação GC% = (ρ_campo / ρ_dmáx) × 100%. Especificações DNIT: capa asfáltica GC ≥97% Proctor, base GC ≥95%, subbase GC ≥93%. Equipamento: densímetro nuclear (readout rápido, ±0.5%), menos invasivo. Amostragem: mínimo 3 pontos/100m² pavimento. Impacto: GC<93% compactação inadequada, afundamento precoce, maior permeabilidade; GC≥97% compactação ótima, vida útil máxima. Curva Proctor: determina ω_ótima (teor água ótimo) e ρ_dmáx (densidade máxima). Execução: lançamento em camadas ≤10cm, cada camada 4-6 passadas rolo vibrante.' as content
  UNION ALL
  SELECT 'equipamentos',
    'Motoniveladoras — modelo CAT 140 (padrão), Volvo GG140 (premium). Produção 200-400 m²/h (espalhamento+nivelação). Custo horário SICRO 2024: R$ 350-450/h. Rolos compactadores — rolo liso (vibrante) 80-130kN (agregados, base), rolo pneumático 100-200kN (uniformidade, acabamento). Sequência: rolo liso (núcleo) + rolo pneumático (finalização). Produção típica motoniveladoras + rolos: 300-400 m²/h em 10cm espessura. Equipamentos adicionais: vibrador de pista, varredor mecânico, imprimadora (ligante). Manutenção: filtro óleo, pneus, correntes.' as content
  UNION ALL
  SELECT 'sequencia_obra',
    'Cronograma típico 100km pavimentação CBUQ: (1) preparo subrasante 10 dias; (2) imprimação/selagem 3 dias; (3) base 15 dias; (4) capa asfáltica 20 dias; (5) acabamento 10 dias. Total ~58 dias. Custos SICRO 2024 CBUQ 5cm: material R$ 85-110/m², mão-obra R$ 35-50/m², equipamento R$ 25-40/m², total R$ 145-200/m². Frentes paralelas aceleram; chuva >5mm ou T<5°C param obra.' as content
  UNION ALL
  SELECT 'orcamento_integrado',
    'Orçamento SICRO 2024 — BDI 30-40%. Composição: material asfáltico 40-45%, agregados 20-25%, mão-obra 15-20%, equipamento 10-15%, impostos 10-15%. Custos regionais: agregados caros NE, ligante flutuante. Contingência +10-15%. Análise CBUQ vs SMA vs CCP. Licitação com composição SICRO obrigatória.' as content
  UNION ALL
  SELECT 'gpr_fwd',
    'GPR (Ground Penetrating Radar) e FWD (Falling Weight Deflectometer) — diagnóstico estrutural. GPR: penetração 0.5-2m, resolução ±2-3cm, custo R$ 3-5k/km. FWD: deflexão dinâmica (50-300kN), módulo retroanalisado, custo R$ 5-10k/km. Integração GPR+FWD: diagnóstico completo estrutura + materiais via retroanálise FEM.' as content
  UNION ALL
  SELECT 'reforco_estrutural',
    'Reforço estrutural — decisão: ICP>60 afundamento<10mm = recapeamento; ICP 40-60 afundamento 10-20mm = reforço 4-6cm; ICP<40 afundamento>20mm = reabilitação. SN_novo = SN_atual + SN_incremental. CAP-modificado sobre CBUQ convencional. Fresagem 2-3cm. Caso BR-116 RJ 2019: reforço 6cm +8 anos vida, R$ 25M/100km.' as content
  UNION ALL
  SELECT 'recapeamento',
    'Recapeamento sobreposição 3-5cm CBUQ, in situ sem demolição, economia 40%, vida +10-15 anos. Com fresagem parcial 2-3cm: remove camada oxidada, custo +20-30%. Aplicação ICP 55-70 simples; ICP 40-55 com fresagem. Prazo 2-3 semanas/100km vs 8-10 reabilitação.' as content
  UNION ALL
  SELECT 'reabilitacao',
    'Reabilitação completa: demolição pavimento, preparo base, reconstrução camadas. Duração 2-3x maior, custo 1.5-2x convencional. Indicação: ICP<40, afundamento>20mm, trincas alligator severas. Caso BR-101 BA 2018: 50km reabilitação total R$ 45M, 18 meses. Impacto: fechamento 12-18 meses.' as content
  UNION ALL
  SELECT 'casos_reais',
    'BR-116 SP-RJ 2019: ICP 65 reforço 6cm +8 anos R$ 25M/100km. BR-101 BA 2018: ICP 32 reabilitação 50km R$ 45M. Imigrantes SP 25% RAP economia R$ 2.3M/100km. Açúcar SP 15% RAP +10% RCD sustentabilidade.' as content
  UNION ALL
  SELECT 'sustentabilidade',
    'Redução CO₂ — CBUQ convencional 350-400kg CO₂/m²; 20% RAP -10%; quente-morno -15-20%; borracha -25-30%. Bio-asfalto -50%, agregados reciclados -30%. Certificações BREEAM, ISO 14040-44. Recomendação: RAP máximo 20-30%, asfalto quente-morno, agregados reciclados.' as content
) chunks;

COMMIT;

SELECT COUNT(*) as total_chunks
FROM manta_rag_chunks
WHERE collection = 'rodovias-pavimentacao';
