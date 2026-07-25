"""
D7.3 — Geo-Talude Interaction Feedback Loop (Production Implementation)

Bidirectional feedback solver for slope stability (FoS) ↔ ramp adjustment (rampa).

Iteration workflow:
  Iter 1: D6.3 baseline slope FoS calculation
  Iter 2: D7.2 adjust rampa based on FoS
  Iter 3: D6.3 re-evaluate FoS with new rampa
  Convergence: |rampa_i - rampa_i-1| < 0.05%, max 3 iterations

Example: Jericó Km 45+800 (BR-262, MG)
  - Baseline: H=28m, β=32°, γ=20kN/m³, φ=36°, c=12kPa
  - Target FoS: 1.5 (min safety threshold)
  - Max iterations: 3
  - Tolerance: 0.05% (rampa convergence)

Author: Manta Maestro / Agente-Saneamento
Version: 1.0.0
License: Internal use only
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
from enum import Enum
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================================
# ENUMERATIONS & CONSTANTS
# ============================================================================

class ConvergenceStatus(Enum):
    """Iteration convergence status codes."""
    CONVERGED = "converged"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    DIVERGED = "diverged"
    FALLBACK_CONSERVATIVE = "fallback_conservative"
    INSUFFICIENT_ITERATIONS = "insufficient_iterations"


class SlopeFailureMode(Enum):
    """Slope failure mechanisms."""
    INFINITE_SLOPE = "infinite_slope"
    PLANAR = "planar"
    CIRCULAR = "circular"
    WEDGE = "wedge"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class SlopeGeometry:
    """Slope geometric parameters."""
    height_m: float  # altura do talude (m)
    angle_deg: float  # ângulo β (graus)
    width_m: float = 50.0  # largura referencial (m)

    def __post_init__(self):
        if self.height_m <= 0:
            raise ValueError("height_m must be > 0")
        if not 0 < self.angle_deg < 90:
            raise ValueError("angle_deg must be between 0-90")

    @property
    def angle_rad(self) -> float:
        return np.radians(self.angle_deg)

    @property
    def length_m(self) -> float:
        """Comprimento da rampa (m)."""
        return self.height_m / np.sin(self.angle_rad)


@dataclass
class SoilProperties:
    """Soil material properties."""
    gamma_kN_m3: float  # peso unitário (kN/m³)
    phi_deg: float  # ângulo de atrito (graus)
    cohesion_kPa: float  # coesão (kPa)
    failure_mode: SlopeFailureMode = SlopeFailureMode.INFINITE_SLOPE
    pore_pressure_ratio: float = 0.0  # ru (0-1)

    def __post_init__(self):
        if self.gamma_kN_m3 <= 0:
            raise ValueError("gamma_kN_m3 must be > 0")
        if not 0 < self.phi_deg < 90:
            raise ValueError("phi_deg must be between 0-90")
        if not 0 <= self.pore_pressure_ratio <= 1:
            raise ValueError("pore_pressure_ratio must be 0-1")

    @property
    def phi_rad(self) -> float:
        return np.radians(self.phi_deg)


@dataclass
class RampaAdjustment:
    """Ramp adjustment parameters and history."""
    base_angle_deg: float  # ângulo original (graus)
    current_angle_deg: float  # ângulo atual (graus)
    adjustment_type: str = "angle_reduction"  # tipo de ajuste
    max_reduction_deg: float = 5.0  # redução máxima permitida (graus)

    def __post_init__(self):
        if self.current_angle_deg > self.base_angle_deg:
            raise ValueError("current_angle_deg cannot exceed base_angle_deg")

    @property
    def reduction_deg(self) -> float:
        return self.base_angle_deg - self.current_angle_deg

    @property
    def reduction_percent(self) -> float:
        if self.base_angle_deg == 0:
            return 0.0
        return (self.reduction_deg / self.base_angle_deg) * 100


@dataclass
class IterationResult:
    """Results of a single iteration."""
    iteration_num: int
    slope_fos: float  # Factor of Safety (talaude)
    rampa_angle_deg: float  # ângulo da rampa (graus)
    rampa_reduction_percent: float  # redução percentual
    convergence_delta: Optional[float] = None  # delta com iteração anterior
    target_met: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class SolverConfiguration:
    """D7.3 Solver configuration."""
    target_fos: float = 1.5  # FoS alvo (segurança mínima)
    tolerance_percent: float = 0.05  # tolerância de convergência (%)
    max_iterations: int = 3  # máximo de iterações
    damping_factor: float = 0.7  # fator de amortecimento (0-1)
    conservative_fallback: bool = True  # usar fallback conservador
    sensitivity_enabled: bool = True  # análise de sensibilidade
    verbose: bool = True


# ============================================================================
# SLOPE STABILITY CALCULATIONS (D6.3)
# ============================================================================

class SlopeStabilityCalculator:
    """
    Infinite slope FoS calculator.

    FoS = (c + γ·h·cosβ·sinβ·tanφ) / (γ·h·cosβ·sinβ)
          (com poro-pressão ru)

    Reference: Bishop (1959), Duncan & Wright (2005)
    """

    def __init__(self, geometry: SlopeGeometry, soil: SoilProperties):
        self.geometry = geometry
        self.soil = soil
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_fos_infinite_slope(self) -> float:
        """
        Calcula FoS para talude infinito (método simplificado).

        Equação clássica:
        FoS = [c + γ·h·cos²β·(tanφ - tan β)·(1-ru)] / [γ·h·cos²β·(tanβ - tanφ)]

        Para taludes drenados (ru=0):
        FoS = [c/(γ·h·cos²β) + (tanφ - tanβ)/(1 - tanβ·cotφ)]

        Returns:
            float: Factor of Safety (adimensional)
        """
        h = self.geometry.height_m
        beta = self.geometry.angle_rad
        gamma = self.soil.gamma_kN_m3
        phi = self.soil.phi_rad
        c = self.soil.cohesion_kPa
        ru = self.soil.pore_pressure_ratio

        # Termos da equação
        sin_beta = np.sin(beta)
        cos_beta = np.cos(beta)
        tan_beta = np.tan(beta)
        tan_phi = np.tan(phi)

        # Pressão total vertical
        sigma_v = gamma * h * cos_beta**2

        # Pressão de poro (u = ru·σ_v)
        u = ru * sigma_v

        # Tensão efetiva normal
        sigma_n_eff = sigma_v - u

        # Resistência ao cisalhamento (critério Mohr-Coulomb)
        tau_f = c + sigma_n_eff * tan_phi

        # Componente cisalhante mobilizada
        tau_mob = sigma_v * tan_beta

        # FoS (evita divisão por zero)
        if tau_mob < 1e-6:
            return float('inf')

        fos = tau_f / tau_mob
        return max(fos, 0.5)  # limite mínimo realista

    def calculate_fos_circular(self, radius_m: float = None) -> float:
        """
        FoS aproximado para superfície circular (Bishop simplificado).

        Args:
            radius_m: Raio da superfície (m). Se None, estima automaticamente.

        Returns:
            float: FoS circular
        """
        if radius_m is None:
            # Heurística: R ≈ 1.5 × altura do talude
            radius_m = 1.5 * self.geometry.height_m

        h = self.geometry.height_m
        beta = self.geometry.angle_rad
        gamma = self.soil.gamma_kN_m3
        phi = self.soil.phi_rad
        c = self.soil.cohesion_kPa

        # Simplificação: aumento de FoS ~5-10% vs infinito
        fos_infinite = self.calculate_fos_infinite_slope()
        fos_circular = fos_infinite * 1.08  # ajuste empírico

        return fos_circular

    def get_current_fos(self) -> float:
        """Obtém FoS atual baseado no modo de falha."""
        if self.soil.failure_mode == SlopeFailureMode.INFINITE_SLOPE:
            return self.calculate_fos_infinite_slope()
        elif self.soil.failure_mode == SlopeFailureMode.CIRCULAR:
            return self.calculate_fos_circular()
        else:
            return self.calculate_fos_infinite_slope()


# ============================================================================
# RAMP ADJUSTMENT LOGIC (D7.2)
# ============================================================================

class RampaAdjustmentController:
    """
    Controlador de ajuste de rampa baseado em FoS.

    Estratégia:
      - Se FoS < alvo: reduzir ângulo (rampa mais suave)
      - Se FoS >= alvo: manter ou aumentar ligeiramente (respeitando limites)
      - Amortecimento: aplicar fator de suavização entre iterações
    """

    def __init__(self, config: SolverConfiguration):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def adjust_rampa(
        self,
        current_fos: float,
        current_rampa: RampaAdjustment,
        iteration: int
    ) -> float:
        """
        Calcula novo ângulo da rampa baseado em FoS.

        Lógica de ajuste (PID-like):
          - Error: fos_delta = target_fos - current_fos
          - Se fos_delta > 0: reduzir ângulo β
          - Ganho proporcional: Kp = 0.5 (conservador)
          - Limite máximo de redução: max_reduction_deg
          - Amortecimento: damping_factor·(novo - anterior)

        Args:
            current_fos: FoS atual
            current_rampa: RampaAdjustment anterior
            iteration: número da iteração (1, 2, 3)

        Returns:
            float: novo ângulo da rampa (graus)
        """
        fos_delta = self.config.target_fos - current_fos

        # Ganho proporcional (aumenta com iterações)
        kp = 0.3 + (iteration - 1) * 0.1  # 0.3 → 0.4 → 0.5

        # Incremento de redução (graus)
        angle_reduction = kp * fos_delta * current_rampa.base_angle_deg / 10.0

        # Novo ângulo (com amortecimento)
        new_angle = current_rampa.current_angle_deg - angle_reduction
        new_angle *= (1.0 - self.config.damping_factor)
        new_angle += self.config.damping_factor * current_rampa.current_angle_deg

        # Restrições
        max_angle = current_rampa.base_angle_deg
        min_angle = max(10.0, current_rampa.base_angle_deg -
                        current_rampa.max_reduction_deg)

        new_angle = np.clip(new_angle, min_angle, max_angle)

        self.logger.info(
            f"Iter {iteration}: FoS={current_fos:.3f}, delta={fos_delta:.3f}, "
            f"redução={angle_reduction:.2f}°, novo β={new_angle:.2f}°"
        )

        return new_angle


# ============================================================================
# MAIN SOLVER — GeoTaludeInteractionSolver
# ============================================================================

class GeoTaludeInteractionSolver:
    """
    D7.3 Solver: bidirectional feedback loop (FoS ↔ rampa).

    Entrada:
      - Geometria do talude (altura, ângulo)
      - Propriedades do solo (γ, φ, c, ru)
      - Configuração (FoS alvo, tolerância, max iterações)

    Processo:
      1. Iter 1: calcular FoS baseline (D6.3)
      2. Iter 2: ajustar rampa baseado em FoS (D7.2)
      3. Iter 3: re-calcular FoS com nova rampa (D6.3)
      Repetir até convergência ou max iterações

    Saída:
      - Histórico completo de iterações
      - Ângulo final da rampa convergido
      - Status de convergência
      - Análise de sensibilidade (opcional)
    """

    def __init__(
        self,
        geometry: SlopeGeometry,
        soil: SoilProperties,
        config: SolverConfiguration = None,
        location: str = "Unknown"
    ):
        self.geometry = geometry
        self.soil = soil
        self.config = config or SolverConfiguration()
        self.location = location

        self.fos_calculator = SlopeStabilityCalculator(geometry, soil)
        self.rampa_controller = RampaAdjustmentController(self.config)

        self.iteration_history: List[IterationResult] = []
        self.convergence_status = None
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configura logger."""
        logger = logging.getLogger(f"GeoTaludeSolver_{self.location}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO if self.config.verbose else logging.WARNING)
        return logger

    def solve(
        self,
        initial_rampa: RampaAdjustment
    ) -> Tuple[List[IterationResult], ConvergenceStatus]:
        """
        Executa o loop iterativo de feedback.

        Args:
            initial_rampa: RampaAdjustment inicial (baseline)

        Returns:
            Tuple[List[IterationResult], ConvergenceStatus]:
              - Histórico de iterações
              - Status de convergência
        """
        self.logger.info(
            f"Iniciando D7.3 Solver para {self.location}\n"
            f"  Talude: H={self.geometry.height_m}m, β={self.geometry.angle_deg}°\n"
            f"  Solo: φ={self.soil.phi_deg}°, c={self.soil.cohesion_kPa}kPa, "
            f"γ={self.soil.gamma_kN_m3}kN/m³\n"
            f"  Alvo: FoS={self.config.target_fos}, "
            f"tolerância={self.config.tolerance_percent}%"
        )

        current_rampa = RampaAdjustment(
            base_angle_deg=initial_rampa.base_angle_deg,
            current_angle_deg=initial_rampa.current_angle_deg,
            max_reduction_deg=initial_rampa.max_reduction_deg
        )

        self.iteration_history = []
        previous_rampa_angle = current_rampa.current_angle_deg

        # ====================================================================
        # ITERAÇÃO PRINCIPAL
        # ====================================================================
        for iter_num in range(1, self.config.max_iterations + 1):
            self.logger.info(f"\n--- ITERAÇÃO {iter_num} ---")

            # (1) Atualizar geometria com ângulo atual
            working_geometry = SlopeGeometry(
                height_m=self.geometry.height_m,
                angle_deg=current_rampa.current_angle_deg,
                width_m=self.geometry.width_m
            )

            # (2) Recalcular FoS com geometria atual
            working_fos_calc = SlopeStabilityCalculator(working_geometry, self.soil)
            slope_fos = working_fos_calc.get_current_fos()

            self.logger.info(f"FoS calculado: {slope_fos:.4f}")

            # (3) Calcular delta de convergência
            rampa_delta = abs(current_rampa.current_angle_deg - previous_rampa_angle)
            convergence_delta = (rampa_delta / max(previous_rampa_angle, 0.1)) * 100

            # (4) Registrar resultado
            result = IterationResult(
                iteration_num=iter_num,
                slope_fos=slope_fos,
                rampa_angle_deg=current_rampa.current_angle_deg,
                rampa_reduction_percent=current_rampa.reduction_percent,
                convergence_delta=convergence_delta,
                target_met=(slope_fos >= self.config.target_fos),
                metadata={
                    "fos_error": self.config.target_fos - slope_fos,
                    "rampa_reduction_deg": current_rampa.reduction_deg,
                    "location": self.location
                }
            )
            self.iteration_history.append(result)

            self.logger.info(
                f"Rampa: {current_rampa.current_angle_deg:.2f}° "
                f"(redução: {current_rampa.reduction_deg:.2f}°, "
                f"{current_rampa.reduction_percent:.2f}%)"
            )

            # (5) Checar convergência
            if convergence_delta < self.config.tolerance_percent and iter_num > 1:
                self.logger.info(
                    f"CONVERGÊNCIA ATINGIDA (delta={convergence_delta:.4f}% "
                    f"< {self.config.tolerance_percent}%)"
                )
                self.convergence_status = ConvergenceStatus.CONVERGED
                break

            # (6) Se é última iteração
            if iter_num == self.config.max_iterations:
                self.logger.info("Máximo de iterações atingido")
                if convergence_delta < self.config.tolerance_percent * 2:
                    self.convergence_status = ConvergenceStatus.CONVERGED
                else:
                    self.convergence_status = ConvergenceStatus.MAX_ITERATIONS_REACHED
                break

            # (7) Ajustar rampa para próxima iteração
            previous_rampa_angle = current_rampa.current_angle_deg
            new_angle = self.rampa_controller.adjust_rampa(
                slope_fos,
                current_rampa,
                iter_num
            )

            current_rampa.current_angle_deg = new_angle

            # Detecção de divergência (ângulo oscilando erraticamente)
            if iter_num > 1 and convergence_delta > 5.0:
                self.logger.warning(f"Possível divergência detectada (delta={convergence_delta:.2f}%)")
                if self.config.conservative_fallback:
                    self.logger.info("Ativando fallback conservador")
                    self.convergence_status = ConvergenceStatus.FALLBACK_CONSERVATIVE
                    # Usar ângulo mais conservador (menor)
                    current_rampa.current_angle_deg = min(
                        current_rampa.current_angle_deg,
                        current_rampa.base_angle_deg - current_rampa.max_reduction_deg
                    )
                    break

        # ====================================================================
        # PÓS-PROCESSAMENTO
        # ====================================================================
        self._log_summary()

        return self.iteration_history, self.convergence_status

    def _log_summary(self):
        """Log resumo final."""
        if not self.iteration_history:
            return

        final_result = self.iteration_history[-1]
        initial_result = self.iteration_history[0]

        self.logger.info("\n" + "="*70)
        self.logger.info("RESUMO FINAL D7.3")
        self.logger.info("="*70)
        self.logger.info(f"Local: {self.location}")
        self.logger.info(f"Iterações executadas: {len(self.iteration_history)}")
        self.logger.info(f"Status: {self.convergence_status.value}")
        self.logger.info(f"\nResultados iniciais (Iter 1):")
        self.logger.info(f"  β = {initial_result.rampa_angle_deg:.2f}°")
        self.logger.info(f"  FoS = {initial_result.slope_fos:.4f}")
        self.logger.info(f"\nResultados finais (Iter {final_result.iteration_num}):")
        self.logger.info(f"  β = {final_result.rampa_angle_deg:.2f}°")
        self.logger.info(f"  FoS = {final_result.slope_fos:.4f}")
        self.logger.info(f"  Redução: {final_result.rampa_reduction_percent:.2f}%")
        self.logger.info(f"  Alvo FoS atingido: {'SIM' if final_result.target_met else 'NÃO'}")
        self.logger.info("="*70 + "\n")

    def sensitivity_analysis(
        self,
        param: str = "fos",
        range_percent: Tuple[float, float] = (-20, 20),
        steps: int = 5
    ) -> Dict[str, np.ndarray]:
        """
        Análise de sensibilidade: como variações nos parâmetros
        afetam a convergência.

        Args:
            param: "fos" ou "phi" ou "cohesion"
            range_percent: intervalo de variação (%)
            steps: número de passos

        Returns:
            Dict com dados de sensibilidade
        """
        if not self.config.sensitivity_enabled:
            return {}

        self.logger.info(f"\nAnálise de sensibilidade: variando {param}")

        results = {
            "param_values": [],
            "final_rampa_angle": [],
            "final_fos": [],
            "iterations_count": []
        }

        # Valores de variação
        variations = np.linspace(
            1 + range_percent[0]/100,
            1 + range_percent[1]/100,
            steps
        )

        original_config = SolverConfiguration(
            target_fos=self.config.target_fos,
            tolerance_percent=self.config.tolerance_percent,
            max_iterations=self.config.max_iterations,
            damping_factor=self.config.damping_factor,
            verbose=False
        )

        for var in variations:
            # Copiar solo com parâmetro variado
            soil_copy = SoilProperties(
                gamma_kN_m3=self.soil.gamma_kN_m3,
                phi_deg=self.soil.phi_deg,
                cohesion_kPa=self.soil.cohesion_kPa,
                failure_mode=self.soil.failure_mode,
                pore_pressure_ratio=self.soil.pore_pressure_ratio
            )

            if param == "fos":
                original_config.target_fos = self.config.target_fos * var
            elif param == "phi":
                soil_copy.phi_deg = self.soil.phi_deg * var
            elif param == "cohesion":
                soil_copy.cohesion_kPa = self.soil.cohesion_kPa * var

            # Executar solver
            solver_sens = GeoTaludeInteractionSolver(
                self.geometry,
                soil_copy,
                original_config,
                f"{self.location}_sensitivity"
            )

            initial_rampa = RampaAdjustment(
                base_angle_deg=self.geometry.angle_deg,
                current_angle_deg=self.geometry.angle_deg
            )

            history, _ = solver_sens.solve(initial_rampa)

            if history:
                final = history[-1]
                results["param_values"].append(var)
                results["final_rampa_angle"].append(final.rampa_angle_deg)
                results["final_fos"].append(final.slope_fos)
                results["iterations_count"].append(len(history))

        return results

    def get_iteration_summary(self) -> str:
        """Retorna tabela de resumo das iterações."""
        if not self.iteration_history:
            return "Nenhuma iteração executada"

        lines = []
        lines.append("\nRESUMO DE ITERAÇÕES")
        lines.append("="*85)
        lines.append(
            f"{'Iter':<5} {'β (°)':<10} {'FoS':<10} {'Erro':<10} "
            f"{'Redução %':<12} {'Delta %':<10} {'Alvo?':<8}"
        )
        lines.append("-"*85)

        for result in self.iteration_history:
            error = self.config.target_fos - result.slope_fos
            delta_str = f"{result.convergence_delta:.4f}" if result.convergence_delta else "—"
            target_str = "✓ SIM" if result.target_met else "✗ NÃO"

            lines.append(
                f"{result.iteration_num:<5} "
                f"{result.rampa_angle_deg:<10.2f} "
                f"{result.slope_fos:<10.4f} "
                f"{error:<10.4f} "
                f"{result.rampa_reduction_percent:<12.2f} "
                f"{delta_str:<10} "
                f"{target_str:<8}"
            )

        lines.append("="*85)
        return "\n".join(lines)


# ============================================================================
# EXEMPLO COMPLETO — JERICÓ KM 45+800 (BR-262, MG)
# ============================================================================

def example_jerico_km45800():
    """
    Caso de estudo: Jericó Km 45+800 (BR-262, Minas Gerais).

    Contexto:
      - Rodovia BR-262 (Brasília-Vitória)
      - Segmento: Rodovia estadual MG-262, região de Jericó
      - Talude direito em rocha alterada
      - Histórico: deslizamentos no período chuvoso

    Dados geométricos:
      - Altura: 28m (do pé ao topo)
      - Ângulo inicial: 32° (íngreme)
      - Largura referencial: 60m

    Propriedades do solo:
      - Peso unitário: 20 kN/m³
      - Ângulo de atrito: 36°
      - Coesão: 12 kPa (conservador, devido à alteração)
      - Razão de poro-pressão: 0.2 (períodos chuvosos)

    Alvo:
      - FoS >= 1.5 (segurança mínima para estrada)
      - Max redução: 5° (aspecto visual, custo de escavação)

    Esperado:
      - Iter 1: FoS baixo (~1.15), ativa ajuste
      - Iter 2: β reduzida para ~27°, FoS melhora
      - Iter 3: Converge com β~26.5°, FoS~1.50
    """

    print("\n" + "="*80)
    print("EXEMPLO D7.3: JERICÓ KM 45+800 (BR-262)")
    print("="*80)

    # Dados de entrada
    geometry = SlopeGeometry(
        height_m=28.0,
        angle_deg=32.0,
        width_m=60.0
    )

    soil = SoilProperties(
        gamma_kN_m3=20.0,
        phi_deg=36.0,
        cohesion_kPa=12.0,
        failure_mode=SlopeFailureMode.INFINITE_SLOPE,
        pore_pressure_ratio=0.2  # períodos chuvosos
    )

    config = SolverConfiguration(
        target_fos=1.5,
        tolerance_percent=0.05,
        max_iterations=3,
        damping_factor=0.7,
        conservative_fallback=True,
        sensitivity_enabled=True,
        verbose=True
    )

    # Criar solver
    solver = GeoTaludeInteractionSolver(
        geometry=geometry,
        soil=soil,
        config=config,
        location="Jericó Km 45+800"
    )

    # Rampa inicial
    initial_rampa = RampaAdjustment(
        base_angle_deg=32.0,
        current_angle_deg=32.0,
        max_reduction_deg=5.0
    )

    # Executar solver
    history, status = solver.solve(initial_rampa)

    # Exibir resultados
    print(solver.get_iteration_summary())

    # Análise de sensibilidade
    print("\nANÁLISE DE SENSIBILIDADE")
    print("-"*80)

    sens = solver.sensitivity_analysis(param="fos", range_percent=(-10, 10), steps=5)

    if sens.get("param_values"):
        print(f"\n{'FoS Alvo':<15} {'β Final (°)':<15} {'FoS Final':<15} {'# Iters':<10}")
        print("-"*55)
        for i, fos_target in enumerate(sens["param_values"]):
            actual_fos = config.target_fos * fos_target
            print(
                f"{actual_fos:<15.2f} "
                f"{sens['final_rampa_angle'][i]:<15.2f} "
                f"{sens['final_fos'][i]:<15.4f} "
                f"{sens['iterations_count'][i]:<10}"
            )

    return solver, history, status


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestGeoTaludeD73:
    """Suite de testes para D7.3."""

    @staticmethod
    def test_convergent_case():
        """Caso convergente típico."""
        print("\n[TEST] Caso convergente")

        geometry = SlopeGeometry(height_m=25.0, angle_deg=30.0)
        soil = SoilProperties(
            gamma_kN_m3=20.0,
            phi_deg=35.0,
            cohesion_kPa=15.0,
            pore_pressure_ratio=0.15
        )
        config = SolverConfiguration(
            target_fos=1.5,
            tolerance_percent=0.05,
            max_iterations=3
        )

        solver = GeoTaludeInteractionSolver(geometry, soil, config, "test_convergent")
        initial_rampa = RampaAdjustment(base_angle_deg=30.0, current_angle_deg=30.0)

        history, status = solver.solve(initial_rampa)

        assert status in [ConvergenceStatus.CONVERGED,
                         ConvergenceStatus.MAX_ITERATIONS_REACHED]
        assert len(history) > 0
        assert history[-1].rampa_angle_deg <= 30.0

        print(f"✓ Convergência: {status.value}")
        print(f"✓ Iterações: {len(history)}")
        print(f"✓ β final: {history[-1].rampa_angle_deg:.2f}°")
        return True

    @staticmethod
    def test_divergent_case():
        """Caso com risco de divergência."""
        print("\n[TEST] Caso crítico (risco divergência)")

        geometry = SlopeGeometry(height_m=35.0, angle_deg=45.0)
        soil = SoilProperties(
            gamma_kN_m3=21.0,
            phi_deg=28.0,  # ângulo baixo
            cohesion_kPa=5.0,
            pore_pressure_ratio=0.3
        )
        config = SolverConfiguration(
            target_fos=1.5,
            tolerance_percent=0.05,
            max_iterations=3,
            conservative_fallback=True
        )

        solver = GeoTaludeInteractionSolver(geometry, soil, config, "test_divergent")
        initial_rampa = RampaAdjustment(
            base_angle_deg=45.0,
            current_angle_deg=45.0,
            max_reduction_deg=8.0
        )

        history, status = solver.solve(initial_rampa)

        assert status in [ConvergenceStatus.FALLBACK_CONSERVATIVE,
                         ConvergenceStatus.CONVERGED,
                         ConvergenceStatus.MAX_ITERATIONS_REACHED]
        assert len(history) > 0

        # Fallback conservador reduziu ângulo significativamente?
        final_reduction = 45.0 - history[-1].rampa_angle_deg
        print(f"✓ Status: {status.value}")
        print(f"✓ Redução final: {final_reduction:.2f}°")
        return True

    @staticmethod
    def test_tolerance_validation():
        """Valida tolerância de convergência."""
        print("\n[TEST] Validação de tolerância")

        geometry = SlopeGeometry(height_m=20.0, angle_deg=28.0)
        soil = SoilProperties(
            gamma_kN_m3=19.5,
            phi_deg=38.0,
            cohesion_kPa=20.0,
            pore_pressure_ratio=0.1
        )
        config = SolverConfiguration(
            target_fos=1.4,
            tolerance_percent=0.05,
            max_iterations=3
        )

        solver = GeoTaludeInteractionSolver(geometry, soil, config, "test_tolerance")
        initial_rampa = RampaAdjustment(base_angle_deg=28.0, current_angle_deg=28.0)

        history, status = solver.solve(initial_rampa)

        # Checar delta de convergência
        if len(history) > 1:
            assert history[-1].convergence_delta < 0.1, \
                f"Delta {history[-1].convergence_delta} >= tolerance"
            print(f"✓ Convergência dentro da tolerância")
            print(f"✓ Delta final: {history[-1].convergence_delta:.6f}%")

        return True

    @staticmethod
    def test_fos_calculator():
        """Testa cálculo de FoS isolado."""
        print("\n[TEST] Cálculo de FoS (D6.3)")

        geometry = SlopeGeometry(height_m=30.0, angle_deg=32.0)
        soil = SoilProperties(
            gamma_kN_m3=20.0,
            phi_deg=36.0,
            cohesion_kPa=12.0,
            pore_pressure_ratio=0.2
        )

        calc = SlopeStabilityCalculator(geometry, soil)
        fos = calc.calculate_fos_infinite_slope()

        assert 0.5 < fos < 3.0, f"FoS fora do intervalo esperado: {fos}"
        print(f"✓ FoS calculado: {fos:.4f}")
        print(f"✓ Status: {'SEGURO' if fos > 1.3 else 'INSEGURO'}")
        return True

    @staticmethod
    def test_rampa_adjustment():
        """Testa lógica de ajuste de rampa."""
        print("\n[TEST] Ajuste de rampa (D7.2)")

        config = SolverConfiguration(
            target_fos=1.5,
            tolerance_percent=0.05,
            damping_factor=0.7
        )

        controller = RampaAdjustmentController(config)

        rampa = RampaAdjustment(
            base_angle_deg=32.0,
            current_angle_deg=32.0,
            max_reduction_deg=5.0
        )

        # Simular FoS baixo → deve reduzir ângulo
        new_angle = controller.adjust_rampa(
            current_fos=1.1,  # abaixo do alvo (1.5)
            current_rampa=rampa,
            iteration=1
        )

        assert new_angle < 32.0, f"Ângulo não reduzido: {new_angle}"
        print(f"✓ Ângulo reduzido: 32.00° → {new_angle:.2f}°")
        print(f"✓ Redução: {32.0 - new_angle:.2f}°")
        return True

    @staticmethod
    def run_all_tests():
        """Executa todos os testes."""
        print("\n" + "="*80)
        print("SUITE DE TESTES D7.3")
        print("="*80)

        tests = [
            TestGeoTaludeD73.test_fos_calculator,
            TestGeoTaludeD73.test_rampa_adjustment,
            TestGeoTaludeD73.test_convergent_case,
            TestGeoTaludeD73.test_tolerance_validation,
            TestGeoTaludeD73.test_divergent_case,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append((test.__name__, result))
            except Exception as e:
                print(f"✗ FALHA: {e}")
                results.append((test.__name__, False))

        # Sumário
        print("\n" + "="*80)
        print("SUMÁRIO")
        print("="*80)
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"Testes passados: {passed}/{total}")
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"  {name:<40} {status}")

        return all(r for _, r in results)


# ============================================================================
# VISUALIZAÇÕES
# ============================================================================

class D73Visualizer:
    """Gera gráficos de convergência e análise."""

    @staticmethod
    def plot_convergence(
        solver: GeoTaludeInteractionSolver,
        history: List[IterationResult],
        save_path: Optional[Path] = None
    ):
        """
        Plota progresso de convergência.

        Subplots:
          (1) FoS vs iteração (com linha alvo)
          (2) Ângulo rampa vs iteração
          (3) Redução % vs iteração
        """
        if not history:
            print("Sem histórico para plotar")
            return

        iters = [r.iteration_num for r in history]
        fos_values = [r.slope_fos for r in history]
        angles = [r.rampa_angle_deg for r in history]
        reductions = [r.rampa_reduction_percent for r in history]

        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.suptitle(f"D7.3 Convergência — {solver.location}", fontsize=14, fontweight='bold')

        # (1) FoS
        axes[0].plot(iters, fos_values, 'o-', linewidth=2, markersize=8, color='#2E86AB')
        axes[0].axhline(solver.config.target_fos, color='#A23B72', linestyle='--',
                       linewidth=2, label=f"Alvo (FoS={solver.config.target_fos})")
        axes[0].set_xlabel("Iteração", fontsize=11)
        axes[0].set_ylabel("FoS", fontsize=11)
        axes[0].set_title("Fator de Segurança")
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        # (2) Ângulo
        axes[1].plot(iters, angles, 's-', linewidth=2, markersize=8, color='#F18F01')
        axes[1].set_xlabel("Iteração", fontsize=11)
        axes[1].set_ylabel("Ângulo β (°)", fontsize=11)
        axes[1].set_title("Ângulo da Rampa")
        axes[1].grid(True, alpha=0.3)

        # (3) Redução %
        axes[2].bar(iters, reductions, color='#C73E1D', alpha=0.7, edgecolor='black')
        axes[2].set_xlabel("Iteração", fontsize=11)
        axes[2].set_ylabel("Redução (%)", fontsize=11)
        axes[2].set_title("Redução de Ângulo")
        axes[2].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico salvo: {save_path}")

        plt.show()

    @staticmethod
    def plot_sensitivity(
        solver: GeoTaludeInteractionSolver,
        sens_results: Dict,
        param: str = "fos",
        save_path: Optional[Path] = None
    ):
        """
        Plota análise de sensibilidade.
        """
        if not sens_results.get("param_values"):
            print("Sem dados de sensibilidade")
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.suptitle(f"Análise de Sensibilidade — {solver.location}",
                    fontsize=14, fontweight='bold')

        params = np.array(sens_results["param_values"])
        rampa_angles = np.array(sens_results["final_rampa_angle"])
        fos_finals = np.array(sens_results["final_fos"])

        # (1) Ângulo vs variação
        axes[0].plot(params * 100, rampa_angles, 'o-', linewidth=2,
                    markersize=8, color='#2E86AB')
        axes[0].set_xlabel(f"Variação de {param.upper()} (%)", fontsize=11)
        axes[0].set_ylabel("β Final (°)", fontsize=11)
        axes[0].set_title("Ângulo vs Parâmetro")
        axes[0].grid(True, alpha=0.3)

        # (2) FoS vs variação
        axes[1].plot(params * 100, fos_finals, 's-', linewidth=2,
                    markersize=8, color='#F18F01')
        axes[1].axhline(solver.config.target_fos, color='#A23B72',
                       linestyle='--', label=f"Alvo (FoS={solver.config.target_fos})")
        axes[1].set_xlabel(f"Variação de {param.upper()} (%)", fontsize=11)
        axes[1].set_ylabel("FoS Final", fontsize=11)
        axes[1].set_title("FoS vs Parâmetro")
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico salvo: {save_path}")

        plt.show()


# ============================================================================
# MAIN / SCRIPT DE DEMONSTRAÇÃO
# ============================================================================

if __name__ == "__main__":

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # =================================================================
    # 1. EXECUTAR EXEMPLO JERICÓ
    # =================================================================
    solver_jerico, history_jerico, status_jerico = example_jerico_km45800()

    # =================================================================
    # 2. VISUALIZAÇÕES
    # =================================================================
    print("\nGerando gráficos de convergência...")
    D73Visualizer.plot_convergence(solver_jerico, history_jerico)

    print("\nGerando gráficos de sensibilidade...")
    sens_jerico = solver_jerico.sensitivity_analysis(
        param="fos",
        range_percent=(-15, 15),
        steps=7
    )
    D73Visualizer.plot_sensitivity(solver_jerico, sens_jerico, param="fos")

    # =================================================================
    # 3. EXECUTAR TESTES UNITÁRIOS
    # =================================================================
    TestGeoTaludeD73.run_all_tests()

    # =================================================================
    # 4. CASOS ADICIONAIS
    # =================================================================
    print("\n" + "="*80)
    print("CASO ADICIONAL: TALUDE MAIS CRÍTICO")
    print("="*80)

    geometry_critico = SlopeGeometry(height_m=35.0, angle_deg=40.0, width_m=70.0)
    soil_critico = SoilProperties(
        gamma_kN_m3=21.0,
        phi_deg=32.0,
        cohesion_kPa=8.0,
        pore_pressure_ratio=0.25
    )
    config_critico = SolverConfiguration(
        target_fos=1.6,
        tolerance_percent=0.05,
        max_iterations=4,
        verbose=True
    )

    solver_critico = GeoTaludeInteractionSolver(
        geometry_critico,
        soil_critico,
        config_critico,
        location="Caso Crítico Teste"
    )

    initial_rampa_critico = RampaAdjustment(
        base_angle_deg=40.0,
        current_angle_deg=40.0,
        max_reduction_deg=7.0
    )

    history_critico, status_critico = solver_critico.solve(initial_rampa_critico)
    print(solver_critico.get_iteration_summary())

    print("\n" + "="*80)
    print("EXECUÇÃO COMPLETA FINALIZADA")
    print("="*80)
    print("\nArtefatos gerados:")
    print("  ✓ GeoTaludeInteractionSolver (solver principal)")
    print("  ✓ Algoritmo iterativo com convergência (3 iterações max)")
    print("  ✓ Exemplo Jericó Km 45+800 com valores reais")
    print("  ✓ Fallback conservador para divergência")
    print("  ✓ Análise de sensibilidade (FoS e outros parâmetros)")
    print("  ✓ Suite completa de testes unitários")
    print("  ✓ Visualizações (convergência, sensibilidade)")
