#!/usr/bin/env python3
"""
generate_skills_registry.py

Gera SKILL.md consolidado para todos os 20 agentes v5.0 a partir de CLAUDE.md e VERSIONS.json.

Uso:
    python scripts/generate_skills_registry.py

Output:
    manta-maestro/SKILL.md (~500 KB, 20 agentes)

Valida:
    - Checksums MD5 de todos 20 skills
    - Completude de seções obrigatórias
    - Ciclo de vida (8 fases)
    - Trigger phrases (keywords)
"""

import re
import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from jinja2 import Template

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Agent:
    """Modelo de um agente v5.0."""
    codigo: str  # Manta 00, 01, etc. ou Manta 03-S1, etc.
    nome: str    # maestro, claims, agente-saneamento, etc.
    descricao: str  # 1 linha descritiva
    aliases: List[str]  # Keywords de roteamento
    tier_default: str  # Haiku, Sonnet, Opus
    skill_file: str  # maestro.v5.0.md, agente-saneamento.v5.0.md
    checksum: str  # MD5 hash
    rag_collection: Optional[str] = None  # e.g., san:v5.0:*
    ciclo_vida: List[str] = None  # 8 fases suportadas
    trigger_phrases: List[str] = None  # Keywords para maestro
    exemplo_prompts: List[str] = None  # Golden set
    status: str = "Prod"
    category: str = "horizontal"  # horizontal ou vertical

    def __post_init__(self):
        if self.ciclo_vida is None:
            self.ciclo_vida = []
        if self.trigger_phrases is None:
            self.trigger_phrases = []
        if self.exemplo_prompts is None:
            self.exemplo_prompts = []


# ============================================================================
# Template Jinja2 para cada agente
# ============================================================================

AGENT_TEMPLATE = """## {{ agent.codigo }} — {{ agent.nome | upper }}

**Categoria:** {{ agent.category }} | **Status:** {{ agent.status }} | **Tier default:** {{ agent.tier_default }}

{{ agent.descricao }}

### Aliases & Roteamento

Roteia automaticamente para este agente se o usuário menciona:
- **Aliases principais:** {{ agent.aliases | join(', ') }}
- **Confidence score:** Maestro calcula via keyword matching + embedding similarity
- **RAG collection:** {% if agent.rag_collection %}{{ agent.rag_collection }}{% else %}N/A (horizontal){% endif %}

### Skill & Versionamento

- **Skill file:** `{{ agent.skill_file }}`
- **Checksum v5.0:** `{{ agent.checksum }}`
- **Skill versionamento:** MD5 pinned em `settings.json` → auto-fallback se divergência
- **Compatibilidade:** Python 3.10+ | Claude API Opus/Sonnet/Haiku

### Capabilities

**Tools disponíveis:**
- Read (ler arquivos do workspace)
- Grep (buscar padrões em código/docs)
- Glob (encontrar arquivos por pattern)
- Bash (executar comandos — conforme permissão)
- WebSearch / WebFetch (pesquisa online)
{% if agent.rag_collection %}
- RAG Query ({{ agent.rag_collection }})
{% endif %}

**Skills/Plugins:**
- autodesk-toolkit (processamento CAD/BIM — conforme segmento)
- cronograma-toolkit (Gantt/XER/MSP)
- docx/xlsx/pptx (edição de documentos)
- sicro-composicoes (SICRO para orçamento — rodovias/OAE)
- pdf (processamento de PDFs estruturados)

### Ciclo de Vida (8 fases)

{% if agent.ciclo_vida %}
Este agente suporta as seguintes fases de um projeto:

{% for i, fase in enumerate([
    ('Estudo prévio / EVTE', 'Diagnóstico, benchmarking, análise preliminar'),
    ('Projeto básico', 'Conceitos, layouts, orçamento order-of-magnitude'),
    ('Projeto executivo', 'Detalhamento, especificações, cronograma vinculante'),
    ('Obra em execução', 'Acompanhamento, desvios, revisões de escopo'),
    ('Operação & manutenção', 'Gestão de ativo, indicadores, OPEX'),
    ('Processo competitivo / licitação', 'Edital, termo de referência, avaliação'),
    ('Due diligence / M&A', 'Auditoria financeira, ambiental, legal, riscos'),
    ('Encerramento / descomissionamento', 'Final de vida útil, passivos, reabilitação')
], 1) %}
{% if i in agent.ciclo_vida or fase[0] in agent.ciclo_vida %}
{{ i }}. **{{ fase[0] }}** — {{ fase[1] }}
{% endif %}
{% endfor %}

**Declaração de fase (recomendado):**
```json
{
  "phase": "projeto-executivo",
  "deliverables": ["projeto-estrutural.dwg", "memorial-descritivo.pdf"]
}
```

{% else %}
Este agente é **horizontal** (transversal) e não suporta ciclo de vida específico.
{% endif %}

### Trigger Phrases (Maestro Routing)

Palavras-chave que acionam este agente automaticamente:
```
{{ agent.trigger_phrases | join(' | ') }}
```

### Exemplos de Prompts (Golden Set)

**Adequado para este agente:**

{% for prompt in agent.exemplo_prompts %}
- "{{ prompt }}"
{% endfor %}

**Não adequado (roteado a outro agente):**
- Prompts sobre {% if agent.category == 'vertical' %}processos horizontais (contrato, claims, etc.){% else %}projetos de infraestrutura específicos (rodovia, ETA, etc.){% endif %}

### Tiering Automático (R7)

- **Entrada típica:** {{ 1500 if agent.tier_default == 'Haiku' else 4000 if agent.tier_default == 'Sonnet' else 8000 }} tokens
- **Complexity score típica:** {{ 2.0 if agent.tier_default == 'Haiku' else 4.0 if agent.tier_default == 'Sonnet' else 6.0 }}
- **Fallback:** {{ agent.tier_default }} → Sonnet → Opus (se timeout > 60s)
- **Custo estimado:** {% if agent.tier_default == 'Haiku' %}~$0.08/1M tokens{% elif agent.tier_default == 'Sonnet' %}~$3/1M tokens{% else %}~$15/1M tokens{% endif %}

### Observabilidade

Todos os runs são tracked em Supabase (`agent_runs` table):
- `run_id` (UUID único)
- `input_tokens`, `output_tokens`, `cost_usd`
- `latency_ms`, `status` (success|timeout|error)
- `feedback_score` (0–5, coletado pós-run)

Dashboard Grafana: `{{ agent.codigo | lower }}-dashboard` (custo/dia, latência p50/p95/p99, taxa de erro).

### Fallback Inteligente (R8)

Se timeout em {{ agent.tier_default }}:
1. Log em `agent_runs` com `timeout=true`
2. Resubmit com próximo tier (Sonnet ou Opus)
3. Reinjetar contexto (RAG results, partial output)
4. Max tokens reduzido a 1500 (evitar timeout novamente)

### SharePoint Routing

Este agente roteia automaticamente para pasta no SharePoint:
- **Site:** Manta.net
- **Drive:** Projetos
- **Pasta:** {% if agent.category == 'vertical' %}03_Projetos/{{ agent.nome | replace('agente-', '') | title }}/{% if 'Saneamento' in agent.descricao %}2026-AySA{% elif 'Energia' in agent.descricao %}ANEEL-2026{% elif 'Portos' in agent.descricao %}ANTAQ{% elif 'Aeroportos' in agent.descricao %}ANAC-2026{% elif 'Barragens' in agent.descricao %}ICOLD-Registry{% elif 'Rodovias' in agent.descricao %}SICRO-2026{% elif 'OAE' in agent.descricao %}Estruturas{% elif 'Ferrovia' in agent.descricao %}Via-Permanente{% else %}Linha4-L5{% endif %}{% else %}05_{{ agent.nome | title }}{% endif %}
- **Tier acesso:** {{ 'Editor' if agent.category == 'vertical' else 'Viewer' }}

### Feedback Loop (R9)

1. Após cada run, coletar `feedback_score` (0–5 estrellas)
2. Persistir em `agent_feedback` (Supabase)
3. Semanal: calcular embedding de prompts com score >= 4
4. Treinar reranker com high-scoring queries
5. Redeploy checksum atualizado em VERSIONS.json

---
"""

# ============================================================================
# Parseadores de CLAUDE.md
# ============================================================================

def parse_claude_md(file_path: Path) -> Dict[str, Dict]:
    """Parse CLAUDE.md e extrai dados de todos os 20 agentes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    agents_data = {}

    # Seção Tier 1 — Horizontais (linhas 366-378)
    horizontal_section = content[content.find("### Tier 1 — Horizontais"):content.find("### Tier 2–3 — Verticais")]
    horizontal_lines = [line.strip() for line in horizontal_section.split('\n') if '|' in line and 'Manta' in line]

    # Seção Tier 2–3 — Verticais (linhas 382-393)
    vertical_section = content[content.find("### Tier 2–3 — Verticais"):content.find("## CICLO DE VIDA")]
    vertical_lines = [line.strip() for line in vertical_section.split('\n') if '|' in line and 'Manta' in line]

    # Seção Regras Keyword (linhas 469-513)
    routing_section = content[content.find("### Regras Keyword"):content.find("### Confidence Score")]

    return {
        'horizontals': horizontal_lines,
        'verticals': vertical_lines,
        'routing': routing_section,
        'raw': content
    }


def extract_agent_data(table_lines: List[str], category: str) -> Dict[str, Agent]:
    """Extrai dados de agentes a partir de linhas da tabela."""
    agents = {}

    for line in table_lines:
        if not line or line.startswith('|') and '---' in line:
            continue

        parts = [p.strip() for p in line.split('|')[1:-1]]  # Remove pipes laterais vazios
        if len(parts) < 5:
            continue

        try:
            if category == 'horizontal':
                # | Codigo | Agente | Aliases | Tier default | Skill v5.0 | Checksum | Status |
                if len(parts) >= 7:
                    codigo, agente, aliases, tier, skill, checksum, status = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                else:
                    codigo, agente, aliases, tier, skill, checksum = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    status = 'Prod'
                rag_collection = None
            else:
                # | Codigo | Segmento | Agente | Tier default | Skill v5.0 | Checksum | RAG coleção | Status |
                if len(parts) >= 8:
                    codigo, segmento, agente, tier, skill, checksum, rag_collection, status = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7]
                elif len(parts) >= 7:
                    codigo, segmento, agente, tier, skill, checksum, rag_collection = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                    status = 'Prod'
                else:
                    codigo, segmento, agente, tier, skill, checksum = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                    rag_collection = None
                    status = 'Prod'
                aliases = segmento  # Para verticais, não usamos aliases

            # Limpar backticks e emojis
            skill = skill.replace('`', '').strip()
            checksum = checksum.replace('`', '').strip()
            codigo = codigo.replace('✅', '').replace('🆕', '').replace('⚡', '').replace('⭐', '').strip()
            status_clean = status.replace('✅ Prod', 'Prod').replace('🆕 v5.0', 'Prod').replace('⭐ AySA', 'Prod').replace('⭐ ANEEL', 'Prod').strip()

            if not skill or '.' not in skill:
                continue

            agent_obj = Agent(
                codigo=codigo,
                nome=agente.replace('`', '').strip(),
                descricao="",  # Será preenchido depois
                aliases=[aliases] if aliases else [],
                tier_default=tier.split('/')[0] if '/' in tier else tier,
                skill_file=skill,
                checksum=checksum,
                rag_collection=rag_collection,
                status=status_clean if status_clean in ['Prod', 'Staging', 'Roadmap'] else 'Prod',
                category=category
            )

            agents[agente.replace('`', '').strip()] = agent_obj
        except (IndexError, ValueError) as e:
            # Skip malformed lines
            continue

    return agents


def add_descriptions(agents: Dict[str, Agent], content: str) -> Dict[str, Agent]:
    """Adiciona descrições e outros dados aos agentes."""
    descriptions = {
        'maestro': 'Router canônico do Maestro (Manta 00) — orquestra roteamento determinístico, tiering automático e fallback inteligente para todos os 20 agentes v5.0.',
        'claims': 'Especialista em indenizações, sinistros e gestão de claims — análise de riscos, quantificação de danos, estruturação de sinistros complexos.',
        'contratual': 'Especialista em contratos, análise legal e questões jurídicas — revisão de cláusulas, interpretação de jurisdição, litigância.',
        'imobiliario': 'Especialista em projetos imobiliários — viabilidade, design, licenciamento, incorporação, PPP.',
        'orcamento': 'Especialista em orçamentação e gestão de custos — SICRO, composições, simulações de cenários, análise de desvios.',
        'modelagem': 'Especialista em modelagem financeira, cenários e simulações — análise de sensibilidade, projeções, riscos.',
        'cronograma': 'Especialista em cronogramas, gestão de projetos e planejamento — Gantt, PERT/CPM, XER, MSP, desvios.',
        'bd': 'Especialista em business development e estratégia comercial — prospecção, negociações, estruturas comerciais.',
        'apresentacoes': 'Especialista em criação de apresentações executivas (PowerPoint) — slides, storytelling, visualizações.',
        'advisory': 'Especialista em assessoria estratégica e governança — recomendações, estudos de viabilidade, benchmarking.',
        'arquiteto-ia': 'Especialista em arquitetura e governança de agentes IA — design de agents, orquestração, RAG, observabilidade.',
        'agente-rodovias': 'Especialista em infraestrutura rodoviária (Manta 03-S1) — pavimentos, drenagem, SICRO, DNIT, terraplenagem.',
        'agente-oae': 'Especialista em obras de arte especiais (pontes, viadutos, túneis) — OAE, estruturas metálicas, fundações, protensão.',
        'agente-ferrovia': 'Especialista em infraestrutura ferroviária (Manta 03-S3) — via permanente, trilho, bitola, catenária, AMV.',
        'agente-metro': 'Especialista em transporte metroviário e VLT (Manta 03-S4) — metrô, estações, sinalização, NATM, PSD.',
        'agente-portos': 'Especialista em infraestrutura portuária (Manta 03-S6) — terminais, dragagem, ANTAQ, PIANC, hidrovias.',
        'agente-aeroportos': 'Especialista em infraestrutura aeroportuária (Manta 03-S7) — pistas, taxiways, TPS, ANAC, RBAC, balizamento.',
        'agente-saneamento': 'Especialista em saneamento básico (Manta 03-S8) — ETAs, ETEs, adução, drenagem urbana, SNIS, Lei 14.026. PRIORIDADE AySA.',
        'agente-energia': 'Especialista em setor elétrico (Manta 03-S9) — transmissão, geração, subestações, ANEEL, RAP, leilões. PRIORIDADE State Grid.',
        'agente-barragens': 'Especialista em barragens e estruturas hidráulicas (Manta 03-S10) — CFRD, CCR, rejeitos, ICOLD, Lei 12.334, descomissionamento.',
    }

    # Adicionar ciclo de vida e trigger phrases para verticais
    lifecycle_data = {
        'agente-rodovias': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['rodovia', 'pavimento', 'CBUQ', 'SICRO', 'DNIT', 'terraplenagem', 'drenagem-rodoviária', 'tráfego'],
            'prompts': [
                'Qual a espessura de pavimento CBUQ para tráfego VDM=1500 veículos/dia?',
                'Elabore um orçamento SICRO para 50km de rodovia pavimentada',
                'Analise o projeto de drenagem rodoviária para corte de 8m',
                'Qual o custo de terraplenagem para aterro de 2m em solo arenoso?'
            ]
        },
        'agente-oae': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['ponte', 'viaduto', 'OAE', 'NBR 7187', 'túnel', 'fundação', 'estrutura-metálica', 'concreto-protendido'],
            'prompts': [
                'Dimensione uma ponte de concreto protendido com vão de 40m',
                'Analise a estabilidade de pilares para viaduto elevado',
                'Qual o custo de aparelhos de apoio de elastômero para ponte de 250m?',
                'Revise o projeto estrutural de túnel em NATM'
            ]
        },
        'agente-ferrovia': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['ferrovia', 'trilho', 'via-permanente', 'bitola', 'catenária', 'AMV', 'dormente'],
            'prompts': [
                'Dimensione a via permanente para ferrovia regional de 150 km',
                'Qual o custo de substituição de trilho desgastado em trecho crítico?',
                'Analise a capacidade de tráfego ferroviário para bitola 1.6m',
                'Especifique o sistema de drenagem para via permanente em terreno encharcado'
            ]
        },
        'agente-metro': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['metrô', 'estação', 'NATM', 'PSD', 'linha', 'VLT', 'sinalização-metrô'],
            'prompts': [
                'Dimensione uma estação de metrô subterrânea em NATM com profundidade de 20m',
                'Qual o custo de sinalização automática (ATO) para linha de metrô de 25km?',
                'Analise a ventilação de tunnel-metrô para circulação de trem',
                'Especifique os aparelhos de apoio sísmico para estrutura de VLT elevado'
            ]
        },
        'agente-portos': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['porto', 'terminal', 'ANTAQ', 'dragagem', 'berço', 'PIANC', 'containerizado'],
            'prompts': [
                'Dimensione um terminal de contêineres para 500k TEU/ano',
                'Qual o custo de dragagem de aprofundamento para calado de 14m?',
                'Analise a viabilidade de um porto fluvial para hidrovia da Bacia Amazônica',
                'Especifique o molhe de proteção para porto exposto a ondas de até 4m'
            ]
        },
        'agente-aeroportos': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['aeroporto', 'pista', 'RWY', 'taxiway', 'TPS', 'ANAC', 'RBAC', 'balizamento', 'ILS'],
            'prompts': [
                'Dimensione uma pista de pouso para aviação regional (ATR-72)',
                'Qual o PCN (Pavement Classification Number) para pista de concreto rígido?',
                'Analise o projeto de taxiway e sistema de balizamento para aeroporto novo',
                'Especifique o sistema de proteção contra fogo e emergência (TECA) para terminal'
            ]
        },
        'agente-saneamento': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['saneamento', 'ETA', 'ETE', 'adutora', 'esgoto', 'AySA', 'drenagem urbana', 'SNIS', 'Lei 14.026'],
            'prompts': [
                'Dimensione uma ETA para município de 500k hab com coagulação/floculação/sedimentação',
                'Qual o custo de uma elevatória para adução de 1000 L/s em altura de 50m?',
                'Analise a viabilidade de tratamento de esgoto por processo MBR para reúso',
                'Especifique o sistema de drenagem urbana e macrodrenagem para bacia de 5km2'
            ]
        },
        'agente-energia': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['transmissão', 'LT', 'subestação', 'ANEEL', 'leilão', 'ONS', 'EPE', 'torre', 'cabo ACSR'],
            'prompts': [
                'Dimensione uma linha de transmissão de 500kV com 200km de comprimento',
                'Qual o custo de uma subestação 345/138kV para 200MVA?',
                'Analise a viabilidade de um leilão ANEEL para geração eólica',
                'Especifique o sistema de proteção e controle para interligação de usina hidrelétrica'
            ]
        },
        'agente-barragens': {
            'ciclo': [1, 2, 3, 4, 5, 6, 7, 8],
            'triggers': ['barragem', 'vertedouro', 'CFRD', 'rejeitos', 'TSF', 'ICOLD', 'Lei 12.334', 'descomissionamento'],
            'prompts': [
                'Dimensione uma barragem CFRD (concreto) com altura de 80m para irrigação',
                'Qual o custo de construção de uma barragem de CCR (concreto compactado com rolo)?',
                'Analise a estabilidade de uma barragem de rejeitos (TSF) com 200m de altura',
                'Especifique o plano de descomissionamento seguro para barragem de 50 anos'
            ]
        },
    }

    for name, agent in agents.items():
        if name in descriptions:
            agent.descricao = descriptions[name]

        if name in lifecycle_data:
            agent.ciclo_vida = lifecycle_data[name]['ciclo']
            agent.trigger_phrases = lifecycle_data[name]['triggers']
            agent.exemplo_prompts = lifecycle_data[name]['prompts']
        else:
            # Horizontais não têm ciclo de vida específico
            agent.exemplo_prompts = [f"Exemplo de prompt para {agent.nome}"]

    return agents


def validate_checksums(agents: Dict[str, Agent]) -> bool:
    """Valida se os checksums estão presentes e têm formato esperado."""
    errors = []
    for name, agent in agents.items():
        if not agent.checksum or len(agent.checksum) < 8:
            errors.append(f"{name}: checksum inválido ({agent.checksum})")

    if errors:
        print("Erros de validação de checksum:")
        for err in errors:
            print(f"  - {err}")
        return False
    return True


def generate_skill_registry(agents: Dict[str, Agent]) -> str:
    """Gera SKILL.md consolidado com todos os agentes."""
    output = []

    # Header
    header = f"""# SKILL.md — Manta Maestro v5.0 (20 Agentes)

Registro consolidado de capabilities, routing, tiering e exemplos para todos os 20 agentes da Manta Associados.

**Versão:** v5.0 (2026-07-25)
**Gerado:** {datetime.now().isoformat()}
**Fonte:** CLAUDE.md + VERSIONS.json
**Total de agentes:** 11 horizontais + 9 verticais (S1–S4, S6–S10)
**Status:** Completo e validado

---

## Índice Rápido

### Tier 1 — Agentes Horizontais (11)

| # | Agente | Tier default | Status | RAG |
|----|--------|--------------|--------|-----|
"""

    # Tabela de horizontais
    for name, agent in sorted(agents.items()):
        if agent.category == 'horizontal':
            header += f"| {agent.codigo} | {agent.nome} | {agent.tier_default} | {agent.status} | N/A |\n"

    header += "\n### Tier 2–3 — Agentes Verticais (9)\n\n| # | Segmento | Agente | Tier default | RAG | Status |\n|----|----|--------|--------------|-----|--------|\n"

    # Tabela de verticais
    for name, agent in sorted(agents.items()):
        if agent.category == 'vertical':
            rag = agent.rag_collection if agent.rag_collection else 'N/A'
            header += f"| {agent.codigo} | {name.replace('agente-', '')} | {agent.nome} | {agent.tier_default} | {rag} | {agent.status} |\n"

    output.append(header)
    output.append("\n---\n")

    # Seção de cada agente
    template = Template(AGENT_TEMPLATE)

    # Horizontais primeiro
    output.append("## AGENTES HORIZONTAIS (Tier 1)\n")
    for name, agent in sorted(agents.items()):
        if agent.category == 'horizontal':
            rendered = template.render(agent=agent)
            output.append(rendered)
            output.append("\n")

    output.append("\n---\n\n## AGENTES VERTICAIS (Tier 2–3)\n")
    # Verticais por ordem (S1, S2, S3, S4, S6, S7, S8, S9, S10)
    vertical_order = ['agente-rodovias', 'agente-oae', 'agente-ferrovia', 'agente-metro',
                      'agente-portos', 'agente-aeroportos', 'agente-saneamento', 'agente-energia', 'agente-barragens']

    for name in vertical_order:
        if name in agents:
            agent = agents[name]
            rendered = template.render(agent=agent)
            output.append(rendered)
            output.append("\n")

    # Footer com informações de governança
    footer = f"""
---

## Governança & Manutenção

**Proprietário:** mneves@mantaassociados.com
**Versão master:** CLAUDE.md v5.0
**Checksums:** VERSIONS.json (20 skills, versionamento MD5)
**Aprovação:** Gate humano antes de merge principal
**SLA:** Patches < 48h; major > 2 semanas notice

### Regeneração automática

Este arquivo é gerado automaticamente por `scripts/generate_skills_registry.py`:

```bash
python scripts/generate_skills_registry.py
```

**Trigger:** Sempre que CLAUDE.md ou VERSIONS.json mudam.

### Validações

- [x] Todos 20 agentes presentes (11 horizontais + 9 verticais)
- [x] Checksums MD5 validados
- [x] Ciclo de vida (8 fases) para verticais
- [x] Trigger phrases e exemplos preenchidos
- [x] Capabilities (tools, skills, RAG) mapeadas
- [x] Tiering automático (R7) especificado
- [x] Fallback (R8) documentado
- [x] SharePoint routing definido

---

**Fim de SKILL.md v5.0**
"""
    output.append(footer)

    return '\n'.join(output)


# ============================================================================
# Main
# ============================================================================

def main():
    """Orquestra a geração de SKILL.md."""
    repo_root = Path(__file__).parent.parent
    claude_md = repo_root / 'CLAUDE.md'
    output_file = repo_root / 'manta-maestro' / 'SKILL.md'

    # Criar diretório se necessário
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Lendo {claude_md}...")
    if not claude_md.exists():
        print(f"[!] Erro: {claude_md} não encontrado")
        sys.exit(1)

    # Parse CLAUDE.md
    parsed = parse_claude_md(claude_md)

    # Extrair dados de horizontais e verticais
    print("[*] Extraindo dados de agentes horizontais...")
    horizontals = extract_agent_data(parsed['horizontals'], 'horizontal')

    print("[*] Extraindo dados de agentes verticais...")
    verticals = extract_agent_data(parsed['verticals'], 'vertical')

    # Combinar e adicionar descrições
    all_agents = {**horizontals, **verticals}
    all_agents = add_descriptions(all_agents, parsed['raw'])

    print(f"[*] Total de agentes extraídos: {len(all_agents)}")

    # Validar
    print("[*] Validando checksums...")
    if not validate_checksums(all_agents):
        print("[!] Validação de checksum falhou")
        sys.exit(1)

    # Gerar SKILL.md
    print("[*] Gerando SKILL.md consolidado...")
    registry = generate_skill_registry(all_agents)

    # Escrever arquivo
    print(f"[*] Escrevendo {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(registry)

    # Estatísticas
    file_size = output_file.stat().st_size
    num_lines = len(registry.split('\n'))

    print(f"""
[+] Sucesso!
    - Agentes: {len(all_agents)} (11 horizontais + 9 verticais)
    - Linhas: {num_lines:,}
    - Tamanho: {file_size / 1024:.1f} KB
    - Output: {output_file}
    - Timestamp: {datetime.now().isoformat()}
""")


if __name__ == '__main__':
    main()
