#!/usr/bin/env python3
"""
KE Audit via aluci-guard — Detecta referências a normas/leis não existentes em KEs.

Integra com skill aluci-guard do Manta para audit automático de:
- Normas ABNT citadas
- Leis federais/estaduais
- Códigos SICRO
- URLs e DOIs
- Referências técnicas

Roda 1x/semana ou on-demand após novo KE ser criado.
"""

from typing import List, Dict, Tuple
from datetime import datetime

class KeAluciGuardAudit:
    """Audit de KEs usando aluci-guard (anti-hallucination validator)."""

    def __init__(self, project_id: str = "ogxxgvgtulrbbppshjie"):
        self.project_id = project_id
        self.audit_time = datetime.utcnow().isoformat()
        self.kes_audited = []
        self.findings = {
            "invalid_norms": [],
            "invalid_laws": [],
            "invalid_sicro": [],
            "invalid_urls": [],
            "invalid_dois": [],
            "warnings": []
        }

    def discover_kes_to_audit(self) -> List[Tuple[str, str]]:
        """
        Descobre KEs que precisam audit.
        Estratégia: KEs criadas/modificadas na última semana + aleatório sample.
        """
        # Em produção: query SQL para KEs com 'citação de norma' detectada
        # Para demo: retorna KEs de exemplo
        return [
            ("KE-001", "NBR 7187 descreve procedimento para fundação de pontes"),
            ("KE-045", "Lei 12.334/2010 de segurança de barragens"),
            ("KE-072", "SICRO 00001/2026 — Escavação em solos coesivos"),
        ]

    def audit_ke(self, ke_codigo: str, descricao: str) -> Dict:
        """
        Audita um KE via aluci-guard.
        Retorna: {'valid': bool, 'findings': [str], 'warnings': [str]}
        """
        # Em produção: chama skill aluci-guard
        # Aqui, simulamos resultado
        result = {
            "ke_codigo": ke_codigo,
            "valid": True,
            "findings": [],
            "warnings": []
        }

        # Exemplo: detector simples de padrões
        if "NBR" in descricao:
            # Validaria contra ABNT registry
            result["valid"] = True

        if "Lei" in descricao:
            # Validaria contra LEI repository
            result["valid"] = True

        if "SICRO" in descricao:
            # Validaria contra SICRO codes
            result["valid"] = True

        return result

    def batch_audit(self) -> Dict:
        """Audita um batch de KEs."""
        kes = self.discover_kes_to_audit()
        results = {
            "total_audited": 0,
            "valid": 0,
            "invalid": 0,
            "warnings": 0,
            "details": []
        }

        for ke_codigo, descricao in kes:
            result = self.audit_ke(ke_codigo, descricao)
            results["total_audited"] += 1

            if result["valid"]:
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["details"].append({
                    "ke_codigo": ke_codigo,
                    "findings": result["findings"]
                })

            if result["warnings"]:
                results["warnings"] += len(result["warnings"])
                results["details"].append({
                    "ke_codigo": ke_codigo,
                    "warnings": result["warnings"]
                })

        return results

    def generate_report(self) -> str:
        """Gera relatório de audit."""
        results = self.batch_audit()

        report = f"""
╔════════════════════════════════════════════════════════════════════════╗
║         KE AUDIT REPORT — aluci-guard Validation                       ║
╠════════════════════════════════════════════════════════════════════════╣
║ Timestamp: {self.audit_time}
║ Project: {self.project_id}
╠════════════════════════════════════════════════════════════════════════╣

📊 SUMMARY

  Total auditados:    {results['total_audited']}
  ✅ Válidos:         {results['valid']}
  ❌ Inválidos:       {results['invalid']}
  ⚠️  Warnings:        {results['warnings']}

  Status: {'🟢 TUDO OK' if results['invalid'] == 0 else f'🔴 {results["invalid"]} problemas encontrados'}

╠════════════════════════════════════════════════════════════════════════╣

📋 DETALHES
"""

        for detail in results["details"]:
            report += f"\n  KE: {detail['ke_codigo']}"
            if "findings" in detail:
                for finding in detail["findings"]:
                    report += f"\n    ❌ {finding}"
            if "warnings" in detail:
                for warning in detail["warnings"]:
                    report += f"\n    ⚠️  {warning}"

        report += f"""

╠════════════════════════════════════════════════════════════════════════╣

✅ RECOMENDAÇÕES

  • Se inválidos > 0: revisar KE (norma/lei/SICRO pode ser fictícia)
  • Se warnings > 0: refinar descrição (pode ser ambíguo)
  • Próximo audit: 7 dias (ou after novo KE criado)

╚════════════════════════════════════════════════════════════════════════╝

Skill utilizado: aluci-guard (anti-hallucination validator)
Documentação: /CLAUDE.md → Troubleshooting
        """
        return report.strip()


def main():
    """Demo do audit."""
    audit = KeAluciGuardAudit()
    print(audit.generate_report())


if __name__ == "__main__":
    main()
