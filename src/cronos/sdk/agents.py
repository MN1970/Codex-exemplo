"""Subagentes do Manta Cronos, alinhados ao Maestro A5-cronograma (L1.7).

O pai (agente-A5-cronograma) fica em main.py. Forense é A7-claims; auditoria é F-guard.
"""
from claude_agent_sdk import AgentDefinition

M = "mcp__cronos__"
REGRA = ("Nunca calcule datas, folgas ou custos de cabeça: use apenas as ferramentas "
         "mcp__cronos__*. Cite a fonte (arquivo › tabela › linha) de todo número. "
         "Todo cronograma é cost-loaded: reporte custo junto com prazo. "
         "R1: nunca escreva nome de contratante, consórcio ou subempreiteiro; use "
         "[CLIENTE], [CONSÓRCIO], [SUBEMPREITEIRO-n]. Linha de base aprovada não muda.")

AGENTES = {
    "a5-6-leitor-multiformato": AgentDefinition(
        description="Importa XER e XML (MS Project) em lote, só versões vigentes, e relata anomalias de leitura.",
        prompt=f"Você importa cronogramas estruturados e aponta anomalias (encoding, "
               f"calendários, loops, atividades sem custo). {REGRA}",
        tools=[f"{M}importar_lote", f"{M}listar_versoes", "Read", "Glob"],
        model="haiku", maxTurns=8, effort="low"),
    "a5-1-baseline-dcma": AgentDefinition(
        description="Qualidade da linha de base: DCMA-14 com a regra A5 (nota ≥ 90%, bloqueios 1, 3, 6, 7, 11).",
        prompt=f"Você audita a linha de base (A5.1). Rode checar_dcma14, explique cada ponto reprovado com "
               f"exemplos e diga se a linha de base pode ser aprovada. Linha de base aprovada não muda. {REGRA}",
        tools=[f"{M}checar_dcma14", f"{M}calcular_cpm", f"{M}listar_versoes"],
        model="sonnet", maxTurns=8),
    "a5-2-atualizacao-comparacao": AgentDefinition(
        description="Compara N versões de cronograma (linha de base × atualização × impactado).",
        prompt=f"Você compara versões (A5.2) e apresenta, antes de qualquer saída: diferença contra "
               f"a versão anterior, mudança do caminho crítico, drift de marcos, variação de custo. {REGRA}",
        tools=[f"{M}comparar_versoes", f"{M}linha_do_tempo", f"{M}calcular_cpm", f"{M}listar_versoes"],
        model="sonnet", maxTurns=12),
    "a5-3-curva-s-valor-agregado": AgentDefinition(
        description="Curva S física e financeira e valor agregado (SPI, CPI, EAC) de uma versão cost-loaded.",
        prompt=f"Você faz o controle de avanço (A5.3): curva S planejado × previsto e valor agregado "
               f"(ANSI/EIA-748). Interprete SPI/CPI/EAC/TCPI e diga se a linha de base é proxy "
               f"(sem datas planejadas) ou se faltam custos reais. {REGRA}",
        tools=[f"{M}curva_s_evm", f"{M}listar_versoes"],
        model="sonnet", maxTurns=8),
    "a5-4-cpm-caminho-critico": AgentDefinition(
        description="Caminho crítico, folgas e marcos de uma versão.",
        prompt=f"Você é planejador sênior (AACE 49R-06). Identifique e explique o caminho "
               f"crítico e as folgas. {REGRA}",
        tools=[f"{M}calcular_cpm", f"{M}listar_versoes"],
        model="opus", maxTurns=10, effort="high"),
    "a5-5-monte-carlo": AgentDefinition(
        description="Simulação Monte Carlo de prazo e custo, cenários e se.",
        prompt=f"Você roda Monte Carlo (AACE 57R-09), justifica os fatores otimista e "
               f"pessimista e interpreta P50/P80 e o índice de criticidade. {REGRA}",
        tools=[f"{M}simular_monte_carlo", f"{M}calcular_cpm"],
        model="sonnet", maxTurns=10),
    "a7-forense-atraso": AgentDefinition(
        description="Análise forense de atraso (AACE 29R-03 MIP 3.1–3.9, SCL, ASCE 67-17).",
        prompt=f"Você é perito em atraso. Escolha o método MIP conforme as evidências "
               f"disponíveis e justifique a escolha. Trate concorrência e folga. Toda "
               f"conclusão é rascunho sujeito à aprovação humana MN. {REGRA}",
        tools=[f"{M}comparar_versoes", f"{M}linha_do_tempo", f"{M}calcular_cpm", f"{M}listar_versoes", "Read"],
        model="opus", maxTurns=20, effort="high"),
    "guard-auditor": AgentDefinition(
        description="Audita o texto final: todo número precisa vir de uma ferramenta.",
        prompt="Você confere cada número, norma e data do texto contra as saídas das "
               "ferramentas. Liste o que não tem lastro. Não reescreva o texto.",
        tools=[f"{M}listar_versoes", f"{M}calcular_cpm"],
        model="haiku", maxTurns=6, effort="low"),
}
