#!/usr/bin/env bash
# validate-syntax.sh — Manta Maestro Agent Registry
#
# Check 1/5 do workflow agent-validation: valida sintaxe estrutural do
# registro, sem interpretar semântica de routing (isso é o check-routing.py).
#
# O que valida:
#   1. CLAUDE.md existe, não está vazio, e todo bloco de código
#      ("```") fecha corretamente (par).
#   2. Toda tabela markdown (bloco de linhas iniciando com "|") tem o
#      mesmo número de colunas em todas as linhas do bloco.
#   3. Cada .claude/agents/*.md tem front-matter YAML bem-formado
#      (delimitado por "---" nas duas primeiras ocorrências) e as
#      chaves obrigatórias: name, description, tools, model.
#   4. O campo `name:` do front-matter bate com o nome do arquivo
#      (agente-portos.md → name: agente-portos).
#   5. Nenhum arquivo tem caracteres tab (indentação inconsistente).
#
# Uso:
#   ./scripts/validate-syntax.sh [repo-root]
#
# Exit code: 0 se tudo passar; 1 se houver qualquer erro (lista todos
# antes de sair, não para no primeiro).

set -uo pipefail

ROOT="${1:-.}"
CLAUDE_MD="${ROOT}/CLAUDE.md"
AGENTS_DIR="${ROOT}/.claude/agents"

ERRORS=()
CHECKS=0

err() { ERRORS+=("$1"); }

# ---------------------------------------------------------------------
# 1. CLAUDE.md — existe e não está vazio
# ---------------------------------------------------------------------
CHECKS=$((CHECKS + 1))
if [[ ! -f "$CLAUDE_MD" ]]; then
  err "CLAUDE.md não encontrado em ${CLAUDE_MD}"
elif [[ ! -s "$CLAUDE_MD" ]]; then
  err "CLAUDE.md está vazio"
fi

# ---------------------------------------------------------------------
# 2. Blocos de código fecham em pares (contagem de linhas "```")
# ---------------------------------------------------------------------
if [[ -f "$CLAUDE_MD" ]]; then
  CHECKS=$((CHECKS + 1))
  FENCE_COUNT=$(grep -c '^```' "$CLAUDE_MD" || true)
  if (( FENCE_COUNT % 2 != 0 )); then
    err "CLAUDE.md: número ímpar de fences \`\`\` (${FENCE_COUNT}) — bloco de código não fechado"
  fi

  # ---------------------------------------------------------------------
  # 3. Tabelas markdown — colunas consistentes por bloco contíguo
  # ---------------------------------------------------------------------
  CHECKS=$((CHECKS + 1))
  TABLE_ERRORS="$(python3 - "$CLAUDE_MD" <<'PYEOF'
import re
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

errors = []
block = []
block_start = None


def flush(block, start):
    if len(block) < 2:
        return
    header_cols = block[0].count("|")
    # segunda linha é o separador (|---|---|); não conta como dado, mas
    # deve existir e parecer um separador de tabela.
    sep = block[1].strip()
    if not re.match(r"^\|?[\s:|-]+\|?$", sep):
        errors.append(f"linha {start + 2}: linha separadora de tabela mal formada: {sep!r}")
    for i, row in enumerate(block[2:], start=2):
        cols = row.count("|")
        if cols != header_cols:
            errors.append(
                f"linha {start + i + 1}: tabela com {cols} colunas, "
                f"esperado {header_cols} (header na linha {start + 1})"
            )


for idx, raw in enumerate(lines):
    line = raw.rstrip("\n")
    if line.strip().startswith("|"):
        if not block:
            block_start = idx
        block.append(line)
    else:
        if block:
            flush(block, block_start)
        block = []
        block_start = None
if block:
    flush(block, block_start)

for e in errors:
    print(e)
PYEOF
)"
  if [[ -n "$TABLE_ERRORS" ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] && err "CLAUDE.md: ${line}"
    done <<< "$TABLE_ERRORS"
  fi
fi

# ---------------------------------------------------------------------
# 4. Agent .md — front-matter YAML + chaves obrigatórias + name==arquivo
# ---------------------------------------------------------------------
REQUIRED_KEYS=(name description tools model)

if [[ ! -d "$AGENTS_DIR" ]]; then
  err "diretório ${AGENTS_DIR} não encontrado"
else
  shopt -s nullglob
  AGENT_FILES=("${AGENTS_DIR}"/*.md)
  shopt -u nullglob

  if [[ ${#AGENT_FILES[@]} -eq 0 ]]; then
    err "nenhum arquivo .md encontrado em ${AGENTS_DIR}"
  fi

  for f in "${AGENT_FILES[@]}"; do
    CHECKS=$((CHECKS + 1))
    base="$(basename "$f" .md)"

    # tabs
    if grep -qP '\t' "$f"; then
      err "$(basename "$f"): contém caracteres TAB (usar espaços)"
    fi

    # front-matter delimitado por --- nas linhas 1 e N
    first_line="$(sed -n '1p' "$f")"
    if [[ "$first_line" != "---" ]]; then
      err "$(basename "$f"): não inicia com front-matter YAML (---)"
      continue
    fi

    # segunda ocorrência de "---"
    end_line=$(awk 'NR>1 && $0=="---"{print NR; exit}' "$f")
    if [[ -z "$end_line" ]]; then
      err "$(basename "$f"): front-matter não fechado (falta segunda linha ---)"
      continue
    fi

    frontmatter="$(sed -n "2,$((end_line - 1))p" "$f")"

    # valida com PyYAML se disponível; senão cai para grep simples
    if python3 -c "import yaml" >/dev/null 2>&1; then
      parsed=$(python3 - "$f" "$end_line" <<'PYEOF'
import sys
import yaml

path, end_line = sys.argv[1], int(sys.argv[2])
with open(path, encoding="utf-8") as fh:
    lines = fh.readlines()
fm_text = "".join(lines[1:end_line - 1])
try:
    data = yaml.safe_load(fm_text) or {}
except yaml.YAMLError as e:
    print(f"YAML_ERROR::{e}")
    sys.exit(0)
if not isinstance(data, dict):
    print("YAML_ERROR::front-matter não é um mapeamento YAML")
    sys.exit(0)
missing = [k for k in ("name", "description", "tools", "model") if k not in data]
if missing:
    print(f"MISSING_KEYS::{','.join(missing)}")
name = data.get("name", "")
print(f"NAME::{name}")
PYEOF
)
      if echo "$parsed" | grep -q '^YAML_ERROR::'; then
        err "$(basename "$f"): YAML inválido no front-matter — $(echo "$parsed" | grep '^YAML_ERROR::' | cut -d: -f3-)"
        continue
      fi
      if echo "$parsed" | grep -q '^MISSING_KEYS::'; then
        missing_keys=$(echo "$parsed" | grep '^MISSING_KEYS::' | cut -d: -f3-)
        err "$(basename "$f"): front-matter sem chave(s) obrigatória(s): ${missing_keys}"
      fi
      name_val=$(echo "$parsed" | grep '^NAME::' | cut -d: -f3-)
      if [[ -n "$name_val" && "$name_val" != "$base" ]]; then
        err "$(basename "$f"): name: '${name_val}' não bate com o nome do arquivo '${base}'"
      fi
    else
      for key in "${REQUIRED_KEYS[@]}"; do
        if ! echo "$frontmatter" | grep -qE "^${key}:"; then
          err "$(basename "$f"): front-matter sem chave obrigatória '${key}:'"
        fi
      done
      name_val=$(echo "$frontmatter" | grep -E '^name:' | head -1 | sed -E 's/^name:\s*//')
      if [[ -n "$name_val" && "$name_val" != "$base" ]]; then
        err "$(basename "$f"): name: '${name_val}' não bate com o nome do arquivo '${base}'"
      fi
    fi
  done
fi

# ---------------------------------------------------------------------
# Relatório final
# ---------------------------------------------------------------------
echo "validate-syntax.sh — ${CHECKS} verificações executadas"
if [[ ${#ERRORS[@]} -eq 0 ]]; then
  echo "OK — nenhum erro de sintaxe encontrado."
  exit 0
fi

echo ""
echo "FALHOU — ${#ERRORS[@]} erro(s):"
for e in "${ERRORS[@]}"; do
  echo "  - ${e}"
done
exit 1
