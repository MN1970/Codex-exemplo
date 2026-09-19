#!/usr/bin/env python3
"""
Aeroportos RAG (S7) Phase 1a Week 3 — URL Validation & Assessment
==================================================================================

Task: Validate ANAC RBAC 154 (14 PDFs) + MPor Manual (1 PDF)
Timeline: Week 3 (6 hours estimated)
Output: QA checklist, schema documentation, ingestion timeline
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# ============================================================================
# Week 3 Source Catalog
# ============================================================================

ANAC_RBAC_154_PDFS = [
    {
        "name": "RBAC 154 EMD 06",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/arquivo_norma/RBAC154EMD06.pdf",
        "title": "REGULAMENTO BRASILEIRO DA AVIAÇÃO CIVIL RBAC nº 154 EMENDA nº 06",
        "edition": "06",
        "category": "Main Regulation",
    },
    {
        "name": "RBAC 154 EMD 08",
        "url": "https://pergamum.anac.gov.br/pergamum/vinculos/RBAC154EMD08.pdf",
        "title": "REGULAMENTO BRASILEIRO DA AVIAÇÃO CIVIL RBAC nº 154 EMENDA nº 08",
        "edition": "08",
        "category": "Main Regulation",
    },
    {
        "name": "RBAC 154 EMD 09",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/arquivo_norma/RBAC154EMD09.pdf",
        "title": "REGULAMENTO BRASILEIRO DA AVIAÇÃO CIVIL RBAC nº 154 EMENDA nº 09",
        "edition": "09",
        "category": "Main Regulation",
    },
    {
        "name": "IS 154-001A",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/IS154-001A.pdf",
        "title": "Orientação Suplementar IS nº 154-001A — Visual Aids for Aircraft Aprons",
        "edition": "001A",
        "category": "Implementation Standard",
    },
    {
        "name": "IS 154-002B",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/IS154-002B.pdf",
        "title": "Orientação Suplementar IS nº 154-002B — Physical Characteristics of Aerodromes",
        "edition": "002B",
        "category": "Implementation Standard",
    },
    {
        "name": "IS 154-003A",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/IS154-003A.pdf",
        "title": "Orientação Suplementar IS nº 154-003A — Visual Aids for Runways and Taxiways",
        "edition": "003A",
        "category": "Implementation Standard",
    },
    {
        "name": "FAQs EMD 05",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Perguntas%20e%20Respostas%20RBAC154-EMD05.pdf",
        "title": "PERGUNTAS E RESPOSTAS RBAC N° 154 - EMENDA nº 05",
        "edition": "05",
        "category": "Guidance",
    },
    {
        "name": "Audit Release 2023",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/arquivo_norma/RBAC154_Publicacao_2023.pdf",
        "title": "RBAC 154 — Publicação Oficial 2023",
        "edition": "2023",
        "category": "Official Publication",
    },
    {
        "name": "Planning Guidelines",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Guia_Planificacao_RBAC154.pdf",
        "title": "Guia de Planificação — RBAC 154",
        "edition": "001",
        "category": "Guidance",
    },
    {
        "name": "Compatibility Chart",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Planilha_Compatibilidade_Aeronaves.xlsx",
        "title": "Planilha Aeronave-Aeródromo — Compatibilidade de Aeronaves",
        "edition": "001",
        "category": "Reference Table",
    },
    {
        "name": "Briefing Note 2022",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/arquivo_norma/Resumo_Executivo_RBAC154_2022.pdf",
        "title": "Resumo Executivo — RBAC 154 (Versão 2022)",
        "edition": "2022",
        "category": "Executive Summary",
    },
    {
        "name": "Case Studies",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Estudos_Caso_RBAC154.pdf",
        "title": "Estudos de Caso — Aplicação Prática de RBAC 154",
        "edition": "001",
        "category": "Case Studies",
    },
    {
        "name": "Manual de Operações",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Manual_Operacoes_RBAC154.pdf",
        "title": "Manual de Operações e Manutenção — RBAC 154",
        "edition": "001",
        "category": "Operations Manual",
    },
    {
        "name": "Maintenance Guide",
        "url": "https://www.gov.br/anac/pt-br/centrais-de-conteudo/publicacoes/publicacoes-arquivos/manual-de-obras-e-servicos-de-manutencao.pdf",
        "title": "Manual de Obras e Serviços de Manutenção",
        "edition": "001",
        "category": "Maintenance",
    },
    {
        "name": "Consultation Comments 2024",
        "url": "https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbha-e-rbac/rbac/rbac-154/@@display-file/anexo_norma/Comentarios_Consulta_Publica_2024.pdf",
        "title": "Comentários da Consulta Pública 2024 — RBAC 154",
        "edition": "2024",
        "category": "Public Consultation",
    },
]

MPOR_MANUAL_PDFS = [
    {
        "name": "Manual de Projetos Aeroportuários",
        "url": "https://www.gov.br/portos-e-aeroportos/pt-br/assuntos/transporte-aereo/arquivos/minframanual_aeroportuariosac_final.pdf",
        "title": "MANUAL DE PROJETOS AEROPORTUÁRIOS — Ministério da Infraestrutura",
        "author": "Secretaria de Aviação Civil (SAC)",
        "publication_date": "2021-09-29",
        "version": "Final",
        "size_mb": 5.37,
        "category": "Design Manual",
    },
]

# ============================================================================
# Validation & Assessment
# ============================================================================


def validate_url_headers(url: str) -> Dict:
    """Validate URL accessibility via HEAD request"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req, timeout=10) as response:
            return {
                "status_code": response.status,
                "accessible": response.status < 400,
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": response.headers.get("content-length", "unknown"),
            }
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "accessible": e.code < 400,
            "error": str(e),
        }
    except Exception as e:
        return {
            "status_code": None,
            "accessible": False,
            "error": str(e),
        }


def estimate_chunks(
    pages_estimated: int,
    tokens_per_page: int = 300,
    chunk_size_tokens: int = 400,
    overlap_tokens: int = 50,
) -> int:
    """Estimate number of chunks based on page count"""
    total_tokens = pages_estimated * tokens_per_page
    stride = chunk_size_tokens - overlap_tokens
    chunks = max(1, (total_tokens - chunk_size_tokens) // stride + 1)
    return chunks


def estimate_pages_from_pdf_name(name: str) -> int:
    """Rough estimate of pages based on PDF type"""
    if "EMD" in name or "Main Regulation" in name:
        return 150  # Main RBAC documents are typically 100-200 pages
    elif "IS" in name or "Implementation Standard" in name:
        return 50  # Implementation standards are shorter
    elif "FAQ" in name or "Guidance" in name:
        return 40
    elif "Manual" in name:
        return 100
    elif "Compatibility" in name or "Reference" in name:
        return 10
    elif "Case Study" in name or "Executive" in name:
        return 30
    else:
        return 50  # Default estimate


@dataclass
class PDFAssessment:
    name: str
    url: str
    title: str
    pages_estimated: int
    chunks_estimated: int
    validation_status: str
    category: str
    size_mb: Optional[float] = None


def assess_source(pdf_info: Dict) -> PDFAssessment:
    """Assess a single PDF source"""
    pages = estimate_pages_from_pdf_name(pdf_info.get("title", ""))
    chunks = estimate_chunks(pages)
    validation = validate_url_headers(pdf_info["url"])
    status = "✓ OK" if validation["accessible"] else f"✗ WARN ({validation.get('status_code', 'N/A')})"

    return PDFAssessment(
        name=pdf_info.get("name", "Unknown"),
        url=pdf_info["url"],
        title=pdf_info.get("title", "Unknown"),
        pages_estimated=pages,
        chunks_estimated=chunks,
        validation_status=status,
        category=pdf_info.get("category", "Unknown"),
        size_mb=pdf_info.get("size_mb"),
    )


# ============================================================================
# Supabase Schema Documentation
# ============================================================================

SUPABASE_SCHEMA = {
    "table_name": "rag_chunks",
    "collection_prefix": "aer:",
    "columns": [
        {
            "name": "id",
            "type": "bigint",
            "primary_key": True,
            "description": "Unique chunk identifier",
        },
        {
            "name": "collection",
            "type": "text",
            "description": "Collection prefix, always 'aer:' for Aeroportos",
        },
        {
            "name": "source_id",
            "type": "text",
            "description": "Unique source identifier (e.g., 'aer:rbac-154-emd-09', 'aer:mpor-manual')",
        },
        {
            "name": "source_title",
            "type": "text",
            "description": "Full title of the source document",
        },
        {
            "name": "chunk_number",
            "type": "int",
            "description": "Sequential chunk number within source (1-indexed)",
        },
        {
            "name": "content",
            "type": "text",
            "description": "Chunk text content (~400 tokens, 50-token overlap with neighbors)",
        },
        {
            "name": "metadata",
            "type": "jsonb",
            "description": "Structured metadata: author, publication_date, regulation_number, edition, category, pages, confidence_score",
        },
        {
            "name": "embedding",
            "type": "vector(384)",
            "description": "OpenAI text-embedding-3-small (1536-dim) or local multilingual-e5-small (384-dim)",
        },
        {
            "name": "created_at",
            "type": "timestamp with time zone",
            "default": "CURRENT_TIMESTAMP",
        },
    ],
}

# ============================================================================
# QA Checklist
# ============================================================================

QA_CHECKLIST = [
    {
        "task": "URL Validation",
        "status": "PENDING",
        "description": "Validate HTTP HEAD on all 15 PDFs",
        "owner": "Crawler",
        "estimated_hours": 0.5,
    },
    {
        "task": "PDF Download",
        "status": "PENDING",
        "description": "Download RBAC 154 (14 PDFs) + MPor (1 PDF) = 15 total",
        "owner": "Crawler",
        "estimated_hours": 1.0,
    },
    {
        "task": "Text Extraction",
        "status": "PENDING",
        "description": "Extract text via pdfplumber; fallback tesseract for scanned PDFs",
        "owner": "Ingestion Pipeline",
        "estimated_hours": 2.0,
    },
    {
        "task": "Metadata Structuring",
        "status": "PENDING",
        "description": "Parse: title, author, publication_date, section, regulation_number, edition, confidence_score",
        "owner": "Ingestion Pipeline",
        "estimated_hours": 1.0,
    },
    {
        "task": "OCR Validation",
        "status": "PENDING",
        "description": "Measure Tesseract confidence ≥0.85 for scanned pages",
        "owner": "QA",
        "estimated_hours": 1.0,
    },
    {
        "task": "Chunk Estimation",
        "status": "PENDING",
        "description": "Verify RBAC 154 (1500 chunks) + MPor (300 chunks) totaling ~1800 chunks",
        "owner": "QA",
        "estimated_hours": 0.5,
    },
    {
        "task": "Schema Validation",
        "status": "PENDING",
        "description": "Confirm Supabase rag_chunks table schema with metadata JSONB",
        "owner": "DevOps",
        "estimated_hours": 0.5,
    },
    {
        "task": "Embedding Model Test",
        "status": "PENDING",
        "description": "Test local multilingual-e5-small or OpenAI text-embedding-3-small",
        "owner": "Ingestion Pipeline",
        "estimated_hours": 0.5,
    },
]

# ============================================================================
# Main Execution
# ============================================================================


def main():
    print("=" * 80)
    print("AEROPORTOS RAG (S7) PHASE 1A WEEK 3 — INGESTION ASSESSMENT")
    print("=" * 80)
    print()

    # ========================================================================
    # ANAC RBAC 154 Assessment
    # ========================================================================

    print("📋 SOURCE 1: ANAC RBAC 154 (Regulamento Brasileiro Aviação Civil)")
    print("-" * 80)

    rbac_assessments = []
    rbac_total_chunks = 0
    rbac_ok_count = 0
    rbac_total_pages = 0

    for pdf in ANAC_RBAC_154_PDFS:
        assessment = assess_source(pdf)
        rbac_assessments.append(assessment)
        rbac_total_chunks += assessment.chunks_estimated
        rbac_total_pages += assessment.pages_estimated
        if "OK" in assessment.validation_status:
            rbac_ok_count += 1
        print(f"  [{assessment.validation_status}] {assessment.name}")
        print(f"    Title: {assessment.title}")
        print(f"    Pages: {assessment.pages_estimated} | Chunks: {assessment.chunks_estimated}")
        print()

    rbac_summary = {
        "fonte": "ANAC RBAC 154",
        "pdfs_total": len(ANAC_RBAC_154_PDFS),
        "pdfs_accessible": rbac_ok_count,
        "pages_estimated": rbac_total_pages,
        "chunks_estimated": rbac_total_chunks,
        "ocr_avg_confidence": 0.88,  # Estimated; depends on PDF quality
        "tempo_estimado_semana_horas": 4.0,
    }

    # ========================================================================
    # MPor Manual Assessment
    # ========================================================================

    print("📋 SOURCE 2: MPor Manual de Projetos Aeroportuários")
    print("-" * 80)

    mpor_assessments = []
    mpor_total_chunks = 0
    mpor_ok_count = 0
    mpor_total_pages = 0

    for pdf in MPOR_MANUAL_PDFS:
        assessment = assess_source(pdf)
        mpor_assessments.append(assessment)
        mpor_total_chunks += assessment.chunks_estimated
        mpor_total_pages += assessment.pages_estimated
        if "OK" in assessment.validation_status:
            mpor_ok_count += 1
        print(f"  [{assessment.validation_status}] {assessment.name}")
        print(f"    Title: {assessment.title}")
        print(f"    Size: {assessment.size_mb} MB | Pages: {mpor_total_pages} | Chunks: {mpor_total_chunks}")
        print()

    mpor_summary = {
        "fonte": "MPor Manual de Projetos",
        "pdfs_total": len(MPOR_MANUAL_PDFS),
        "pdfs_accessible": mpor_ok_count,
        "pages_estimated": 100,  # Manual de Projetos typical size
        "chunks_estimated": estimate_chunks(100),
        "ocr_confidence": 0.92,  # Typically well-formatted government manual
        "tempo_estimado_semana_horas": 2.0,
    }

    # ========================================================================
    # Final Report
    # ========================================================================

    report = {
        "segmento": "S7-Aeroportos",
        "week": 3,
        "data_avaliacao": datetime.now().isoformat(),
        "fontes": [rbac_summary, mpor_summary],
        "totais": {
            "pdfs_total": len(ANAC_RBAC_154_PDFS) + len(MPOR_MANUAL_PDFS),
            "pdfs_acessiveis": rbac_ok_count + mpor_ok_count,
            "pages_estimadas": rbac_total_pages + 100,
            "chunks_estimados": rbac_total_chunks + estimate_chunks(100),
            "tempo_total_estimado_semana": 6.0,
        },
        "qa_checklist": QA_CHECKLIST,
        "schema_supabase": SUPABASE_SCHEMA,
        "blockers": [],
        "ready_for_ingestion": (rbac_ok_count + mpor_ok_count) == (
            len(ANAC_RBAC_154_PDFS) + len(MPOR_MANUAL_PDFS)
        ),
    }

    # ========================================================================
    # Print Summary
    # ========================================================================

    print()
    print("=" * 80)
    print("📊 SUMMARY — WEEK 3 READINESS")
    print("=" * 80)
    print()
    print(f"✓ Total PDFs Found: {report['totais']['pdfs_total']}")
    print(f"✓ PDFs Accessible: {report['totais']['pdfs_acessiveis']}/{report['totais']['pdfs_total']}")
    print(f"✓ Estimated Pages: {report['totais']['pages_estimadas']}")
    print(f"✓ Estimated Chunks: {report['totais']['chunks_estimados']}")
    print(f"✓ Timeline: {report['totais']['tempo_total_estimado_semana']} hours")
    print()

    if report["ready_for_ingestion"]:
        print("✅ READY FOR WEEK 3 INGESTION")
    else:
        print("⚠️  BLOCKERS DETECTED — REVIEW ACCESSIBILITY")

    print()
    print("=" * 80)
    print("📁 QA CHECKLIST")
    print("=" * 80)
    print()
    for task in QA_CHECKLIST:
        print(f"  [ ] {task['task']} ({task['estimated_hours']}h) — {task['description']}")
    print()

    # ========================================================================
    # Save JSON Report
    # ========================================================================

    report_path = "/tmp/claude-0/-home-user/74556235-ea2e-5c11-aba7-46453a6f553e/scratchpad/aeroportos_week3_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Full report saved to: {report_path}")
    print()

    return report


if __name__ == "__main__":
    main()
