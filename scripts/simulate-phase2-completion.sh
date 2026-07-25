#!/bin/bash

# ============================================================================
# SIMULATE-PHASE2-COMPLETION.SH
# Creates realistic test documents to simulate Phase 2 completion
# Useful for testing Phase 3 pipeline without manual downloads
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOC_DIR="${PROJECT_ROOT}/data/rag-docs"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $@"; }
log_success() { echo -e "${GREEN}✓${NC} $@"; }

# ============================================================================
# CREATE REALISTIC TEST DOCUMENTS
# ============================================================================

create_saneamento_docs() {
    log_info "Creating Saneamento documents (200 target)..."
    
    local count=0
    
    # Federal law
    cat > "${DOC_DIR}/san/lei-14026-2020.txt" <<'DOC'
# LEI Nº 14.026, DE 26 DE JULHO DE 2020
## Atualiza o marco legal do saneamento básico

### Capítulo I - Disposições Gerais
A política federal de saneamento básico tem como objetivo garantir o acesso
de todos os domicílios ocupados a serviços de água potável, coleta e tratamento
de esgoto sanitário, limpeza urbana, coleta e destinação final de resíduos sólidos.

### Capítulo II - Estação de Tratamento de Água (ETA)
A ETA deve estar localizada em ponto que permita gravitação da água tratada
e facilite o recebimento de água bruta. O projeto deve considerar:

1. Vazão de projeto (L/s)
2. Qualidade da água bruta
3. Tecnologia de tratamento
4. Requisitos de operação e manutenção
5. Acessibilidade para limpeza e manutenção

### Capítulo III - Estação de Tratamento de Esgoto (ETE)
A ETE deve ser localizada em terreno apropriado que permita:
- Operação eficiente
- Segurança de trabalhadores
- Conformidade ambiental
- Acesso facilitado para manutenção

### Capítulo IV - Requisitos de Qualidade
Todos os sistemas devem atender aos padrões estabelecidos pela ABNT
e pelas normas técnicas aplicáveis.
DOC
    ((count++))
    
    # SNIS documents
    for i in {1..10}; do
        cat > "${DOC_DIR}/san/snis-report-$(printf "%03d" $i).txt" <<'DOC'
# SNIS - SISTEMA NACIONAL DE INFORMAÇÕES EM SANEAMENTO
## Relatório Anual de Diagnóstico

### Seção 1: Indicadores de Cobertura
- Cobertura de água (urbana): 94.2%
- Cobertura de esgoto (urbana): 71.3%
- Atendimento adequado: 64.5%

### Seção 2: Qualidade dos Serviços
- Conformidade de cloro residual: 98.5%
- Perdas na distribuição: 28.7%
- Inadimplência de clientes: 15.2%

### Seção 3: Eficiência Operacional
- Índice de consumo de água: 145 L/hab/dia
- Custo da água produzida: R$ 2.15/m³
- Despesa com pessoal: 35% da receita operacional
DOC
        ((count++))
    done
    
    # BNDES documents
    for i in {1..15}; do
        cat > "${DOC_DIR}/san/bndes-manual-$(printf "%03d" $i).txt" <<'DOC'
# BNDES - BANCO NACIONAL DE DESENVOLVIMENTO ECONÔMICO E SOCIAL
## Manual de Viabilidade de Projetos de Saneamento

### Parte 1: Pré-Dimensionamento
A população de projeto deve ser estimada considerando:
1. Taxa de crescimento demográfico
2. Horizonte de projeto (20-25 anos)
3. Densidade populacional
4. Dinâmica de ocupação do solo

### Parte 2: Seleção de Tecnologia
Critérios para escolha de tecnologia:
- Adequação à qualidade da água bruta
- Requisitos de confiabilidade
- Capacidade de operação local
- Custo de implantação e operação
- Impactos ambientais

### Parte 3: Projeto Básico
O projeto básico deve incluir:
- Plantas e cortes (escala 1:100)
- Especificações técnicas
- Cronograma físico
- Orçamento detalhado
- Análise de viabilidade econômico-financeira
DOC
        ((count++))
    done
    
    echo "$count"
}

create_energia_docs() {
    log_info "Creating Energia documents (300 target)..."
    
    local count=0
    
    # Federal law
    cat > "${DOC_DIR}/ene/lei-9074-1995.txt" <<'DOC'
# LEI Nº 9.074, DE 7 DE JULHO DE 1995
## Estabelece normas para outorga e prorrogação de concessões de energia

### Artigo 1º
Fica estabelecida a política de concessão de exploração de energia elétrica,
com o objetivo de incrementar o aumento de oferta de energia ao mercado
e a competitividade dos preços.

### Artigo 2º - Linhas de Transmissão
As linhas de transmissão de energia elétrica devem ser projetadas de acordo
com as normas técnicas estabelecidas pela ABNT e pelas regulações da ANEEL.

### Especificações Técnicas:
1. Tensão nominal (kV): 138, 230, 345, 500, 600
2. Frequência: 60 Hz
3. Impedância característica: 400 ohms (típico)
4. Suportabilidade: Conforme IEC 60826

### Artigo 3º - Subestações
As subestações devem incluir equipamentos para:
- Transformação de tensão
- Proteção de circuitos
- Medição de energia
- Controle de frequência
DOC
    ((count++))
    
    # ANEEL documents
    for i in {1..40}; do
        cat > "${DOC_DIR}/ene/aneel-resolucao-$(printf "%03d" $i).txt" <<'DOC'
# ANEEL - AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA
## Resolução Normativa

### Objetivo
Regulamentar aspectos técnicos e operacionais de linhas de transmissão
de energia elétrica.

### Seção 1: Classificação
- Linhas de tensão extra alta (EAT): > 230 kV
- Linhas de alta tensão (AT): 69 kV a 230 kV
- Linhas de média tensão (MT): 1 kV a 69 kV

### Seção 2: Requisitos de Projeto
1. Margem de estabilidade transitória
2. Taxa de amortecimento de oscilações
3. Tempo máximo de eliminação de falta (150-200 ms)
4. Capacidade de transmissão reserva

### Seção 3: Operação e Manutenção
- Inspeções periódicas: anual ou conforme recomendado
- Testes de disjuntores: a cada 2 anos
- Manutenção preventiva: programa anual
DOC
        ((count++))
    done
    
    # EPE documents
    for i in {1..30}; do
        cat > "${DOC_DIR}/ene/epe-pde-relatorio-$(printf "%03d" $i).txt" <<'DOC'
# EPE - EMPRESA DE PESQUISA ENERGÉTICA
## Plano Decenal de Expansão de Energia

### Cenários de Demanda
- Conservador: crescimento 2.0% a.a.
- Referência: crescimento 2.5% a.a.
- Otimista: crescimento 3.5% a.a.

### Matriz Energética Brasileira
- Hidroeletricidade: 64%
- Termeletricidade: 18%
- Eólica: 11%
- Solar: 4%
- Outras: 3%

### Investimentos Previstos
- Geração: R$ 80 bilhões
- Transmissão: R$ 25 bilhões
- Distribuição: R$ 40 bilhões

### Metas de Eficiência
- Redução de perdas técnicas: 7.5%
- Redução de consumo: 5% em 10 anos
- Aumento de geração renovável: 50%
DOC
        ((count++))
    done
    
    echo "$count"
}

create_portos_docs() {
    log_info "Creating Portos documents (150 target)..."
    
    local count=0
    
    cat > "${DOC_DIR}/por/lei-12815-2013.txt" <<'DOC'
# LEI Nº 12.815, DE 5 DE JUNHO DE 2013
## Autoridade Portuária Nacional

### Capítulo I - Disposições Preliminares
Estabelece a organização, o funcionamento e a exploração da infraestrutura
portuária e das instalações de interesse público.

### Capítulo II - Porto Organizado
Porto organizado é aquele construído e aparelhado com equipamentos e
instalações de uso público, explorado pela administração pública ou privada.

### Seção 1: Características Técnicas
- Calado natural: mínimo 5m
- Bacia de evolução: adequada para manobras
- Cais: comprimento e altura conforme navios esperados
- Infraestrutura: energia, água, esgotos

### Seção 2: Terminais Especializados
- Terminal de contêineres: 300-1000 TEU/navio
- Terminal de carga geral: 5000-20000 toneladas
- Terminal de granéis líquidos: 30000+ toneladas
- Terminal de granéis sólidos: 50000+ toneladas

### Seção 3: Operação
- Horário de operação: 24 horas, 6 dias/semana (mínimo)
- Produtividade: movimentos/hora conforme tipo de carga
- Segurança: conforme ISPS e regulamentações IMO
DOC
    ((count++))
    
    for i in {1..60}; do
        cat > "${DOC_DIR}/por/antaq-regulacao-$(printf "%03d" $i).txt" <<'DOC'
# ANTAQ - AGÊNCIA NACIONAL DE TRANSPORTES AQUAVIÁRIOS
## Normas para Operação de Terminais

### Capitulo 1: Segurança Portuária
1. Identificação de riscos
2. Plano de segurança operacional
3. Treinamento de pessoal
4. Equipamentos de proteção obrigatórios

### Capitulo 2: Controle de Carga
- Conferência de manifesto
- Inspeção de saúde
- Verificação de documentação
- Armazenagem conforme regulamentação

### Capitulo 3: Tarifas e Cobranças
- Taxa de utilização de instalações
- Despachante aduaneiro: mínimo 1
- Armazenagem: primeira 14 dias gratuitos
- Demurrage: conforme tabela estabelecida
DOC
        ((count++))
    done
    
    echo "$count"
}

create_aeroportos_docs() {
    log_info "Creating Aeroportos documents (120 target)..."
    
    local count=0
    
    cat > "${DOC_DIR}/aer/lei-13182-2015.txt" <<'DOC'
# LEI Nº 13.182, DE 13 DE NOVEMBRO DE 2015
## Dispõe sobre concessão de aeroportos brasileiros

### Capítulo I - Definições
Pista: superfície preparada para decolagem e pouso de aeronaves
Taxiway: via de circulação de aeronaves no solo
TPS: Terminal de Passageiros
TECA: Terminal de Cargas

### Capítulo II - Padrões de Projeto
A pista deve atender aos padrões ICAO Annex 14:
- Comprimento mínimo: 2000m (operações domésticas)
- Largura: 45m (código 4)
- Pavimento: CBUQ ou concreto rígido
- Declividade: máximo 1.5%

### Seção 1: Pista de Pouso
Especificações:
- Resistência estrutural: CBR 15 (mínimo)
- Drenagem subsuperficial: conforme projeto
- Sinalização: conforme ICAO
- Iluminação noturna: obrigatória em aeroportos 24h

### Seção 2: Terminal de Passageiros
Requisitos:
- Capacidade: 5000-50000 pax/dia (conforme categoria)
- Pé direito: mínimo 4.5m em saguões
- Estacionamento: 500-5000 vagas
- Acesso: viário e ferroviário (quando possível)
DOC
    ((count++))
    
    for i in {1..50}; do
        cat > "${DOC_DIR}/aer/anac-rbac-$(printf "%03d" $i).txt" <<'DOC'
# ANAC - AGÊNCIA NACIONAL DE AVIAÇÃO CIVIL
## Regulamento Brasileiro de Aviação Civil (RBAC)

### Parte 1: Certificação de Aeródromo
1. Operação em condições IFR (Voo por Instrumento)
2. Operação em condições VFR (Voo Visual)
3. Requisitos de pessoal
4. Programa de manutenção

### Parte 2: Segurança Operacional
- Acesso restrito à área de manobra
- Procedimentos de emergência
- Plano de segurança aeroportuária (PSA)
- Capacitação contínua de pessoal

### Parte 3: Infraestrutura
- Pavimentos: resistência estrutural conforme projeto
- Serviços de navegação: VOR, ILS, NDB
- Comunicações: frequências padronizadas
- Meteorologia: estação própria ou parceria

### Parte 4: Operação Comercial
- Slots de decolagem/pouso
- Taxas aeroportuárias
- Serviços de apoio (handling, catering)
- Controle de tráfego aéreo
DOC
        ((count++))
    done
    
    echo "$count"
}

create_barragens_docs() {
    log_info "Creating Barragens documents (180 target)..."
    
    local count=0
    
    cat > "${DOC_DIR}/bar/lei-12334-2010.txt" <<'DOC'
# LEI Nº 12.334, DE 20 DE SETEMBRO DE 2010
## Estabelece a Política Nacional de Segurança de Barragens (PNSB)

### Capítulo I - Disposições Gerais
A PNSB tem por objetivos:
1. Garantir a observância de padrões de segurança
2. Promover benefícios socioeconômicos
3. Proteger o meio ambiente
4. Maximizar a eficiência de aproveitamento

### Capítulo II - Classificação de Barragens
Por altura:
- Pequena: h < 15m
- Média: 15m ≤ h < 60m
- Grande: h ≥ 60m

Por material:
- Concreto (CCV, CCR, CFRD)
- Terra
- Enrocamento
- Rejeitos (TSF, Dry Stack)

### Seção 1: Projeto de Barragem de Concreto
Requisitos:
- Estudos geológicos: profundidade 3x altura mínima
- Análise de estabilidade: FOS ≥ 1.5
- Drenagem interna: função do plano de fraturamento
- Instrumentação: piezômetros, extensômetros

### Seção 2: Projeto de Barragem de Terra
Requisitos:
- Núcleo impermeável: k ≤ 10⁻⁷ cm/s
- Filtro de transição: conforme critério de Terzaghi
- Drenagem: pé da barragem (sistema de drenagem)
- Vertedor: capacidade para PMF

### Seção 3: Barragens de Rejeitos
Requisitos especiais:
- Altura máxima recomendada: conforme método construtivo
- Phreatic line control: fundamental
- Linha de carga: monitoria contínua
- Estabilidade dinâmica: análise de liquefação
DOC
    ((count++))
    
    for i in {1..80}; do
        cat > "${DOC_DIR}/bar/icold-guideline-$(printf "%03d" $i).txt" <<'DOC'
# ICOLD - INTERNATIONAL COMMISSION ON LARGE DAMS
## Design Guidelines for Small and Medium Dams

### Section 1: Planning Phase
1. Hydrological studies
   - Precipitation data (30+ years)
   - Runoff analysis
   - Flood routing

2. Geological studies
   - Foundation mapping
   - Rock classification
   - Joint system analysis

3. Environmental assessment
   - Flora and fauna
   - Water quality
   - Cultural heritage

### Section 2: Design Standards
- Safety factor for sliding: minimum 1.5 (static), 1.1 (pseudo-static)
- Foundation preparation: removal of weathered rock (min 1m)
- Spillway capacity: design flood (100-500 years)
- Freeboard: minimum 1.5m + wave run-up

### Section 3: Construction Quality Control
1. Earthwork compaction: 95% SPD
2. Concrete strength: f'c ≥ 30 MPa (mínimo)
3. Instrumentation: pressure cells, inclinometers
4. Quality assurance: independent inspection

### Section 4: Monitoring and Maintenance
- Piezometric monitoring: monthly or continuous
- Visual inspections: quarterly
- Geotechnical surveys: every 5 years
- Maintenance program: preventive and corrective
DOC
        ((count++))
    done
    
    echo "$count"
}

# ============================================================================
# MAIN
# ============================================================================

mkdir -p "${DOC_DIR}"/{san,ene,por,aer,bar}

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║ SIMULATING PHASE 2 COMPLETION                          ║"
echo "║ Creating realistic test documents (950 total)          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

san_count=$(create_saneamento_docs)
ene_count=$(create_energia_docs)
por_count=$(create_portos_docs)
aer_count=$(create_aeroportos_docs)
bar_count=$(create_barragens_docs)

total=$((san_count + ene_count + por_count + aer_count + bar_count))

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║ SIMULATION COMPLETE                                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Documents created:"
echo "  san: $san_count / 200"
echo "  ene: $ene_count / 300"
echo "  por: $por_count / 150"
echo "  aer: $aer_count / 120"
echo "  bar: $bar_count / 180"
echo ""
echo "TOTAL: $total / 950"
echo ""
echo "Next: Test RAG extraction"
echo "  export DRY_RUN=true"
echo "  bash scripts/extract-and-populate-rag.sh"
echo ""
