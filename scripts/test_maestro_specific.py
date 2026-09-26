#!/usr/bin/env python3
"""
Teste específico de roteamento do Maestro com os 5 prompts solicitados.
"""

import re

# Regras de roteamento baseadas em CLAUDE.md
ROUTING_RULES = {
    "agente-saneamento": [
        r"\bsaneamento\b",
        r"\bETA\b",
        r"\bETE\b",
        r"\badutora\b",
        r"\besgoto\b",
        r"\bAySA\b",
        r"drenagem urbana",
        r"\bSNIS\b",
        r"\bPMSB\b",
        r"Lei 14\.026",
        r"\bEEE\b",
        r"\bEEAB\b",
    ],
    "agente-energia": [
        r"\btransmissão\b",
        r"\bLT\b",
        r"\bsubestação\b",
        r"\bANEEL\b",
        r"\bRAP\b",
        r"leilão transmissão",
        r"\bONS\b",
        r"\bEPE\b",
        r"\bACsr\b",
        r"\bkV\b",
    ],
    "agente-portos": [
        r"\bporto\b",
        r"\bterminal\b",
        r"\bANTAQ\b",
        r"\bdragagem\b",
        r"\bmolhe\b",
        r"\bberço\b",
        r"\bcalado\b",
        r"\bcontêiner\b",
        r"\bgranel\b",
    ],
    "agente-aeroportos": [
        r"\baeroporto\b",
        r"pista pouso",
        r"pista de pouso",
        r"\bANAC\b",
        r"\bICAO\b",
        r"\bTPS\b",
        r"\bTECA\b",
        r"\bbalizamento\b",
        r"\bRWY\b",
        r"\bPCN\b",
        r"\bCAT II\b",
        r"\brbac\b",
        r"\bPAPI\b",
    ],
    "agente-barragens": [
        r"\bbarragem\b",
        r"\bvertedouro\b",
        r"\bCFRD\b",
        r"\bCCR\b",
        r"\brejeitos\b",
        r"\bPNSB\b",
        r"\bICOLD\b",
        r"\bCBDB\b",
        r"\bTSF\b",
        r"\bdam breach\b",
        r"\bSIGBM\b",
    ],
}

def match_prompt_to_agent(prompt):
    """
    Match um prompt contra as regras de roteamento.
    Retorna lista de agentes que fazem match (em ordem de especificidade).
    """
    matches = {}

    for agent, patterns in ROUTING_RULES.items():
        match_count = 0
        for pattern in patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                match_count += 1
        if match_count > 0:
            matches[agent] = match_count

    # Ordenar por número de matches (descendente)
    if matches:
        return sorted(matches.items(), key=lambda x: x[1], reverse=True)
    return []

# Testes específicos solicitados pelo usuário
SPECIFIC_TESTS = [
    {
        'numero': 1,
        'segmento': 'Saneamento',
        'prompt': 'Preciso de análise de ETA para distribuição de água em São Paulo com EEE',
        'esperado': 'agente-saneamento',
    },
    {
        'numero': 2,
        'segmento': 'Energia',
        'prompt': 'Análise de LT com ACSR em leilão ANEEL',
        'esperado': 'agente-energia',
    },
    {
        'numero': 3,
        'segmento': 'Portos',
        'prompt': 'Dragagem de berço com contêiner em terminal da ANTAQ',
        'esperado': 'agente-portos',
    },
    {
        'numero': 4,
        'segmento': 'Aeroportos',
        'prompt': 'Projeto de pista RWY com PAPI em aeroporto ANAC',
        'esperado': 'agente-aeroportos',
    },
    {
        'numero': 5,
        'segmento': 'Barragens',
        'prompt': 'Análise de TSF e rejeitos para CBDB',
        'esperado': 'agente-barragens',
    },
]

def run_specific_tests():
    """Executa os 5 testes específicos solicitados."""
    total = len(SPECIFIC_TESTS)
    passed = 0
    failed_details = []

    print("=" * 90)
    print("TESTE MAESTRO ROUTING — 5 SEGMENTOS (S6-S10)")
    print("=" * 90)

    for test in SPECIFIC_TESTS:
        numero = test['numero']
        segmento = test['segmento']
        prompt = test['prompt']
        esperado = test['esperado']

        matches = match_prompt_to_agent(prompt)
        roteado_para = matches[0][0] if matches else "NENHUM"

        # Normalizar para comparação
        esperado_norm = esperado.replace('_', '-')
        roteado_norm = roteado_para.replace('_', '-')

        test_passed = esperado_norm == roteado_norm

        if test_passed:
            passed += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
            failed_details.append({
                'numero': numero,
                'prompt': prompt,
                'esperado': esperado,
                'obtido': roteado_para,
                'matches': matches,
            })

        print(f"\nTeste {numero} ({segmento}):")
        print(f"  Status: {status}")
        print(f"  Prompt: {prompt}")
        print(f"  Esperado: {esperado}")
        print(f"  Obtido:   {roteado_para}")
        if matches:
            print(f"  Matches: {matches}")

    # Resumo final
    print("\n" + "=" * 90)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram ({100*passed/total:.1f}%)")
    print("=" * 90)

    # Detalhes de falhas
    if failed_details:
        print("\nDETALHES DAS FALHAS:")
        print("-" * 90)
        for detail in failed_details:
            print(f"\nTeste {detail['numero']}:")
            print(f"  Prompt: {detail['prompt']}")
            print(f"  Esperado: {detail['esperado']}")
            print(f"  Obtido: {detail['obtido']}")
            print(f"  Matches: {detail['matches']}")

    return {
        'testes_passados': passed,
        'total_testes': total,
        'detalhes': [
            {
                'teste': f['numero'],
                'prompt': f['prompt'][:80],
                'esperado': f['esperado'],
                'obtido': f['obtido'],
            }
            for f in failed_details
        ]
    }

if __name__ == '__main__':
    result = run_specific_tests()
