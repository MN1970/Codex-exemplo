#!/usr/bin/env python3
"""
Auditoria Automática — SharePoint 03_Projetos
Catalogar todos os arquivos por segmento e gerar inventário RAG
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configuração
SHAREPOINT_LOCAL = Path("/home/user/Codex-exemplo/sharepoint")
PROJECTS_FOLDER = SHAREPOINT_LOCAL / "03_Projetos"
OUTPUT_DIR = Path("/home/user/Codex-exemplo/docs/rag-sources")
AUDIT_REPORT = OUTPUT_DIR / "AUDIT-CONSOLIDADO.xlsx"

SEGMENTS = {
    "S1": "Rodovias",
    "S2": "OAE",
    "S3": "Ferrovia",
    "S4": "Metrô",
    "S6": "Portos",
    "S7": "Aeroportos",
    "S8": "Saneamento",
    "S9": "Energia",
    "S10": "Barragens",
}

RAG_PREFIXES = {
    "S1": "rod:",
    "S2": "oae:",
    "S3": "fer:",
    "S4": "mtr:",
    "S6": "por:",
    "S7": "aer:",
    "S8": "san:",
    "S9": "ene:",
    "S10": "bar:",
}

def get_file_info(file_path):
    """Extrair metadados de um arquivo"""
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "path": str(file_path.relative_to(PROJECTS_FOLDER)),
        "type": file_path.suffix.lower(),
        "size_mb": round(stat.st_size / (1024*1024), 2),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }

def categorize_file(file_path, segment):
    """Categorizar arquivo por tipo (Projeto, Norma, Template, etc)"""
    path_str = str(file_path).lower()
    name_lower = file_path.name.lower()

    if any(x in path_str for x in ["projeto", "case", "executado", "bndes"]):
        return "Projetos_Executados"
    elif any(x in path_str for x in ["norma", "nbr", "dnit", "abnt", "aneel", "antaq", "anac", "lei", "resolucao"]):
        return "Normas_Referencias"
    elif any(x in path_str for x in ["estudo", "tecnico", "calculo", "analise", "metodologia"]):
        return "Estudos_Tecnicos"
    elif any(x in path_str for x in ["template", "modelo", "padrao"]):
        return "Templates_Documentos"
    elif any(x in path_str for x in ["edital", "licitacao", "concorrencia"]):
        return "Licitacoes_Editais"
    else:
        return "Outros"

def audit_segment(segment_code, segment_name):
    """Auditar um segmento específico"""
    segment_path = PROJECTS_FOLDER / segment_name

    if not segment_path.exists():
        return {
            "segment": segment_code,
            "name": segment_name,
            "status": "PASTA_NAO_EXISTE",
            "files": [],
            "categories": {},
            "total_files": 0,
            "total_size_mb": 0,
        }

    files = []
    categories = defaultdict(list)
    total_size = 0

    # Recursivo: encontrar todos os arquivos
    for file_path in segment_path.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            file_info = get_file_info(file_path)
            category = categorize_file(file_path, segment_code)

            files.append({
                **file_info,
                "category": category,
            })
            categories[category].append(file_info["name"])
            total_size += file_info["size_mb"]

    return {
        "segment": segment_code,
        "name": segment_name,
        "status": "OK" if segment_path.exists() else "VAZIO",
        "files": files,
        "categories": dict(categories),
        "total_files": len(files),
        "total_size_mb": round(total_size, 2),
        "rag_prefix": RAG_PREFIXES.get(segment_code, ""),
    }

def estimate_rag_chunks(segment_audit):
    """Estimar chunks RAG potenciais baseado em arquivos"""
    chunks_estimate = 0

    for category, files in segment_audit["categories"].items():
        if category == "Normas_Referencias":
            chunks_estimate += len(files) * 15  # ~15 chunks por norma
        elif category == "Projetos_Executados":
            chunks_estimate += len(files) * 5   # ~5 chunks por projeto
        elif category == "Estudos_Tecnicos":
            chunks_estimate += len(files) * 10  # ~10 chunks por estudo
        elif category == "Templates_Documentos":
            chunks_estimate += len(files) * 2   # ~2 chunks por template
        elif category == "Licitacoes_Editais":
            chunks_estimate += len(files) * 3   # ~3 chunks por edital

    return chunks_estimate

def generate_csv_report(all_audits):
    """Gerar relatório CSV"""
    csv_file = OUTPUT_DIR / "AUDIT-SHAREPOINT.csv"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Segmento",
            "Nome",
            "Status",
            "Total Arquivos",
            "Tamanho Total (MB)",
            "RAG Prefix",
            "Chunks Potenciais",
            "Projetos",
            "Normas",
            "Estudos",
            "Templates",
            "Editais",
        ])

        for audit in all_audits:
            chunks = estimate_rag_chunks(audit)
            writer.writerow([
                audit["segment"],
                audit["name"],
                audit["status"],
                audit["total_files"],
                audit["total_size_mb"],
                audit["rag_prefix"],
                chunks,
                len(audit["categories"].get("Projetos_Executados", [])),
                len(audit["categories"].get("Normas_Referencias", [])),
                len(audit["categories"].get("Estudos_Tecnicos", [])),
                len(audit["categories"].get("Templates_Documentos", [])),
                len(audit["categories"].get("Licitacoes_Editais", [])),
            ])

    return csv_file

def generate_json_report(all_audits):
    """Gerar relatório JSON (mais detalhado)"""
    json_file = OUTPUT_DIR / "AUDIT-SHAREPOINT.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_segments": len(all_audits),
        "segments_with_files": sum(1 for a in all_audits if a["total_files"] > 0),
        "total_files": sum(a["total_files"] for a in all_audits),
        "total_size_mb": round(sum(a["total_size_mb"] for a in all_audits), 2),
        "estimated_rag_chunks": sum(estimate_rag_chunks(a) for a in all_audits),
        "audits": all_audits,
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return json_file

def generate_markdown_report(all_audits):
    """Gerar relatório Markdown (human-friendly)"""
    md_file = OUTPUT_DIR / "AUDIT-CONSOLIDADO.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# Auditoria SharePoint — Consolidado\n\n")
        f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Sumário geral
        total_files = sum(a["total_files"] for a in all_audits)
        total_size = sum(a["total_size_mb"] for a in all_audits)
        total_chunks = sum(estimate_rag_chunks(a) for a in all_audits)

        f.write("## Resumo Geral\n\n")
        f.write(f"| Métrica | Valor |\n")
        f.write(f"|---------|-------|\n")
        f.write(f"| Segmentos | {len(all_audits)} |\n")
        f.write(f"| Segmentos com arquivos | {sum(1 for a in all_audits if a['total_files'] > 0)} |\n")
        f.write(f"| Total de arquivos | {total_files} |\n")
        f.write(f"| Tamanho total | {total_size:.2f} MB |\n")
        f.write(f"| Chunks RAG potenciais | {total_chunks} |\n\n")

        # Tabela por segmento
        f.write("## Por Segmento\n\n")
        f.write("|Seg|Nome|Status|Arquivos|Tamanho|RAG Chunks|Proj|Norm|Est|Tmpl|Edit|\n")
        f.write("|---|----|----|--------|-------|----------|----|----|----|----|----|\n")

        for audit in all_audits:
            chunks = estimate_rag_chunks(audit)
            f.write(f"|{audit['segment']}|{audit['name']}|{audit['status']}|")
            f.write(f"{audit['total_files']}|{audit['total_size_mb']:.1f}MB|{chunks}|")
            f.write(f"{len(audit['categories'].get('Projetos_Executados', []))}|")
            f.write(f"{len(audit['categories'].get('Normas_Referencias', []))}|")
            f.write(f"{len(audit['categories'].get('Estudos_Tecnicos', []))}|")
            f.write(f"{len(audit['categories'].get('Templates_Documentos', []))}|")
            f.write(f"{len(audit['categories'].get('Licitacoes_Editais', []))}\n")

        f.write("\n")

        # Detalhes por segmento
        f.write("## Detalhes por Segmento\n\n")
        for audit in all_audits:
            if audit["status"] == "PASTA_NAO_EXISTE":
                f.write(f"### {audit['segment']} — {audit['name']} ⚠️ PASTA NÃO EXISTE\n\n")
            else:
                f.write(f"### {audit['segment']} — {audit['name']}\n\n")
                f.write(f"**Arquivos**: {audit['total_files']} | **Tamanho**: {audit['total_size_mb']:.2f} MB\n\n")

                if audit["categories"]:
                    for category, files in sorted(audit["categories"].items()):
                        f.write(f"#### {category} ({len(files)})\n")
                        for fname in files[:5]:  # Show first 5
                            f.write(f"- {fname}\n")
                        if len(files) > 5:
                            f.write(f"- ... e mais {len(files)-5} arquivos\n")
                        f.write("\n")

    return md_file

def main():
    print("🔍 Iniciando auditoria SharePoint...")
    print(f"📁 Procurando em: {PROJECTS_FOLDER}")

    if not PROJECTS_FOLDER.exists():
        print(f"⚠️  Pasta {PROJECTS_FOLDER} NÃO EXISTE")
        print("   Criando estrutura vazia para referência...")
        PROJECTS_FOLDER.mkdir(parents=True, exist_ok=True)
        for seg_code, seg_name in SEGMENTS.items():
            (PROJECTS_FOLDER / seg_name).mkdir(exist_ok=True)

    # Auditar cada segmento
    all_audits = []
    for seg_code, seg_name in SEGMENTS.items():
        print(f"  📊 Auditando {seg_code} — {seg_name}...", end="")
        audit = audit_segment(seg_code, seg_name)
        all_audits.append(audit)
        print(f" ✓ ({audit['total_files']} arquivos)")

    # Gerar relatórios
    print("\n📝 Gerando relatórios...")
    csv_file = generate_csv_report(all_audits)
    print(f"  ✓ CSV: {csv_file}")

    json_file = generate_json_report(all_audits)
    print(f"  ✓ JSON: {json_file}")

    md_file = generate_markdown_report(all_audits)
    print(f"  ✓ Markdown: {md_file}")

    print("\n✅ Auditoria concluída!")
    print(f"\n📊 Resumo:\n")
    total_files = sum(a["total_files"] for a in all_audits)
    total_chunks = sum(estimate_rag_chunks(a) for a in all_audits)
    print(f"   Total de arquivos: {total_files}")
    print(f"   Chunks RAG potenciais: {total_chunks}")
    print(f"   Relatórios em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
