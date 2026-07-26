#!/usr/bin/env bash
# detect-breaking.sh — Manta Maestro Agent Registry
#
# Check 5/5 do workflow agent-validation: compara o PR (HEAD) contra o
# ref base e sinaliza mudanças "breaking" no registro de agentes — ou
# seja, mudanças que quebrariam contratos que outros sistemas (RAG,
# SharePoint, o próprio Maestro em runtime) já dependem:
#
#   1. Um agente vertical (linha "Manta 03-S<n>") foi removido da
#      tabela Eixo 2 do CLAUDE.md.
#   2. Uma regra do bloco ROUTING que existia na base sumiu no HEAD
#      (um segmento perdeu seu dispatch).
#   3. Um arquivo .claude/agents/*.md que existia na base foi deletado
#      no HEAD.
#   4. O front-matter `name:` de um agente existente mudou (rename
#      silencioso — quebra qualquer referência por slug).
#   5. Uma linha da tabela RAG ou da tabela SHAREPOINT foi removida.
#
# Isso não impede o merge por si só (o CLAUDE.md já exige "Gate
# humano: aprovação MN" no checklist) — o job existe para tornar
# essas mudanças VISÍVEIS no comentário do PR antes do gate humano,
# não para bloquear silenciosamente.
#
# Uso:
#   ./scripts/detect-breaking.sh [repo-root] [base-ref]
#
# base-ref default: $BASE_REF do ambiente, senão "origin/main".
# Se o base-ref não existir (ex.: rodando local sem remoto, ou é o
# primeiro commit do repo), o script reporta isso e sai 0 — não há
# "antes" para comparar, então não há como haver regressão.
#
# Exit code: 0 = sem breaking changes (ou sem base para comparar);
#            1 = pelo menos um breaking change encontrado.

set -uo pipefail

ROOT="${1:-.}"
BASE_REF="${2:-${BASE_REF:-origin/main}}"

cd "$ROOT" || { echo "ERRO: não foi possível entrar em ${ROOT}"; exit 1; }

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERRO: ${ROOT} não é um repositório git"
  exit 1
fi

if ! git rev-parse --verify --quiet "${BASE_REF}" >/dev/null; then
  echo "detect-breaking.sh: base-ref '${BASE_REF}' não existe neste checkout."
  echo "Nada para comparar — assumindo OK (primeiro commit / sem remoto fetched)."
  exit 0
fi

# HEAD == BASE_REF (ex.: push direto no main, ou workflow_dispatch sem PR)
if [[ "$(git rev-parse "${BASE_REF}")" == "$(git rev-parse HEAD)" ]]; then
  echo "detect-breaking.sh: HEAD == ${BASE_REF}, nada a comparar."
  exit 0
fi

ERRORS=()
err() { ERRORS+=("$1"); }

show_base_file() {
  # imprime o conteúdo do arquivo em BASE_REF, ou vazio se não existia
  git show "${BASE_REF}:$1" 2>/dev/null || true
}

file_exists_in_base() {
  git cat-file -e "${BASE_REF}:$1" 2>/dev/null
}

# NOTA: as três funções abaixo recebem o texto do CLAUDE.md via stdin
# (`echo "$text" | extract_...`). `python3 - <<'EOF'` NÃO funciona aqui
# porque o heredoc tomaria conta do stdin do próprio python (que é
# como "python3 -" lê o código-fonte a executar), deixando nada para
# o `sys.stdin.read()` de dentro do script ler — o pipe seria
# descartado silenciosamente. Por isso usamos `python3 <(cat <<'EOF')`:
# a substituição de processo entrega o heredoc como um ARQUIVO de
# script (via /dev/fd/N), e o stdin real do processo python continua
# livre para receber o pipe.

extract_agente_slugs() {
  # lê o CLAUDE.md (via stdin) e imprime um slug de agente vertical por linha
  # a partir das linhas "| Manta 03-S<n> | ... | <agente> | ... |"
  python3 <(cat <<'PYEOF'
import re
import sys

text = sys.stdin.read()
for m in re.finditer(
    r"^\|\s*Manta 03-S(\d+)\s*\|[^|]*\|\s*([^|]+?)\s*\|[^|]*\|\s*$",
    text,
    re.MULTILINE,
):
    seg, agente_raw = m.groups()
    slug = re.sub(r"\s*\(.*\)\s*$", "", agente_raw).strip()
    print(f"S{seg}\t{slug}")
PYEOF
)
}

extract_routing_targets() {
  python3 <(cat <<'PYEOF'
import re
import sys

text = sys.stdin.read()
m = re.search(r"## ROUTING.*?```\n(.*?)```", text, re.DOTALL)
if not m:
    sys.exit(0)
body = m.group(1)
for rm in re.finditer(r"→\s*([^\n]+)", body):
    target = re.sub(r"\s*\(S\d+\)\s*$", "", rm.group(1).strip())
    print(target)
PYEOF
)
}

extract_table_rows() {
  # $1 = título da seção a procurar (ex.: "## RAG", "## SHAREPOINT")
  python3 <(cat <<'PYEOF'
import re
import sys

heading_pat = sys.argv[1]
text = sys.stdin.read()
m = re.search(re.escape(heading_pat) + r".*?\n\n(?P<table>(?:\|.*\n)+)", text)
if not m:
    sys.exit(0)
rows = m.group("table").splitlines()
# pula header + linha separadora
for row in rows[2:]:
    print(row.strip())
PYEOF
) "$1"
}

CLAUDE_CHANGED=false
if ! git diff --quiet "${BASE_REF}"...HEAD -- CLAUDE.md 2>/dev/null; then
  CLAUDE_CHANGED=true
fi

if $CLAUDE_CHANGED && file_exists_in_base CLAUDE.md; then
  base_text="$(show_base_file CLAUDE.md)"
  head_text="$(cat CLAUDE.md 2>/dev/null || true)"

  # 1. agentes verticais removidos da tabela Eixo 2
  base_agents="$(echo "$base_text" | extract_agente_slugs)"
  head_agents="$(echo "$head_text" | extract_agente_slugs)"
  while IFS=$'\t' read -r seg slug; do
    [[ -z "$seg" ]] && continue
    if ! echo "$head_agents" | grep -qF "$(printf '%s\t%s' "$seg" "$slug")"; then
      err "CLAUDE.md: Manta 03-${seg} (${slug}) existia na base e sumiu da tabela Eixo 2"
    fi
  done <<< "$base_agents"

  # 2. regras de ROUTING removidas
  base_targets="$(echo "$base_text" | extract_routing_targets | sort -u)"
  head_targets="$(echo "$head_text" | extract_routing_targets | sort -u)"
  while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    if ! echo "$head_targets" | grep -qxF "$target"; then
      err "CLAUDE.md: regra ROUTING para '${target}' existia na base e sumiu do bloco ROUTING"
    fi
  done <<< "$base_targets"

  # 5. linhas removidas das tabelas RAG e SHAREPOINT
  for heading in "## RAG — Coleções em Supabase" "## SHAREPOINT — Routing rules (sp_agent_routing)"; do
    base_rows="$(echo "$base_text" | extract_table_rows "$heading")"
    head_rows="$(echo "$head_text" | extract_table_rows "$heading")"
    while IFS= read -r row; do
      [[ -z "$row" ]] && continue
      if ! echo "$head_rows" | grep -qxF "$row"; then
        err "CLAUDE.md: linha removida da tabela '${heading}': ${row}"
      fi
    done <<< "$base_rows"
  done
else
  echo "detect-breaking.sh: CLAUDE.md não mudou (ou não existia na base) — pulando checks 1/2/5."
fi

# ---------------------------------------------------------------------
# 3 e 4. arquivos de agente deletados ou renomeados (front-matter name:)
# ---------------------------------------------------------------------
shopt -s nullglob
for f in .claude/agents/*.md; do
  rel="$f"
  if file_exists_in_base "$rel"; then
    # arquivo existia na base — segue existindo? nullglob já garante que
    # só listamos o que existe no HEAD, então checamos deleções via
    # `git diff --diff-filter=D` abaixo, e aqui só checamos rename de name:
    base_name=$(show_base_file "$rel" | awk -F': *' '/^name:/{print $2; exit}')
    head_name=$(awk -F': *' '/^name:/{print $2; exit}' "$f")
    if [[ -n "$base_name" && -n "$head_name" && "$base_name" != "$head_name" ]]; then
      err "${rel}: front-matter name mudou de '${base_name}' para '${head_name}' (rename silencioso)"
    fi
  fi
done
shopt -u nullglob

while IFS= read -r deleted; do
  [[ -z "$deleted" ]] && continue
  err "arquivo de agente deletado neste PR: ${deleted}"
done < <(git diff --name-only --diff-filter=D "${BASE_REF}"...HEAD -- '.claude/agents/*.md' 2>/dev/null)

# ---------------------------------------------------------------------
# Relatório final
# ---------------------------------------------------------------------
echo "detect-breaking.sh — comparando HEAD vs ${BASE_REF}"
if [[ ${#ERRORS[@]} -eq 0 ]]; then
  echo "OK — nenhuma mudança breaking detectada."
  exit 0
fi

echo ""
echo "ATENÇÃO — ${#ERRORS[@]} mudança(s) potencialmente breaking (requer revisão humana MN):"
for e in "${ERRORS[@]}"; do
  echo "  - ${e}"
done
exit 1
