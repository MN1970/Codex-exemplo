#!/usr/bin/env python3
"""
KE Indexing Dashboard — Visualiza status de indexação em tempo real.

Métricas:
- Total KEs
- KEs com embedding
- KEs pendentes
- Taxa de indexação (KEs/dia)
- Histórico de indexação (7 dias)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class KeIndexingDashboard:
    """Dashboard de status de indexação de KEs."""

    def __init__(self, project_id: str = "ogxxgvgtulrbbppshjie"):
        self.project_id = project_id
        self.snapshot_time = datetime.utcnow().isoformat()

    def get_current_status(self) -> Dict:
        """Obtém status atual via queries SQL."""
        # Em produção: result = supabase.execute_sql(query)
        # Para demo:
        return {
            "total_kes": 86,
            "com_embedding": 86,
            "sem_embedding": 0,
            "percentage": 100.0,
            "last_update": datetime.utcnow().isoformat()
        }

    def get_indexing_history(self, days: int = 7) -> List[Dict]:
        """Obtém histórico de indexação (últimos N dias)."""
        # Em produção: busca em tabela de audit
        history = [
            {"date": "2026-07-27", "indexed_today": 5, "cumulative": 86},
            {"date": "2026-07-26", "indexed_today": 8, "cumulative": 81},
            {"date": "2026-07-25", "indexed_today": 12, "cumulative": 73},
            {"date": "2026-07-24", "indexed_today": 15, "cumulative": 61},
            {"date": "2026-07-23", "indexed_today": 10, "cumulative": 46},
            {"date": "2026-07-22", "indexed_today": 20, "cumulative": 36},
            {"date": "2026-07-21", "indexed_today": 36, "cumulative": 16},
        ]
        return history[:days]

    def calculate_metrics(self) -> Dict:
        """Calcula métricas de indexação."""
        status = self.get_current_status()
        history = self.get_indexing_history(7)

        today_indexed = history[0]["indexed_today"] if history else 0
        avg_indexed = sum(h["indexed_today"] for h in history) / len(history) if history else 0

        return {
            "total_kes": status["total_kes"],
            "indexed": status["com_embedding"],
            "pending": status["sem_embedding"],
            "percentage": status["percentage"],
            "today_indexed": today_indexed,
            "avg_per_day_7d": round(avg_indexed, 1),
            "eta_remaining_days": 0 if status["sem_embedding"] == 0 else (
                status["sem_embedding"] / avg_indexed if avg_indexed > 0 else 999
            )
        }

    def render_text_dashboard(self) -> str:
        """Renderiza dashboard em formato texto."""
        status = self.get_current_status()
        metrics = self.calculate_metrics()
        history = self.get_indexing_history(7)

        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                   KE INDEXING DASHBOARD — Manta Maestro                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Snapshot: {self.snapshot_time}
║  Project: {self.project_id}
╠══════════════════════════════════════════════════════════════════════════╣

📊 STATUS ATUAL

  Total KEs:        {metrics['total_kes']:>3}
  ✅ Com embedding: {metrics['indexed']:>3} ({metrics['percentage']:.1f}%)
  ⏳ Pendentes:     {metrics['pending']:>3}

  Status: {'🟢 COMPLETO' if metrics['pending'] == 0 else f'🟡 {metrics["pending"]} pendentes'}

╠══════════════════════════════════════════════════════════════════════════╣

📈 HISTÓRICO — Últimos 7 dias

  Data       Indexados hoje   Acumulado   Linha
  ─────────────────────────────────────────────────────────"""

        for h in history:
            bar = "█" * (h["indexed_today"] // 2)
            dashboard += f"\n  {h['date']}   {h['indexed_today']:>3}              {h['cumulative']:>3}       {bar}"

        dashboard += f"""

╠══════════════════════════════════════════════════════════════════════════╣

📊 MÉTRICAS

  Indexados hoje:     {metrics['today_indexed']} KEs
  Média (7 dias):     {metrics['avg_per_day_7d']:.1f} KEs/dia
  Taxa atual:         {metrics['avg_per_day_7d'] / 7:.1f} KEs/hora (extrapolado)

  ETA (pendentes):    {metrics['eta_remaining_days']:.1f} dias (se continuar taxa atual)

╠══════════════════════════════════════════════════════════════════════════╣

🎯 AÇÕES PRÓXIMAS

  • Status: Tudo OK (100% indexado)
  • Próximo: Monitorar discovery automático (cron 1x/dia)
  • SLA: 0 KEs pendentes > 24h

╚══════════════════════════════════════════════════════════════════════════╝

Gerado em: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        return dashboard.strip()

    def render_html_dashboard(self) -> str:
        """Renderiza dashboard em HTML."""
        metrics = self.calculate_metrics()
        history = self.get_indexing_history(7)

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KE Indexing Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-top: 5px; }}
        .status-ok {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .chart {{ margin-top: 20px; }}
        .bar {{ display: flex; align-items: center; margin: 8px 0; }}
        .bar-label {{ width: 100px; font-size: 12px; }}
        .bar-value {{ flex: 1; background: #0066cc; height: 20px; margin: 0 10px; border-radius: 3px; }}
        .bar-number {{ width: 50px; text-align: right; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 KE Indexing Dashboard — Manta Maestro</h1>
        <p style="color: #666; margin-bottom: 20px;">Snapshot: {self.snapshot_time}</p>

        <div class="grid">
            <div class="card">
                <div class="metric">{metrics['total_kes']}</div>
                <div class="label">Total KEs</div>
            </div>
            <div class="card">
                <div class="metric status-ok">{metrics['indexed']}</div>
                <div class="label">Com Embedding ✅</div>
            </div>
            <div class="card">
                <div class="metric {('status-ok' if metrics['pending'] == 0 else 'status-warning')}">{metrics['pending']}</div>
                <div class="label">Pendentes {'✅' if metrics['pending'] == 0 else '⏳'}</div>
            </div>
            <div class="card">
                <div class="metric">{metrics['percentage']:.1f}%</div>
                <div class="label">Taxa de Indexação</div>
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h2 style="margin-bottom: 15px;">📈 Histórico — Últimos 7 dias</h2>
            <div class="chart">
"""
        for h in history:
            pct = (h["indexed_today"] / 50) * 100  # Normalizar para 50 KEs max
            html += f"""
                <div class="bar">
                    <div class="bar-label">{h['date']}</div>
                    <div class="bar-value" style="width: {pct}%;"></div>
                    <div class="bar-number">{h['indexed_today']}</div>
                </div>
"""
        html += f"""
            </div>
        </div>

        <div class="card" style="margin-top: 20px;">
            <h2 style="margin-bottom: 15px;">📊 Métricas</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px;">Indexados hoje:</td>
                    <td style="padding: 8px; font-weight: bold;">{metrics['today_indexed']} KEs</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px;">Média (7 dias):</td>
                    <td style="padding: 8px; font-weight: bold;">{metrics['avg_per_day_7d']:.1f} KEs/dia</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 8px;">ETA (pendentes):</td>
                    <td style="padding: 8px; font-weight: bold;">{metrics['eta_remaining_days']:.1f} dias</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
        """
        return html.strip()


def main():
    """Demo do dashboard."""
    dashboard = KeIndexingDashboard()

    # Renderizar em texto
    print(dashboard.render_text_dashboard())

    # (Opcional) Renderizar em HTML para arquivo
    # with open('/tmp/ke_dashboard.html', 'w') as f:
    #     f.write(dashboard.render_html_dashboard())
    # print("\n✅ HTML dashboard salvo em /tmp/ke_dashboard.html")


if __name__ == "__main__":
    main()
