"""Fixtures do Manta Cronos: XER sintéticos (nenhum dado de cliente)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cronos_xer_sintetico import montar_xer, t  # noqa: E402


@pytest.fixture
def xer_basico():
    """A(5d) -FS-> B(3d) -SS+2d-> C(4d) -> M(fim). D(2d) paralela até M. Feriado 20/01/2025."""
    tarefas = [t("1", "A100", 40), t("2", "A110", 24), t("3", "A120", 32), t("4", "A130", 16),
               t("5", "M900", 0, tipo="TT_FinMile")]
    ligs = [("1", "2", "PR_FS"), ("2", "3", "PR_SS", "1", 16), ("3", "5", "PR_FS"), ("4", "5", "PR_FS")]
    return montar_xer(tarefas, ligs, recursos=[("1", 100000), ("2", 50000), ("3", 80000)])
