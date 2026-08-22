"""
Maestro OS v6.0 — Normative Parser
Extract rules from Lei 12.334, ICOLD, CBDB → verifiable constraints.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ConstraintCategory(Enum):
    """Categoria de constraint."""
    SAFETY = "safety"
    ENVIRONMENTAL = "environmental"
    STRUCTURAL = "structural"
    GEOTECHNICAL = "geotechnical"
    PROCEDURAL = "procedural"


@dataclass
class NormativeRule:
    """Regra extraída de norma/lei."""
    rule_id: str
    source: str                    # 'Lei 12.334', 'ICOLD-194', 'CBDB'
    category: ConstraintCategory
    description: str
    requirement: str               # Descrição do requisito
    verification_method: str       # Como verificar compliance
    applies_to: List[str]          # Tipos de projeto ['barragem', 'concreto']
    penalty_if_violated: str       # Consequência de violação
    is_mandatory: bool = True


class Lei12334Parser:
    """
    Parser de Lei 12.334/2010 (Política Nacional de Segurança de Barragens).

    Extrai regras de:
    - Classificação de barragens (Alto, Médio, Baixo risco)
    - Inspeção periódica
    - Plano de Ação Emergencial (PAE)
    - Revisão de Segurança da Barragem (RSB)
    - Detalhamento de Engenharia (DCE)
    """

    # Mapeamento de palavras-chave para categorias
    KEYWORD_RULES = {
        "pae": "Plano de Ação Emergencial deve ser elaborado para toda barragem",
        "rsb": "Revisão de Segurança da Barragem a cada 5 anos",
        "dce": "Detalhamento de Engenharia deve ser apresentado",
        "inspecao": "Inspeção visual semestral obrigatória",
        "piezometro": "Piezômetros devem ser instalados e monitorados",
        "monitoramento": "Monitoramento contínuo de indicadores críticos",
    }

    def parse_lei_12334(self) -> List[NormativeRule]:
        """
        Extrai regras de Lei 12.334.

        Returns:
            Lista de NormativeRule
        """
        rules = [
            NormativeRule(
                rule_id="lei-12334-001",
                source="Lei 12.334/2010",
                category=ConstraintCategory.PROCEDURAL,
                description="Classificação de barragens por dano potencial",
                requirement="Toda barragem deve ser classificada como Alto, Médio ou Baixo",
                verification_method="Análise de dam breach + população afetada",
                applies_to=["barragem", "hidrelétrica", "saneamento"],
                penalty_if_violated="Multa + proibição de operação"
            ),

            NormativeRule(
                rule_id="lei-12334-002",
                source="Lei 12.334/2010",
                category=ConstraintCategory.SAFETY,
                description="Plano de Ação Emergencial (PAE)",
                requirement="PAE deve ser elaborado e testado anualmente",
                verification_method="Documento PAE + registro de simulado",
                applies_to=["barragem"],
                penalty_if_violated="Multa + suspensão de operação"
            ),

            NormativeRule(
                rule_id="lei-12334-003",
                source="Lei 12.334/2010",
                category=ConstraintCategory.SAFETY,
                description="Revisão de Segurança da Barragem (RSB)",
                requirement="RSB deve ser realizada a cada 5 anos",
                verification_method="Laudo técnico assinado por MENGE",
                applies_to=["barragem"],
                penalty_if_violated="Multa + proibição de operação se RSB vencer"
            ),

            NormativeRule(
                rule_id="lei-12334-004",
                source="Lei 12.334/2010",
                category=ConstraintCategory.PROCEDURAL,
                description="Inspeção periódica",
                requirement="Inspeção visual semestral + inspeção detalhada bienal",
                verification_method="Relatório de inspeção com fotos e métricas",
                applies_to=["barragem"],
                penalty_if_violated="Multa + advertência"
            ),

            NormativeRule(
                rule_id="lei-12334-005",
                source="Lei 12.334/2010",
                category=ConstraintCategory.GEOTECHNICAL,
                description="Instrumentação de monitoramento",
                requirement="Piezômetros, inclinômetros, extensômetros conforme projeto",
                verification_method="Leitura mensal de instrumentação + relatório",
                applies_to=["barragem", "terra", "enrocamento"],
                penalty_if_violated="Multa + obrigação de instalar"
            ),
        ]

        return rules


class ICOLDParser:
    """
    Parser de diretrizes ICOLD (International Commission on Large Dams).

    Bulletins principais:
    - 164: Concrete Face Rockfill Dams (CFRD)
    - 194: Filtered Tailings (Dry Stack)
    - 164: Construction of Embankment Dams
    """

    def parse_icold_bulletins(self) -> List[NormativeRule]:
        """Extrai regras de ICOLD Bulletins."""
        rules = [
            NormativeRule(
                rule_id="icold-164-001",
                source="ICOLD Bulletin 164 (CFRD)",
                category=ConstraintCategory.STRUCTURAL,
                description="Face de concreto em barragem de enrocamento",
                requirement="Espessura mínima 30cm + reforço Q=2φ8@20cm",
                verification_method="Inspeção construtiva + controle de qualidade",
                applies_to=["CFRD", "enrocamento"],
                penalty_if_violated="Reforço obrigatório antes operação"
            ),

            NormativeRule(
                rule_id="icold-194-001",
                source="ICOLD Bulletin 194 (Filtered Tailings)",
                category=ConstraintCategory.GEOTECHNICAL,
                description="Dry stack (rejeitos filtrados)",
                requirement="Teor de umidade < 10% + filtro reverso + drenagem",
                verification_method="Ensaios de laboratório + inspeção de obra",
                applies_to=["rejeitos", "mineração", "TSF"],
                penalty_if_violated="Proibição de alteamento + reprocessamento"
            ),

            NormativeRule(
                rule_id="icold-general-001",
                source="ICOLD Guidelines",
                category=ConstraintCategory.SAFETY,
                description="Análise probabilística de risco (PRA)",
                requirement="PRA para barragens de alto dano potencial",
                verification_method="Modelagem e análise especializada",
                applies_to=["barragem"],
                penalty_if_violated="Análise obrigatória antes operação"
            ),
        ]

        return rules


class ComplianceChecker:
    """
    Verificador de conformidade com normas.

    Fluxo:
    1. Carregador regras de Lei 12.334, ICOLD, CBDB
    2. Receber projeto (features, execução)
    3. Validar contra cada regra
    4. Gerar relatório de conformidade
    """

    def __init__(self):
        self.lei_parser = Lei12334Parser()
        self.icold_parser = ICOLDParser()
        self.all_rules: List[NormativeRule] = []
        self._load_all_rules()

    def _load_all_rules(self):
        """Carrega todas regras disponíveis."""
        self.all_rules = []
        self.all_rules.extend(self.lei_parser.parse_lei_12334())
        self.all_rules.extend(self.icold_parser.parse_icold_bulletins())

    def check_compliance(
        self,
        project_type: str,
        project_features: Dict[str, any]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Verifica conformidade com normas aplicáveis.

        Args:
            project_type: Tipo de projeto ('barragem', 'concreto', etc)
            project_features: Features do projeto

        Returns:
            (compliant_rules, warnings, violations)
        """
        applicable_rules = [
            r for r in self.all_rules
            if any(applies in project_type.lower() for applies in r.applies_to)
        ]

        compliant = []
        warnings = []
        violations = []

        for rule in applicable_rules:
            # Simular verificação
            if self._is_compliant(rule, project_features):
                compliant.append(f"✓ {rule.rule_id}: {rule.description}")
            else:
                if rule.is_mandatory:
                    violations.append(f"✗ {rule.rule_id}: {rule.requirement}")
                else:
                    warnings.append(f"⚠ {rule.rule_id}: {rule.description}")

        return compliant, warnings, violations

    def _is_compliant(self, rule: NormativeRule, features: Dict) -> bool:
        """Simula verificação de conformidade."""
        # Stub: em produção verificar contra features reais
        # Ex: se rule.rule_id == "lei-12334-002" e "pae" em features
        return True

    def generate_compliance_report(
        self,
        project_id: str,
        project_type: str,
        features: Dict
    ) -> str:
        """Gera relatório de conformidade."""
        compliant, warnings, violations = self.check_compliance(project_type, features)

        lines = [
            f"=== RELATÓRIO DE CONFORMIDADE REGULATÓRIA ===",
            f"Projeto: {project_id}",
            f"Tipo: {project_type}",
            f"Data: {__import__('datetime').datetime.utcnow().isoformat()}",
            f"",
            f"CONFORMIDADES ({len(compliant)}):",
        ]

        for item in compliant:
            lines.append(f"  {item}")

        lines.extend([
            f"",
            f"AVISOS ({len(warnings)}):",
        ])

        for item in warnings:
            lines.append(f"  {item}")

        lines.extend([
            f"",
            f"VIOLAÇÕES ({len(violations)}):",
        ])

        for item in violations:
            lines.append(f"  {item}")

        return "\n".join(lines)
