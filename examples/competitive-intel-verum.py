#!/usr/bin/env python3
"""
Competitive Intelligence — Rastrear Verum com Obscura.

Exemplo prático de como usar Obscura para monitorar concorrentes:
- Extrair info da página principal
- Listar projetos/cases
- Monitorar contatos e equipe
- Acompanhar tecnologias usadas

Uso:
    python examples/competitive-intel-verum.py
"""

import subprocess
import json
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CompetitorIntel:
    url: str
    company_name: Optional[str] = None
    services: List[str] = None
    projects: List[str] = None
    contact_info: Optional[str] = None
    technologies: List[str] = None
    team_size: Optional[str] = None
    raw_text: Optional[str] = None

    def __post_init__(self):
        if self.services is None:
            self.services = []
        if self.projects is None:
            self.projects = []
        if self.technologies is None:
            self.technologies = []


def fetch_with_obscura(url: str) -> str:
    """Fetch de um site com Obscura (stealth + render)."""
    cmd = [
        "/root/.local/bin/obscura",
        "fetch",
        url,
        "--dump",
        "markdown"  # markdown é mais fácil de parsear
    ]

    print(f"📡 Fetchando {url}...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"❌ Erro: {result.stderr[:200]}")
        return None

    return result.stdout


def extract_services(text: str) -> List[str]:
    """Extrair serviços mencionados no texto."""
    services_keywords = [
        "engenharia",
        "consultoria",
        "projeto",
        "design",
        "software",
        "infraestrutura",
        "desenvolvimento",
        "modelagem",
        "gestão de projetos",
        "BIM",
        "CAD",
        "análise",
        "planejamento",
    ]

    found = []
    text_lower = text.lower()
    for keyword in services_keywords:
        if keyword in text_lower:
            found.append(keyword)

    return list(set(found))


def extract_projects(text: str) -> List[str]:
    """Extrair menções a projetos/clientes."""
    # Padrão: "Projeto: [nome]" ou "Case: [nome]"
    patterns = [
        r"(?:Projeto|Case|Clientes?|Obras?):\s*([^\n]+)",
        r"(?:projeto|case|cliente|obra)\s*-\s*([^\n]+)",
    ]

    projects = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        projects.extend(matches)

    return [p.strip() for p in projects if p.strip()]


def extract_technologies(text: str) -> List[str]:
    """Extrair tecnologias/ferramentas mencionadas."""
    tech_keywords = [
        "Python",
        "Java",
        "JavaScript",
        "React",
        "Node.js",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "Google Cloud",
        "PostgreSQL",
        "MongoDB",
        "AutoCAD",
        "Revit",
        "QGIS",
        "ArcGIS",
        "SAP",
        "Oracle",
        "Salesforce",
    ]

    found = []
    for tech in tech_keywords:
        if tech in text:
            found.append(tech)

    return found


def analyze_competitor(url: str) -> CompetitorIntel:
    """Análise completa de um concorrente."""

    intel = CompetitorIntel(url=url)

    # 1. Fetch com Obscura
    text = fetch_with_obscura(url)
    if not text:
        print(f"⚠️  Não foi possível buscar {url}")
        return intel

    intel.raw_text = text

    # 2. Extrair informações
    intel.services = extract_services(text)
    intel.projects = extract_projects(text)
    intel.technologies = extract_technologies(text)

    # 3. Extrair nome da empresa (primeira linha, título, etc)
    lines = text.split("\n")
    for line in lines:
        if len(line) > 10 and len(line) < 100:
            intel.company_name = line.strip()
            break

    # 4. Extrair contato (email, telefone)
    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    emails = re.findall(email_pattern, text)
    if emails:
        intel.contact_info = emails[0]

    return intel


def print_report(intel: CompetitorIntel):
    """Imprimir relatório de inteligência competitiva."""
    print("\n" + "=" * 70)
    print(f"🎯 COMPETITIVE INTELLIGENCE — {intel.url}")
    print("=" * 70)

    if intel.company_name:
        print(f"\n📛 Empresa: {intel.company_name}")

    if intel.services:
        print(f"\n💼 Serviços: {', '.join(intel.services)}")

    if intel.projects:
        print(f"\n🏗️  Projetos/Casos: {', '.join(intel.projects[:5])}")
        if len(intel.projects) > 5:
            print(f"   ... e mais {len(intel.projects) - 5}")

    if intel.technologies:
        print(f"\n⚙️  Tecnologias: {', '.join(intel.technologies)}")

    if intel.contact_info:
        print(f"\n📧 Contato: {intel.contact_info}")

    print("\n" + "=" * 70)


def main():
    """Rastrear Verum."""

    # URL da Verum (exemplo real)
    url = "https://verum.com.br"

    print(f"\n🕵️  Iniciando análise de competitive intelligence...")
    print(f"🎯 Alvo: {url}\n")

    # Análise
    intel = analyze_competitor(url)

    # Relatório
    print_report(intel)

    # Salvar como JSON para posterior análise
    if intel.raw_text:
        report = {
            "url": intel.url,
            "empresa": intel.company_name,
            "servicos": intel.services,
            "projetos": intel.projects,
            "tecnologias": intel.technologies,
            "contato": intel.contact_info,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        with open("/tmp/verum-intel.json", "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Relatório salvo: /tmp/verum-intel.json")
    else:
        print(f"\n⚠️  Não foi possível gerar relatório (sem acesso à rede)")


if __name__ == "__main__":
    main()
