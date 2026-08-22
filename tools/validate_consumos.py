#!/usr/bin/env python3
"""Validador da base de consumos por receita setorial (Manta Maestro).

Usa apenas a biblioteca padrao. Le os JSON Schema como fonte de verdade dos
vocabularios controlados, em vez de duplicar as listas aqui.

Uso:
    python3 tools/validate_consumos.py            # valida, exit 1 em falha
    python3 tools/validate_consumos.py --stats    # + contagens
    python3 tools/validate_consumos.py --selftest # prova que as regras duras disparam
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "data" / "consumos"
SCHEMA_DIR = DADOS / "schema"

INTENSIDADES = DADOS / "intensidades-setor.csv"
FONTES = DADOS / "registro-fontes.csv"
ESTRUTURA = DADOS / "estrutura-custo-setor.csv"
CROSSWALK = DADOS / "crosswalk-cnae-setores.csv"

TOLERANCIA_SOMA_PCT = 2.0  # pontos percentuais


class Erros:
    def __init__(self) -> None:
        self.itens: list[str] = []

    def add(self, arquivo: str, linha: int | str, msg: str) -> None:
        self.itens.append(f"{arquivo}:{linha}: {msg}")

    def __len__(self) -> int:
        return len(self.itens)


def carregar_schema(nome: str) -> dict:
    with open(SCHEMA_DIR / nome, encoding="utf-8") as f:
        return json.load(f)


def ler_csv(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def enum_de(schema: dict, campo: str) -> list[str] | None:
    prop = schema.get("properties", {}).get(campo, {})
    valores = prop.get("enum")
    if valores is None:
        return None
    return [v for v in valores if v is not None]


def tipos_de(schema: dict, campo: str) -> list[str]:
    prop = schema.get("properties", {}).get(campo, {})
    t = prop.get("type", "string")
    return t if isinstance(t, list) else [t]


def valida_contra_schema(rows: list[dict], schema: dict, arquivo: str, erros: Erros) -> None:
    obrigatorios = schema.get("required", [])
    permitidos = set(schema.get("properties", {}))
    for i, row in enumerate(rows, start=2):  # linha 1 = cabecalho
        extras = set(row) - permitidos
        if extras:
            erros.add(arquivo, i, f"colunas fora do schema: {sorted(extras)}")
        for campo in obrigatorios:
            if not (row.get(campo) or "").strip():
                erros.add(arquivo, i, f"campo obrigatorio vazio: {campo}")
        for campo, valor in row.items():
            valor = (valor or "").strip()
            if campo not in permitidos:
                continue
            permitidos_enum = enum_de(schema, campo)
            if permitidos_enum and valor and valor not in permitidos_enum:
                erros.add(arquivo, i, f"{campo}='{valor}' fora do vocabulario {permitidos_enum}")
            tipos = tipos_de(schema, campo)
            if valor and "number" in tipos:
                try:
                    float(valor)
                except ValueError:
                    erros.add(arquivo, i, f"{campo}='{valor}' nao e numero")
            if valor and "integer" in tipos:
                try:
                    int(valor)
                except ValueError:
                    erros.add(arquivo, i, f"{campo}='{valor}' nao e inteiro")


def valida_intensidades(rows: list[dict], fontes: dict[str, dict], erros: Erros) -> None:
    arquivo = INTENSIDADES.name
    vistos: set[str] = set()
    for i, row in enumerate(rows, start=2):
        rid = row.get("id", "")
        if rid in vistos:
            erros.add(arquivo, i, f"id duplicado: {rid}")
        vistos.add(rid)

        # --- integridade referencial ------------------------------------
        fid = row.get("fonte_id", "")
        fonte = fontes.get(fid)
        if fonte is None:
            erros.add(arquivo, i, f"fonte_id '{fid}' nao existe em {FONTES.name}")
            fonte = {}

        # --- regra dura: cite_only nunca carrega valor -------------------
        if row.get("licenca") == "cite_only" and (row.get("valor") or "").strip():
            erros.add(arquivo, i, "licenca=cite_only com 'valor' preenchido - conteudo licenciado nao entra na base")

        # --- regra dura: fonte agregada nao gera linha de intensidade ----
        if fonte.get("entrega") == "custo_unitario_agregado":
            erros.add(arquivo, i,
                      f"fonte {fid} entrega 'custo_unitario_agregado' e nao pode originar linha de intensidade "
                      f"(pertence a uma base de benchmark top-down)")

        # --- metodo indireto exige memoria de calculo -------------------
        if row.get("metodo") == "indireto" and len((row.get("memoria_calculo") or "").strip()) < 10:
            erros.add(arquivo, i, "metodo=indireto sem memoria_calculo reproduzivel")

        # --- valor positivo --------------------------------------------
        v = (row.get("valor") or "").strip()
        if v:
            try:
                if float(v) <= 0:
                    erros.add(arquivo, i, f"valor '{v}' deve ser positivo")
            except ValueError:
                pass  # ja reportado pelo schema

        # --- coerencia moeda x unidade ---------------------------------
        unidade = row.get("unidade_fisica", "")
        moeda = row.get("moeda", "")
        if "R$" in unidade and moeda != "BRL":
            erros.add(arquivo, i, f"unidade '{unidade}' em R$ mas moeda='{moeda}'")
        if "US$" in unidade and not moeda.startswith("USD"):
            erros.add(arquivo, i, f"unidade '{unidade}' em US$ mas moeda='{moeda}'")

        # --- rastreabilidade -------------------------------------------
        if len((row.get("fonte_localizacao") or "").strip()) < 3:
            erros.add(arquivo, i, "fonte_localizacao vazia ou curta - todo numero precisa de endereco na fonte")


def valida_estrutura_custo(rows: list[dict], fontes: dict[str, dict], erros: Erros) -> None:
    arquivo = ESTRUTURA.name
    # O bloco e a chave (setor, ano, DENOMINADOR, fonte). O denominador entra na
    # chave porque participacao sobre "valor das obras" e sobre "custos e despesas"
    # sao bases distintas e nao se somam entre si.
    blocos: dict[tuple, float] = defaultdict(float)
    denominadores_validos = {"valor_obras_paic", "receita_paic", "custos_despesas_paic",
                             "capex_projeto", "valor_obra_contratada", "vbp"}
    for i, row in enumerate(rows, start=2):
        fid = row.get("fonte_id", "")
        if fid not in fontes:
            erros.add(arquivo, i, f"fonte_id '{fid}' nao existe em {FONTES.name}")
        den = (row.get("denominador") or "").strip()
        if not den:
            erros.add(arquivo, i, "denominador obrigatorio - participacao sem base declarada nao diz nada")
        elif den not in denominadores_validos:
            erros.add(arquivo, i, f"denominador '{den}' fora de {sorted(denominadores_validos)}")
        try:
            pct = float(row["participacao_pct"])
        except (KeyError, ValueError):
            erros.add(arquivo, i, "participacao_pct ausente ou nao numerica")
            continue
        if not 0 <= pct <= 100:
            erros.add(arquivo, i, f"participacao_pct={pct} fora de [0,100]")
        blocos[(row.get("setor"), row.get("ano_base"), den, fid)] += pct

    for (setor, ano, den, fid), soma in sorted(blocos.items()):
        if abs(soma - 100.0) > TOLERANCIA_SOMA_PCT:
            erros.add(arquivo, "bloco",
                      f"({setor}, {ano}, {den}, {fid}) soma {soma:.1f}% - fora de "
                      f"100% +/- {TOLERANCIA_SOMA_PCT:.0f} pp")


def valida_crosswalk(rows: list[dict], intensidades: list[dict], erros: Erros) -> None:
    arquivo = CROSSWALK.name
    setores_crosswalk = {r["setor_manta"] for r in rows}
    for i, row in enumerate(rows, start=2):
        if row.get("aderencia") not in {"exato", "parcial", "agregado"}:
            erros.add(arquivo, i, f"aderencia '{row.get('aderencia')}' invalida")
    for i, row in enumerate(intensidades, start=2):
        if row.get("setor") not in setores_crosswalk:
            erros.add(INTENSIDADES.name, i,
                      f"setor '{row.get('setor')}' nao mapeado em {CROSSWALK.name}")


def estatisticas(intensidades: list[dict], fontes: list[dict]) -> None:
    print("\n=== ESTATISTICAS ===")
    print(f"intensidades: {len(intensidades)} linhas")
    for campo in ("setor", "familia_insumo", "tier", "verificacao", "metodo", "ano_base"):
        c = Counter(r[campo] for r in intensidades)
        print(f"  por {campo}: {dict(sorted(c.items()))}")
    print(f"\nfontes: {len(fontes)} catalogadas")
    for campo in ("camada", "entrega", "licenca", "verificacao"):
        c = Counter(r[campo] for r in fontes)
        print(f"  por {campo}: {dict(sorted(c.items()))}")

    lidas = sum(1 for r in intensidades if r["verificacao"] == "fonte_primaria_lida")
    print(f"\nlinhas com fonte primaria efetivamente lida: {lidas}/{len(intensidades)}")
    if lidas < len(intensidades):
        print("  ATENCAO: as demais NAO foram conferidas no documento original.")

    # matriz de cobertura setor x familia
    schema = carregar_schema("intensidade.schema.json")
    familias = enum_de(schema, "familia_insumo") or []
    setores = enum_de(schema, "setor") or []
    preenchido = {(r["setor"], r["familia_insumo"]) for r in intensidades}
    print(f"\n=== MATRIZ DE COBERTURA ({len(preenchido)}/{len(setores)*len(familias)} celulas) ===")
    largura = max(len(f) for f in familias) + 1
    print(" " * 6 + "".join(f[:3].upper().ljust(4) for f in familias))
    for s in setores:
        marcas = "".join(("X".ljust(4) if (s, f) in preenchido else ".".ljust(4)) for f in familias)
        print(f"{s:<6}{marcas}")
    print("\nlegenda das familias: " + ", ".join(f"{f[:3].upper()}={f}" for f in familias))


def selftest() -> int:
    """Prova que as regras duras realmente reprovam. Nao toca nos dados reais."""
    print("=== SELFTEST ===")
    schema = carregar_schema("intensidade.schema.json")
    fontes = {
        "F-XXX": {"fonte_id": "F-XXX", "entrega": "coeficiente_fisico"},
        "F-AGG": {"fonte_id": "F-AGG", "entrega": "custo_unitario_agregado"},
    }
    base = {
        "id": "INT-CF-ACO-999", "setor": "CF", "cnae": "F", "familia_insumo": "aco",
        "valor": "10", "unidade_fisica": "t/R$ mi", "denominador": "valor_obras_paic",
        "ano_base": "2024", "deflator": "nominal_corrente", "moeda": "BRL", "pais": "BR",
        "metodo": "direto", "memoria_calculo": "", "premissas": "",
        "fonte_id": "F-XXX", "fonte_localizacao": "tabela 1", "tier": "A",
        "licenca": "publico", "verificacao": "fonte_primaria_lida", "url": "", "notas": "",
    }
    casos = [
        ("cite_only com valor",        {**base, "licenca": "cite_only"}),
        ("indireto sem memoria",       {**base, "metodo": "indireto"}),
        ("fonte agregada",             {**base, "fonte_id": "F-AGG"}),
        ("fonte_id inexistente",       {**base, "fonte_id": "F-000"}),
        ("valor negativo",             {**base, "valor": "-5"}),
        ("moeda incoerente",           {**base, "moeda": "USD"}),
        ("localizacao vazia",          {**base, "fonte_localizacao": ""}),
        ("enum invalido",              {**base, "familia_insumo": "titanio"}),
    ]
    falhas = 0
    for nome, row in casos:
        e = Erros()
        valida_contra_schema([row], schema, "selftest", e)
        valida_intensidades([row], fontes, e)
        if len(e) == 0:
            print(f"  FALHOU  {nome}: deveria ter sido reprovado e passou")
            falhas += 1
        else:
            print(f"  ok      {nome} -> {len(e)} erro(s)")
    # caso valido tem de passar limpo
    e = Erros()
    valida_contra_schema([base], schema, "selftest", e)
    valida_intensidades([base], fontes, e)
    if len(e):
        print(f"  FALHOU  linha valida foi reprovada: {e.itens}")
        falhas += 1
    else:
        print("  ok      linha valida passa limpa")
    print("SELFTEST OK" if not falhas else f"SELFTEST COM {falhas} FALHA(S)")
    return 1 if falhas else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    erros = Erros()
    intensidades = ler_csv(INTENSIDADES)
    fontes_rows = ler_csv(FONTES)
    estrutura = ler_csv(ESTRUTURA)
    crosswalk = ler_csv(CROSSWALK)
    fontes = {r["fonte_id"]: r for r in fontes_rows}

    valida_contra_schema(intensidades, carregar_schema("intensidade.schema.json"),
                         INTENSIDADES.name, erros)
    valida_contra_schema(fontes_rows, carregar_schema("fonte.schema.json"), FONTES.name, erros)
    valida_intensidades(intensidades, fontes, erros)
    valida_estrutura_custo(estrutura, fontes, erros)
    valida_crosswalk(crosswalk, intensidades, erros)

    if len(erros):
        print(f"FALHA - {len(erros)} problema(s):")
        for it in erros.itens:
            print(f"  {it}")
        return 1

    print(f"OK - {len(intensidades)} intensidades, {len(fontes_rows)} fontes, "
          f"{len(estrutura)} linhas de estrutura de custo, {len(crosswalk)} mapeamentos CNAE")
    if "--stats" in sys.argv:
        estatisticas(intensidades, fontes_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
