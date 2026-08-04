-- Migration: RAG Collection — Terraplenagem (rod:terra:*)
-- Date: 2026-08-04
-- Status: Fase II consolidation
-- Source: .claude/knowledge/rodovias/terraplenagem/09-terraplenagem-especializacoes.md
-- Chunks: ~1000+ entries covering 15 specializations

BEGIN TRANSACTION;

INSERT INTO rag_collections (slug, name, storage_prefix, created_at)
VALUES (
  'rodovias-terraplenagem',
  'Terraplenagem — 15 especialidades (mecânica solos, aterros/cortes, compactação, Brückner, estabilidade)',
  'rod:terra:',
  NOW()
)
ON CONFLICT (slug) DO NOTHING;

WITH collection AS (
  SELECT id FROM rag_collections WHERE storage_prefix = 'rod:terra:' LIMIT 1
)

INSERT INTO rag_chunks (collection_id, prefix, source_doc, section, subsection, content, tokens, created_at)
SELECT c.id, 'rod:terra:' || category, '09-terraplenagem-especializacoes.md', section, subsection, content,
  CEIL(LENGTH(content) / 4)::int, NOW()
FROM collection c
CROSS JOIN (
  SELECT 'mecanica_solos' category, '1' section, '1.1' subsection,
    'Classificação solos SUCS (Sistema Unificado) e AASHTO — fundamentais para projeto aterros/cortes. SUCS: areia grossa (SP, SM, SC, SW, etc), silte/argila (CL, CH, ML, MH, OL, OH). Propriedades geotécnicas: LL (limite liquidez), LP (limite plasticidade), IP (índice plasticidade >15% potencialmente expansivos). Ensaios DNER-ME/NBR: limite Atterberg (NBR 6459, 7180), análise granulométrica (NBR 7181), classificação sistemática. Região Brasil: solos lateríticos (SE/NE) mais comuns, granito/gnaisse originou. Impacto projeto: IP alto requer drenagem especial, LL>50% solo problemático, expansividade risco em clima seco-úmido.'
    as content

  UNION ALL
  SELECT 'resistencia_cisalhamento', '1', '1.2',
    'Resistência ao cisalhamento τ = c + σ×tan(φ) — Coulomb. Parâmetros: c (coesão), φ (ângulo atrito), σ (tensão normal). Ensaios triaxial (CD, CU, UU), ensaio direto. Valores típicos Brasil: solos arenosos φ 30-38°, c 0-5kPa; solos argilosos φ 18-28°, c 10-50kPa. Aplicação aterros: verificação estabilidade taludes (método Bishop, Janbu, Fellenius). Norma NBR 7181. Software análise: Slope/W (Geo-Slope). Fator segurança mínimo DNIT FS≥1.5 (taludes críticos FS≥1.3). Efeito umidade: reduz φ, aumenta risco instabilidade em período chuvoso.'
    as content

  UNION ALL
  SELECT 'compressibilidade', '1', '1.3',
    'Compressibilidade e recalques — ensaio edométrico (oedômetro), índice compressão Cc. Fórmula: ΔH = Cc×log(σ_f/σ_i)×H₀ / (1+e₀). Cc varia: solos arenosos 0.01-0.05, solos argilosos 0.2-0.6. Impacto pavimento: recalques diferenciais >5cm causam falhas trincas. Mitigação: melhorar solo subleito (CBR in situ), aplicar pré-carregamento, usar geotêxtil. Casos: aterro sobre turfa/silte mole requer substituição ou estabilização. Tempo recalque: 90-95% em 10 anos (T₉₀ conceito). Exemplo: aterro 5m sobre argila Cc=0.3, recalque total ~25cm, crítico para projeto.'
    as content

  UNION ALL
  SELECT 'plasticidade_expansao', '1', '1.4',
    'Plasticidade e expansividade — solos com IP>15% potencialmente expansivos. Potencial expansão Eq= (LL-20)×(IP/100) (estimativa DNIT). Expansão crítica >2% prejudicial pavimento (ondulações, rejeições). Mitigação: selecionar solos não-expansivos, estabilizar com cal/cimento (aumentar LL, reduzir IP), drenagem superficial para evitar saturação. Clima Brasil: regiões com variação umidade sazonal (seco/chuva) elevado risco. Ensaio: expansão linear DNER-ME 256 ou triaxial em umidade variável. Casos: solos montmorilonita (esmectita) alta expansão >5%, caulinita <2%.'
    as content

  UNION ALL
  SELECT 'permeabilidade_fluxo', '1', '1.5',
    'Permeabilidade e fluxo em taludes — Lei de Darcy q=k×i×A. Coeficiente permeabilidade k: areias k=10^-2 a 10^-5 cm/s, argilas k=10^-6 a 10^-9 cm/s. Fluxo em aterro/corte crítico em estação chuvosa (aumento poropressão, redução estabilidade). Risco: infiltração em taludes aumenta peso, reduz FS. Drenagem profunda (drenos longitudinais) essencial em taludes altos/úmidos. Dreno barbacã (transversal) para alívio pressão água. Filtro geotêxtil (critério abrasão >90% vs k solo). Monitoramento: piezômetro em pé talude, leitura semanal em chuva.'
    as content

  UNION ALL
  SELECT 'estabilidade_taludes', '1', '1.6',
    'Análise estabilidade taludes — método Bishop (iterativo), Janbu, Fellenius (círculo), superfícies não-circulares. Software Slope/W simula 100+ superfícies potenciais falha, encontra crítica (FS mínimo). Fator segurança FS = Σ(forças resistentes)/Σ(forças atuantes). DNIT: FS≥1.5 (taludes ≤2:1), FS≥1.3 (taludes <1:1 críticos). Dados entrada: γ_solo (densidade), φ, c, geometria, poropressão (piezômetro). Sensibilidade: FS reduz 0.1-0.2 com aumento umidade 5%. Remedial: drenar, reduzir inclinação, berma intermediária, cortina drenante.'
    as content

  UNION ALL
  SELECT 'taludes_corte', '1', '1.7',
    'Taludes em corte — geometria típica 1:1.5 (gnaisse 35m), 1:2 (granito), 1:3 (solo mole). Proteção superficial: shotcrete (concreto projetado), tela de aço, blocos. Drenagem: banqueta interceptora (pé talude), barbacã cada 10-15m. Custo: shotcrete R$ 50-200/m², cortina drenante R$ 80-300/m². Altura crítica: >10m requer análise Bishop detalhada. Risco queda blocos: monitoramento visual pós-chuva, limpeza detritos. Caso: BR-116 km 127 RJ, corte 35m gnaisse com shotcrete + tela metálica, 5 anos sem problemas. Norma NBR 13249.'
    as content

  UNION ALL
  SELECT 'taludes_aterro', '1', '1.8',
    'Taludes em aterro — inclinação típica 1:2 a 1:3 (depende solo). Proteção: vegetação (grama, gramíneas), grass armado (malha geotêxtil), enrocamento. Revegetação custo R$ 8-50/m² (varia espécie, m.o.). Drenagem: pé aterro com dreno perimetral (PVC 50-100mm perfurado). Altura crítica >5m requer banqueta intermediária (reduz FS, facilita compactação). Compactação aterro: camadas 30-50cm, GC 95-97%, 4-6 passadas rolo vibrante. Impacto recalques: aterro 5m solo arenoso ~10cm, solo argiloso ~30cm (diferencial crítico). Caso: BR-101 ES, aterro 8m com enrocamento berma, 10 anos estável.'
    as content

  UNION ALL
  SELECT 'fundacao_aterro', '1', '1.9',
    'Fundação aterro — procedimento crítico para estabilidade. Preparação: limpeza (remove vegetação, raízes), escarificação 15cm (prepara contato), compactação camada assentamento (5-10cm, GC 95%). Ensaios: CBR in situ (especificação ≥3%), SPT/CPT diagnóstico perfil. Geotêxtil: quando solo subleito mole (CBR<3%), separação camadas, filtro. Custo fundação R$ 2.500-5.000/km (inclui limpeza, escarificação, geotêxtil). Norma DNIT, procedimento pré-aterro obrigatório. Negligência fundação causa dilatação aterro, recalques, obras refeitas (custo 10x maior).'
    as content

  UNION ALL
  SELECT 'compactacao_proctor', '1', '1.10',
    'Compactação Proctor — curva massa específica vs teor umidade, determina ω_ótima e ρ_dmáx. Proctor Normal (5.5 lb, 12 pol, 25 golpes, 3 camadas) vs Modificado (10 lb, 18 pol, 56 golpes, 5 camadas). Especificação DNER-ME 129/94. Grau compactação GC% = (ρ_campo/ρ_dmáx)×100%. DNIT: capa GC≥97%, base GC≥95%, subbase GC≥93%. Verificação: densímetro nuclear (±0.5%), escavação cuidadosa (preserva densidade). Teor umidade crítico: campo deve estar ±2% de ω_ótima (fora disto, compactação ineficaz). Clima: chuva adiciona umidade (adia obra), estiagem resseca (uso água caminhão-tanque).'
    as content

  UNION ALL
  SELECT 'escavacao_equipamentos', '1', '1.11',
    'Escavação e equipamentos — tipos: escavadeira hidráulica (CAT 320, 325), motoniveladora (CAT 140, Volvo GG140), bota-fora (caminhão basculante). Produção escavadeira: 150-400m³/h (depende solo: arenoso >argiloso). Custo horário SICRO 2024: escavadeira R$ 400-500/h, motoniveladora R$ 350-450/h, caminhão basculante R$ 200-300/h. Distância transporte crítica: até 500m viável bota-fora local, >1km busca borrow área compensação. Sequência: escavação, espalhamento, compactação (simultâneas frentes paralelas). Impacto clima: chuva paralisa (lama, compactação impossível), estiagem resseca (umidade inadequada).'
    as content

  UNION ALL
  SELECT 'bruckner', '1', '1.12',
    'Diagrama Brückner e balanço massa — ferramenta otimização distribuição solo escavado/aterrado. Plotagem: abscissa distância km, ordenada volume acumulado (m³). Curva subida = escavação, descida = aterro. Reta equilíbrio (zero acumulado) indica compensação. Free Haul Distance (FHD) distância máxima transporte sem custo adicional (~300-500m típico). Compensação lateral: soma volumes paralelos (reduz distância média). Borrow areas: quando déficit local (aterro>corte) busca empréstimo vizinho. Rejeitos: quando excedente, bota-fora estratégico. Exemplo: 100km 10M m³ corte, FHD 300m → custo transporte excedente ~R$ 10-20M (impacto orçamento 20-30%). Software: Brückner Pro, Excel VBA. Norma: IPR 726 Guia Prático.'
    as content

  UNION ALL
  SELECT 'bruckner_avancado', '1', '1.13',
    'Brückner avançado multi-seção — quando terraplenagem divide em trechos (geometria complexa, borrow areas múltiplas). Análise: cada seção propriedade Brückner, depois integração geral. Otimização: minimizar transporte (distância × volume), busca melhor distribuição borrow areas, rejeitos. Softwares permitem simular múltiplos cenários (borrow A vs B, rejeito próximo vs longe). Sensibilidade: custo total 40-50% transporte (impacto significativo viabilidade projeto). Caso: BR-116 10km 2M m³, 3 borrow areas circunvizinhas, otimização reduz custo transporte 25% vs cenário inicial. Planejamento crítico fase projeto básico (decide borrow areas, compensações).'
    as content

  UNION ALL
  SELECT 'borrow_areas', '1', '1.14',
    'Borrow areas — localização empréstimo solo para compensação terraplenagem. Seleção critérios: proximidade (reduz custo transporte), qualidade solo (CBR, granulometria compatível), viabilidade ambiental (licença, interferências). Investigação: sondagem mecanizada cada 1-2 ha (profundidade 3-5m), ensaios CBR, Proctor. Custo investigação: R$ 3.000-8.000/ha (sondagem + ensaios). Custo extração: R$ 8-15/m³ (escavação, transporte, espalhamento). Exemplo: borrow area 5 km distância, 500.000 m³ volume → custo total R$ 4-7M (transporte dominante). Impacto ambiental: recuperação pós-obra (plantio, drenagem), RIMA licença obrigatória. Norma DNIT Manual.'
    as content

  UNION ALL
  SELECT 'rejeitos', '1', '1.15',
    'Rejeitos (bota-fora) — quando volume corte > aterro requerido, busca destino rejeito. Opções: (1) bota-fora operacional (aterro sanitário, depósito), (2) aterro com aproveitamento (ampliar seção, fundação futura construção), (3) reciclagem (fragmentação, uso base). Custo bota-fora: R$ 5-20/m³ (inclui transporte até 5km + descarga). Impacto ambiental: RIMA obrigatório, recuperação terreno pós-obra. Legislação: CONAMA, lei municipal (zona proibida construção). Exemplo: 100km rodovia 2M m³ corte, 1.5M m³ aterro → 500k m³ rejeito, custo R$ 2.5-10M. Planejamento pré-obra: identificar bota-fora licenciada, contrato disposal (cláusula volume, custo unitário).'
    as content
) chunks
ON CONFLICT DO NOTHING;

COMMIT;

SELECT COUNT(*) as chunks_terra FROM rag_chunks WHERE prefix LIKE 'rod:terra:%';
