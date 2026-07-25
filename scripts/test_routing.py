#!/usr/bin/env python3
"""
Validação de Routing — Manta Maestro v4.2
Testa se o Maestro roteia cada prompt ao agente correto conforme CLAUDE.md
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict

# Regras de routing baseadas no CLAUDE.md v4.2
ROUTING_RULES = [
    # S6 — Portos
    {
        "agent": "agente-portos",
        "keywords": ["porto", "terminal", "antaq", "dragagem", "molhe", "quebra-mar",
                     "berço", "calado", "contêiner", "granel", "cais", "píer",
                     "retroárea", "pátio de estocagem", "tup", "tps", "pianc", "arrendamento portuário", "hidrovia"],
        "segment": "S6"
    },
    # S7 — Aeroportos
    {
        "agent": "agente-aeroportos",
        "keywords": ["aeroporto", "pista", "rwy", "taxiway", "twy", "pátio", "tps terminal",
                     "teca", "anac", "rbac", "icao annex 14", "faa ac", "balizamento",
                     "papi", "ils", "pcn", "gate", "ponte de embarque", "jetway",
                     "aviação geral", "aviação regional", "concessão aeroportuária", "código 3c", "cat ii"],
        "segment": "S7"
    },
    # S8 — Saneamento
    {
        "agent": "agente-saneamento",
        "keywords": ["saneamento", "eta", "ete", "adutora", "esgoto", "água tratada",
                     "aysa", "drenagem urbana", "macrodrenagem", "snis", "pmsb",
                     "lei 14.026", "subsídio cruzado", "elevatória", "reservatório",
                     "rap", "eee", "eeab", "reúso", "lodo", "digestor", "uasb", "mbr", "nbr 9649",
                     "golpe de aríete", "drenagem", "universalização"],
        "segment": "S8"
    },
    # S9 — Energia
    {
        "agent": "agente-energia",
        "keywords": ["transmissão", "lt", "subestação", "aneel", "rap", "leilão transmissão",
                     "ons", "epe", "pde", "r1", "r2", "r3", "r4", "r5", "torre estaiada",
                     "cabo condutor", "acsr", "caa", "atsr", "mre", "acr", "acl", "weg",
                     "state grid", "isa cteep", "alupar", "taesa", "geração eólica",
                     "pv", "hidráulica", "pch", "uhe", "ampacidade", "fluxo de potência"],
        "segment": "S9"
    },
    # S10 — Barragens
    {
        "agent": "agente-barragens",
        "keywords": ["barragem", "vertedouro", "cfrd", "ccr", "rcc", "rejeitos", "tsf",
                     "pnsb", "icold", "cbdb", "dique", "sigbm", "anm", "ana", "lei 12.334",
                     "fundão", "brumadinho", "descomissionamento", "alteamento",
                     "filtragem de rejeitos", "dry stack", "pae", "paebm", "zas", "zss", "hhp",
                     "dam breach", "categoria de risco", "barragem de rejeitos"],
        "segment": "S10"
    },
    # S1 — Rodovias
    {
        "agent": "agente-infraestrutura S1",
        "keywords": ["rodovia", "pavimento", "cbuq", "bgs", "terraplenagem", "sicro", "dnit"],
        "segment": "S1"
    },
    # S2 — OAE (Pontes)
    {
        "agent": "agente-infraestrutura S2",
        "keywords": ["ponte", "viaduto", "oae", "nbr 7187", "túnel rodoviário", "prp"],
        "segment": "S2"
    },
    # S3 — Ferrovia
    {
        "agent": "agente-infraestrutura S3",
        "keywords": ["ferrovia", "trilho", "amv", "dormente", "via permanente", "pátio ferroviário"],
        "segment": "S3"
    },
    # S4 — Metrô
    {
        "agent": "agente-infraestrutura S4",
        "keywords": ["metrô", "estação", "natm", "psd", "linha 4", "linha 5", "vlt"],
        "segment": "S4"
    },
]

def extract_tests_from_markdown(filepath: str) -> List[Tuple[str, str]]:
    """Extrai prompts e agentes esperados do arquivo prompts.md"""
    tests = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern: `- [ ] "prompt" → **agent**`
    pattern = r'- \[ \] `([^`]+)` → \*\*([^*]+)\*\*'

    matches = re.findall(pattern, content)
    for prompt, expected_agent in matches:
        tests.append((prompt.strip(), expected_agent.strip()))

    return tests

def tokenize_prompt(prompt: str) -> List[str]:
    """Tokeniza o prompt em palavras-chave minúsculas"""
    # Remove pontuação, divide em palavras, converte para minúsculas
    words = re.sub(r'[^\w\s]', ' ', prompt).lower().split()
    return words

def match_keywords(prompt_tokens: List[str], rule_keywords: List[str]) -> int:
    """Conta quantas keywords da rule aparecem no prompt (score)"""
    score = 0
    for keyword in rule_keywords:
        # Verifica se a keyword (ou sua variação) aparece no prompt
        keyword_words = keyword.lower().split()
        # Se é uma palavra simples, verifica diretamente
        if len(keyword_words) == 1:
            if keyword_words[0] in prompt_tokens:
                score += 1
        else:
            # Se é composição (ex: "nbr 9649"), verifica se todas as partes estão juntas
            keyword_str = ' '.join(keyword_words)
            prompt_str = ' '.join(prompt_tokens)
            if keyword_str in prompt_str:
                score += 1
    return score

def dispatch_prompt(prompt: str) -> Tuple[str, int]:
    """
    Roteia o prompt para o agente mais apropriado.
    Retorna (agent_name, confidence_score)
    """
    tokens = tokenize_prompt(prompt)
    best_match = None
    best_score = 0

    for rule in ROUTING_RULES:
        score = match_keywords(tokens, rule['keywords'])
        if score > best_score:
            best_score = score
            best_match = rule['agent']

    # Se não encontrou nada, retorna claude (fallback)
    if best_match is None:
        return "claude", 0

    return best_match, best_score

def run_tests(prompts_file: str) -> Dict:
    """Executa todos os testes e retorna resultados"""
    tests = extract_tests_from_markdown(prompts_file)

    results = {
        "timestamp": datetime.now().isoformat(),
        "total": len(tests),
        "passes": 0,
        "fails": 0,
        "tests": []
    }

    for idx, (prompt, expected_agent) in enumerate(tests, 1):
        dispatched_agent, score = dispatch_prompt(prompt)
        match = dispatched_agent == expected_agent

        if match:
            results["passes"] += 1
            status = "✅ PASS"
        else:
            results["fails"] += 1
            status = "❌ FAIL"

        results["tests"].append({
            "number": idx,
            "prompt": prompt[:80] + "..." if len(prompt) > 80 else prompt,
            "expected": expected_agent,
            "dispatched": dispatched_agent,
            "score": score,
            "status": status
        })

    results["accuracy"] = (results["passes"] / results["total"] * 100) if results["total"] > 0 else 0

    return results

def print_summary(results: Dict):
    """Imprime sumário dos testes no console"""
    print("\n" + "="*80)
    print("BLOCO E — Validação de Routing (Manta Maestro v4.2)")
    print("="*80)
    print(f"Data: {results['timestamp']}")
    print(f"Total de testes: {results['total']}")
    print(f"Passes: {results['passes']}")
    print(f"Fails: {results['fails']}")
    print(f"Taxa de acurácia: {results['accuracy']:.1f}%")

    # Status final
    if results['accuracy'] >= 90:
        status = "✅ PASS"
    elif results['accuracy'] >= 85:
        status = "⚠️ PARTIAL"
    else:
        status = "❌ FAIL"

    print(f"Status: {status}")
    print("="*80)

    # Mostra falhas
    fails = [t for t in results['tests'] if t['status'] == "❌ FAIL"]
    if fails:
        print("\nFalhas detectadas:")
        for test in fails:
            print(f"  #{test['number']}: {test['prompt']}")
            print(f"     Esperado: {test['expected']}")
            print(f"     Despachado: {test['dispatched']}")
            print()

def generate_report(results: Dict, output_file: str):
    """Gera relatório em Markdown"""
    status_map = {
        0.9: ("✅ PASS", "Todos os testes aprovados"),
        0.85: ("⚠️ PARTIAL", "Alguns testes falharam — ajustar routing rules"),
        0.0: ("❌ FAIL", "Muitos testes falharam — bloqueador para Trilha 4"),
    }

    accuracy = results['accuracy'] / 100
    status = "❌ FAIL"
    msg = ""

    if accuracy >= 0.90:
        status = "✅ PASS"
        msg = "Todos os testes aprovados"
    elif accuracy >= 0.85:
        status = "⚠️ PARTIAL"
        msg = "Alguns testes falharam — ajustar routing rules"
    else:
        status = "❌ FAIL"
        msg = "Muitos testes falharam — bloqueador para Trilha 4"

    # Agrupa por segmento
    by_segment = {}
    for test in results['tests']:
        # Extrai segmento da resposta esperada
        if "S1" in test['expected']:
            seg = "S1 Rodovias"
        elif "S2" in test['expected']:
            seg = "S2 OAE"
        elif "S3" in test['expected']:
            seg = "S3 Ferrovia"
        elif "S4" in test['expected']:
            seg = "S4 Metrô"
        elif "portos" in test['expected']:
            seg = "S6 Portos"
        elif "aeroportos" in test['expected']:
            seg = "S7 Aeroportos"
        elif "saneamento" in test['expected']:
            seg = "S8 Saneamento"
        elif "energia" in test['expected']:
            seg = "S9 Energia"
        elif "barragens" in test['expected']:
            seg = "S10 Barragens"
        else:
            seg = "Outros"

        if seg not in by_segment:
            by_segment[seg] = {"pass": 0, "fail": 0}

        if test['status'] == "✅ PASS":
            by_segment[seg]["pass"] += 1
        else:
            by_segment[seg]["fail"] += 1

    # Gera markdown
    md = f"""# Resultado Final — Bloco E — Validação de Routing

**Data**: {results['timestamp']}
**Status**: {status}
**Taxa de acurácia**: {results['accuracy']:.1f}%

## Sumário

{msg}

- **Total de testes**: {results['total']}
- **Passes**: {results['passes']}
- **Fails**: {results['fails']}

---

## Resultado por Segmento

| Segmento | Passes | Fails | Taxa |
|----------|--------|-------|------|
"""

    for seg in sorted(by_segment.keys()):
        stats = by_segment[seg]
        total = stats['pass'] + stats['fail']
        rate = stats['pass'] / total * 100 if total > 0 else 0
        md += f"| {seg} | {stats['pass']}/{total} | {stats['fail']} | {rate:.0f}% |\n"

    md += "\n---\n\n## Detalhamento de Testes\n\n"

    # Detalhes dos testes
    for test in results['tests']:
        status_emoji = test['status'].split()[0]
        md += f"### #{test['number']} {test['status']}\n\n"
        md += f"**Prompt**: {test['prompt']}\n"
        md += f"**Esperado**: `{test['expected']}`\n"
        md += f"**Despachado**: `{test['dispatched']}`\n"
        md += f"**Score**: {test['score']}\n\n"

    # Falhas
    md += "\n---\n\n## Falhas Documentadas\n\n"
    fails = [t for t in results['tests'] if t['status'] == "❌ FAIL"]

    if fails:
        md += "| # | Prompt | Esperado | Despachado | Ação |\n"
        md += "|---|--------|----------|-----------|------|\n"
        for test in fails:
            md += f"| {test['number']} | {test['prompt'][:40]}... | {test['expected']} | {test['dispatched']} | Revisar routing rule |\n"
    else:
        md += "Nenhuma falha detectada.\n"

    md += "\n---\n\n## Recomendações\n\n"
    if results['accuracy'] >= 90:
        md += "✅ **Nenhuma ação necessária.** Aprovar Bloco E e prosseguir para Trilha 4.\n"
    elif results['accuracy'] >= 85:
        md += "⚠️ **Ações corretivas**:\n"
        md += "1. Revisar as regras de routing para os segmentos com falhas\n"
        md += "2. Validar keywords das rules vs prompts que falharam\n"
        md += "3. Re-executar teste após ajustes\n"
    else:
        md += "❌ **BLOQUEADOR**:\n"
        md += "1. Escalar para MN (revisão de routing logic)\n"
        md += "2. Reconsiderar estratégia de dispatch multimodal\n"
        md += "3. Pode ser necessário ajuste estrutural do Maestro\n"

    # Escreve arquivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"\n✅ Relatório gerado: {output_file}")

if __name__ == "__main__":
    prompts_file = "tests/routing/prompts.md"
    output_file = "tests/routing/RESULTADO-BLOCO-E-VALIDACAO.md"

    # Verifica se arquivo de testes existe
    if not Path(prompts_file).exists():
        print(f"❌ Erro: {prompts_file} não encontrado")
        sys.exit(1)

    # Executa testes
    print(f"Executando testes de routing a partir de {prompts_file}...")
    results = run_tests(prompts_file)

    # Imprime sumário
    print_summary(results)

    # Gera relatório
    generate_report(results, output_file)
