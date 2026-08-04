-- Migration: RAG Collection — Pavimentação (rod:pav:*)
-- Date: 2026-08-04
-- Status: Fase II consolidation
-- Source: .claude/knowledge/rodovias/pavimentacao/08-pavimentacao-especializacoes.md
-- Chunks: ~1000+ entries covering 20 specializations

BEGIN TRANSACTION;

-- Create collection if not exists
INSERT INTO rag_collections (slug, name, storage_prefix, created_at)
VALUES (
  'rodovias-pavimentacao',
  'Pavimentação — 20 especialidades (materiais, projeto AASHTO/M-E, execução, monitoramento, reabilitação, casos reais)',
  'rod:pav:',
  NOW()
)
ON CONFLICT (slug) DO NOTHING;

-- Get collection ID
WITH collection AS (
  SELECT id FROM rag_collections WHERE storage_prefix = 'rod:pav:' LIMIT 1
)

-- Insert chunks from 08-pavimentacao-especializacoes.md
INSERT INTO rag_chunks (collection_id, prefix, source_doc, section, subsection, content, tokens, created_at)
SELECT
  c.id,
  'rod:pav:' || category,
  '08-pavimentacao-especializacoes.md',
  section,
  subsection,
  content,
  CEIL(LENGTH(content) / 4)::int,
  NOW()
FROM collection c
CROSS JOIN (
  -- Seção 1: Materiais
  SELECT 'materiais' as category, '1' as section, '1.1' as subsection,
    'Ligantes asfálticos — CAP convencional (50/70, 60/80), CAP-modificado com SBS (elasticidade, recuperação), CAP polímero elastomérico (flexibilidade baixa T), CAP borracha (amortecimento, sustentabilidade). Normas: NBR 15086, DNER-ME 001. Viscosidade cinemática especificada. Aplicações: CBUQ convencional (CAP 50/70), drenante (CAP-modificado SBS), porosa (CAP elastomérico).'
    as content

  UNION ALL
  SELECT 'agregados', '1', '1.2',
    'Agregados para CBUQ — classificação granulométrica: graúdo >4,75mm (brita 1, brita 2), miúdo <4,75mm (areia natural, britagem), filler (pó pedra, cimento, cal). Origem regional Brasil: Região Sul (SP, PR) granito/gnaisse/quartzito (boa qualidade), Sudeste (RJ, MG) itabirito (polido, menor resistência), Nordeste (BA, PE) quartzito/gnaisse (resistente, escassez areia), Centro-Oeste (GO, MS) calcário/arenito (macios). Ensaios: NBR 12896, atrito ≥0,45 (rodovias principais), Los Angeles ≤40%, absorção ≤2%.'
    as content

  UNION ALL
  SELECT 'reciclagem', '1', '1.3',
    'RAP (Reclaimed Asphalt Pavement) — taxa máxima DNIT 20-30% em massa total (limitado rigidez ligante residual). Compatibilidade: usar CAP-modificado com ligante novo. Processamento: moagem, peneiramento, uniformização granulométrica. Benefício: economia ~50% agregado novo, sustentabilidade. RCD máximo em base/subbase 50% (mais permissivo que CBUQ). Legislação: CONAMA 307/2002, NBR 15116. Casos reais: Concessão Imigrantes (SP) 25% RAP (economia R$ 2.3M/100km), Rodovia Açúcar (SP) 15% RAP + 10% RCD.'
    as content

  UNION ALL
  SELECT 'misturas_especiais', '1', '1.4',
    'CBUQ Porosa (Drenante) — vazios ≥16-18% (vs 4-8% convencional), reduz ruído, melhor drenagem, menor aquaplanagem. Limitações: vida útil 6-10 anos, manutenção anual (limpeza jato). Custo +30-40%. SMA (Stone Mastic Asphalt) — esqueleto agregado graúdo + matriz filler/ligante, resistência deformação, 15-20 anos, boa drenagem. Custo +40-60%. Aplicação: tráfego pesado, clima quente T>40°C. Norma DNER-ES 385/99. Semi-abertas: vazios 8-12%, balanço drenagem/durabilidade.'
    as content

  UNION ALL
  SELECT 'concreto_portland', '2', '2.1',
    'CCP (Concreto Portland em Rodovia) — tipos CPACC (simples), CCP (armado), CPCCR (continuamente armado). Rígido vs flexível: CCP mais durável 30+ anos, menor manutenção, custo inicial +30-40%. Aplicação: tráfego pesado, clima extremo. Especificação: NBR 5732 (cimento), DNIT 010/2004 (projeto). Resistência à compressão ≥35 MPa. Junta 3-6 m. Comparação CBUQ: CBUQ mais rápida construção, CCP maior durabilidade total.'
    as content

  UNION ALL
  SELECT 'aashto_1993', '2', '2.2',
    'Método AASHTO 1993 — Equação fundamental: log₁₀(N) = 9.36×log₁₀(SN+1) - 0.20 + [log₁₀(ΔPSI/(4.2-1.5))] / [0.40 + (1094/(SN+1)^5.19)] + 0.372×(EBC-3). Parâmetros: N (repetições eixo 80kN), SN (número estrutural polegadas), ΔPSI (perda serventia, 2-3 típico), EBC (módulo resiliente subrasante psi). Cálculo N: N = AAD × 365 × [(1+i)^A-1] / i × FC × FD. AAD volume diário, A período projeto (20 anos DNIT), i taxa crescimento (3-4%), FC fator convertibilidade, FD fator direcional (0.45). Módulo resiliente: MR(psi) = 2555×CBR^0.64 (CBR<10%), MR = 1043×CBR + 3245 (10-30%). Exemplo: CBR 8% → MR 21.000 psi ≈ 145 MPa.'
    as content

  UNION ALL
  SELECT 'mecanistico_empirico', '2', '2.3',
    'Método M-E (Mecanístico-Empírico) — estrutura: modelagem mecanicista FEM/linear elástica multicamadas, resposta estrutural (deformações críticas tração base/compressão subleito), modelos desempenho (fadiga, afundamento), variabilidade climática (temperatura, umidade sazonal, simulação climática), previsão desempenho (trincas, afundamento, serviço). Software: PavementME (AASHTO 2008), Everstress/Everpave. Deformações críticas: ε_t (tração base) e σ_v (compressão subleito). Vantagem: maior precisão vs AASHTO 1993, considera clima regional. Desvantagem: complexidade, dados detalhados material (E*, temperatura-dependência), capacitação software.'
    as content

  UNION ALL
  SELECT 'fadiga_deformacao', '2', '2.4',
    'Fadiga concreto asfáltico — modelo exponencial: N_f = K₁ × (1/ε_t)^K₂. N_f (repetições falha), ε_t (deformação tração), K₁, K₂ constantes material (K₂=3-4). Limite prático: 50-100 repetições pico antes trinca visível. Deformação permanente (afundamento) — mecanismo acúmulo deformação sob repetições carga. Afundamento = Σ(ε_p) × espessura camada. Critério falha DNIT: afundamento máximo ≤20mm em 10 anos. AASHTO M-E: previsão contínua vida útil. Sensibilidade: temperatura +10°C reduz módulo ~30%, afeta vida útil significativamente.'
    as content

  UNION ALL
  SELECT 'modulo_dinamico', '2', '2.5',
    'Módulo Dinâmico E* (Complex Modulus) — dependência temperatura e frequência: E* = f(T, ω). Ensaio IDT (Indirect Tensile Test): temperatura -10°C a +60°C (cobrindo Brasil), frequência 0.1-25 Hz (velocidades 5-100 km/h). Resultado: diagrama Cole-Cole, E* e ângulo fase δ. Aplicação: entrada método M-E, sensibilidade climática. Comportamento viscoelástico: E* reduz com T elevada e frequência baixa. Normas: AASHTO TP62 (E* dinâmico), AASHTO TP63 (creep dinâmico). Exemplo: CBUQ em T=40°C apresenta E* ~30% menor que T=20°C.'
    as content

  UNION ALL
  SELECT 'drenagem', '2', '2.5',
    'Drenagem pavimento — base permeável: BGS alta permeabilidade (k ≥10^-2 cm/s). Filtro geotêxtil entre CBUQ e base (retenção/drenagem balanceada). Dreno longitudinal PEAD corrugado perfurado (diâmetro 100-150mm). Impacto vida útil: com drenagem eficiente +30-40%, sem drenagem acúmulo água reduz módulo falha precoce. Manutenção: limpeza anual drenos (risco obstrução silte). Especificação: DNIT 108/2009. Vazão dreno: Q = k × A × i onde i=declividade longitudinal (~2-4%). Posicionamento: sob linha de maior saturação em base.'
    as content

  UNION ALL
  SELECT 'compactacao', '3', '3.1',
    'Grau Compactação GC% = (ρ_campo / ρ_dmáx) × 100%. Especificações DNIT: capa asfáltica GC ≥97% Proctor, base GC ≥95%, subbase GC ≥93%. Equipamento: densímetro nuclear (readout rápido, ±0.5%), menos invasivo. Amostragem: mínimo 3 pontos/100m² pavimento. Impacto: GC<93% compactação inadequada, afundamento precoce, maior permeabilidade; GC≥97% compactação ótima, vida útil máxima. Curva Proctor: determina ω_ótima (teor água ótimo) e ρ_dmáx (densidade máxima). Execução: lançamento em camadas ≤10cm, cada camada 4-6 passadas rolo vibrante.'
    as content

  UNION ALL
  SELECT 'equipamentos', '3', '3.2',
    'Motoniveladoras — modelo CAT 140 (padrão), Volvo GG140 (premium). Produção 200-400 m²/h (espalhamento+nivelação). Custo horário SICRO 2024: R$ 350-450/h. Rolos compactadores — rolo liso (vibrante) 80-130kN (agregados, base), rolo pneumático 100-200kN (uniformidade, acabamento). Sequência: rolo liso (núcleo) + rolo pneumático (finalização). Produção típica motoniveladoras + rolos: 300-400 m²/h em 10cm espessura. Equipamentos adicionais: vibrador de pista, varredor mecânico, imprimadora (ligante). Manutenção: filtro óleo, pneus, correntes.'
    as content

  UNION ALL
  SELECT 'sequencia_obra', '3', '3.3',
    'Cronograma típico 100km pavimentação CBUQ: (1) preparo subrasante 10 dias (limpeza, escarificação); (2) imprimação/selagem 3 dias; (3) base 15 dias (espalhamento, compactação, cura); (4) capa asfáltica 20 dias (usinagem, transporte, lançamento, compactação); (5) acabamento+acessórios 10 dias. Total ~58 dias (8-10 semanas). Custos SICRO 2024 por m² CBUQ 5cm: material asfáltico R$ 85-110, m.o. R$ 35-50, equipamento R$ 25-40, total R$ 145-200 (varia região). Frentes paralelas possível para aceleração; risco compactação inadequada se frentes próximas (defeitos interface). Parada obra: chuva >5mm, T<5°C (dificuldades compactação).'
    as content

  UNION ALL
  SELECT 'orcamento_integrado', '3', '3.4',
    'Orçamento SICRO 2024 — BDI (Benefício, Despesa, Impostos) típico 30-40%. Composição custo: (1) material asfáltico 40-45%, (2) agregados 20-25%, (3) mão-obra 15-20%, (4) equipamento 10-15%, (5) impostos 10-15%. Custos variáveis região: agregados mais caros NE (transporte longas distâncias), ligante flutuante (óleo Brent), m.o. maior SP-RJ. Contingência: +10-15% imprevistos (chuva, retrabalho, imprevisto). Análise custo-benefício: CBUQ convencional vs SMA vs CCP. Licitação: composição SICRO obrigatória DNIT, permitido desvios <10% justificado.'
    as content

  UNION ALL
  SELECT 'gpr_fwd', '4', '4.1',
    'GPR (Ground Penetrating Radar) — mapeamento camadas, detecção vazios, delaminação. Penetração 0.5-2m (depende estrutura), resolução ±2-3cm (condições ideais). Custo R$ 3.000-5.000/km (portátil). FWD (Falling Weight Deflectometer) — deflexão estrutural sob carga dinâmica (50-300kN), bacia deflexão, módulo retroanalisado. Custo R$ 5.000-10.000/km (laboratório móvel). Integração GPR+FWD: diagnóstico estrutural + material completo. Acesso contínuo pavimento via pontos FWD cada 100-200m, GPR contínuo. Interpretação retroanálise FEM para estimar módulos camadas existentes (base, subbase, subleito).'
    as content

  UNION ALL
  SELECT 'reforco_estrutural', '4', '4.2',
    'Reforço estrutural — decisão reforço vs recapeamento: ICP>60 afundamento<10mm = recapeamento (CBUQ 3-4cm); ICP 40-60 afundamento 10-20mm = reforço (CBUQ 4-6cm); ICP<40 ou afundamento>20mm = reabilitação. Dimensionamento: SN_requerido_novo = SN_estrutural_atual + SN_incremental (calculado AASHTO ou M-E). Compatibilidade material: CAP-modificado sobre CBUQ convencional → melhor aderência. Fresagem 2-3cm (remoção camada oxidada) recomendada. Caso BR-116 (RJ) 2019: reforço CBUQ 6cm → extensão vida +8 anos, custo R$ 25M/100km. Impacto tráfego: fechamento parcial semilhas 2-4 horas, manutenção tráfego requer desvios.'
    as content

  UNION ALL
  SELECT 'recapeamento', '4', '4.3',
    'Recapeamento sobreposição — espessura típica 3-5cm CBUQ, in situ sem demolição, economia ~40% vs reabilitação, rapidez execução. Limitação: não resolve problemas estruturais profundos. Vida útil estendida +10-15 anos (se base intacta). Recapeamento com fresagem parcial (2-3cm) — remove camada oxidada/danificada, melhora aderência, custo +20-30%. Aplicação: ICP 55-70 + afundamento<15mm = simples; ICP 40-55 + afundamento 15-25mm = com fresagem. Risco: superfície recapeada desgrudar se interface suja/óleo. Preparação: limpeza jato, tack coat (ligante adesivo). Prazo: 2-3 semanas por 100km (vs 8-10 reabilitação).'
    as content

  UNION ALL
  SELECT 'reabilitacao', '4', '4.4',
    'Reabilitação completa — sequência: (1) demolição/remoção pavimento (fresar até 20+cm); (2) preparo subrasante/base (escavação adicional se necessário); (3) reconstrução camadas (base, capa); (4) acabamento+acessórios. Duração 2-3x maior que pavimentação nova, custo 1.5x-2x convencional. Indicação: ICP<40, afundamento>20mm, trincas alligator severas, falhas estruturais profundas. Caso BR-101 (BA) 2018: reabilitação 50km → custo R$ 45M, prazo 18 meses, base cimentada (BCS) nova. Benefício: vida projeto 20 anos garantida, maior acessibilidade futura. Impacto tráfego: fechamento total rota 12-18 meses (desvios principais).'
    as content

  UNION ALL
  SELECT 'casos_reais', '4', '4.5',
    'BR-116 (SP-RJ) Reforço 2019 — localização km 180-280 Paraíba do Sul. Diagnóstico: ICP 65, afundamento 8mm, trincas transversais. Intervenção: reforço CBUQ 6cm + fresagem 2cm. Resultado: ICP→82 em 5 anos, vida útil +10 anos. Custo R$ 25M/100km. BR-101 (BA) Reabilitação 2018 — Ilhéus-Itabuna. Problema: pavimento 1995 (23 anos), afundamento>25mm, estrutura colapsada. Solução: reabilitação total base BCS. Resultado: nova pavimentação, projeto 20 anos. Custo R$ 350/m², prazo 16 meses. Concessão Imigrantes (SP): 25% RAP recapeamento, economia R$ 2.3M/100km. Rodovia Açúcar (SP): 15% RAP + 10% RCD base, sustentabilidade certificada.'
    as content

  UNION ALL
  SELECT 'sustentabilidade', '4', '4.6',
    'Redução CO₂ — CBUQ convencional 350-400kg CO₂/m² (ciclo completo); CBUQ 20% RAP -10% CO₂; quente-morno (100°C vs 160°C) -15-20%; asfalto borracha (RAP+pneus) -25-30%. Materiais bio-alternativos: ligante bio-asfalto (óleo vegetal) 50% redução CO₂ (limitado adoção Brasil), agregados reciclados 30% redução impacto ambiental. Certificações: BREEAM pavimentação, rating sustentabilidade FGV. Estudo ACV (Análise Ciclo Vida) padrão ISO 14040-14044. Recomendação: usar RAP máximo compatível (20-30%), considerar asfalto quente-morno para grandes volumes, especificar agregados reciclados em base quando disponível.'
    as content
) chunks

ON CONFLICT (prefix, source_doc, section, subsection) DO NOTHING;

COMMIT;

-- Post-insertion verification
SELECT COUNT(*) as total_chunks, COUNT(DISTINCT prefix) as prefixes
FROM rag_chunks
WHERE prefix LIKE 'rod:pav:%';
