#!/usr/bin/env python3
"""
init_rag_golden_set.py — Inicializa golden set de 50 QA pairs para RAG eval

Objetivo:
  Cria dataset base para avaliação de qualidade da busca RAG (retrieval):

  1. Gera 50 QA pairs distribuídos entre segmentos (S1-S10):
     - Questões variadas (projeto, norma, cálculo, regulação)
     - Respostas esperadas (golden answer)
     - Agent alvo (expected_agent)
     - Chunk IDs esperados (expected_chunk_ids)

  2. Baseline de recall@5 e MRR na config BM25 atual
     - Teste de que chunks corretos aparecem nos top-5
     - Mean Reciprocal Rank (posição média do melhor chunk)

  3. Output: CSV + JSON schema para A/B testing (embedding v1 vs v2)
     - Formato permitido para futuros testes de busca
     - Versionado e reproduzível (seed controlado)

Inputs:
  --seed: random seed para reprodutibilidade (default: 42)
  --num-pairs: quantidade de QA pairs (default: 50)
  --segments: agentes a incluir (default: saneamento,energia,portos,aeroportos,barragens)
  --output-dir: diretório de saída (default: rag_evals)
  --verbose: logging detalhado (default: False)

Output:
  rag_evals/golden_set_v1.csv — 50 rows com colunas:
    qa_id, question, golden_answer, agent_id, expected_chunks,
    difficulty_level, source_domain, created_at

  rag_evals/golden_set_schema.json — schema de validação para A/B tests

Exit codes:
  0: Sucesso
  1: Erro crítico
"""

import sys
import os
import json
import logging
import argparse
import csv
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple
import uuid
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# Golden set templates per segment
GOLDEN_SET_TEMPLATES = {
    "saneamento": [
        {
            "question": "Como dimensionar uma ETA de ciclo completo para 150 mil habitantes?",
            "golden_answer": "ETA de ciclo completo inclui coagulação, floculação, decantação, filtração e desinfecção. Para 150k hab com consumo de 200 L/hab.dia, considera taxas de floculação hidráulica 400-600 m³/m².dia e decantação 40-60 m³/m².dia.",
            "source_domain": "water_treatment",
            "difficulty": "medium"
        },
        {
            "question": "Qual método para calcular golpe de aríete em adutoras pressurizadas?",
            "golden_answer": "Usar fórmula de Joukowsky: ΔH = (a/g) × Δv, onde 'a' é celeridade (1200-1400 m/s em PVC), 'g' gravidade, 'Δv' mudança de velocidade. Alternativa: método das características para transientes hidráulicos.",
            "source_domain": "hydraulics",
            "difficulty": "hard"
        },
        {
            "question": "AySA me pediu um estudo de reabilitação da Planta Norte. Por onde começar?",
            "golden_answer": "Diagnóstico de capacidade atual (ETE primária vs secundária), teste de eficiência de remoção de carga (DBO, DQO), avaliação de lodo, definição de tecnologia nova (UASB, MBR, lodo ativado).",
            "source_domain": "wastewater_argentina",
            "difficulty": "medium"
        },
        {
            "question": "Qual é o método para dimensionar rede coletora de esgoto pela NBR 9649?",
            "golden_answer": "NBR 9649 estabelece: diâmetro mínimo 100mm, declividade mínima 0.5% (esgoto doméstico), velocidade mín 0.6 m/s, máx 3 m/s, profundidade máx 5.5m. Usar fórmula de Manning para verificação.",
            "source_domain": "sewerage_design",
            "difficulty": "medium"
        },
        {
            "question": "O que é subsídio cruzado na Lei 14.026 de saneamento?",
            "golden_answer": "Subsídio cruzado: arrecadação em cliente classe A (alta renda) subsidia cliente classe C (baixa renda) para universalização de 99% água e 90% esgoto até 2033. Tarifa social obrigatória.",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como avaliar a colmatação de filtro de areias em ETA?",
            "golden_answer": "Monitorar perda de carga (manômetro diferencial), velocidade de filtração (taxa aplicação), qualidade turbidez efluente. Retrolavagem quando ΔP > 1.5-2.0 m ou turbidez > 1 UNT.",
            "source_domain": "water_treatment",
            "difficulty": "medium"
        },
        {
            "question": "Qual a diferença entre EPANET e SWMM para modelagem de redes de água?",
            "golden_answer": "EPANET: redes pressurizadas de distribuição de água, análise de qualidade e vazão. SWMM: drenagem urbana e escoamento superficial, simulação de chuva-vazão.",
            "source_domain": "software",
            "difficulty": "easy"
        },
        {
            "question": "Como calcular a altura manométrica de uma estação elevatória?",
            "golden_answer": "Hm = Hg + ΔH, onde Hg é altura geométrica (sucção + recalque) e ΔH são perdas de carga. Verificar NPSH disponível >= NPSH requerido da bomba. Sobre-elevação típica 10-20%.",
            "source_domain": "hydraulics",
            "difficulty": "medium"
        },
        {
            "question": "O que significa RAP no contexto de concessões de saneamento?",
            "golden_answer": "RAP = Remuneração por Aumento de Qualidade ou Receita, conforme regulação. Mecanismo para remunerar investimentos de melhoria (eficiência, qualidade, universalização).",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como dimensionar um reservatório de retenção para drenagem urbana?",
            "golden_answer": "Volume = (i × A × (Tr/3600)) - (C × Tr), onde i é intensidade chuva (mm/h), A área drenagem (m²), Tr período retorno (s), C vazão de saída (m³/s). Método racional ou hidrograma unitário.",
            "source_domain": "stormwater",
            "difficulty": "hard"
        }
    ],
    "energia": [
        {
            "question": "Como dimensionar uma linha de transmissão de 500kV para 250km?",
            "golden_answer": "Usar coordenadas de torre (altura, base), calcular impedância série (R, L, C), capacidade térmica (ampacidade), queda de tensão (< 5%), estabilidade transitória. Normas: ABNT NBR 6655, IEEE 738.",
            "source_domain": "transmission",
            "difficulty": "hard"
        },
        {
            "question": "Qual é a celeridade do cabo ACSR 636 MCM em LT de 345kV?",
            "golden_answer": "Celeridade de propagação onda eletromagnética em linha aérea: v = c / sqrt(εr) ≈ 0.97c (300k km/s aprox). Para cabo ACSR 636 MCM, tabelado em normas IEEE, típico ~0.95-0.97c.",
            "source_domain": "transmission_design",
            "difficulty": "medium"
        },
        {
            "question": "O que é RAP em leilão de transmissão ANEEL?",
            "golden_answer": "RAP = Receita Anual Permitida, determinada por ANEEL em edital de concessão. Define remuneração garantida ao concessionário por T anos (tipicamente 30-35). Revisão tarifária a cada 4-5 anos.",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como fazer estudo de ampacidade para condutor em LT?",
            "golden_answer": "Usar metodologia IEEE 738 ou IEC 60287: balançear ganhos de calor por efeito Joule vs perdas por radiação/convecção. Dados: temperatura ambiente, velocidade vento, elevação, fator solar, emissividade.",
            "source_domain": "transmission_design",
            "difficulty": "hard"
        },
        {
            "question": "Qual é a diferença entre leilão de transmissão e concessão direta?",
            "golden_answer": "Leilão: competição pública, ANEEL fixa RAP mínima. Concessão direta: empresa privada propõe projeto, ANEEL avalia. Leilão reduz custos, concessão direta permite inovação.",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como projetar uma subestação de 230kV isolada em gás (GIS)?",
            "golden_answer": "GIS vs isolação ar: menor footprint, menor manutenção, custo inicial maior. Equipamentos: transformador, disjuntor GIS, para-raios, seccionadora, transformador de corrente/tensão. Arranjo: barra simples ou dupla conforme carga.",
            "source_domain": "substation_design",
            "difficulty": "medium"
        },
        {
            "question": "O que é MRE na operação do SIN brasileiro?",
            "golden_answer": "MRE = Mecanismo de Realocação de Energia. Hidroelétricas brasileiras colocam energia em pool e dividem risco de vazão. Diferenças de receita compensadas entre usinas (geração real vs garantida).",
            "source_domain": "operation",
            "difficulty": "medium"
        },
        {
            "question": "Qual RBAC orienta projeto de pista de subestação?",
            "golden_answer": "Norma ABNT NBR 14039 (instalações elétricas em MT) e IEC 61936 (MT de corrente alternada). Distâncias de segurança, aterramento, layout, sinalização, proteção.",
            "source_domain": "standards",
            "difficulty": "easy"
        },
        {
            "question": "Como calcular a queda de tensão em um circuito de distribuição?",
            "golden_answer": "ΔV(%) = (R×P + X×Q) / (10 × V²), onde R, X são resistência/reatância (Ω/km), P, Q são potência ativa/reativa (kW, kVAr), V é tensão (kV). Máximo: 8% em distribuição primária.",
            "source_domain": "distribution",
            "difficulty": "medium"
        },
        {
            "question": "Qual é o período de concessão típico para geração eólica no Brasil?",
            "golden_answer": "Tipicamente 20-30 anos em contrato de concessão. PPA (Power Purchase Agreement) entre gerador e distribuidor/grande consumidor, preço fixo ou variável com indexação.",
            "source_domain": "renewable_energy",
            "difficulty": "easy"
        }
    ],
    "portos": [
        {
            "question": "Como dimensionar a defensa de um berço para navio Panamax?",
            "golden_answer": "Panamax: 300m comprimento, 33m boca, 12m calado. Defensa absorve energia cinética (0.5×M×V²). Tipo: tubo cilíndrico, pneu, fender pneumático. Espaçamento 30-50m, resistência > força de amarração.",
            "source_domain": "terminal_design",
            "difficulty": "hard"
        },
        {
            "question": "Qual é o calado máximo permitido no Porto de Santos?",
            "golden_answer": "Calado operacional ~ 14-15m em maré alta (Porto de Santos tem 12.5m de profundidade nominal). Limitado por dragagem e batimetria. Revisar ANTAQ/Porto Authority para dados atualizados.",
            "source_domain": "port_operation",
            "difficulty": "easy"
        },
        {
            "question": "Como calculo o número de portêineres para um terminal de contêineres com throughput de 2M TEU/ano?",
            "golden_answer": "Produtividade portêiner: 30-40 moves/hora. Para 2M TEU, ciclo anual ÷ (dias úteis × horas × produtividade) = número equipamentos. Típico: 8-12 portêineres para 2M TEU.",
            "source_domain": "port_equipment",
            "difficulty": "medium"
        },
        {
            "question": "Qual PIANC bulletin cobre projeto de quebra-mar em enrocamento?",
            "golden_answer": "PIANC WG33 (2016): Design of Low-Crested Coastal Defence Structures. Para berço-porto: WG34 (Breakwater Design), analisa ondas, recorrência tempestade, altura de onda (H1/3, Hmax).",
            "source_domain": "standards",
            "difficulty": "medium"
        },
        {
            "question": "O que é TUP no contexto de concessão portuária?",
            "golden_answer": "TUP = Terminal de Uso Privado. Pessoa jurídica autorizada ANTAQ a operar terminal portuário por concessão (20-40 anos típico). Diferente de Terminal Público (porto organizado).",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como planejo dragagem de canal de acesso com maré de 2.5m?",
            "golden_answer": "Profundidade projeto = (calado operacional - maré mínima) + allowance de segurança (0.5-1.0m). Dragagem mecânica vs hidráulica. Volante de dragagem considerando reciclagem e sazonalidade.",
            "source_domain": "dredging",
            "difficulty": "medium"
        },
        {
            "question": "Qual é a diferença entre um píer e um cais?",
            "golden_answer": "Cais: estrutura paralela ao costado, amarração lateral do navio. Píer: estrutura perpendicular, amarração em tandem (proa-popa). Píer permite maior throughput, cais maior flexibilidade de acesso.",
            "source_domain": "terminal_design",
            "difficulty": "easy"
        },
        {
            "question": "Como calcular o volume de areia em praia artificial para mitigação portuária?",
            "golden_answer": "Volume = (profundidade × comprimento × largura) com fator de compactação (1.3-1.5). Material: areia com granulometria 0.15-2mm (conforme norma). Manutenção anual para erosão (5-15% ao ano).",
            "source_domain": "environmental",
            "difficulty": "medium"
        },
        {
            "question": "O que é arrendamento portuário conforme ANTAQ?",
            "golden_answer": "ANTAQ autoriza arrendamento de áreas/berços em portos organizados para operação de terminal. Contrato por 25-40 anos, renovável. Operador paga à administração portuária taxa de arrendamento e taxa de utilização.",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como dimensiono o pátio de estocagem para cargas contêiner + granel?",
            "golden_answer": "TEU/m² (contêiner): 8-12 (altura até 5 camadas). Granel: t/m² (3-5 metros altura). Mix: considerar rotatividade, dwell time. Equipamentos de movimentação: RTG, SC, carretas.",
            "source_domain": "terminal_design",
            "difficulty": "medium"
        }
    ],
    "aeroportos": [
        {
            "question": "Como dimensiono uma pista de pouso para aeronaves tipo A320neo?",
            "golden_answer": "A320neo: comprimento 37.6m, altura 12.5m, peso máximo 73-80t (MTOW), distância decolagem ~2400m, pouso ~1500m. Pista: mínimo 2500m (margem segurança), pavimento rígido ou flexível (NBR 14054).",
            "source_domain": "airfield_design",
            "difficulty": "hard"
        },
        {
            "question": "Qual é o PCN (Pavement Classification Number) da minha pista?",
            "golden_answer": "PCN (ICAO Annex 14): número que caracteriza capacidade de pavimento em suportar carga de aeronave. Cálculo: resistência CBR do subleito, espessura camadas, método FAA ACN-PCN. Escala 10-100.",
            "source_domain": "airfield_design",
            "difficulty": "medium"
        },
        {
            "question": "O que é RBAC em aviação civil brasileira?",
            "golden_answer": "RBAC = Regulamento Brasileiro de Aviação Civil (editado por ANAC). RBAC 14: Operações de aeródromos comerciais. RBAC 154: Projeto de aeródromos. Normas de segurança, pavimento, sinalização.",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como projeto o balizamento CAT II para operação noturna em aeroporto?",
            "golden_answer": "CAT II (decisão altura 100-200 ft, visibilidade 400-800m). Luzes de aproximação, pista, zona de toque. ILS (Instrument Landing System) com localizer, glideslope, marker beacons. Norma ICAO Annex 14, parte 4.",
            "source_domain": "navigation_aids",
            "difficulty": "hard"
        },
        {
            "question": "ICAO Annex 14 permite offset lateral de RWY (pista)?",
            "golden_answer": "Offset de RWY: máximo 2% do comprimento (norma ICAO). Utilizado para desviar de obstáculos ou considerar topografia. Deve manter operacionalidade em ambas as direções.",
            "source_domain": "standards",
            "difficulty": "medium"
        },
        {
            "question": "Qual é a diferença entre TPS e TECA em um aeroporto?",
            "golden_answer": "TPS = Terminal de Passageiros (landside, gates, check-in, bagagem, embarque). TECA = Terminal de Cargas (logística, alfândega, armazenagem). Independentes, com infraestrutura própria (pátio, garagens, docas).",
            "source_domain": "terminal_design",
            "difficulty": "easy"
        },
        {
            "question": "Como calculo o tamanho do pátio de aeronaves para 20 A320 simultâneos?",
            "golden_answer": "A320: footprint ~40m × 37m = ~1480 m² com margens de segurança (20-25m entre proas). Para 20 A320: ~30-35k m² pátio + rodovias de acesso, pontes de embarque (~500m²/unidade).",
            "source_domain": "airfield_design",
            "difficulty": "medium"
        },
        {
            "question": "O que é código ICAO de referência de um aeroporto?",
            "golden_answer": "Código referência ICAO Annex 14: classe de aeródromo (1-4) × comprimento RWY (A-F). Ex: código 4F = aeronaves até A380 e RWY >= 2400m. Define requerimentos de segurança, espaçamentos, equipamentos.",
            "source_domain": "standards",
            "difficulty": "easy"
        },
        {
            "question": "Como projeto as rodovias de táxi (taxiways) de um aeroporto regional?",
            "golden_answer": "Largura mínima: 15-23m (conforme código ICAO, aceleração requerida). Raio curva: 200-300m (A320). Distância eixo-eixo RWY-TWY: 150-300m (safety buffer). Pavimento: rígido ou flexível, CBR > 4-8.",
            "source_domain": "airfield_design",
            "difficulty": "medium"
        },
        {
            "question": "Qual é a vida útil típica de pavimento rígido (concreto) em pista?",
            "golden_answer": "20-30 anos com manutenção preventiva (junta de dilatação, selagem). Pavimento flexível (asfalto): 15-20 anos. Considerar tráfego acumulado (ESA = Equivalent Single Axle), clima, drenagem.",
            "source_domain": "pavement_design",
            "difficulty": "easy"
        }
    ],
    "barragens": [
        {
            "question": "Como projeto uma barragem CFRD (Concrete Face Rockfill Dam) de 80m?",
            "golden_answer": "CFRD: núcleo de enrocamento + face de concreto (0.5-1.0m espessura). Projeto: estabilidade encosta (inclinação 1:1.5 a 1:2), drenagem interna, geotêxtil anti-erosão, construção faseada (seção 1-2m altura).",
            "source_domain": "dam_engineering",
            "difficulty": "hard"
        },
        {
            "question": "Qual é o coeficiente de segurança mínimo contra ruptura em barragem?",
            "golden_answer": "FS (fator segurança) mínimo: 1.5 (estado normal) a 1.3 (estado acidental). Cálculo: momento resistente / momento tomba, método lamelas ou Bishop simplificado, superfície crítica.",
            "source_domain": "stability_analysis",
            "difficulty": "medium"
        },
        {
            "question": "Como faço dam breach analysis pós-Brumadinho?",
            "golden_answer": "HEC-RAS ou similar: modelo 1D/2D de inundação. Inputs: hidrografia, DEM, parâmetros roughness. Cenários: ruptura parcial vs total, velocidade propagação onda. Mapa de inundação, altura água, velocidade.",
            "source_domain": "hazard_assessment",
            "difficulty": "hard"
        },
        {
            "question": "Qual bulletin ICOLD cobre rejeitos filtrados (dry stack)?",
            "golden_answer": "ICOLD Bulletin 164 (2016): Filtered Tailings. Tecnologia compactação de rejeitos (< 8% água), filtração, segregação granulométrica. Menor risco de liquefação vs rejeito convencional.",
            "source_domain": "standards",
            "difficulty": "medium"
        },
        {
            "question": "O que é PNSB e quais são as exigências para inspeção periódica?",
            "golden_answer": "PNSB = Plano Nacional de Segurança de Barragens (Lei 12.334/2010). Inspeção periódica: anual para barragem categoria alta/risco alto, avaliação de estabilidade a cada 2 anos (engenheiro registrado CREA).",
            "source_domain": "regulation",
            "difficulty": "easy"
        },
        {
            "question": "Como projeto filtro drenante em barragem de enrocamento?",
            "golden_answer": "Filtro (areia grossa ou pedrisco) entre núcleo e drenagem. Critério: D₁₅(filtro) / D₈₅(núcleo) < 5. Reduz erosão regressiva, dissipa pressão poro. Espessura mínima 2-3m.",
            "source_domain": "seepage_control",
            "difficulty": "medium"
        },
        {
            "question": "Qual é a diferença entre barragem de concreto CCR e CCV?",
            "golden_answer": "CCR = Concreto Compactado a Rolo (baixo cimento, alto friccionante, construção rápida). CCV = Concreto Convencional (lançamento convencional). CCR: mais econômico, menos calor, maior resistência fricção.",
            "source_domain": "dam_engineering",
            "difficulty": "medium"
        },
        {
            "question": "O que é TSF (Tailings Storage Facility) e qual a vida útil típica?",
            "golden_answer": "TSF = barragem de rejeitos (mineração). Vida útil: 20-50 anos conforme volume anual de rejeito. Risco de liquefação em alteamento a montante. Monitoramento: piezômetros, inclinômetros.",
            "source_domain": "tailings_management",
            "difficulty": "easy"
        },
        {
            "question": "Como calcular a altura máxima de água (HMC) em barragem?",
            "golden_answer": "HMC = elevação (cota de coroamento - 1-2m borda livre) menos efeito de onda. Margem segurança: borda livre >= 1.5-2.0m. Hidrograma de cheia, método estatístico (tempo retorno 500-1000 anos).",
            "source_domain": "hydrology",
            "difficulty": "medium"
        },
        {
            "question": "O que significa categoria de risco (baixa/média/alta) conforme PNSB?",
            "golden_answer": "PNSB: classificação por altura, volume, população afetada, dano potencial. Categoria alta: H > 15m, V > 3M m³, ou dano > 100 pessoas. Define frequência inspeção, requisitos projeto, estudo de confiabilidade.",
            "source_domain": "regulation",
            "difficulty": "easy"
        }
    ]
}


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Inicializa golden set de 50 QA pairs para RAG evaluation"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--num-pairs",
        type=int,
        default=50,
        help="Number of QA pairs (default: 50)"
    )
    parser.add_argument(
        "--segments",
        default="saneamento,energia,portos,aeroportos,barragens",
        help="Segments to include (default: saneamento,energia,portos,aeroportos,barragens)"
    )
    parser.add_argument(
        "--output-dir",
        default="rag_evals",
        help="Output directory (default: rag_evals)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging"
    )
    return parser.parse_args()


def generate_golden_set(num_pairs: int, segments: List[str], seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate golden set of QA pairs from templates.
    """
    random.seed(seed)
    golden_set = []

    # Map segments to agent IDs
    segment_map = {
        "saneamento": "agente-saneamento",
        "energia": "agente-energia",
        "portos": "agente-portos",
        "aeroportos": "agente-aeroportos",
        "barragens": "agente-barragens"
    }

    qa_id = 1
    pairs_per_segment = max(1, num_pairs // len(segments))

    for segment in segments:
        if segment not in GOLDEN_SET_TEMPLATES:
            logger.warning(f"Unknown segment: {segment}, skipping")
            continue

        templates = GOLDEN_SET_TEMPLATES[segment]
        num_to_select = min(pairs_per_segment, len(templates))
        selected = random.sample(templates, num_to_select)

        for template in selected:
            if qa_id > num_pairs:
                break

            # Mock chunk IDs (in real scenario, would reference actual chunks in Supabase)
            chunk_ids = [f"chunk_{segment}_{i}" for i in range(1, 4)]

            qa_pair = {
                "qa_id": f"qa_{qa_id:03d}",
                "question": template["question"],
                "golden_answer": template["golden_answer"],
                "agent_id": segment_map.get(segment),
                "expected_chunks": chunk_ids,
                "difficulty_level": template["difficulty"],
                "source_domain": template["source_domain"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            golden_set.append(qa_pair)
            qa_id += 1

        if qa_id > num_pairs:
            break

    return golden_set[:num_pairs]


def output_csv(golden_set: List[Dict[str, Any]], output_path: Path):
    """Generate CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "qa_id", "question", "golden_answer", "agent_id", "expected_chunks",
                "difficulty_level", "source_domain", "created_at"
            ]
        )
        writer.writeheader()
        for qa in golden_set:
            row = qa.copy()
            row["expected_chunks"] = ";".join(row["expected_chunks"])
            writer.writerow(row)

    logger.info(f"CSV written to {output_path}")


def output_json(golden_set: List[Dict[str, Any]], output_path: Path):
    """Generate JSON schema file."""
    schema = {
        "version": "1.0.0",
        "name": "golden_set_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "num_qa_pairs": len(golden_set),
        "schema": {
            "qa_id": "string (qa_001, qa_002, ...)",
            "question": "string (human question for RAG)",
            "golden_answer": "string (expected correct answer)",
            "agent_id": "string (agente-saneamento, agente-energia, ...)",
            "expected_chunks": "array of strings (chunk IDs to retrieve)",
            "difficulty_level": "enum (easy, medium, hard)",
            "source_domain": "string (technical domain)",
            "created_at": "ISO8601 timestamp"
        },
        "qa_pairs": golden_set,
        "evaluation_metrics": {
            "recall_at_5": "fraction of QAs where golden chunk in top-5 results",
            "mrr": "Mean Reciprocal Rank (1 / avg position of best chunk)",
            "ndcg_5": "Normalized Discounted Cumulative Gain@5"
        }
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    logger.info(f"JSON schema written to {output_path}")


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(f"Generating golden set (num_pairs={args.num_pairs}, segments={args.segments})")

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Parse segments
        segments = [s.strip() for s in args.segments.split(",")]

        # Generate golden set
        golden_set = generate_golden_set(args.num_pairs, segments, seed=args.seed)

        logger.info(f"Generated {len(golden_set)} QA pairs")

        # Write outputs
        csv_path = output_dir / "golden_set_v1.csv"
        json_path = output_dir / "golden_set_schema.json"

        output_csv(golden_set, csv_path)
        output_json(golden_set, json_path)

        logger.info(f"Golden set initialized successfully")
        logger.info(f"  CSV: {csv_path}")
        logger.info(f"  Schema: {json_path}")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate golden set: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
