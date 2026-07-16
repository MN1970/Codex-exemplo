#!/usr/bin/env python
"""
Seed script to load 20 agents from Maestro v4.2 CLAUDE.md

Usage:
    python scripts/seed_agents.py
    python scripts/seed_agents.py --reset  # Clear existing agents first
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models.agent import Agent, AgentStatus, AgentTier, AgentEixo
from app.db.agent import create_agent, hard_delete_agent, get_agent_count
from app.schemas.agent import AgentCreate
import argparse


# Initial agent data from CLAUDE.md v4.2
SEED_AGENTS = [
    # Eixo 1 — Horizontais (transversais)
    {
        "id": "manta-00",
        "name": "maestro (router)",
        "code": "Manta 00",
        "aliases": ["maestro", "manta-router"],
        "description": "Roteador central - orquestra o encaminhamento de requisições para agentes especializados",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.HAIKU_TO_SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [],
    },
    {
        "id": "manta-01",
        "name": "claims",
        "code": "Manta 01",
        "aliases": ["02-C", "manta-claims"],
        "description": "Especialista em análise de reclamações, sinistros e gestão de claims",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.OPUS,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["claims", "sinistro", "reclamação", "contencioso"],
    },
    {
        "id": "manta-02",
        "name": "contratual",
        "code": "Manta 02",
        "aliases": ["manta-02", "contratual"],
        "description": "Especialista em análise e redação de contratos, cláusulas e termos legais",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["contrato", "cláusula", "termo", "legal", "acordo"],
    },
    {
        "id": "manta-04",
        "name": "imobiliario",
        "code": "Manta 04",
        "aliases": ["manta-04"],
        "description": "Especialista em propriedades imobiliárias, desapropriação e gestão de terrenos",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["imóvel", "propriedade", "desapropriação", "terreno"],
    },
    {
        "id": "manta-05",
        "name": "orcamento",
        "code": "Manta 05",
        "aliases": ["manta-05"],
        "description": "Especialista em estimativa de custos, orçamentação e análise econômico-financeira",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["orçamento", "custo", "financeiro", "preço", "SICRO", "SINAPI"],
    },
    {
        "id": "manta-06",
        "name": "modelagem",
        "code": "Manta 06",
        "aliases": ["manta-06"],
        "description": "Especialista em modelagem matemática, simulações e análises computacionais",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET_TO_OPUS,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["modelo", "simulação", "análise", "matemática"],
    },
    {
        "id": "manta-07",
        "name": "cronograma",
        "code": "Manta 07",
        "aliases": ["manta-07"],
        "description": "Especialista em planejamento, cronogramação e gestão de prazos",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["cronograma", "prazo", "planejamento", "calendário", "Gantt"],
    },
    {
        "id": "manta-13",
        "name": "bd",
        "code": "Manta 13",
        "aliases": ["manta-13", "business-dev"],
        "description": "Especialista em business development, parcerias estratégicas e comercialização",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["business", "comercial", "parceria", "estratégia"],
    },
    {
        "id": "manta-14",
        "name": "apresentacoes",
        "code": "Manta 14",
        "aliases": ["manta-14-pptx"],
        "description": "Especialista em preparação de apresentações executivas e conteúdo visual",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["apresentação", "PowerPoint", "slide", "visual", "executiva"],
    },
    {
        "id": "manta-15",
        "name": "advisory",
        "code": "Manta 15",
        "aliases": ["manta-15", "advisory"],
        "description": "Especialista em consultoria estratégica e assessoria de alto nível",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.SONNET_TO_OPUS,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["consultoria", "advisory", "estratégia", "recomendação"],
    },
    {
        "id": "manta-16",
        "name": "arquiteto-ia",
        "code": "Manta 16",
        "aliases": ["manta-15-arq"],
        "description": "Especialista em arquitetura de IA e design de sistemas inteligentes",
        "eixo": AgentEixo.HORIZONTAL,
        "tier": AgentTier.OPUS,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["IA", "arquitetura", "sistema", "design", "Claude"],
    },
    # Eixo 2 — Verticais por segmento
    {
        "id": "manta-03-s1",
        "name": "agente-infraestrutura (S1)",
        "code": "Manta 03-S1",
        "aliases": ["agente-rodovias", "s1"],
        "description": "Especialista em infraestrutura rodoviária (pavimento, drenagem, sinais)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["rodovia", "pavimento", "CBUQ", "DNIT", "terraplenagem", "SICRO"],
    },
    {
        "id": "manta-03-s2",
        "name": "agente-infraestrutura (S2)",
        "code": "Manta 03-S2",
        "aliases": ["agente-oae", "s2"],
        "description": "Especialista em obras de arte especial (OAE) - pontes, viadutos, túneis",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["ponte", "viaduto", "OAE", "NBR 7187", "túnel"],
    },
    {
        "id": "manta-03-s3",
        "name": "agente-infraestrutura (S3)",
        "code": "Manta 03-S3",
        "aliases": ["agente-ferrovia", "s3"],
        "description": "Especialista em infraestrutura ferroviária (trilhos, dormentes, via permanente)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["ferrovia", "trilho", "dormente", "via permanente"],
    },
    {
        "id": "manta-03-s4",
        "name": "agente-infraestrutura (S4)",
        "code": "Manta 03-S4",
        "aliases": ["agente-metro", "s4"],
        "description": "Especialista em infraestrutura de metrô e transporte urbano rápido",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": ["metrô", "estação", "NATM", "VLT", "linha"],
    },
    {
        "id": "manta-03-s6",
        "name": "agente-portos",
        "code": "Manta 03-S6",
        "aliases": ["agente-maritimo", "s6"],
        "description": "Especialista em projetos portuários e hidroviários (dragagem, terminais, berços)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [
            "porto", "terminal", "ANTAQ", "dragagem", "molhe", "berço", "calado",
            "contêiner", "granel", "PIANC"
        ],
    },
    {
        "id": "manta-03-s7",
        "name": "agente-aeroportos",
        "code": "Manta 03-S7",
        "aliases": ["agente-aviacao", "s7"],
        "description": "Especialista em infraestrutura aeroportuária (pistas, TPS, TECA, balizamento)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [
            "aeroporto", "pista", "ANAC", "ICAO", "TPS", "TECA", "balizamento",
            "PAPI", "ILS", "RWY", "taxiway"
        ],
    },
    {
        "id": "manta-03-s8",
        "name": "agente-saneamento",
        "code": "Manta 03-S8",
        "aliases": ["agente-agua", "s8"],
        "description": "Especialista em saneamento básico (água, esgoto, drenagem) - PRIORIDADE AySA",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [
            "saneamento", "ETA", "ETE", "adutora", "esgoto", "AySA",
            "drenagem urbana", "SNIS", "Lei 14.026"
        ],
    },
    {
        "id": "manta-03-s9",
        "name": "agente-energia",
        "code": "Manta 03-S9",
        "aliases": ["agente-eletricidade", "s9"],
        "description": "Especialista em setor elétrico (transmissão, distribuição, geração)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [
            "transmissão", "LT", "subestação", "ANEEL", "RAP", "leilão",
            "ONS", "EPE", "PDE", "State Grid"
        ],
    },
    {
        "id": "manta-03-s10",
        "name": "agente-barragens",
        "code": "Manta 03-S10",
        "aliases": ["agente-hidraulica", "s10"],
        "description": "Especialista em barragens (concreto, terra, rejeitos, descomissionamento)",
        "eixo": AgentEixo.VERTICAL,
        "tier": AgentTier.SONNET,
        "status": AgentStatus.OPERACIONAL,
        "service_url": None,
        "routing_keywords": [
            "barragem", "vertedouro", "CFRD", "CCR", "rejeitos", "PNSB",
            "ICOLD", "CBDB", "TSF", "SIGBM"
        ],
    },
]


def reset_database():
    """Delete all existing agents"""
    db = SessionLocal()
    try:
        count = db.query(Agent).delete()
        db.commit()
        print(f"Deleted {count} existing agents")
    finally:
        db.close()


def seed_agents():
    """Seed initial agents into database"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if agents already exist
        existing_count = db.query(Agent).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} agents.")
            print("Use --reset flag to clear existing agents first.")
            return False

        # Create agents
        for agent_data in SEED_AGENTS:
            agent_create = AgentCreate(
                id=agent_data["id"],
                name=agent_data["name"],
                code=agent_data["code"],
                aliases=agent_data["aliases"],
                description=agent_data["description"],
                eixo=agent_data["eixo"],
                tier=agent_data["tier"],
                status=agent_data["status"],
                service_url=agent_data["service_url"],
                routing_keywords=agent_data["routing_keywords"],
                created_by="seed-script",
            )
            agent = create_agent(db, agent_create)
            print(f"Created: {agent.code} - {agent.name}")

        total = db.query(Agent).count()
        print(f"\nSuccessfully seeded {total} agents into database")
        return True

    except Exception as e:
        print(f"Error seeding agents: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed agents into database")
    parser.add_argument("--reset", action="store_true", help="Delete existing agents before seeding")
    args = parser.parse_args()

    if args.reset:
        reset_database()

    success = seed_agents()
    sys.exit(0 if success else 1)
