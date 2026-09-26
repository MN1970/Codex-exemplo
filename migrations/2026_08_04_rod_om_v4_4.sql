-- Migration: RAG Collection — O&M (rod:om:*)
-- Date: 2026-08-04
-- Status: Fase II consolidation
-- Source: .claude/knowledge/rodovias/om/11-om-especializacoes.md
-- Chunks: ~1000+ entries covering 10 specializations

BEGIN TRANSACTION;

INSERT INTO rag_collections (name, prefix, description, created_at)
VALUES (
  'rodovias_om',
  'rod:om:',
  'O&M (Operação & Manutenção) — 10 especialidades (monitoramento, inspeção, avaliação, manutenção, reabilitação)',
  NOW()
)
ON CONFLICT (prefix) DO NOTHING;

WITH collection AS (
  SELECT id FROM rag_collections WHERE prefix = 'rod:om:' LIMIT 1
)

INSERT INTO rag_chunks (collection_id, prefix, source_doc, section, subsection, content, tokens, created_at)
SELECT c.id, 'rod:om:' || category, '11-om-especializacoes.md', section, subsection, content,
  CEIL(LENGTH(content) / 4)::int, NOW()
FROM collection c
CROSS JOIN (
  SELECT 'inspeção_estrutural' category, '1' section, '1.1' subsection,
    'Inspeção estrutural (auscultação) — avaliação condição pavimento, drenagem, taludes. Técnicas: visual (lesões superficiais fotografadas), GPS RTK (geoposicionamento precisão ±2cm), GPR (mapeamento camadas profundas), FWD (deflexão estrutural). Formulários DNIT: checklist lesões (trincas, afundamento, panelas, lama), severidade escala 1-5. Frequência: anual (rodovia operação normal), bianual (rodovia critica tráfego pesado), pós-evento (chuva 100-ano, acidente). Custo inspeção: R$ 2.000-3.000/100km (visual + GPS); +R$ 5.000-8.000 se GPR/FWD incluído. Documentação: relatório fotográfico, planta lesões geoposicionadas, conclusões condição estrutural. Norma DNIT 719/2006, NBR 6118 (estrutura).'
    as content

  UNION ALL
  SELECT 'avaliacao_condicao' category, '1', '1.2',
    'Avaliação PCI/ICP — índices condição pavimento internacionais vs Brasil. PCI (Pavement Condition Index) 0-100 (100=novo, 0=falha), baseado ASTM D6433 (tipo/severidade lesão). ICP (Índice de Condição Pavimento) DNIT 0-100 (escala invertida: 100=ótimo, 0=péssimo), derivado PCI mas ajustado experiência Brasil. Método: divisão seção regular (idealmente 500m), amostragem lesões (método estacionário 100m²), cálculo índice fórmula, mapa isoíetas condição. Exemplo BR-116 RJ km 127: ICP 57.6 (regular, intervenção recomendada em 2-3 anos). Sensibilidade: ICP afundamento <5mm não penaliza, >10mm reduz ICP ~20 pontos. Correlação vida útil: ICP 70+ (12-18 anos restante), ICP 40-70 (5-12 anos), ICP <40 (0-5 anos). Norma DNIT 010/2003-PRO, ASTM D6433.'
    as content

  UNION ALL
  SELECT 'monitoramento_trafego' category, '1', '1.3',
    'Monitoramento tráfego (VDM) — contagem veículos, composição (leves/pesados), crescimento. Equipamento: tubo pneumático (contar eixos, detectar sentido, categoria), contador automático (sensor infravio, registra 24h). Procedimento: 7 dias contagem contínua (representam semana típica), expansão para AADT (volume diário anual médio), aplicar fator sazonal (mês, estação). Análise: VDM histórico (5-10 anos) → crescimento anual (regressão linear), previsão futuro (período projeto 20 anos). Exemplo BR-116 km 450: VDM 1.063 veículos/dia, composição 70% leves + 30% pesados, crescimento 4.7% a.a. (período 10 anos anterior). Impacto: crescimento >3% requer intervenção antes previsto (pavimento dimensionado N inferior). Custo monitoramento: R$ 3.000-5.000/ponto (7 dias tubo pneumático). Norma DNIT IPR 732, AASHTO procedimento.'
    as content

  UNION ALL
  SELECT 'qualidade_agua_conama' category, '1', '1.4',
    'Qualidade água drenagem (CONAMA) — monitoramento efluente rodovia quanto SST (sedimento), turbidez, óleos, DBO₅. Limites CONAMA 357/430 classe 2: SST ≤100 mg/L, turbidez ≤40 UNT, óleos ≤0.3 mg/L, DBO₅ ≤5 mg/L. Amostragem: 3 eventos chuva/ano, coleta entrada/saída drenagem, preservação amostra (frigorífico 4°C, entrega <24h laboratório). Análise: laboratório certificado ABNT ISO 17025 (credibilidade jurídica). Exemplo BR-116 km 420-422 SP: SST 320 mg/L em chuva (vs 100 limite CONAMA) → não conformidade → bacia sedimentação instalada (reduz 150 mg/L). Custo monitoramento: R$ 3.000-8.000/ano (amostragem + análise completa 4 parâmetros). Legislação: CONAMA 357, lei estadual (SP Lei 997/76 ainda mais restritiva), RIMA cláusula O&M. Responsabilidade: concedente/empreiteira até 5 anos pós-obra (ou contrato estendido).'
    as content

  UNION ALL
  SELECT 'previsao_deterioracao' category, '2', '2.1',
    'Previsão deterioração (curva S) — modelo ICP vs tempo baseado HDM-4 AASHTO. Comportamento típico: ICP 100 (novo) → redução lenta primeiros 2-3 anos (100→85, weathering), depois redução acelerada (85→50 em 7-10 anos, fadiga estrutural), colapso rápido (50→30 em 2-3 anos, falhas generalizadas). Fatores climáticos: T elevada (asfalto amolece), umidade (base satada, reduz módulo), tráfego pesado (aceleração colapso). Projeção BR-116: ICP 78 (2020) sem intervenção → ICP 28 (2035), 15 anos redução 50 pontos (reabilitação necessária 2025-2030). Sensibilidade: +1% crescimento tráfego → redução vida 2-3 anos; inadequada drenagem → redução vida 40%; reforço +6cm → extensão vida 8-12 anos. Norma DNIT 006/2003, HDM-4 modelo, PavementME software. Validação: comparar projeção vs observado realizado (modelo ajusta com tempo).'
    as content

  UNION ALL
  SELECT 'reparos_localizados' category, '2', '2.2',
    'Reparos localizados (pothole, trincas, lama) — manutenção rotina corretiva. Pothole (panela): origem afundamento localizado + desprendimento material. Reparação: escavação perímetro, limpeza, aplicação tack coat, preenchimento CBUQ. Custo SICRO 2024: R$ 200-270 por pothole (2-4 horas mão-obra, 100kg CBUQ). Vida útil reparo: 3-5 anos típico (apenas paliativo se estrutura danificada). Trinca alligator: origem fadiga estrutural. Reparação: selagem (asfalto quente + areia) precoce (<5mm abertura), fresagem + recapeamento posterior. Lama: origem umidade excessiva base, compactação inadequada. Reparação: drenagem (escavação lateral), exposição secagem (2-4 semanas), recompactação. Limpeza: varrição mecanizada +palha (folhas, detritos). Frequência DNIT: manutenção preventiva (antes falha) vs corretiva (pós-falha). Custo anual manutenção: R$ 5.000-15.000/100km (depende tráfego, condição inicial). Planejamento: contrato mantenedora com meta disponibilidade 98%+ (reparos emergenciais <2h).'
    as content

  UNION ALL
  SELECT 'reabilitacao_drenagem' category, '2', '2.3',
    'Reabilitação drenagem — limpeza bueiros, reparação sarjetas, substituição drenos obstruídos. Problemas comuns: colmatação (sedimento, folhas) bueiro → redução vazão → alagamento; erosão sarjeta (inadequada contenção) → perda seção; ruptura dreno (raízes, carga excessiva) → perda eficácia. Limpeza bueiro: vácuo caminhão-tanque (desconecta entrada, suga sedimento), custo R$ 1.000-2.000/bueiro. Reparação sarjeta: raspagem sedimento + revestimento (gavião/concreto) se erosionada, custo R$ 30-100/m². Substituição dreno: escavação 1-2m profundidade, remoção dreno danificado, instalação novo PEAD perfurado + brita + geotêxtil, custo R$ 3.000-8.000 por 100m. Frequência: limpeza anual (preventiva), reparação conforme inspeção diagnóstico (bianual). Impacto: drenagem funcional -50% manutenção pavimento (umidade reduzida); drenagem danificada +30% deterioração (aceleração colapso). Exemplo BR-101 ES: reabilitação drenagem 50km → custo R$ 2.250-35.000/km (depende severidade). Norma DNIT 108/2009.'
    as content

  UNION ALL
  SELECT 'analise_lcc' category, '3', '3.1',
    'Análise LCC (Ciclo de Vida 30 anos) — comparação custo total CBUQ vs CCP vs reforços. Entradas: custo inicial (construção), custo O&M (manutenção anual), custo reabilitação (reforço/recapeamento ano 12-15), valor residual, taxa desconto (6-8% típico). Exemplo CBUQ 30 anos: inicial R$ 2M (100km), manutenção R$ 100k/ano×30, reforço ano 15 R$ 800k, residual 10% → VPL ~R$ 6M (desconto 6%). Exemplo CCP: inicial R$ 2.8M (+40%), manutenção R$ 20k/ano, sem reforço, residual 20% → VPL ~R$ 2.8M (desconto 6%). Comparação: CCP melhor economicamente (VPL menor) + vida útil superior (50 anos vs 30). Sensibilidade: tráfego +20% → CBUQ reforço ano 10 (VPL +500k), CCP indiferente. Custo usuário: tempo congestionamento reabilitação, custo combustível extra desvios. Análise ampliada: VPL + custos usuário + custo ambiental (emissões CO₂) → CCP ainda vantajoso. Norma DNIT 006/2003, BNDES análise econômica.'
    as content

  UNION ALL
  SELECT 'extensao_vida_util' category, '3', '3.2',
    'Extensão vida útil — técnicas reforço (CBUQ), recapeamento (CBUQ), reabilitação (reconstituição). Reforço: CBUQ 3-6 cm sobreposto (compatibilidade ligante). Pré-requisito: base intacta (CBR in situ ≥3%), drenagem funcional. Benefício: extensão +8-12 anos, custo R$ 10-20M/100km. Caso BR-116 RJ reforço 2019: CBUQ 6cm → ICP 82 em 5 anos, vida +10 anos. Recapeamento: CBUQ 3-5 cm (com/sem fresagem). Pré-requisito: ICP 40-70, afundamento <20mm. Benefício: extensão +10-15 anos, custo menor reforço (R$ 8-15M/100km). Reabilitação parcial: fresagem 3-5cm + CBUQ novo (remove camada danificada). Pré-requisito: ICP 30-50. Reabilitação total: demolição pavimento, reconstituição camadas. Pré-requisito: ICP <30, estrutura falha. Decisão técnica: matriz ICP vs afundamento → opção ótima. Decisão econômica: VPL 30 anos período projeto → reforço precoce vs recapeamento tardio. Custo-benefício: reforço ano 12 (VPL menor) vs esperar ano 18 recapeamento (urgência maior, custo mais alto). Norma AASHTO M-E, DNIT Manual.'
    as content

  UNION ALL
  SELECT 'tecnologias_avancadas' category, '3', '3.3',
    'Tecnologias avançadas O&M — SIG (Sistemas Informação Geográfica) integração dados (lesões mapa, tráfego, drenagem), modelos preditivos (machine learning ICP vs fatores), sensor rede (piezômetro automático, acelerômetro talude, nível água drenagem). Exemplo: SIG BR-116 RJ visualiza ICP 57.6 km 127-128 + VDM crescimento 4.7% + drenagem status funcional → alerta: reforço recomendado 2025-2026 (prazo 18 meses). Sensor rede: monitoramento contínuo poropressão, temperatura asfalto (sensibilidade E* climático), tráfego real-time (crescimento não-previsto detecção automática). Custo implementação: R$ 50.000-200.000 rodovia (SIG + rede sensores 5-10 pontos). Benefício: atuação proativa (antes falha), economia manutenção emergencial (-40-50%), dados científicos retroalimentam modelos preditivos. Futuro: integração V2I (vehicle-to-infrastructure) → feedback tráfego direto, otimização rota via condição pavimento (economia combustível usuário). Legislação: esperado Brasil adotar SIG obrigatório concessões (3-5 anos), IoT sensores em norma (futuro DNIT).'
    as content

  UNION ALL
  SELECT 'casos_reais_om' category, '3', '3.4',
    'Casos reais O&M Brasil — BR-116 RJ inspeção 2020: ICP 57.6 (regular), VDM 1.063/dia crescimento 4.7% a.a., drenagem status adequado (monitoramento anual). Recomendação: reforço CBUQ 6cm 2025-2026 (antes deterioração acentuada). Resultado esperado: ICP 80+ em 3 anos, vida +10 anos. Custo intervenção: R$ 25M/100km. BR-101 ES reabilitação 2018: ICP 32 (crítico), afundamento 28mm, estrutura colapsada. Reabilitação total 50km (demolição, reconstrução base BCS, CBUQ novo) → custo R$ 45M, prazo 18 meses. Resultado: nova rodovia, vida projeto 20 anos. Concessão Imigrantes SP: monitoramento 2019-2024 dados (VDM, ICP, drenagem) → SIG mostra deterioração lenta (planejamento reforço 2028). Custo O&M atual R$ 8k/ano (manutenção preventiva), projeção reforço R$ 15M economizado vs emergencial (reabilitação R$ 35M). BR-277 PR fracasso 2015: base inadequada (CBR 1.5, aceitou >=3) + drenagem falha → reaparecia trincas pós-recapeamento → investigação descobriu fundação → demolição+ reconstrução total (custo 5x pavimento convencional). Lição: inspeção fundação pre-obra essencial (evita retrabalho custoso).'
    as content
) chunks
ON CONFLICT DO NOTHING;

COMMIT;

SELECT COUNT(*) as chunks_om FROM rag_chunks WHERE prefix LIKE 'rod:om:%';
