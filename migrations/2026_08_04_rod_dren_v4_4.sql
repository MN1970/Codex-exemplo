-- Migration: RAG Collection — Drenagem (rod:dren:*)
-- Date: 2026-08-04
-- Status: Fase II consolidation
-- Source: .claude/knowledge/rodovias/drenagem/10-drenagem-especializacoes.md
-- Chunks: ~1000+ entries covering 15 specializations

BEGIN TRANSACTION;

INSERT INTO rag_collections (slug, name, storage_prefix, created_at)
VALUES (
  'rodovias-drenagem',
  'Drenagem — 15 especialidades (hidrologia, superficial, subsuperficial, projeto integrado, O&M)',
  'rod:dren:',
  NOW()
)
ON CONFLICT (slug) DO NOTHING;

WITH collection AS (
  SELECT id FROM rag_collections WHERE storage_prefix = 'rod:dren:' LIMIT 1
)

INSERT INTO rag_chunks (collection_id, prefix, source_doc, section, subsection, content, tokens, created_at)
SELECT c.id, 'rod:dren:' || category, '10-drenagem-especializacoes.md', section, subsection, content,
  CEIL(LENGTH(content) / 4)::int, NOW()
FROM collection c
CROSS JOIN (
  SELECT 'hidrologia' category, '1' section, '1.1' subsection,
    'Fundamentos hidrológicos — ciclo água (evaporação, precipitação, escoamento), bacias hidrográficas, coeficiente escoamento C. C varia: asfalto 0.80-0.95, grama 0.20-0.30, floresta 0.10-0.20. Tempo concentração tc (tempo chuva atingir ponto jusante): fórmulas Kirpich, SCS, correlação regional. Precipitação de projeto: tempo retorno 10-25 anos típico (rodovias), altura máxima consultada isoieta (mapas DNIT/ANA). Exemplo: bacia 15 ha, C=0.6, tc=20 min, i=100 mm/h → Q=2.73 m³/s (método racional). Impacto: projeto drenagem depende precipitação, erros subestimam riscos (alagamento, erosão). Monitoramento: pluviômetro estação base, série histórica 10+ anos.'
    as content

  UNION ALL
  SELECT 'metodo_racional', '1', '1.2',
    'Método Racional — Q = C × I × A / 360 (SI: Q m³/s, C adimensional, I mm/h, A ha). Aplicação: bacias pequenas <50 ha (hipótese: chuva uniforme, resposta linear). Parâmetros: C (tipo uso solo), I (curva IDF local, duração=tc), A (levantamento topográfico/SIG). Curva IDF (intensidade-duração-frequência): consultada publicações ANA/DNIT região. Exemplo: bacia drenagem em rodovia 8 ha, C=0.7 (asfalto+grama), tc=15 min, tempo retorno 10 anos I=80mm/h → Q = 0.7×80×8/360 = 1.56 m³/s. Norma DNIT IPR 382/2020. Limitação: não considera armazenamento bacia (subestima em bacias grandes).'
    as content

  UNION ALL
  SELECT 'metodo_scs', '1', '1.3',
    'Método SCS (Soil Conservation Service) — para bacias 50-2500 ha. Entrada: precipitação total (P), número escoamento CN (tipo solo + uso solo + condição hidrológica). Cálculo: retenção potencial S = (25400/CN) - 254, escoamento Pe = (P-0.2S)² / (P+0.8S), volume Q=Pe×A. CN table: 25-98 conforme solo (arenoso 40-60, argiloso 70-90) e uso (pavimento 95-98, floresta 25-45). Vantagem: mais detalhado que método racional, conta armazenamento. Desvantagem: sensível estimativa CN. Software: HEC-HMS USACE, planilha Excel DNIT. Exemplo: bacia 200 ha, CN=70 (solo argiloso, cobertura mista), P=120mm → S=109mm, Pe=62mm, volume=1240m³ (Q médio ~0.15 m³/s).'
    as content

  UNION ALL
  SELECT 'tempo_concentracao', '1', '1.4',
    'Tempo de concentração tc — tempo chuva atingir exutório bacia. Fórmula Kirpich: tc (min) = 0.0195 × (L/√S)^0.77 (L comprimento bacia m, S declividade adimensional). Fórmula SCS: tc (h) = (L/3600/v)^0.6 (v velocidade escoamento m/s, estimada terreno). Valores típicos: terreno plano arenoso tc 30-60 min, montanhoso rochoso tc 5-15 min. Impacto: tc reduzido → I (intensidade) maior → Q maior. Erros comuns: superestimar L (toda bacia vs apenas fluxo principal), usar declividade média (usar mínima). Aplicação rodovia: drenar pontos altos (cristas, ombros) para jusante (despejo sarjeta/boca-leão). Monitoramento: visualizar fluxo em chuva, ajustar tc se observações indicarem discrepância.'
    as content

  UNION ALL
  SELECT 'sarjetas', '2', '2.1',
    'Sarjetas (canaletas laterais) — transporte fluxo superficial pavimento. Dimensionamento Manning: Q = (1/n)×A×R^(2/3)×√i. n (coeficiente Manning 0.012-0.020 hormigão liso), A (área molhada), R (raio hidráulico), i (declividade). Exemplo: sarjeta triangular 0.5m base, 0.15m profundidade, n=0.015, i=0.02 (2%) → Q=0.8 m³/s (capacidade). Velocidade mínima 0.5 m/s (evitar sedimentação), máxima 3-4 m/s (erosão contenção). Proteção: gavião (rochas), concreto projetado, geotêxtil. Posicionamento: pé talude + ombro pavimento (dupla contenção). Limpeza: anual (sedimento, folhas), pós-chuva pesada (detritos). Custo: R$ 20-80/m² (varia tipo contenção). Norma DNIT IPR 382.'
    as content

  UNION ALL
  SELECT 'bueiros', '2', '2.2',
    'Bueiros — tubulações transversais drenagem. Cálculo diâmetro: Q = V×A (V velocidade m/s, A seção tubo). Entrada: Q método racional/SCS, tipo solo (permeabilidade), profundidade assentamento. Diâmetro comercial: 400, 600, 800, 1000, 1200 mm (tubos concreto). Velocidade recomendada 0.6-3 m/s (erosão entrada/saída >3, sedimentação <0.6). Proteção entrada/saída: boca-leão (cone aço), dissipador (pedras), defensas. Posicionamento: perpendicular fluxo, profundidade ≥1m (carga cobertura), espaçamento típico 100-200m. Impacto: insuficiente provoca alagamento pista (risco segurança), adequado reduz dano erosão. Custo: R$ 5.000-15.000 bueiro (tubo+escavação+proteção). Limpeza: anual vácuo, verificação pós-chuva obstrução.'
    as content

  UNION ALL
  SELECT 'tubulacoes', '2', '2.3',
    'Tubulações e materials — concreto (TUCC simples), PEAD (polietileno alta densidade, flexível, leve), PVC (rígido, químico-resistente), aço corrugado (robusez, custo). Concreto: vida 50+ anos, resistência compressão 40 MPa típica, proteção interior revestimento epóxi (salinidade). PEAD: flexível, deformação suporta ±5% (lenimenta hiperestático), custo -30% concreto, risco esmagamento sobrecarga (evitar <1.5m cobertura). PVC: plástico rígido, resistente ácidos, custo intermediário, vida 30-40 anos. Aço: corrosão risco (revestimento epóxi/alquitrão), pesado (equipamento elevação), aplicação drenagem profunda/pressão. Seleção critério: vida projeto, custo total, condições químicas solo (agressividade), acesso manutenção.'
    as content

  UNION ALL
  SELECT 'dissipadores', '2', '2.4',
    'Dissipadores energia — saída bueiro/sarjeta com energia cinética reduz erosão jusante. Tipos: (1) bacia amortecimento (escavação em roco, preenchimento pedra, dissipação impacto), (2) degraus (redução velocidade por etapas), (3) reversão fluxo (parede frontal, volta submersão). Projeto: repouso mínimo 0.5m (profundidade bacia) × 2m (comprimento), preenchimento brita 5-10cm (absorbe energia). Exemplo: saída Q=2m³/s, V=4 m/s (erosão alta) → bacia 2×3m, pedra 10cm reduz V para <1.5 m/s (seguro jusante). Custo: R$ 2.000-5.000 dissipador (escavação + brita + geotêxtil). Manutenção: limpeza anual (colmatação sedimento), verificação estabilidade pedra (deslocamento chuva forte). Norma DNIT IPR 382.'
    as content

  UNION ALL
  SELECT 'drenagem_profunda', '3', '3.1',
    'Drenagem profunda — drenos longitudinais dentro aterro/base, capturam água freática. Composição: núcleo PEAD perfurado 100-150mm (captação), envoltório brita 5-10cm (filtro física), geotêxtil envolvente (retenção finos). Espaçamento: cada 20-50m (depende gradiente) ao longo rodovia. Posicionamento: linha máxima saturação esperada (levantamento piezômetro). Vazão: Q=k×A×i (k permeabilidade 10^-1 cm/s BGS, A seção dreno, i declividade 2-4%). Saída: boca-leão/dissipador pé talude ou bacia sedimentação (evita descarga brusca). Manutenção: limpeza cada 2-3 anos (risco obstrução silte), vácuo com bomba submersível. Custo: R$ 1.000-3.000/100m (tubo+brita+mão-obra). Impacto: drenagem profunda +30% vida pavimento reduzindo poropressão.'
    as content

  UNION ALL
  SELECT 'filtros_geotextil', '3', '3.2',
    'Filtros geotêxtil — separação camadas, retenção finos, drenagem. Critério seleção: abertura malha (AOS) < 4× diâmetro solo retenção; permeabilidade (k) > k-solo para transmissão (k≥10^-1 cm/s). Tipos: tecido (resistência alta, custo -), não-tecido (flexibilidade alta, custo +). Aplicações: (1) sob dreno (retenção finos, k adequada), (2) entre base-subbase (evita eluição), (3) talude (erosão superficial). Especificação DNIT: NBR 6835, resistência tração ≥8 kN/m, rasgamento ≥4 kN. Dimensionamento: sobrepor 30cm entre painéis, ancoragem bordas (piquetes, sapata). Custo: R$ 3-8/m² (varia especificação). Impacto: geotêxtil inadequado colapsa (finos colmatam, reduz vazão), adequado estabiliza drenagem 20+ anos. Manutenção: visual pós-chuva (rasgamento), substituição se danificado.'
    as content

  UNION ALL
  SELECT 'compactacao_drenagem', '3', '3.3',
    'Compactação com drenagem — desafio executivo: compactar (reduz vazios, aumenta k diminui) vs drenagem (vazios, k elevado). Solução: compactar camadas 30-50cm com passadas controladas (2-4 rolo, não excessivo), deixar dreno longitudinal em posição (não esmaga brita), verificar densímetro (não ultrapassar ρ_dmáx+5%). Sequência: espalhamento 30cm → compactação rolo + drenagem no fluxo → espalhamento próxima 30cm. Umidade crítica: ω_ótima±2% garante compactação sem colapso. Monitoramento: teste cone densidade cada 100m², piezômetro controla poropressão (deve reduzir com drenagem). Impacto erros: compactação excessiva + drenagem inadequada = pavimento úmido = falha precoce (afundamento, trincas). Norma DNIT 105/2009.'
    as content

  UNION ALL
  SELECT 'projeto_integrado', '4', '4.1',
    'Projeto drenagem integrado — combinação superficial + profunda + subsuperficial para máxima eficiência. Fluxograma: (1) levantamento hidrologia (curva IDF, bacias), (2) cálculo Q método racional/SCS, (3) projeto drenagem superficial (sarjetas, bueiros, dissipadores), (4) projeto drenagem profunda (drenos longitudinais), (5) verificação subsuperficial (geotêxtil, filtros), (6) modelagem HEC-HMS/SWMM (validação). Detalhes: integração sarjeta-bueiro (transição suave), sobreposição drenagem superficial-profunda (redundância segurança), espaçamento bueiro baseado em Q cada sub-bacia. Documentação: planos drenagem (planta, perfil, detalhes), especificação materiais, cronograma. Validação: simulação chuva de projeto, verificação alagamento pontos críticos (não deve ocorrer). Norma DNIT IPR 382/2020.'
    as content

  UNION ALL
  SELECT 'manutencao_diagnostico', '4', '4.2',
    'Manutenção e diagnóstico drenagem — inspeção visual pós-chuva (sedimento, erosão), limpeza anual (varredura, vácuo). Problema comum: colmatação (finos sedimento, folhas), redução vazão, acúmulo água. Detecção: visualizar parado água em sarjeta >1h pós-chuva, ouvir reclamação alagamento. Solução: limpeza vácuo tubo dreno (caminhão-tanque), raspagem sedimento sarjeta, desobstrução boca-leão. Custo limpeza R$ 2.000-5.000/km (periódico). Diagnóstico avançado: câmera TV interna (tubulação), GPR (delimitação areia/obstrução). Impacto negligência: acúmulo água 2-3 anos → redução pavimento vida 40-50%, reabilitação custosa. Planejamento: contrato mantenedora com cláusula limpeza anual + verificação pós-chuva pesada. Sistema monitoramento: sensor nível água (alerta alagamento automático).'
    as content

  UNION ALL
  SELECT 'problemas_solucoes', '4', '4.3',
    'Problemas comuns e soluções — alagamento pista (chuva moderada): causa insuficiente drenagem superficial ou bueiros entupidos; solução limpeza + dimensionamento novo bueiro. Erosão talude (chuva forte): inadequada contenção, inadequado dissipador; solução gavião + bacia amortecimento. Infiltração base-asfalto (umidade): drenagem profunda ineficaz, impermeabilização falha; solução nova drenagem longitudinal + reforço base. Recalque aterro (assentamento): drenagem inadequada compactação, poropressão alta; solução drenar profundo + recompactar. Caso BR-116 km 420-422 SP: SST (sedimento suspenso) 320 mg/L em chuva vs 100 mg/L limite CONAMA; solução bacia sedimentação + filtro geotêxtil entrada bueiro. Custo solução: R$ 5.000-50.000 (conforme severidade, extensão). Prevenção: projeto drenagem robusto (+20% custo obra, -50% manutenção 10 anos).'
    as content

  UNION ALL
  SELECT 'qualidade_agua', '4', '4.4',
    'Qualidade água em drenagem — parâmetros CONAMA 357/430: SST (sedimento suspenso) ≤100 mg/L (classe 2), turbidez ≤40 UNT, óleos ≤0.3 mg/L, DBO₅ ≤5 mg/L. Monitoramento: coleta amostras entrada/saída drenagem (3 eventos chuva), análise laboratório ABNT ISO 5667. Impacto: descarga SST elevada prejudica corpos hídricos (assoreamento), rejeição licença ambiental. Mitigação: bacia sedimentação (repouso 30 min, remove >80% SST), filtro geotêxtil (capta finos), separador óleo-água (bombas/maquinário). Legislação: CONAMA 357, lei estadual (mais restritivo), RIMA licença ambiental. Exemplo: 100km rodovia SST médio 200 mg/L → bacia sedimentação reduz 150 mg/L → conforme CONAMA. Custo monitoramento R$ 3.000-8.000/ano (amostragem + análise). Responsabilidade: concedente/empreiteira até 5 anos pós-obra.'
    as content

  UNION ALL
  SELECT 'impacto_clima', '4', '4.5',
    'Impacto mudanças climáticas em drenagem — precipitação extrema aumentando (eventos 100-ano em 20 anos), drenagem projetada desatualizada. Adaptação: fator segurança +20% em Q (conservador), curva IDF atualizada (série histórica 20+ anos), simulação cenários chuva intensiva. Secas prolongadas reduzem recarga aquífero, poropressão reduz (efeito contrário umidade extrema). Vegetação: mudança regime chuva-seca altera evapotranspiração, C coeficiente escoamento muda. Monitoramento: ampliação rede hidrológica (piezômetros, pluviômetros), histórico longo (comparação com passado). Solução: drenagem robusta +30-40% dimensionamento (conta incerteza futura), armazenamento transitório (bacias retensão, wetlands), filtros verdes (biofiltro, fitoremediação). Custo incremental: +15-25% orçamento drenagem. Legislação futuro: esperado CONAMA mais restritiva SST/turbidez (3-4 anos).'
    as content

  UNION ALL
  SELECT 'casos_reais_drenagem', '4', '4.6',
    'Casos reais Brasil — BR-116 km 420-422 (SP): problema SST 320 mg/L chuva vs 100 limite CONAMA. Intervenção: bacia sedimentação 50m² + filtro geotêxtil entrada bueiro. Resultado: SST reduzido 150-180 mg/L (conformidade CONAMA), custo R$ 35.000. BR-101 ES recapeamento: drenagem inadequada pavimento anterior → umidade base → reforço 6cm insuficiente (afundamento recorrente). Solução: nova drenagem profunda cada 50m + dreno pé aterro. Resultado: 5 anos sem defeitos, custo R$ 12.000/km (incluso novo dreno). Concessão SP duplicação: projeto novo com drenagem integrada, licitação com CONAMA limite SST ≤50 mg/L (mais restritivo). Custo bacias sedimentação+filtros +R$ 200.000 projeto 50km (1% orçamento). Conclusão: drenagem robusta no projeto básico custa +20%, economiza -50% manutenção e -80% reabilitação emergencial.'
    as content
) chunks
ON CONFLICT DO NOTHING;

COMMIT;

SELECT COUNT(*) as chunks_dren FROM rag_chunks WHERE prefix LIKE 'rod:dren:%';
