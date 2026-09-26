"""Servidor MCP em processo `cronos` — expõe o motor aos subagentes (mcp__cronos__<ferramenta>).

Requer `claude-agent-sdk`. O motor (`cronos.engine`) não depende do SDK.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from claude_agent_sdk import ToolAnnotations, create_sdk_mcp_server, tool

from ..engine import (Projeto, calcular, comparar, curva_s, dcma14, e_historico, folga_dias, gravar_mspdi,
                      gravar_xer, ler_arquivo, linha_do_tempo, monte_carlo, valor_agregado)

ESTOQUE: dict[str, Projeto] = {}          # versões carregadas na sessão (F2: Supabase)
LEITURA = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


def _ok(dados: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(dados, ensure_ascii=False, default=str)}]}


def _erro(msg: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": msg}], "is_error": True}


def _versao(chave: str) -> Projeto | None:
    return ESTOQUE.get(chave)


@tool("importar_lote", "Importa vários cronogramas (.xer, .xml MSPDI) de uma vez. Cada projeto recebe a chave "
      "<arquivo>#<proj_id>. Ignora versões obsoletas (OBSOLETO, DEPRECATED, 99-backup) salvo incluir_historico.",
      {"type": "object", "properties": {"caminhos": {"type": "array", "items": {"type": "string"}},
                                        "incluir_historico": {"type": "boolean"}},
       "required": ["caminhos"]})
async def importar_lote(args: dict[str, Any]) -> dict[str, Any]:
    resumo = []
    for c in args["caminhos"]:
        if e_historico(c) and not args.get("incluir_historico"):
            resumo.append({"arquivo": c, "status": "ignorado: versão histórica (use incluir_historico)"})
            continue
        try:
            projetos = ler_arquivo(c, incluir_historico=bool(args.get("incluir_historico")))
        except (ValueError, OSError, PermissionError) as e:
            resumo.append({"arquivo": c, "status": f"erro: {e}"})
            continue
        for p in projetos:
            ESTOQUE[p.chave] = p
            resumo.append({"chave": p.chave, "projeto": p.nome, "data_status": p.data_status,
                           "atividades": len(p.atividades), "ligacoes": len(p.ligacoes),
                           "custo_total": round(p.custo_total, 2), "alertas": p.alertas
                           + ([] if p.custo_total else ["SEM CARREGAMENTO DE CUSTOS"])})
    return _ok(resumo)


@tool("calcular_cpm", "Calcula ida e volta por datas e calendários (data de status, datas reais, restrições, "
      "lógica retida): término, caminho crítico e folgas.", {"chave": str}, annotations=LEITURA)
async def calcular_cpm(args: dict[str, Any]) -> dict[str, Any]:
    p = _versao(args["chave"])
    if not p:
        return _erro(f"Versão não carregada: {args['chave']}")
    try:
        r = calcular(p)
    except ValueError as e:
        return _erro(str(e))
    crit = sorted(r["criticas"], key=lambda u: r["es"][u])
    return _ok({"data_status": r["data_status"], "termino": r["termino"], "avisos": r["avisos"],
                "n_criticas": len(crit), "caminho_critico": [
                    {"codigo": p.atividades[u].codigo, "nome": p.atividades[u].nome, "inicio": r["es"][u],
                     "termino": r["ef"][u], "folga_dias": round(folga_dias(p, r, u), 1),
                     "fonte": p.atividades[u].fonte} for u in crit[:200]]})


@tool("checar_dcma14", "Checagem DCMA-14 com a regra A5 (nota ≥ 90% e sem bloqueio nos pontos 1, 3, 6, 7, 11).",
      {"chave": str}, annotations=LEITURA)
async def checar_dcma14(args: dict[str, Any]) -> dict[str, Any]:
    p = _versao(args["chave"])
    if not p:
        return _erro(f"Versão não carregada: {args['chave']}")
    return _ok(dcma14(p))


@tool("simular_monte_carlo", "Monte Carlo triangular sobre as durações remanescentes (AACE 57R-09): P10–P90 do "
      "término e índice de criticidade.",
      {"type": "object", "properties": {"chave": {"type": "string"},
                                        "n": {"type": "integer", "minimum": 50, "maximum": 5000},
                                        "otimista": {"type": "number"}, "pessimista": {"type": "number"}},
       "required": ["chave"]}, annotations=LEITURA)
async def simular_monte_carlo(args: dict[str, Any]) -> dict[str, Any]:
    p = _versao(args["chave"])
    if not p:
        return _erro(f"Versão não carregada: {args['chave']}")
    return _ok(monte_carlo(p, n=args.get("n", 500), otimista=args.get("otimista", 0.9),
                           pessimista=args.get("pessimista", 1.3)))


@tool("comparar_versoes", "Compara duas versões: término, custo, atividades incluídas/excluídas, variação de "
      "início, duração e custo, mudança de criticidade.", {"chave_a": str, "chave_b": str}, annotations=LEITURA)
async def comparar_versoes(args: dict[str, Any]) -> dict[str, Any]:
    a, b = _versao(args["chave_a"]), _versao(args["chave_b"])
    if not (a and b):
        return _erro("Carregue as duas versões com importar_lote antes de comparar")
    c = comparar(a, b)
    c["alteradas"] = c["alteradas"][:200]
    return _ok(c)


@tool("exportar", "Exporta a versão calculada para .xer (Primavera) ou .xml (MS Project; salve como .mpp no Project).",
      {"chave": str, "formato": str, "destino": str})
async def exportar(args: dict[str, Any]) -> dict[str, Any]:
    p = _versao(args["chave"])
    if not p:
        return _erro(f"Versão não carregada: {args['chave']}")
    r = calcular(p)
    fmt = args["formato"].lower().lstrip(".")
    try:
        if fmt == "xer":
            Path(args["destino"]).write_bytes(gravar_xer(p, r).encode("latin-1", errors="replace"))
        elif fmt == "xml":
            Path(args["destino"]).write_text(gravar_mspdi(p, r), encoding="utf-8")
        else:
            return _erro("Formato deve ser xer ou xml")
    except ValueError as e:
        return _erro(str(e))
    return _ok({"arquivo": args["destino"], "formato": fmt, "termino": r["termino"]})


@tool("curva_s_evm", "Curva S física e financeira mensal (planejado × previsto) e valor agregado na data de status: "
      "BAC, PV, EV, AC, SPI, CPI, EAC, TCPI (ANSI/EIA-748).", {"chave": str}, annotations=LEITURA)
async def curva_s_evm(args: dict[str, Any]) -> dict[str, Any]:
    p = _versao(args["chave"])
    if not p:
        return _erro(f"Versão não carregada: {args['chave']}")
    try:
        r = calcular(p)
    except ValueError as e:
        return _erro(str(e))
    return _ok({"curva_s": curva_s(p, r), "valor_agregado": valor_agregado(p, r),
                "alertas": [] if p.custo_total else ["SEM CARREGAMENTO DE CUSTOS: curva financeira vazia"]})


@tool("linha_do_tempo", "Linha do tempo de N versões (ordem de data de status): término, custo e variação contra a "
      "anterior, e tendência de marcos (deslizamento por marco).",
      {"type": "object", "properties": {"chaves": {"type": "array", "items": {"type": "string"}}}},
      annotations=LEITURA)
async def linha_do_tempo_versoes(args: dict[str, Any]) -> dict[str, Any]:
    chaves = args.get("chaves") or list(ESTOQUE)
    faltam = [c for c in chaves if c not in ESTOQUE]
    if faltam:
        return _erro(f"Versões não carregadas: {', '.join(faltam)}")
    lt = linha_do_tempo([ESTOQUE[c] for c in chaves])
    lt["tendencia_marcos"] = lt["tendencia_marcos"][:100]
    return _ok(lt)


@tool("listar_versoes", "Lista as versões carregadas na sessão.", {}, annotations=LEITURA)
async def listar_versoes(args: dict[str, Any]) -> dict[str, Any]:
    return _ok([{"chave": k, "projeto": p.nome, "data_status": p.data_status} for k, p in ESTOQUE.items()])


FERRAMENTAS = [importar_lote, calcular_cpm, checar_dcma14, simular_monte_carlo, comparar_versoes, curva_s_evm,
               linha_do_tempo_versoes, exportar, listar_versoes]
SERVIDOR = create_sdk_mcp_server(name="cronos", version="0.3.0", tools=FERRAMENTAS)
NOMES = [f"mcp__cronos__{t.name}" for t in FERRAMENTAS]
