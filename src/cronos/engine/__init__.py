"""Motor determinístico do Manta Cronos (sem dependência do Agent SDK)."""
from .calendar import Calendario, calendario_padrao, ler_clndr_data
from .dcma import dcma14
from .model import Atividade, Ligacao, Projeto, Restricao
from .mspdi import gravar_mspdi, ler_mspdi
from .schedule import calcular, comparar, folga_dias, monte_carlo
from .xer import e_historico, gravar_xer, ler_xer


def ler_arquivo(caminho: str, incluir_historico: bool = False) -> list[Projeto]:
    """Lê .xer ou .xml. Versões obsoletas (OBSOLETO, DEPRECATED, 99-backup) são recusadas
    salvo `incluir_historico=True`, conforme a regra "só dados vigentes"."""
    if e_historico(caminho) and not incluir_historico:
        raise PermissionError(f"Versão histórica ignorada: {caminho} (use incluir_historico)")
    ext = caminho.lower().rsplit(".", 1)[-1]
    if ext == "xer":
        return ler_xer(caminho)
    if ext == "xml":
        return ler_mspdi(caminho)
    raise ValueError(f"Formato ainda não suportado: .{ext} (.mpp: salve como XML no MS Project)")


__all__ = ["Atividade", "Calendario", "Ligacao", "Projeto", "Restricao", "calcular", "calendario_padrao",
           "comparar", "dcma14", "e_historico", "folga_dias", "gravar_mspdi", "gravar_xer", "ler_arquivo",
           "ler_clndr_data", "ler_mspdi", "ler_xer", "monte_carlo"]
