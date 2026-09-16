#!/usr/bin/env python3
"""
Auditor anti-alucinação — Pacote A (referência factual).
Detecta e valida: normas ABNT, leis federais, codes SICRO, URLs, DOIs.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Importar registries
from registry.normas_abnt import NORMAS_ABNT
from registry.leis_federais import LEIS_FEDERAIS
from registry.sicro import SICRO_CODES


def detectar_padroes(texto: str) -> Dict[str, List[Dict]]:
    """Detecta padrões de normas, leis, SICRO, URLs, DOIs no texto."""

    achados = {
        "normas_abnt": [],
        "leis": [],
        "sicro": [],
        "urls": [],
        "dois": [],
    }

    # Padrão: NBR XXXX, NBR XXXX-X, etc.
    for match in re.finditer(r"\b(NBR\s+(\d+(?:[.-]\d+)?(?:/\d+)?))\b", texto, re.IGNORECASE):
        achados["normas_abnt"].append({
            "texto": match.group(1),
            "codigo": match.group(2),
            "start": match.start(),
            "end": match.end(),
        })

    # Padrão: Lei nº XXXX/YYYY ou Lei nº X.XXX/YYYY
    for match in re.finditer(r"\bLei\s+(?:n[°º]\s+)?(\d+(?:[.,]\d+)?/\d{4})\b", texto, re.IGNORECASE):
        achados["leis"].append({
            "texto": match.group(0),
            "codigo": match.group(1),
            "start": match.start(),
            "end": match.end(),
        })

    # Padrão: SICRO XXXXXXX
    for match in re.finditer(r"\bSICRO\s+(\d{7})\b", texto, re.IGNORECASE):
        achados["sicro"].append({
            "texto": match.group(0),
            "codigo": match.group(1),
            "start": match.start(),
            "end": match.end(),
        })

    # Padrão: URLs
    for match in re.finditer(r"https?://[^\s]+", texto):
        achados["urls"].append({
            "texto": match.group(0),
            "start": match.start(),
            "end": match.end(),
        })

    # Padrão: DOI
    for match in re.finditer(r"\bdoi[:\s]+([^\s]+)\b", texto, re.IGNORECASE):
        achados["dois"].append({
            "texto": match.group(0),
            "doi": match.group(1),
            "start": match.start(),
            "end": match.end(),
        })

    return achados


def validar_norma_abnt(codigo: str) -> Dict[str, Any]:
    """Valida uma norma ABNT contra o registry."""
    # Normalizar formato (remover espaços, converter para maiúsculas)
    # Extrair apenas a numeração
    codigo_norm = re.sub(r"\D", "", codigo)  # Remove tudo que não é dígito

    # Buscar no registry
    for entry in NORMAS_ABNT:
        entry_codigo_norm = re.sub(r"\D", "", entry["codigo"])
        if entry_codigo_norm == codigo_norm:
            return {
                "verdict": "OK",
                "norma": entry.get("titulo", ""),
                "data_publicacao": entry.get("data", ""),
                "url": entry.get("url", ""),
            }

    # Não encontrado
    return {
        "verdict": "INEXISTENTE",
        "sugestao": f"Norma NBR {codigo} não está no registry. Verifique a numeração.",
    }


def validar_lei(codigo: str) -> Dict[str, Any]:
    """Valida uma lei federal contra o registry."""
    # Normalizar: Lei 14.026/2020 → 14026/2020
    codigo_norm = codigo.replace(".", "").replace(",", "")

    for entry in LEIS_FEDERAIS:
        if entry["codigo"].replace(".", "").replace(",", "") == codigo_norm:
            return {
                "verdict": "OK",
                "titulo": entry.get("titulo", ""),
                "data_sancao": entry.get("data_sancao", ""),
                "url": entry.get("url", ""),
            }

    # Não encontrado
    return {
        "verdict": "INEXISTENTE",
        "sugestao": f"Lei {codigo} não está no registry (escopo federal). Pode ser estadual/municipal.",
    }


def validar_sicro(codigo: str) -> Dict[str, Any]:
    """Valida um código SICRO contra o registry."""
    for entry in SICRO_CODES:
        if entry["codigo"] == codigo:
            return {
                "verdict": "OK",
                "descricao": entry.get("descricao", ""),
                "categoria": entry.get("categoria", ""),
            }

    return {
        "verdict": "INEXISTENTE",
        "sugestao": f"SICRO {codigo} não localizado. Verifique o código de 7 dígitos.",
    }


def auditar_texto(texto: str, online: bool = False) -> Dict[str, Any]:
    """
    Audita um texto procurando por aluci fabricadas.
    Retorna um envelope com achados e verdicts.
    """

    if not texto or not isinstance(texto, str):
        return {
            "confidence": 0.0,
            "achados": [],
            "erro": "Texto vazio ou inválido",
        }

    # Detectar padrões
    padroes = detectar_padroes(texto)

    achados = []
    total_validacoes = 0
    sucessos = 0

    # Validar normas ABNT
    for pattern in padroes["normas_abnt"]:
        total_validacoes += 1
        resultado = validar_norma_abnt(pattern["codigo"])
        achados.append({
            "tipo": "norma_abnt",
            "texto": pattern["texto"],
            "codigo": pattern["codigo"],
            **resultado,
        })
        if resultado["verdict"] == "OK":
            sucessos += 1

    # Validar leis
    for pattern in padroes["leis"]:
        total_validacoes += 1
        resultado = validar_lei(pattern["codigo"])
        achados.append({
            "tipo": "lei_federal",
            "texto": pattern["texto"],
            "codigo": pattern["codigo"],
            **resultado,
        })
        if resultado["verdict"] == "OK":
            sucessos += 1

    # Validar SICRO
    for pattern in padroes["sicro"]:
        total_validacoes += 1
        resultado = validar_sicro(pattern["codigo"])
        achados.append({
            "tipo": "sicro",
            "texto": pattern["texto"],
            "codigo": pattern["codigo"],
            **resultado,
        })
        if resultado["verdict"] == "OK":
            sucessos += 1

    # Validar URLs e DOIs (offline = apenas estrutura)
    if padroes["urls"]:
        for pattern in padroes["urls"]:
            achados.append({
                "tipo": "url",
                "texto": pattern["texto"],
                "verdict": "OK" if _validar_url_estrutura(pattern["texto"]) else "INVALIDA",
            })

    if padroes["dois"]:
        for pattern in padroes["dois"]:
            achados.append({
                "tipo": "doi",
                "texto": pattern["texto"],
                "doi": pattern.get("doi", ""),
                "verdict": "OK" if _validar_doi_estrutura(pattern.get("doi", "")) else "INVALIDA",
            })

    # Calcular confidence
    if total_validacoes == 0:
        confidence = 1.0  # Sem padrões detectáveis = passa
    else:
        confidence = sucessos / total_validacoes

    return {
        "timestamp": datetime.now().isoformat(),
        "confidence": confidence,
        "achados": achados,
        "resumo": {
            "total_padroes": total_validacoes,
            "sucessos": sucessos,
            "falhas": total_validacoes - sucessos,
        },
    }


def relatorio_json(envelope: Dict) -> str:
    """Formata o envelope como JSON."""
    return json.dumps(envelope, indent=2, ensure_ascii=False)


def relatorio_markdown(envelope: Dict) -> str:
    """Formata o envelope como Markdown."""
    lines = [
        "# Relatório de Auditoria — aluci-guard",
        "",
        f"**Data**: {envelope.get('timestamp', 'N/A')}",
        f"**Confiança**: {envelope.get('confidence', 0.0):.1%}",
        "",
    ]

    resumo = envelope.get("resumo", {})
    lines.append(f"## Resumo")
    lines.append(f"- Total de padrões detectados: {resumo.get('total_padroes', 0)}")
    lines.append(f"- Validados com sucesso: {resumo.get('sucessos', 0)}")
    lines.append(f"- Falhas encontradas: {resumo.get('falhas', 0)}")
    lines.append("")

    achados = envelope.get("achados", [])
    if achados:
        lines.append("## Achados Detalhados")
        lines.append("")
        for achado in achados:
            tipo = achado.get("tipo", "desconhecido").upper()
            verdict = achado.get("verdict", "?")
            texto = achado.get("texto", "")
            lines.append(f"### [{verdict}] {tipo}")
            lines.append(f"- **Texto**: `{texto}`")
            if achado.get("codigo"):
                lines.append(f"- **Código**: {achado['codigo']}")
            if achado.get("sugestao"):
                lines.append(f"- **Sugestão**: {achado['sugestao']}")
            lines.append("")
    else:
        lines.append("## Nenhum padrão detectado")
        lines.append("")

    return "\n".join(lines)


def _validar_url_estrutura(url: str) -> bool:
    """Valida estrutura básica de URL."""
    return bool(re.match(r"^https?://", url))


def _validar_doi_estrutura(doi: str) -> bool:
    """Valida estrutura básica de DOI."""
    return bool(re.match(r"^10\.\d+/", doi))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python auditor.py <arquivo.txt> [--json] [--online]")
        sys.exit(1)

    arquivo = sys.argv[1]
    json_output = "--json" in sys.argv
    online = "--online" in sys.argv

    with open(arquivo) as f:
        texto = f.read()

    envelope = auditar_texto(texto, online=online)

    if json_output:
        print(relatorio_json(envelope))
    else:
        print(relatorio_markdown(envelope))
