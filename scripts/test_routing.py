#!/usr/bin/env python3
"""
Teste de roteamento Maestro v4.2
Valida que os prompts de teste disparam o roteamento correto para cada agente.
"""

import re
import sys
from pathlib import Path

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
        r"\bPIANC\b",
        r"quebra-mar",
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
        r"\bANM\b",
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

def parse_test_file(file_path):
    """Parse prompts.md e extrai os testes."""
    tests = {}
    current_section = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()

            # Detectar seções (S6, S7, etc.)
            match = re.match(r"## (S\d+) — (\w+)", line)
            if match:
                current_section = match.group(2).lower()
                tests[current_section] = []
                continue

            # Detectar items de teste
            if current_section and line.strip().startswith("- [ ]"):
                # Extrair prompt e agente esperado
                match = re.match(r'- \[ \] `(.+?)` → \*\*(\w+(?:-\w+)*)\*\*', line)
                if match:
                    prompt = match.group(1)
                    expected_agent = match.group(2)
                    tests[current_section].append({
                        'prompt': prompt,
                        'expected': expected_agent,
                    })

    return tests

def run_tests(test_file):
    """Executa os testes e relata resultados."""
    tests = parse_test_file(test_file)

    total = 0
    passed = 0
    failed_tests = []

    print("=" * 80)
    print("TESTE DE ROTEAMENTO MAESTRO v4.2")
    print("=" * 80)

    for section, test_list in tests.items():
        print(f"\n[{section.upper()}]")
        print("-" * 80)

        for test in test_list:
            total += 1
            prompt = test['prompt']
            expected = test['expected']

            matches = match_prompt_to_agent(prompt)
            routed_to = matches[0][0] if matches else "NENHUM"

            # Normalizar nomes para comparação
            expected_normalized = expected.replace('_', '-')
            routed_normalized = routed_to.replace('_', '-')

            test_passed = routed_normalized == expected_normalized

            if test_passed:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"
                failed_tests.append({
                    'prompt': prompt,
                    'expected': expected,
                    'got': routed_to,
                    'matches': matches,
                })

            print(f"{status:4s} | {prompt[:60]:60s}")
            if not test_passed:
                print(f"       Expected: {expected}, Got: {routed_to}")
                if matches:
                    print(f"       Matches: {matches}")

    # Resumo
    print("\n" + "=" * 80)
    print(f"RESUMO: {passed}/{total} testes passaram ({100*passed/total if total>0 else 0:.1f}%)")
    print("=" * 80)

    if failed_tests:
        print("\nFALHAS DETALHADAS:")
        print("-" * 80)
        for failure in failed_tests:
            print(f"\nPrompt: {failure['prompt']}")
            print(f"Esperado: {failure['expected']}")
            print(f"Obtido: {failure['got']}")
            print(f"Matches encontrados: {failure['matches']}")

    return {
        'testes_passados': passed,
        'total_testes': total,
        'detalhes': [
            {
                'prompt': f.get('prompt', '')[:60],
                'esperado': f.get('expected', ''),
                'obtido': f.get('got', ''),
            }
            for f in failed_tests
        ]
    }

if __name__ == '__main__':
    test_file = Path(__file__).parent.parent / 'tests' / 'routing' / 'prompts.md'

    if not test_file.exists():
        print(f"Arquivo de testes não encontrado: {test_file}")
        sys.exit(1)

    result = run_tests(test_file)
    sys.exit(0 if result['testes_passados'] == result['total_testes'] else 1)
