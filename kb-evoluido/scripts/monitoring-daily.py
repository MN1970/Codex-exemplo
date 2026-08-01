#!/usr/bin/env python3
"""
🚀 DAILY HEALTH CHECK — KB Evoluído Maestro v4.2
Executa verificações de saúde diárias durante estabilização (Ago 01-31)
"""

import json
import requests
import os
from datetime import datetime
from pathlib import Path

class DailyHealthCheck:
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()
        self.results = {}
        self.errors = []

        # Environment
        self.supabase_url = os.getenv("SUPABASE_URL", "http://localhost:54321")
        self.supabase_key = os.getenv("SUPABASE_KEY", "test-key")
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        self.alertmanager_url = "http://localhost:9093"
        self.callback_url = "http://127.0.0.1:8001"
        self.airflow_url = "http://localhost:8080"

    def check_supabase(self):
        """Verificar Supabase connectivity e constantes"""
        try:
            headers = {"Authorization": f"Bearer {self.supabase_key}"}
            url = f"{self.supabase_url}/rest/v1/kb_constants?select=id"

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                constants = response.json()
                self.results["supabase"] = {
                    "status": "UP",
                    "constants_count": len(constants),
                    "last_check": self.timestamp
                }
            else:
                self.results["supabase"] = {
                    "status": "ERROR",
                    "code": response.status_code,
                    "error": "Connection failed"
                }
                self.errors.append("Supabase: HTTP error")
        except Exception as e:
            self.results["supabase"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"Supabase: {str(e)}")

    def check_airflow(self):
        """Verificar Airflow DAG status"""
        try:
            url = f"{self.airflow_url}/api/v1/dags/kb_evolution_dag"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                dag = response.json()
                self.results["airflow"] = {
                    "status": "UP",
                    "dag_status": dag.get("is_paused", False),
                    "dag_id": "kb_evolution_dag",
                    "last_check": self.timestamp
                }
            else:
                self.results["airflow"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                self.errors.append("Airflow: HTTP error")
        except Exception as e:
            self.results["airflow"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"Airflow: {str(e)}")

    def check_prometheus(self):
        """Verificar Prometheus"""
        try:
            url = f"{self.prometheus_url}/-/healthy"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                self.results["prometheus"] = {
                    "status": "UP",
                    "last_check": self.timestamp
                }
            else:
                self.results["prometheus"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                self.errors.append("Prometheus: HTTP error")
        except Exception as e:
            self.results["prometheus"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"Prometheus: {str(e)}")

    def check_grafana(self):
        """Verificar Grafana"""
        try:
            url = f"{self.grafana_url}/api/health"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                self.results["grafana"] = {
                    "status": "UP",
                    "last_check": self.timestamp
                }
            else:
                self.results["grafana"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                self.errors.append("Grafana: HTTP error")
        except Exception as e:
            self.results["grafana"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"Grafana: {str(e)}")

    def check_alertmanager(self):
        """Verificar AlertManager"""
        try:
            url = f"{self.alertmanager_url}/api/v1/alerts"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                alerts = response.json().get("data", [])
                critical_count = len([a for a in alerts if a.get("labels", {}).get("severity") == "critical"])

                self.results["alertmanager"] = {
                    "status": "UP",
                    "active_alerts": len(alerts),
                    "critical_alerts": critical_count,
                    "last_check": self.timestamp
                }

                if critical_count > 0:
                    self.errors.append(f"AlertManager: {critical_count} CRITICAL alerts")
            else:
                self.results["alertmanager"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                self.errors.append("AlertManager: HTTP error")
        except Exception as e:
            self.results["alertmanager"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"AlertManager: {str(e)}")

    def check_callback_handler(self):
        """Verificar Callback Handler"""
        try:
            url = f"{self.callback_url}/health"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                health = response.json()
                self.results["callback"] = {
                    "status": health.get("status", "UNKNOWN"),
                    "service": health.get("service", "unknown"),
                    "last_check": self.timestamp
                }
            else:
                self.results["callback"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
                self.errors.append("Callback: HTTP error")
        except Exception as e:
            self.results["callback"] = {
                "status": "DOWN",
                "error": str(e)
            }
            self.errors.append(f"Callback: {str(e)}")

    def check_feedback_summary(self):
        """Verificar Feedback Loop Summary"""
        try:
            url = f"{self.callback_url}/feedback/summary"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                summary = response.json()
                self.results["feedback"] = {
                    "status": "UP",
                    "approval_rate": summary.get("approval_rate", 0),
                    "patterns_detected": summary.get("patterns_detected", 0),
                    "last_check": self.timestamp
                }
            else:
                self.results["feedback"] = {
                    "status": "ERROR",
                    "code": response.status_code
                }
        except Exception as e:
            self.results["feedback"] = {
                "status": "DOWN",
                "error": str(e)
            }

    def run_all_checks(self):
        """Executar todas as verificações"""
        self.check_supabase()
        self.check_airflow()
        self.check_prometheus()
        self.check_grafana()
        self.check_alertmanager()
        self.check_callback_handler()
        self.check_feedback_summary()

    def generate_report(self):
        """Gerar relatório de saúde"""
        print("\n" + "="*70)
        print(f"📊 DAILY HEALTH CHECK — {self.timestamp}")
        print("="*70 + "\n")

        # Summary
        total_checks = len(self.results)
        up_count = sum(1 for r in self.results.values() if r.get("status") == "UP")
        down_count = sum(1 for r in self.results.values() if r.get("status") == "DOWN")
        error_count = sum(1 for r in self.results.values() if r.get("status") == "ERROR")

        print(f"✅ UP: {up_count}/{total_checks}")
        print(f"⚠️  ERROR: {error_count}/{total_checks}")
        print(f"❌ DOWN: {down_count}/{total_checks}\n")

        # Details
        for service, result in self.results.items():
            status_icon = "✅" if result.get("status") == "UP" else "❌"
            print(f"{status_icon} {service.upper():20} {result.get('status')}")

            # Extra info
            if service == "supabase" and "constants_count" in result:
                print(f"   └─ Constants: {result['constants_count']}")
            elif service == "alertmanager" and "active_alerts" in result:
                print(f"   └─ Alerts: {result['active_alerts']} (Critical: {result['critical_alerts']})")
            elif service == "feedback" and "approval_rate" in result:
                print(f"   └─ Approval rate: {result['approval_rate']:.1%}")
            elif service == "airflow" and "dag_status" in result:
                dag_status = "PAUSED" if result['dag_status'] else "ACTIVE"
                print(f"   └─ DAG status: {dag_status}")

        print("\n" + "="*70)

        # Errors
        if self.errors:
            print("\n⚠️  ERRORS DETECTED:")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("\n✅ NO ERRORS")

        print("\n" + "="*70)

        return {
            "timestamp": self.timestamp,
            "summary": {
                "total_checks": total_checks,
                "up": up_count,
                "error": error_count,
                "down": down_count
            },
            "results": self.results,
            "errors": self.errors
        }

    def save_report(self):
        """Salvar relatório em JSON"""
        report = self.generate_report()

        # Create monitoring directory if needed
        Path("monitoring").mkdir(exist_ok=True)

        # Salvar com timestamp
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"monitoring/health_check_{date_str}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved: {filename}")
        return report

if __name__ == "__main__":
    health_check = DailyHealthCheck()
    health_check.run_all_checks()
    health_check.save_report()
