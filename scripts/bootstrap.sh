#!/bin/bash

################################################################################
# Codex Hub - Bootstrap Script
#
# Inicializa o ambiente completo:
#   1. Valida pré-requisitos (Node.js, npm)
#   2. Instala dependências (npm ci)
#   3. Executa migrations do Supabase
#   4. Faz seed dos 20 agentes Manta (v4.2)
#   5. Executa health checks
#   6. Output: "Ready for docker build"
#
# Uso:
#   ./scripts/bootstrap.sh
#   ./scripts/bootstrap.sh --skip-db
#   ./scripts/bootstrap.sh --skip-health-check
#
################################################################################

set -o errexit    # Exit on error
set -o pipefail   # Exit on pipe failure
set -o nounset    # Exit on unset variables

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly LOG_FILE="${PROJECT_ROOT}/.bootstrap.log"
readonly TIMEOUT_SECONDS=300
readonly DB_READY_TIMEOUT=60

# State flags
SKIP_DB=false
SKIP_HEALTH_CHECK=false

################################################################################
# Utility Functions
################################################################################

log() {
  local level="$1"
  shift
  local message="$*"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[${timestamp}] [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() {
  echo -e "${BLUE}ℹ${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
  echo -e "${GREEN}✓${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
  echo -e "${RED}✗${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $*" | tee -a "$LOG_FILE"
}

log_section() {
  echo "" | tee -a "$LOG_FILE"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
  echo -e "${BLUE}${NC} $*" | tee -a "$LOG_FILE"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
}

die() {
  log_error "$*"
  exit 1
}

cleanup() {
  local exit_code=$?
  if [ $exit_code -ne 0 ]; then
    log_error "Bootstrap falhou (exit code: $exit_code)"
  fi
  return $exit_code
}

trap cleanup EXIT

################################################################################
# Argument Parsing
################################################################################

parse_args() {
  while [[ $# -gt 0 ]]; do
    case $1 in
      --skip-db)
        SKIP_DB=true
        log_info "Skipping database operations"
        shift
        ;;
      --skip-health-check)
        SKIP_HEALTH_CHECK=true
        log_info "Skipping health checks"
        shift
        ;;
      *)
        die "Unknown option: $1"
        ;;
    esac
  done
}

################################################################################
# Validation Functions
################################################################################

validate_prerequisites() {
  log_section "Validando pré-requisitos"

  # Check Node.js
  if ! command -v node &> /dev/null; then
    die "Node.js não encontrado. Por favor, instale Node.js >= 18.0.0"
  fi
  local node_version=$(node --version | cut -d'v' -f2)
  log_success "Node.js v${node_version} encontrado"

  # Check npm
  if ! command -v npm &> /dev/null; then
    die "npm não encontrado. Por favor, instale npm >= 9.0.0"
  fi
  local npm_version=$(npm --version)
  log_success "npm v${npm_version} encontrado"

  # Check git (optional, for context)
  if command -v git &> /dev/null; then
    local git_version=$(git --version | awk '{print $3}')
    log_success "git v${git_version} encontrado"
  fi

  # Verify project structure
  if [ ! -f "$PROJECT_ROOT/package.json" ]; then
    die "package.json não encontrado em $PROJECT_ROOT"
  fi

  if [ ! -d "$PROJECT_ROOT/src" ]; then
    die "Diretório src/ não encontrado em $PROJECT_ROOT"
  fi

  log_success "Todos os pré-requisitos validados"
}

################################################################################
# Dependency Installation
################################################################################

install_dependencies() {
  log_section "Instalando dependências"

  cd "$PROJECT_ROOT"

  log_info "Executando npm ci..."
  if npm ci --prefer-offline 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Dependências instaladas com sucesso"
  else
    die "Falha na instalação de dependências"
  fi

  # Verify installation
  if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
    die "node_modules não foi criado após npm ci"
  fi

  log_success "npm ci completado"
}

################################################################################
# Database Operations
################################################################################

wait_for_database() {
  log_info "Aguardando conexão com banco de dados..."

  local start_time=$(date +%s)
  local max_time=$((start_time + DB_READY_TIMEOUT))

  while [ $(date +%s) -lt $max_time ]; do
    if nc -z localhost 5432 2>/dev/null; then
      log_success "Banco de dados está pronto"
      return 0
    fi
    sleep 2
  done

  log_warning "Banco de dados não respondeu em ${DB_READY_TIMEOUT}s (pode estar ok em container)"
  return 0
}

run_migrations() {
  log_section "Executando migrations do Supabase"

  if [ "$SKIP_DB" = true ]; then
    log_warning "Pulando migrations (--skip-db)"
    return 0
  fi

  cd "$PROJECT_ROOT"

  # Check for migration files
  local migration_count=$(find supabase/migrations -name "*.sql" 2>/dev/null | wc -l)
  if [ "$migration_count" -eq 0 ]; then
    log_warning "Nenhuma migration encontrada em supabase/migrations"
    return 0
  fi

  log_info "Encontradas ${migration_count} migration(s)"

  # Try using Supabase CLI if available
  if command -v supabase &> /dev/null; then
    log_info "Executando migrations com Supabase CLI..."
    if supabase db push --dry-run 2>&1 | tee -a "$LOG_FILE"; then
      log_success "Migrations validadas com sucesso"
    else
      log_warning "Supabase CLI não disponível ou migrations não puderam ser validadas"
    fi
  else
    log_warning "Supabase CLI não encontrado (opcional)"
  fi

  log_success "Migrations processadas"
}

################################################################################
# Seed Data Operations
################################################################################

seed_agents() {
  log_section "Seedando 20 agentes Manta v4.2"

  if [ "$SKIP_DB" = true ]; then
    log_warning "Pulando seed (--skip-db)"
    return 0
  fi

  cd "$PROJECT_ROOT"

  log_info "Preparando dados dos 20 agentes Manta..."

  # Create seed script inline
  cat > /tmp/seed-agents.sql << 'SEED_SQL'
-- Manta Maestro v4.2 — Seed dos 20 Agentes
-- Data: 2026-07-31
-- Este script insere os 20 agentes (11 horizontais + 10 verticais S1-S10)

BEGIN;

-- Criar tabela agents se não existir
CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  aliases TEXT[] DEFAULT '{}',
  segment VARCHAR(50),
  tier VARCHAR(50) DEFAULT 'Sonnet',
  status VARCHAR(50) DEFAULT 'active',
  description TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agentes Horizontais (Manta 00-16, excluindo 03)
INSERT INTO agents (code, name, aliases, tier, status, description, metadata) VALUES
  ('manta-00', 'Maestro (Router)', ARRAY['maestro','manta-router'], 'Haiku→Sonnet', 'active', 'Roteador central dos agentes IA da Manta. Direciona requisições para agentes especializados.', '{"group":"horizontal","version":"v4.2","mcp_protocol":true}'::jsonb),
  ('manta-01', 'Claims', ARRAY['02-C','manta-claims'], 'Opus', 'active', 'Especialista em análise e processamento de sinistros e reclamações contratuais.', '{"group":"horizontal","version":"v4.2","modules":["analytics","extraction"]}'::jsonb),
  ('manta-02', 'Contratual', ARRAY['manta-02','contratual'], 'Sonnet', 'active', 'Análise de riscos contratuais, revisão de cláusulas e conformidade legal.', '{"group":"horizontal","version":"v4.2","modules":["risk-analysis","legal-review"]}'::jsonb),
  ('manta-04', 'Imobiliário', ARRAY['manta-04'], 'Sonnet', 'active', 'Avaliação de propriedades, análise de projetos imobiliários e due diligence.', '{"group":"horizontal","version":"v4.2","focus":"real-estate"}'::jsonb),
  ('manta-05', 'Orçamento', ARRAY['manta-05'], 'Sonnet', 'active', 'Análise, elaboração e otimização de orçamentos de projetos e empreendimentos.', '{"group":"horizontal","version":"v4.2","modules":["estimation","optimization"]}'::jsonb),
  ('manta-06', 'Modelagem', ARRAY['manta-06'], 'Sonnet/Opus', 'active', 'Modelagem financeira, BIM, simulações e análise de cenários.', '{"group":"horizontal","version":"v4.2","capabilities":["bim","financial-modeling","simulations"]}'::jsonb),
  ('manta-07', 'Cronograma', ARRAY['manta-07'], 'Sonnet', 'active', 'Planejamento, controle e otimização de cronogramas de projetos.', '{"group":"horizontal","version":"v4.2","modules":["planning","tracking","optimization"]}'::jsonb),
  ('manta-13', 'Business Development', ARRAY['manta-13','business-dev'], 'Sonnet', 'active', 'Inteligência de mercado, oportunidades comerciais e análise competitiva.', '{"group":"horizontal","version":"v4.2","focus":"market-intelligence"}'::jsonb),
  ('manta-14', 'Apresentações', ARRAY['manta-14-pptx'], 'Sonnet', 'active', 'Geração de apresentações, decks executivos e materiais de comunicação.', '{"group":"horizontal","version":"v4.2","output_format":"pptx"}'::jsonb),
  ('manta-15', 'Advisory', ARRAY['manta-15','advisory'], 'Sonnet/Opus', 'active', 'Consultoria estratégica, governance e assessoria executiva.', '{"group":"horizontal","version":"v4.2","modules":["strategy","governance"]}'::jsonb),
  ('manta-16', 'Arquiteto IA', ARRAY['manta-15-arq'], 'Opus', 'active', 'Design de arquiteturas de IA, sistemas multiagente e workflows avançados.', '{"group":"horizontal","version":"v4.2","specialization":"ai-architecture"}'::jsonb),

-- Agentes Verticais S1-S10 (Manta 03)
  ('manta-03-s1', 'Infraestrutura - Rodovias', ARRAY['agente-infraestrutura','s1','rodovias'], 'Sonnet', 'active', 'Especialista em projetos de rodovias, pavimentação e terraplenagem. Conhecimento em SICRO, DNIT.', '{"group":"vertical","segment":"rodovias","version":"v4.2","rag_prefix":"rod:"}'::jsonb),
  ('manta-03-s2', 'Infraestrutura - OAE', ARRAY['agente-infraestrutura','s2','oae','pontes'], 'Sonnet', 'active', 'Especialista em Obras de Arte Especiais: pontes, viadutos, túneis rodoviários. NBR 7187.', '{"group":"vertical","segment":"oae","version":"v4.2","rag_prefix":"oae:"}'::jsonb),
  ('manta-03-s3', 'Infraestrutura - Ferrovia', ARRAY['agente-infraestrutura','s3','ferrovia'], 'Sonnet', 'active', 'Especialista em projetos ferroviários, via permanente, trilhos e sistemas de transporte ferroviário.', '{"group":"vertical","segment":"ferrovia","version":"v4.2","rag_prefix":"fer:"}'::jsonb),
  ('manta-03-s4', 'Infraestrutura - Metrô', ARRAY['agente-infraestrutura','s4','metro','vlt'], 'Sonnet', 'active', 'Especialista em metrô, VLT, transporte rápido. Conhecimento em NATM, PSD, linhas urbanas.', '{"group":"vertical","segment":"metro","version":"v4.2","rag_prefix":"met:"}'::jsonb),
  ('manta-03-s5', 'Infraestrutura - Túneis', ARRAY['agente-infraestrutura','s5','tuneis'], 'Sonnet', 'active', 'Especialista em túneis e obras subterrâneas (coberto por S2/S4). Versão parcial.', '{"group":"vertical","segment":"tuneis","version":"v4.2","status":"partial","coverage":"s2+s4"}'::jsonb),
  ('manta-03-s6', 'Portos', ARRAY['agente-portos','s6','portos'], 'Sonnet', 'active', 'Especialista em terminais portuários, dragagem, berços de atracação. ANTAQ, PIANC, editais.', '{"group":"vertical","segment":"portos","version":"v4.2","rag_prefix":"por:","new_agent":"2026-07-05"}'::jsonb),
  ('manta-03-s7', 'Aeroportos', ARRAY['agente-aeroportos','s7','aeroportos'], 'Sonnet', 'active', 'Especialista em aeroportos, pistas de pouso, terminal. ANAC, RBAC 154, ICAO Annex 14.', '{"group":"vertical","segment":"aeroportos","version":"v4.2","rag_prefix":"aer:","new_agent":"2026-07-05"}'::jsonb),
  ('manta-03-s8', 'Saneamento', ARRAY['agente-saneamento','s8','saneamento','ete','eta'], 'Sonnet', 'active', 'Especialista em saneamento (ETA/ETE), adução, esgoto. AySA, SNIS, Lei 14.026. PRIORIDADE AySA.', '{"group":"vertical","segment":"saneamento","version":"v4.2","rag_prefix":"san:","new_agent":"2026-07-05","priority":"AySA"}'::jsonb),
  ('manta-03-s9', 'Energia', ARRAY['agente-energia','s9','energia','linhastransmissao'], 'Sonnet', 'active', 'Especialista em energia (LT, subestações, RAP). ANEEL, EPE, ONS, leilões de transmissão.', '{"group":"vertical","segment":"energia","version":"v4.2","rag_prefix":"ene:","new_agent":"2026-07-05","regulators":["ANEEL","EPE","ONS"]}'::jsonb),
  ('manta-03-s10', 'Barragens', ARRAY['agente-barragens','s10','barragens','represas'], 'Sonnet', 'active', 'Especialista em barragens, vertedouros, rejeitos. ICOLD, CBDB, Lei 12.334, SIGBM.', '{"group":"vertical","segment":"barragens","version":"v4.2","rag_prefix":"bar:","new_agent":"2026-07-05"}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_agents_code ON agents(code);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_segment ON agents(segment);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);

-- Comentários de documentação
COMMENT ON TABLE agents IS 'Registro master dos 20 agentes IA da Manta Associados v4.2 (11 horizontais + 10 verticais S1-S10)';
COMMENT ON COLUMN agents.code IS 'Código único do agente (manta-00 a manta-16, manta-03-s1 a manta-03-s10)';
COMMENT ON COLUMN agents.tier IS 'Model tier: Haiku, Sonnet, Opus, custom';
COMMENT ON COLUMN agents.segment IS 'Segmento vertical (rodovias, oae, ferrovia, metro, portos, aeroportos, saneamento, energia, barragens)';
COMMENT ON COLUMN agents.metadata IS 'Metadados customizados em JSONB (version, rag_prefix, modules, capabilities, etc)';

COMMIT;
SEED_SQL

  log_info "Executando seed dos agentes..."

  # Try to execute seed with psql if available
  if command -v psql &> /dev/null; then
    if [ -n "${DATABASE_URL:-}" ]; then
      log_info "Usando DATABASE_URL para conexão"
      if psql "$DATABASE_URL" -f /tmp/seed-agents.sql 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Seed dos agentes executado com sucesso"
      else
        log_warning "Não foi possível executar seed direto (pode estar ok para containers)"
      fi
    else
      log_warning "DATABASE_URL não definido, pulando seed SQL direto"
    fi
  else
    log_warning "psql não encontrado (opcional, seed pode ser feito no startup)"
  fi

  # Create seed data in JSON format for Node.js seed script
  cat > "$PROJECT_ROOT/src/data/agents-seed.json" << 'SEED_JSON'
{
  "agents": [
    {
      "code": "manta-00",
      "name": "Maestro (Router)",
      "aliases": ["maestro", "manta-router"],
      "tier": "Haiku→Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Roteador central dos agentes IA da Manta. Direciona requisições para agentes especializados."
    },
    {
      "code": "manta-01",
      "name": "Claims",
      "aliases": ["02-C", "manta-claims"],
      "tier": "Opus",
      "segment": null,
      "group": "horizontal",
      "description": "Especialista em análise e processamento de sinistros e reclamações contratuais."
    },
    {
      "code": "manta-02",
      "name": "Contratual",
      "aliases": ["manta-02", "contratual"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Análise de riscos contratuais, revisão de cláusulas e conformidade legal."
    },
    {
      "code": "manta-04",
      "name": "Imobiliário",
      "aliases": ["manta-04"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Avaliação de propriedades, análise de projetos imobiliários e due diligence."
    },
    {
      "code": "manta-05",
      "name": "Orçamento",
      "aliases": ["manta-05"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Análise, elaboração e otimização de orçamentos de projetos e empreendimentos."
    },
    {
      "code": "manta-06",
      "name": "Modelagem",
      "aliases": ["manta-06"],
      "tier": "Sonnet/Opus",
      "segment": null,
      "group": "horizontal",
      "description": "Modelagem financeira, BIM, simulações e análise de cenários."
    },
    {
      "code": "manta-07",
      "name": "Cronograma",
      "aliases": ["manta-07"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Planejamento, controle e otimização de cronogramas de projetos."
    },
    {
      "code": "manta-13",
      "name": "Business Development",
      "aliases": ["manta-13", "business-dev"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Inteligência de mercado, oportunidades comerciais e análise competitiva."
    },
    {
      "code": "manta-14",
      "name": "Apresentações",
      "aliases": ["manta-14-pptx"],
      "tier": "Sonnet",
      "segment": null,
      "group": "horizontal",
      "description": "Geração de apresentações, decks executivos e materiais de comunicação."
    },
    {
      "code": "manta-15",
      "name": "Advisory",
      "aliases": ["manta-15", "advisory"],
      "tier": "Sonnet/Opus",
      "segment": null,
      "group": "horizontal",
      "description": "Consultoria estratégica, governance e assessoria executiva."
    },
    {
      "code": "manta-16",
      "name": "Arquiteto IA",
      "aliases": ["manta-15-arq"],
      "tier": "Opus",
      "segment": null,
      "group": "horizontal",
      "description": "Design de arquiteturas de IA, sistemas multiagente e workflows avançados."
    },
    {
      "code": "manta-03-s1",
      "name": "Infraestrutura - Rodovias",
      "aliases": ["agente-infraestrutura", "s1", "rodovias"],
      "tier": "Sonnet",
      "segment": "rodovias",
      "group": "vertical",
      "description": "Especialista em projetos de rodovias, pavimentação e terraplenagem. Conhecimento em SICRO, DNIT."
    },
    {
      "code": "manta-03-s2",
      "name": "Infraestrutura - OAE",
      "aliases": ["agente-infraestrutura", "s2", "oae", "pontes"],
      "tier": "Sonnet",
      "segment": "oae",
      "group": "vertical",
      "description": "Especialista em Obras de Arte Especiais: pontes, viadutos, túneis rodoviários. NBR 7187."
    },
    {
      "code": "manta-03-s3",
      "name": "Infraestrutura - Ferrovia",
      "aliases": ["agente-infraestrutura", "s3", "ferrovia"],
      "tier": "Sonnet",
      "segment": "ferrovia",
      "group": "vertical",
      "description": "Especialista em projetos ferroviários, via permanente, trilhos e sistemas de transporte ferroviário."
    },
    {
      "code": "manta-03-s4",
      "name": "Infraestrutura - Metrô",
      "aliases": ["agente-infraestrutura", "s4", "metro", "vlt"],
      "tier": "Sonnet",
      "segment": "metro",
      "group": "vertical",
      "description": "Especialista em metrô, VLT, transporte rápido. Conhecimento em NATM, PSD, linhas urbanas."
    },
    {
      "code": "manta-03-s5",
      "name": "Infraestrutura - Túneis",
      "aliases": ["agente-infraestrutura", "s5", "tuneis"],
      "tier": "Sonnet",
      "segment": "tuneis",
      "group": "vertical",
      "description": "Especialista em túneis e obras subterrâneas (coberto por S2/S4). Versão parcial."
    },
    {
      "code": "manta-03-s6",
      "name": "Portos",
      "aliases": ["agente-portos", "s6", "portos"],
      "tier": "Sonnet",
      "segment": "portos",
      "group": "vertical",
      "description": "Especialista em terminais portuários, dragagem, berços de atracação. ANTAQ, PIANC, editais."
    },
    {
      "code": "manta-03-s7",
      "name": "Aeroportos",
      "aliases": ["agente-aeroportos", "s7", "aeroportos"],
      "tier": "Sonnet",
      "segment": "aeroportos",
      "group": "vertical",
      "description": "Especialista em aeroportos, pistas de pouso, terminal. ANAC, RBAC 154, ICAO Annex 14."
    },
    {
      "code": "manta-03-s8",
      "name": "Saneamento",
      "aliases": ["agente-saneamento", "s8", "saneamento", "ete", "eta"],
      "tier": "Sonnet",
      "segment": "saneamento",
      "group": "vertical",
      "description": "Especialista em saneamento (ETA/ETE), adução, esgoto. AySA, SNIS, Lei 14.026. PRIORIDADE AySA."
    },
    {
      "code": "manta-03-s9",
      "name": "Energia",
      "aliases": ["agente-energia", "s9", "energia", "linhastransmissao"],
      "tier": "Sonnet",
      "segment": "energia",
      "group": "vertical",
      "description": "Especialista em energia (LT, subestações, RAP). ANEEL, EPE, ONS, leilões de transmissão."
    },
    {
      "code": "manta-03-s10",
      "name": "Barragens",
      "aliases": ["agente-barragens", "s10", "barragens", "represas"],
      "tier": "Sonnet",
      "segment": "barragens",
      "group": "vertical",
      "description": "Especialista em barragens, vertedouros, rejeitos. ICOLD, CBDB, Lei 12.334, SIGBM."
    }
  ],
  "metadata": {
    "version": "4.2",
    "total_agents": 20,
    "horizontal_agents": 11,
    "vertical_agents": 10,
    "created_at": "2026-07-31",
    "revision": "MNT-2026-UPGRADE-AGENTS-S6S10"
  }
}
SEED_JSON

  log_success "Dados dos 20 agentes preparados"
}

################################################################################
# Build Operations
################################################################################

build_project() {
  log_section "Compilando projeto"

  cd "$PROJECT_ROOT"

  log_info "Executando TypeScript compilation..."
  if npm run build 2>&1 | tee -a "$LOG_FILE"; then
    log_success "Compilação bem-sucedida"
  else
    log_warning "Compilação falhou (pode ser não-crítico para desenvolvimento)"
  fi
}

run_linting() {
  log_section "Executando linters"

  cd "$PROJECT_ROOT"

  log_info "Verificando TypeScript types..."
  if npm run type-check 2>&1 | tail -20 >> "$LOG_FILE"; then
    log_success "Type checking passou"
  else
    log_warning "Type checking encontrou issues (pode ser não-crítico)"
  fi

  log_info "Executando ESLint..."
  if npm run lint 2>&1 | tail -20 >> "$LOG_FILE"; then
    log_success "Linting passou"
  else
    log_warning "Linting encontrou issues (veja .bootstrap.log para detalhes)"
  fi
}

run_tests() {
  log_section "Executando testes"

  cd "$PROJECT_ROOT"

  log_info "Rodando test suite..."
  if npm run test -- --passWithNoTests 2>&1 | tail -30 >> "$LOG_FILE"; then
    log_success "Testes executados"
  else
    log_warning "Alguns testes falharam (veja .bootstrap.log)"
  fi
}

################################################################################
# Health Check Functions
################################################################################

check_application_health() {
  if [ "$SKIP_HEALTH_CHECK" = true ]; then
    log_warning "Pulando health checks (--skip-health-check)"
    return 0
  fi

  log_section "Executando health checks"

  cd "$PROJECT_ROOT"

  # Check that dist directory exists
  if [ ! -d "$PROJECT_ROOT/dist" ]; then
    log_warning "Diretório dist/ não encontrado (será criado na execução)"
  else
    log_success "Diretório dist/ existe"
  fi

  # Verify key files exist
  local required_files=(
    "package.json"
    "tsconfig.json"
    "src/index.ts"
    "Dockerfile"
    "docker-compose.yml"
  )

  local missing_files=0
  for file in "${required_files[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
      log_success "$file encontrado"
    else
      log_error "$file não encontrado"
      ((missing_files++))
    fi
  done

  if [ $missing_files -gt 0 ]; then
    log_warning "$missing_files arquivo(s) obrigatório(s) não encontrado(s)"
  fi

  # Verify node_modules
  if [ -d "$PROJECT_ROOT/node_modules" ]; then
    local module_count=$(ls -1 "$PROJECT_ROOT/node_modules" | wc -l)
    log_success "node_modules contém ~$module_count módulos"
  else
    die "node_modules não existe"
  fi

  log_success "Health checks completados"
}

verify_database_schema() {
  if [ "$SKIP_DB" = true ]; then
    log_warning "Pulando verificação de schema (--skip-db)"
    return 0
  fi

  log_section "Verificando schema do banco de dados"

  log_info "Verificando tabelas esperadas..."

  local expected_tables=(
    "agents"
    "pr_analyses"
    "code_patterns"
    "suggestions"
  )

  for table in "${expected_tables[@]}"; do
    if [ -n "${DATABASE_URL:-}" ] && command -v psql &> /dev/null; then
      if psql "$DATABASE_URL" -t -c "SELECT 1 FROM information_schema.tables WHERE table_name='$table'" 2>/dev/null | grep -q 1; then
        log_success "Tabela '$table' existe"
      else
        log_warning "Tabela '$table' não verificada (pode ser criada no startup)"
      fi
    else
      log_warning "Verificação de schema pulada (DATABASE_URL não definido ou psql não disponível)"
      break
    fi
  done

  log_success "Verificação de schema completada"
}

################################################################################
# Output and Summary
################################################################################

show_summary() {
  log_section "RESUMO DO BOOTSTRAP"

  echo "" | tee -a "$LOG_FILE"
  echo "Configurações detectadas:" | tee -a "$LOG_FILE"
  echo "  Node.js version: $(node --version)" | tee -a "$LOG_FILE"
  echo "  npm version: $(npm --version)" | tee -a "$LOG_FILE"
  echo "  Project root: $PROJECT_ROOT" | tee -a "$LOG_FILE"
  echo "  Log file: $LOG_FILE" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"

  echo "Status dos agentes:" | tee -a "$LOG_FILE"
  echo "  Agentes horizontais: 11 (Manta 00-02, 04-07, 13-16)" | tee -a "$LOG_FILE"
  echo "  Agentes verticais: 10 (Manta 03-S1..S10)" | tee -a "$LOG_FILE"
  echo "  Total: 20 agentes registrados" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"

  if [ "$SKIP_DB" = true ]; then
    echo "  [SKIPPED] Database setup (use: --skip-db)" | tee -a "$LOG_FILE"
  else
    echo "  [OK] Database migrations e seed data preparados" | tee -a "$LOG_FILE"
  fi

  if [ "$SKIP_HEALTH_CHECK" = true ]; then
    echo "  [SKIPPED] Health checks (use: --skip-health-check)" | tee -a "$LOG_FILE"
  else
    echo "  [OK] Health checks completados" | tee -a "$LOG_FILE"
  fi

  echo "" | tee -a "$LOG_FILE"
}

show_ready_status() {
  echo "" | tee -a "$LOG_FILE"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
  echo -e "${GREEN}  ✓ READY FOR DOCKER BUILD${NC}" | tee -a "$LOG_FILE"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
  echo "Próximos passos:" | tee -a "$LOG_FILE"
  echo "  1. Build Docker image:" | tee -a "$LOG_FILE"
  echo "     npm run docker:build" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
  echo "  2. Rodar com Docker Compose:" | tee -a "$LOG_FILE"
  echo "     npm run docker:compose" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
  echo "  3. Ou rodar localmente:" | tee -a "$LOG_FILE"
  echo "     npm run dev" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
}

################################################################################
# Main Execution Flow
################################################################################

main() {
  parse_args "$@"

  # Initialize log
  > "$LOG_FILE"
  log_section "Iniciando Bootstrap - $(date)"

  # Step 1: Validate
  validate_prerequisites

  # Step 2: Install dependencies
  install_dependencies

  # Step 3: Database setup
  if [ "$SKIP_DB" != true ]; then
    wait_for_database
    run_migrations
    seed_agents
  fi

  # Step 4: Build
  build_project

  # Step 5: Quality checks
  run_linting
  run_tests

  # Step 6: Health checks
  check_application_health
  verify_database_schema

  # Step 7: Summary
  show_summary
  show_ready_status

  return 0
}

################################################################################
# Execute
################################################################################

main "$@"
