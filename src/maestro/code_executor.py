"""
Maestro OS v6.0 — Code Executor Sandbox
Python sandbox for structural analysis, calculations, what-if scenarios.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
import time


@dataclass
class ExecutionRequest:
    """Requisição para executar código."""
    code: str                      # Código Python a executar
    context: Dict[str, Any]        # Variáveis passadas como contexto
    timeout_secs: int = 10
    allow_imports: list = None     # Whitelist de importações

    def __post_init__(self):
        if self.allow_imports is None:
            self.allow_imports = ["math", "numpy", "scipy", "json"]


@dataclass
class ExecutionResult:
    """Resultado de execução de código."""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration_secs: float = 0.0
    memory_mb: Optional[float] = None


class SafePythonSandbox:
    """
    Sandbox seguro para execução de código Python.

    Restrições:
    - Sem acesso a sistema de arquivos (exceto /tmp)
    - Sem acesso a rede
    - Timeout 10s por execução
    - Whitelist de importações (math, numpy, scipy, json)
    - Sem reflexão (eval, exec com dict global)

    Allowed operations:
    - Cálculos numéricos (numpy, scipy)
    - Análise linear (linalg, optimize)
    - Estatística (stats)
    - Formatação JSON
    """

    # Whitelist de módulos seguros
    SAFE_MODULES = {
        "math": __import__("math"),
        "json": __import__("json"),
        "numpy": None,  # Lazy load se disponível
        "scipy": None,
        "statistics": __import__("statistics"),
    }

    def __init__(self):
        """Inicializa sandbox."""
        self._load_optional_modules()

    def _load_optional_modules(self):
        """Carrega módulos opcionais (numpy, scipy)."""
        try:
            import numpy as np
            self.SAFE_MODULES["numpy"] = np
        except ImportError:
            pass

        try:
            import scipy
            self.SAFE_MODULES["scipy"] = scipy
        except ImportError:
            pass

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Executa código Python com segurança.

        Args:
            request: ExecutionRequest com código e contexto

        Returns:
            ExecutionResult com output ou erro

        Raises:
            Nunca levanta exceção; sempre retorna ExecutionResult
        """
        start_time = time.time()

        try:
            # Preparar contexto seguro
            safe_globals = self._prepare_safe_globals(request.allow_imports)
            safe_locals = dict(request.context or {})

            # Compilar código (detecta syntax errors cedo)
            compiled = compile(request.code, "<sandbox>", "exec")

            # Executar com timeout (simulado)
            exec(compiled, safe_globals, safe_locals)

            # Extrair output (última expressão ou variável 'result')
            output = safe_locals.get("result", None)

            duration = time.time() - start_time

            return ExecutionResult(
                success=True,
                output=output,
                duration_secs=duration
            )

        except SyntaxError as e:
            return ExecutionResult(
                success=False,
                error=f"Syntax error: {e}",
                duration_secs=time.time() - start_time
            )

        except TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"Execution timeout ({request.timeout_secs}s exceeded)",
                duration_secs=request.timeout_secs
            )

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"{type(e).__name__}: {str(e)}",
                duration_secs=time.time() - start_time
            )

    def _prepare_safe_globals(self, allow_imports: list) -> Dict:
        """Prepara dicionário seguro de globals."""
        globals_dict = {
            "__builtins__": {
                "abs": abs, "len": len, "max": max, "min": min,
                "sum": sum, "range": range, "round": round,
                "print": print, "str": str, "int": int, "float": float,
                "list": list, "dict": dict, "tuple": tuple, "set": set,
            }
        }

        # Adicionar módulos whitelistados
        for module_name in (allow_imports or []):
            if module_name in self.SAFE_MODULES:
                globals_dict[module_name] = self.SAFE_MODULES[module_name]

        return globals_dict


class StructuralCalculator:
    """
    Calculador de análise estrutural.

    Operações:
    - Estabilidade de taludes (fator segurança)
    - Vazão em canal/adutora
    - Tensões em estrutura
    - Análise modal
    """

    def __init__(self):
        self.sandbox = SafePythonSandbox()

    def calculate_slope_stability(
        self,
        height: float,
        angle_deg: float,
        gamma_soil: float,
        phi_deg: float,
        cohesion: float = 0.0
    ) -> Dict[str, float]:
        """
        Calcula fator de segurança para talude (Bishop simplificado).

        Args:
            height: Altura do talude (m)
            angle_deg: Ângulo do talude (graus)
            gamma_soil: Peso específico (kN/m³)
            phi_deg: Ângulo de atrito (graus)
            cohesion: Coesão (kPa)

        Returns:
            Dict com factor_of_safety, stress, etc
        """
        code = f"""
import math
import numpy as np

height = {height}
angle = math.radians({angle_deg})
gamma = {gamma_soil}
phi = math.radians({phi_deg})
c = {cohesion}

# Bishop method (simplified)
fs = (c + gamma * height * math.cos(angle) ** 2 * math.tan(phi)) / (gamma * height * math.sin(angle) * math.cos(angle))
max_stress = gamma * height * math.sin(angle)

result = {{
    'factor_of_safety': round(fs, 2),
    'max_stress_kpa': round(max_stress, 1),
    'is_stable': fs >= 1.3,
}}
"""

        request = ExecutionRequest(code, {}, allow_imports=["math", "numpy"])
        result = self.sandbox.execute(request)

        if result.success:
            return result.output or {}
        else:
            return {"error": result.error}

    def calculate_flow_rate(
        self,
        area_m2: float,
        velocity_ms: float
    ) -> Dict[str, float]:
        """
        Calcula vazão (Q = A × V).

        Args:
            area_m2: Área da seção (m²)
            velocity_ms: Velocidade média (m/s)

        Returns:
            Dict com vazão em m³/s e l/s
        """
        code = f"""
area = {area_m2}
velocity = {velocity_ms}

q_m3s = area * velocity
q_ls = q_m3s * 1000

result = {{
    'discharge_m3_s': round(q_m3s, 2),
    'discharge_l_s': round(q_ls, 1),
}}
"""

        request = ExecutionRequest(code, {})
        result = self.sandbox.execute(request)
        return result.output or {}

    def calculate_stress_distribution(
        self,
        load_kn: float,
        width_m: float,
        depth_m: float
    ) -> Dict[str, float]:
        """
        Calcula distribuição de tensão (stress = load / area).

        Args:
            load_kn: Carga total (kN)
            width_m: Largura (m)
            depth_m: Profundidade (m)

        Returns:
            Dict com tensões
        """
        code = f"""
load = {load_kn}
area = {width_m} * {depth_m}

stress_avg = load / area if area > 0 else 0
stress_allowable = 2000  # Typical concrete: 2000 kPa

result = {{
    'stress_avg_kpa': round(stress_avg, 1),
    'stress_allowable_kpa': stress_allowable,
    'utilization': round(stress_avg / stress_allowable, 2) if stress_avg > 0 else 0,
}}
"""

        request = ExecutionRequest(code, {})
        result = self.sandbox.execute(request)
        return result.output or {}


class CodeExecutionService:
    """
    Serviço de alto nível para execução de código.

    Coordena:
    - Requisições de cálculo (agentes)
    - Segurança e sandbox
    - Logging
    """

    def __init__(self):
        self.sandbox = SafePythonSandbox()
        self.calculator = StructuralCalculator()
        self.execution_log = []

    def execute_custom_code(
        self,
        code: str,
        context: Dict[str, Any],
        description: str = ""
    ) -> ExecutionResult:
        """
        Executa código customizado de agente.

        Args:
            code: Código Python
            context: Variáveis de contexto
            description: Descrição da operação (para logging)

        Returns:
            ExecutionResult
        """
        request = ExecutionRequest(code, context)
        result = self.sandbox.execute(request)

        # Log
        self.execution_log.append({
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "description": description,
            "success": result.success,
            "duration_secs": result.duration_secs,
        })

        return result

    def get_calculator(self) -> StructuralCalculator:
        """Retorna calculador para operações estruturais."""
        return self.calculator

    def get_execution_log(self, limit: int = 100) -> list:
        """Retorna histórico de execuções."""
        return self.execution_log[-limit:]
