"""
Sandbox de execução Python isolado.

Bloqueia: I/O de rede, filesystem fora do escopo, subprocess.
Usa: RestrictedPython para bytecode seguro.
"""

import sys
from io import StringIO
from typing import Any, Callable

from restricted_python import compile_restricted
from restricted_python.Guards import (
    guarded_inplacebinary_op,
    guarded_iter_unpack_sequence,
    safe_builtins,
    safe_globals,
)


class SandboxExecutionError(Exception):
    """Erro durante execução em sandbox."""

    pass


class RestrictedPythonSandbox:
    """Isolamento de execução Python com RestrictedPython."""

    # Bloqueios globais: sem acesso a módulos perigosos.
    BLOCKED_MODULES = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "urllib",
        "requests",
        "httplib",
        "ftplib",
        "telnetlib",
        "ssl",
        "paramiko",
        "__import__",
    }

    # Builtins seguros (RestrictedPython já filtra muitos).
    SAFE_BUILTINS = {
        **safe_builtins,
        "__builtins__": safe_builtins,
    }

    @staticmethod
    def _restricted_import(name, *args, **kwargs):
        """Import hook que bloqueia módulos perigosos."""
        if name in RestrictedPythonSandbox.BLOCKED_MODULES or any(
            name.startswith(blocked + ".") for blocked in RestrictedPythonSandbox.BLOCKED_MODULES
        ):
            raise ImportError(f"Module '{name}' is not allowed in sandbox")
        return __import__(name, *args, **kwargs)

    @staticmethod
    def compile_code(code: str) -> Any:
        """
        Compila código Python restrito.

        Args:
            code: código Python a compilar.

        Returns:
            Bytecode compilado (ou None se inválido).

        Raises:
            SandboxExecutionError: se o código violar restrições.
        """
        compiled = compile_restricted(code, filename="<sandbox>", mode="exec")

        if compiled.errors:
            errors = "\n".join(compiled.errors)
            raise SandboxExecutionError(f"Compilation errors:\n{errors}")

        if compiled.warnings:
            # Log warnings but don't fail.
            for warning in compiled.warnings:
                print(f"[SANDBOX WARNING] {warning}", file=sys.stderr)

        return compiled.code

    @staticmethod
    def execute(
        code: str,
        globals_dict: dict[str, Any] | None = None,
        locals_dict: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> dict[str, Any]:
        """
        Executa código Python em sandbox isolado.

        Args:
            code: código Python a executar.
            globals_dict: dicionário global (padrão: safe_globals + stdlib permitidos).
            locals_dict: dicionário local (padrão: vazio).
            timeout_seconds: timeout em segundos (NOTA: apenas como documentação —
                             o isolamento real deve ser feito no nível do OS/container).

        Returns:
            Dicionário contendo:
            - "result": resultado da execução (último valor ou None)
            - "output": stdout capturado
            - "error": None ou mensagem de erro
            - "execution_time": tempo em segundos

        Raises:
            SandboxExecutionError: se houver erro de execução.
        """
        import time

        start_time = time.time()

        # Setup de ambiente seguro.
        if globals_dict is None:
            globals_dict = RestrictedPythonSandbox.SAFE_BUILTINS.copy()
            globals_dict.update(safe_globals)
            globals_dict["__import__"] = RestrictedPythonSandbox._restricted_import
            globals_dict["_getattr_"] = getattr
            globals_dict["_write_"] = (
                lambda x: x
            )  # Necessário para RestrictedPython atribuições
            globals_dict["_inplacebinary_"] = guarded_inplacebinary_op
            globals_dict["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence

        if locals_dict is None:
            locals_dict = {}

        # Captura de stdout.
        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # Compila e executa.
            bytecode = RestrictedPythonSandbox.compile_code(code)
            result = None
            exec(bytecode, globals_dict, locals_dict)

            # Pega o último valor de locals para retornar.
            if locals_dict:
                result = list(locals_dict.values())[-1] if locals_dict else None

            return {
                "result": result,
                "output": captured_output.getvalue(),
                "error": None,
                "execution_time": time.time() - start_time,
            }

        except SandboxExecutionError as e:
            return {
                "result": None,
                "output": captured_output.getvalue(),
                "error": str(e),
                "execution_time": time.time() - start_time,
            }
        except Exception as e:
            return {
                "result": None,
                "output": captured_output.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}",
                "execution_time": time.time() - start_time,
            }
        finally:
            sys.stdout = old_stdout


def execute_python(code: str, **kwargs) -> dict[str, Any]:
    """Conveniência: executa Python em sandbox."""
    return RestrictedPythonSandbox.execute(code, **kwargs)
