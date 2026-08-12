#!/bin/bash
# block-sql-in-skill.sh
# Hook para bloquear execução de comandos SQL via Bash em skills
# Previne injeção de SQL e execução acidental de queries

set -euo pipefail

# Padrões SQL perigosos a detectar
SQL_PATTERNS=(
    "^[[:space:]]*SELECT[[:space:]]"
    "^[[:space:]]*INSERT[[:space:]]"
    "^[[:space:]]*UPDATE[[:space:]]"
    "^[[:space:]]*DELETE[[:space:]]"
    "^[[:space:]]*DROP[[:space:]]"
    "^[[:space:]]*ALTER[[:space:]]"
    "^[[:space:]]*CREATE[[:space:]]"
    "^[[:space:]]*TRUNCATE[[:space:]]"
    "^[[:space:]]*EXEC[[:space:]]"
    "^[[:space:]]*psql"
    "^[[:space:]]*mysql"
    "^[[:space:]]*sqlite3"
    "^[[:space:]]*sqlplus"
)

# Captura o comando que será executado
COMMAND="${1:-.}"

# Converte para maiúsculas para matching case-insensitive
COMMAND_UPPER=$(echo "$COMMAND" | tr '[:lower:]' '[:upper:]')

# Verifica cada padrão
for pattern in "${SQL_PATTERNS[@]}"; do
    if [[ "$COMMAND_UPPER" =~ $pattern ]]; then
        echo "❌ BLOQUEADO: Execução de SQL detectada em skill" >&2
        echo "   Comando: $COMMAND" >&2
        echo "   Padrão: $pattern" >&2
        echo "" >&2
        echo "   Por segurança, comandos SQL não são permitidos em bash skills." >&2
        echo "   Use o agente específico ou ferramentas dedicadas para operações de BD." >&2
        exit 1
    fi
done

# Comando aprovado
exit 0
