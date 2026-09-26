"""agente-A5-cronograma (pai) — orquestrador do Manta Cronos.  Uso:  PYTHONPATH=src python -m cronos.sdk.main "pergunta" arq1.xer arq2.xer"""
import asyncio
import sys

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

from .agents import AGENTES
from .tools import NOMES, SERVIDOR

SISTEMA = """Você é o agente-A5-cronograma do Manta Maestro (L1.7), usando o motor Cronos.
1. Delegue a importação ao a5-6-leitor-multiformato e a qualidade (DCMA-14) ao a5-1-baseline-dcma.
2. Delegue atualização/comparação e linha do tempo de versões (a5-2), curva S e valor
   agregado (a5-3), caminho crítico (a5-4), Monte Carlo (a5-5)
   e forense (a7) conforme o pedido; rode subagentes independentes em paralelo.
3. Antes de responder, peça ao guard-auditor que confira os números.
4. Regras A5: linha de base aprovada não muda; DCMA-14 >= 90%; confirmação
   pré-saída (diferença, caminho crítico, drift, SPI/CPI) e aprovação MN.
5. R1: nunca escreva nome de contratante, consórcio ou subempreiteiro.
Só delegue quando a tarefa pedir; responda direto o que for simples.
Resposta final em português, resumida, com tabela e fonte de cada número."""


async def executar(pedido: str, arquivos: list[str]) -> None:
    opcoes = ClaudeAgentOptions(
        model="opus",
        system_prompt=SISTEMA,
        mcp_servers={"cronos": SERVIDOR},
        agents=AGENTES,
        allowed_tools=["Agent", "Read", "Glob", *NOMES],
        max_turns=40,
        max_budget_usd=5.0,                       # teto de gasto por consulta
        env={"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
             "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "6"},
    )
    prompt = f"{pedido}\n\nArquivos: " + ", ".join(arquivos)
    async for msg in query(prompt=prompt, options=opcoes):
        if isinstance(msg, ResultMessage):
            print(msg.result)
            print(f"\n[{msg.subtype}] custo estimado: US$ {msg.total_cost_usd}")


if __name__ == "__main__":
    asyncio.run(executar(sys.argv[1], sys.argv[2:]))
