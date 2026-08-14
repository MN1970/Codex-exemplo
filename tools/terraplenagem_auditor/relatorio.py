from .models import ResultadoAuditoria


def gerar_relatorio(resultado: ResultadoAuditoria, formato: str = "markdown") -> str:
    if formato != "markdown":
        raise ValueError(f"Formato de relatório não suportado: {formato}")

    linhas = ["# Relatório de Auditoria de Movimento de Terra", ""]

    custo_estudo_txt = f"R$ {resultado.custo_estudo:,.2f}" if resultado.custo_estudo is not None else "não informado"
    linhas.append(f"- **Custo proposto no estudo:** {custo_estudo_txt}")
    linhas.append(f"- **Custo ótimo calculado:** R$ {resultado.custo_otimo:,.2f}")
    if resultado.gap_percentual is not None:
        linhas.append(f"- **Gap de otimalidade:** {resultado.gap_percentual:.2f}%")
    linhas.append(f"- **Volume total alocado:** {resultado.volume_total_m3:,.0f} m³")
    linhas.append("")

    linhas.append("## Alocações ótimas")
    linhas.append("")
    linhas.append("| Origem | Destino | Volume (m³) | Distância (m) | Custo (R$) |")
    linhas.append("|---|---|---|---|---|")
    for alocacao in resultado.alocacoes_otimas:
        linhas.append(
            f"| {alocacao.origem} | {alocacao.destino} | {alocacao.volume_m3:,.0f} | "
            f"{alocacao.distancia_m:,.0f} | {alocacao.custo_total:,.2f} |"
        )
    linhas.append("")

    linhas.append("## Alertas")
    linhas.append("")
    if resultado.alertas:
        for alerta in resultado.alertas:
            linhas.append(f"- {alerta}")
    else:
        linhas.append("- Nenhum alerta.")

    return "\n".join(linhas)
