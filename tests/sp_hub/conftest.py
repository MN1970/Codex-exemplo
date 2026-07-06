"""
Fixtures compartilhadas para os testes do SP Hub.

Fornece um FakeSupabase in-memory que implementa a superfície de query builder
usada por `sp_hub.db` — chega para exercitar os fluxos completos sem
supabase-py real.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest


class _Result:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class _Query:
    def __init__(self, fake: "FakeSupabase", table_name: str):
        self.fake = fake
        self.table_name = table_name
        self._filters: list = []
        self._select_cols: str = "*"
        self._order: tuple[str, bool] | None = None
        self._limit: int | None = None
        self._insert_rows: list[dict[str, Any]] | None = None
        self._upsert_rows: list[dict[str, Any]] | None = None
        self._upsert_on_conflict: str | None = None

    def select(self, cols: str) -> "_Query":
        self._select_cols = cols
        return self

    def eq(self, col: str, value: Any) -> "_Query":
        self._filters.append(("eq", col, value))
        return self

    def gt(self, col: str, value: Any) -> "_Query":
        self._filters.append(("gt", col, value))
        return self

    def order(self, col: str, desc: bool = False) -> "_Query":
        self._order = (col, desc)
        return self

    def limit(self, n: int) -> "_Query":
        self._limit = n
        return self

    def insert(self, rows) -> "_Query":
        self._insert_rows = rows if isinstance(rows, list) else [rows]
        return self

    def upsert(self, rows, on_conflict=None) -> "_Query":
        self._upsert_rows = rows if isinstance(rows, list) else [rows]
        self._upsert_on_conflict = on_conflict
        return self

    def execute(self) -> _Result:
        table = self.fake.tables.setdefault(self.table_name, [])

        if self._insert_rows is not None:
            for row in self._insert_rows:
                table.append(dict(row))
            return _Result(list(self._insert_rows))

        if self._upsert_rows is not None:
            key_cols = (
                [c.strip() for c in self._upsert_on_conflict.split(",")]
                if self._upsert_on_conflict
                else []
            )
            written: list[dict[str, Any]] = []
            for row in self._upsert_rows:
                new_row = dict(row)
                if key_cols:
                    match_idx = next(
                        (
                            i
                            for i, existing in enumerate(table)
                            if all(existing.get(k) == new_row.get(k) for k in key_cols)
                        ),
                        None,
                    )
                    if match_idx is not None:
                        table[match_idx].update(new_row)
                        written.append(dict(table[match_idx]))
                        continue
                table.append(new_row)
                written.append(dict(new_row))
            return _Result(written)

        rows = list(table)
        for op, col, value in self._filters:
            if op == "eq":
                rows = [r for r in rows if r.get(col) == value]
            elif op == "gt":
                rows = [r for r in rows if _cmp_gt(r.get(col), value)]

        if self._order is not None:
            col, desc = self._order
            rows.sort(key=lambda r: r.get(col) or "", reverse=desc)

        if self._limit is not None:
            rows = rows[: self._limit]

        return _Result(rows)


def _cmp_gt(left: Any, right: Any) -> bool:
    if left is None:
        return False
    if isinstance(left, str) and isinstance(right, str):
        return left > right
    if isinstance(left, datetime) and isinstance(right, str):
        return left.isoformat() > right
    return left > right  # fallback numérico


class FakeSupabase:
    """Cliente Supabase fake in-memory."""

    def __init__(self):
        self.tables: dict[str, list[dict[str, Any]]] = {}

    def table(self, name: str) -> _Query:
        return _Query(self, name)

    def seed(self, table_name: str, rows: list[dict[str, Any]]) -> None:
        self.tables.setdefault(table_name, []).extend(dict(r) for r in rows)


@pytest.fixture
def fake_client() -> FakeSupabase:
    return FakeSupabase()


@pytest.fixture
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture
def sample_rules() -> list[dict[str, Any]]:
    """Subset representativo das 24 rules seed (mesma semântica da migração)."""
    return [
        {
            "id": 1,
            "rule_name": "cliente_contrato",
            "path_pattern": "02_CLIENTE/*/01_CONTRATO/*",
            "file_ext_pattern": "*",
            "name_pattern": None,
            "target_agents": ["M1", "M2"],
            "doc_type": "contrato",
            "priority": "alta",
            "active": True,
        },
        {
            "id": 4,
            "rule_name": "cliente_projeto",
            "path_pattern": "02_CLIENTE/*/04_PROJETO/*",
            "file_ext_pattern": "*",
            "name_pattern": None,
            "target_agents": ["M3", "M4"],
            "doc_type": "projeto",
            "priority": "alta",
            "active": True,
        },
        {
            "id": 12,
            "rule_name": "ext_dwg_dxf",
            "path_pattern": None,
            "file_ext_pattern": ".dwg,.dxf",
            "name_pattern": None,
            "target_agents": ["M3", "M4"],
            "doc_type": "projeto_cad",
            "priority": "alta",
            "active": True,
        },
        {
            "id": 16,
            "rule_name": "name_sicro",
            "path_pattern": None,
            "file_ext_pattern": "*",
            "name_pattern": r".*SICRO.*",
            "target_agents": ["M7"],
            "doc_type": "composicao_custo",
            "priority": "alta",
            "active": True,
        },
        {
            "id": 15,
            "rule_name": "ext_pdf_generico",
            "path_pattern": None,
            "file_ext_pattern": ".pdf",
            "name_pattern": None,
            "target_agents": ["M18"],
            "doc_type": "pdf_generico",
            "priority": "baixa",
            "active": True,
        },
    ]
