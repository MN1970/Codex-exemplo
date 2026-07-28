# maestro-protocolos — P1 + P2 Executor

Skill de orquestração dos Protocolos Operacionais Maestro:
- **P1:** Confirmação obrigatória de Banco de Dados + Data
- **P2:** Execução paralela com até 16 agentes Sonnet

**Versão:** 4.3 | **Status:** ✅ Operacional

---

## P1 — Confirmação Banco de Dados + Data

### Aplicação
Ativado automaticamente quando usuário menciona:
- SICRO, DER-SP, ORSE, SINAPI
- Orçamento, preço unitário, TPU
- Análise de custos

### Fluxo obrigatório
```
1. ❓ Qual banco de dados você quer usar?
   • SICRO (DNIT)
   • DER-SP (São Paulo)
   • ORSE (Rio de Janeiro)
   • SINAPI (CAIXA)
   • Outro?

2. ❓ Qual data de referência?
   • JAN/2026
   • DEZ/2025
   • Outra?

3. ℹ️ Se não houver data:
   "Não encontrei essa data. Vou usar a disponível: SICRO JAN/2026. Confirma?"

4. ✅ CONFIRMA? (Espera resposta antes de executar)
```

### Roteamento automático após P1
- Manta 05 (Orçamento) — montar BDI, composição
- Agentes S1-S10 — análise segmentada
- Comparador SICRO ↔ DER-SP (se relevante)

### Exemplo
```
Usuário: "Orçamento DER-SP para sondagem"
↓
Maestro: "❓ Banco: DER-SP ✓ Data: qual? (JAN/2026 disponível?)"
Usuário: "Jan 2026"
↓
Maestro: "✅ Usando DER-SP JAN/2026. Prosseguindo..."
```

---

## P2 — Execução Paralela 16x Sonnet

### Aplicação
Ativado quando usuário menciona:
- "Execute com 16 agentes"
- "Paralelo 16x Sonnet"
- "/maestro-parallel 16"
- "16 agentes em paralelo"

### Capacidade
| Parâmetro | Valor |
|-----------|-------|
| **Máximo simultâneos** | 16 agentes |
| **Recomendação** | 15 agentes (medium tier) |
| **Modelo** | Sonnet (qualquer versão) |
| **Modo** | parallel() ou pipeline() |
| **Overhead worktree** | ~3-8s total |
| **Limite lifetime** | 1.000 agentes/workflow |

### Fluxo P2
```
1. Recebe: tarefas independentes (1-16)
2. Dispara: Workflow "maestro-16-agentes-paralelo"
3. Modo: parallel() se sem dependência
4. Resultado: array [resultado1, resultado2, ...]
5. Filtra: .filter(Boolean) para remover nulls
```

### Exemplo
```
Usuário: "Execute com 16 agentes: analise EVTE de 16 sub-projetos"
↓
Maestro: "Disparando 16x Sonnet paralelo. Tempo estimado: 8-15 min"
[Agente 1 → resultado] [Agente 2 → resultado] ... [Agente 16 → resultado]
↓
Maestro: "✅ 16 análises concluídas. Sintetizando..."
```

### Quando usar P2
✅ **USE:**
- Tarefas **independentes** (não dependem umas das outras)
- Cada uma leva **2-10 minutos**
- Precisa resultado em **< 15 min**
- Tem **budget +300k tokens**

❌ **NÃO USE:**
- Agentes dependem de outros (use `pipeline()`)
- Quer resultado em **< 1 min** (setup demora)
- Budget muito apertado (use 4-6 agentes)

---

## Ativação

### Automática
Configurada em `.claude/settings.json`:
```json
{
  "hooks": {
    "on_message_received": [
      { "pattern": "SICRO|DER-SP|orçamento", "action": "p1-confirm-banco-data" },
      { "pattern": "16 agentes|paralelo.*16", "action": "p2-parallel-16-sonnet" }
    ]
  }
}
```

### Manual
```
/maestro-protocolos p1
/maestro-protocolos p2
/maestro-parallel 16
/maestro-banco SICRO JAN/2026
```

---

## Status v4.3

```
🟢 P1 ativo — Confirma banco+data
🟢 P2 ativo — Paralelo 16x Sonnet
🟢 Hooks configurados
🟢 Workflow template pronto
🟢 Roteamento integrado ao Maestro
```

**Pronto para operação contínua.** 🚀
