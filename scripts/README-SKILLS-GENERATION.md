# Geração Automática de SKILL.md (Manta Maestro v5.0)

## Visão Geral

Este diretório contém scripts para gerar automaticamente documentação de agentes (SKILL.md) a partir de CLAUDE.md e VERSIONS.json.

**Output final:**
- `manta-maestro/SKILL.md` — Documentação consolidada de todos os 20 agentes (11 horizontais + 9 verticais)
- ~2,400 linhas | ~72 KB
- Regenerado a cada push/merge que altere CLAUDE.md ou VERSIONS.json

---

## Arquivos

### 1. `generate_skills_registry.py`

**Propósito:** Script principal que orquestra a geração de SKILL.md.

**Uso:**
```bash
python scripts/generate_skills_registry.py
```

**Processo:**
1. Lê CLAUDE.md (mapa de 20 agentes, tabelas, routing rules)
2. Extrai dados de agentes horizontais e verticais
3. Valida checksums MD5
4. Adiciona descrições, ciclo de vida e trigger phrases
5. Renderiza template Jinja2 para cada agente
6. Consolidar em `manta-maestro/SKILL.md`

**Output:**
```
[+] Sucesso!
    - Agentes: 20 (11 horizontais + 9 verticais)
    - Linhas: 2,424
    - Tamanho: 71.6 KB
    - Output: manta-maestro/SKILL.md
    - Timestamp: 2026-07-25T02:18:26.544191
```

---

### 2. `agent_template.j2`

**Propósito:** Template Jinja2 reutilizável para gerar documentação de um agente.

**Seções geradas:**
- Metadados (código, nome, categoria, status, tier)
- Aliases & roteamento
- Skill e versionamento
- Capabilities (tools, skills, RAG)
- Ciclo de vida (8 fases para verticais)
- Trigger phrases (keywords para maestro)
- Exemplos de prompts (golden set)
- Tiering automático (R7)
- Observabilidade (run tracking)
- Fallback inteligente (R8)
- SharePoint routing
- Feedback loop (R9)

**Uso em Python:**
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('scripts'))
template = env.get_template('agent_template.j2')

# Renderizar um agente
rendered = template.render(agent=agent_obj)
```

---

## Modelos de Dados

### `Agent` (dataclass)

```python
@dataclass
class Agent:
    codigo: str                           # "Manta 00", "Manta 03-S8"
    nome: str                             # "maestro", "agente-saneamento"
    descricao: str                        # 1 linha descritiva
    aliases: List[str]                    # ["router", "manta-router"]
    tier_default: str                     # "Haiku", "Sonnet", "Opus"
    skill_file: str                       # "maestro.v5.0.md"
    checksum: str                         # "d3a2f1c8e4b7" (MD5)
    rag_collection: Optional[str]         # "san:v5.0:*" ou None
    ciclo_vida: List[str]                 # [1,2,3,4,5,6,7,8] ou []
    trigger_phrases: List[str]            # Keywords para maestro router
    exemplo_prompts: List[str]            # Golden set de prompts
    status: str                           # "Prod", "Staging", "Roadmap"
    category: str                         # "horizontal" ou "vertical"
```

---

## Fluxo de Parsing

### Entrada: CLAUDE.md

```markdown
### Tier 1 — Horizontais (transversais)

| Código | Agente | Aliases | Tier default | Skill v5.0 | Checksum | Status |
|--------|--------|---------|--------------|-----------|----------|--------|
| Manta 00 | maestro | router, manta-router | Haiku→Sonnet | maestro.v5.0.md | `d3a2f1c8e4b7` | ✅ Prod |
| Manta 01 | claims | manta-claims, claim-mgmt | Opus | claims.v5.0.md | `c1f4b7d3a2e6` | ✅ Prod |
...

### Tier 2–3 — Verticais por segmento

| Código | Segmento | Agente | Tier default | Skill v5.0 | Checksum | RAG coleção | Status |
|--------|----------|--------|--------------|-----------|----------|-------------|--------|
| Manta 03-S1 | Rodovias | agente-rodovias | Sonnet | rodovias.v5.0.md | `f7a3b2c1d4e6` | rod:v5.0:* | ✅ Prod |
...
```

### Parsing Steps

1. **Extract horizontal lines** → Regex split de pipes
2. **Extract vertical lines** → Regex split de pipes
3. **Clean data** → Remove backticks, emojis, espaços
4. **Map to Agent** → Instanciar dataclass
5. **Enrich** → Add descriptions, ciclo_vida, trigger_phrases, exemplo_prompts
6. **Validate** → Checksums MD5, completude

---

## Dados Enriquecidos (pós-parsing)

### Descrições (de CLAUDE.md)

```python
descriptions = {
    'maestro': 'Router canônico do Maestro (Manta 00) — orquestra roteamento determinístico...',
    'agente-saneamento': 'Especialista em saneamento básico (Manta 03-S8) — ETAs, ETEs...',
    # ... (20 agentes)
}
```

### Ciclo de Vida (para verticais apenas)

Todos os 9 agentes verticais (S1–S4, S6–S10) suportam:
```
[1, 2, 3, 4, 5, 6, 7, 8]  # 8 fases
```

1. Estudo prévio / EVTE
2. Projeto básico
3. Projeto executivo
4. Obra em execução
5. Operação & manutenção
6. Processo competitivo / licitação
7. Due diligence / M&A
8. Encerramento / descomissionamento

### Trigger Phrases (keywords para maestro)

Exemplo: `agente-saneamento`
```python
trigger_phrases = [
    'saneamento', 'ETA', 'ETE', 'adutora', 'esgoto', 'AySA',
    'drenagem urbana', 'SNIS', 'Lei 14.026'
]
```

### Exemplos de Prompts (golden set)

Exemplo: `agente-saneamento`
```python
exemplo_prompts = [
    'Dimensione uma ETA para município de 500k hab...',
    'Qual o custo de uma elevatória para adução de 1000 L/s...',
    # ... (4 prompts típicos)
]
```

---

## Validações Automáticas

✓ **Checksum MD5** — Todos 20 agentes têm checksum válido (8+ chars)
✓ **Completude** — Nenhum campo obrigatório está vazio
✓ **Contagem** — 11 horizontais + 9 verticais = 20 total
✓ **Ciclo de vida** — Verticais têm 8 fases; horizontais têm []
✓ **Trigger phrases** — Verticais têm >= 5 keywords
✓ **Exemplos** — Verticais têm >= 4 prompts

---

## Estrutura do Output (SKILL.md)

```markdown
# SKILL.md — Manta Maestro v5.0 (20 Agentes)

Registro consolidado de capabilities, routing, tiering e exemplos...

---

## Índice Rápido

### Tier 1 — Agentes Horizontais (11)

| # | Agente | Tier default | Status | RAG |
| Manta 00 | maestro | Haiku→Sonnet | Prod | N/A |
...

### Tier 2–3 — Agentes Verticais (9)

| # | Segmento | Agente | Tier default | RAG | Status |
| Manta 03-S1 | Rodovias | agente-rodovias | Sonnet | rod:v5.0:* | Prod |
...

---

## AGENTES HORIZONTAIS (Tier 1)

## Manta 15 — ADVISORY

**Categoria:** horizontal | **Status:** Prod | **Tier default:** Sonnet

Especialista em assessoria estratégica e governança...

### Aliases & Roteamento
### Skill & Versionamento
### Capabilities
### Ciclo de Vida (8 fases)
### Trigger Phrases (Maestro Routing)
### Exemplos de Prompts (Golden Set)
### Tiering Automático (R7)
### Observabilidade
### Fallback Inteligente (R8)
### SharePoint Routing
### Feedback Loop (R9)

---

## AGENTES VERTICAIS (Tier 2–3)

## Manta 03-S1 — AGENTE-RODOVIAS
... (idem estrutura)

---

## Governança & Manutenção

Proprietário: mneves@mantaassociados.com
...
```

---

## Ciclo de Vida de Manutenção

### Quando regenerar SKILL.md?

1. **Após alterar CLAUDE.md** — Novos agentes, mudança de tier, routing rules
2. **Após alterar VERSIONS.json** — Novos checksums, deprecações
3. **Antes de PR/merge principal** — Gate de validação automático

### Automação (sugerida)

**Git hook (pre-commit):**
```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached CLAUDE.md VERSIONS.json | grep -q .; then
    echo "[*] Detected changes in CLAUDE.md or VERSIONS.json..."
    python scripts/generate_skills_registry.py
    
    if [ $? -eq 0 ]; then
        git add manta-maestro/SKILL.md
        echo "[+] SKILL.md regenerated and staged."
    else
        echo "[!] SKILL.md generation failed. Aborting commit."
        exit 1
    fi
fi
```

**CI/CD (GitHub Actions):**
```yaml
name: Validate SKILL.md
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install jinja2
      - run: python scripts/generate_skills_registry.py
      - run: git diff --exit-code manta-maestro/SKILL.md
        || (echo "SKILL.md is out of sync" && exit 1)
```

---

## Estendendo o Script

### Adicionar novo agente

1. **Editar CLAUDE.md** — Adicionar linha na tabela (horizontais ou verticais)
2. **Adicionar checksum** — Calcular MD5 do arquivo .md do agente
3. **Executar script** — `python scripts/generate_skills_registry.py`
4. **Validar output** — Verificar novo agente em `manta-maestro/SKILL.md`

### Customizar template

1. **Editar `agent_template.j2`** — Modificar seções conforme necessário
2. **Re-run script** — Jinja2 recarregará template na próxima execução
3. **Teste local** — Verificar em `manta-maestro/SKILL.md`

### Adicionar nova métrica (ex: custo estimado por fase)

```python
# Em add_descriptions(), adicionar:
cost_by_phase = {
    'agente-saneamento': {
        'estudo-previo': 2500,
        'projeto-basico': 5000,
        'projeto-executivo': 15000,
        # ...
    }
}

# Passar para template via render context
```

---

## Dependencies

- Python 3.10+
- `jinja2` (for template rendering)
- Built-in: `re`, `json`, `hashlib`, `pathlib`, `datetime`

**Instalar:**
```bash
pip install jinja2
```

---

## Troubleshooting

### Script falha no parsing de CLAUDE.md

**Symptom:** `UnboundLocalError: cannot access local variable 'aliases'`

**Fix:** Verificar formatação de tabelas em CLAUDE.md — pipes alinhados, sem linhas vazias entre rows.

### Checksum não validado

**Symptom:** `checksum inválido ()`

**Fix:** Editar CLAUDE.md — adicionar checksum backtick-escaped. Ex: `` `d3a2f1c8e4b7` ``

### SKILL.md não é gerado

**Symptom:** Nenhuma saída de sucesso

**Fix:** 
1. Verificar CLAUDE.md existe: `ls -la /home/user/Codex-exemplo/CLAUDE.md`
2. Verificar diretório de output: `mkdir -p manta-maestro/`
3. Verificar permissões de escrita: `touch manta-maestro/test.txt`

### Jinja2 TemplateError

**Symptom:** `jinja2.exceptions.UndefinedError: 'X' is undefined`

**Fix:** Verificar contexto passado para `template.render()` — todos os campos do Agent devem estar presente.

---

## Performance

| Operação | Tempo |
|----------|-------|
| Parse CLAUDE.md | ~50ms |
| Extract 20 agentes | ~100ms |
| Validate checksums | ~30ms |
| Render 20 templates | ~200ms |
| Write SKILL.md | ~50ms |
| **Total** | **~430ms** |

---

## Contato & Governança

**Owner:** mneves@mantaassociados.com
**Version:** v5.0 (2026-07-25)
**Ticket:** MNT-2026-UPGRADE-AGENTS-V5

---

**Fim de README-SKILLS-GENERATION.md**
