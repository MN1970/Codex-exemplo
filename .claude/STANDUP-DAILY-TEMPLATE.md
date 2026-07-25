# DAILY STANDUP TEMPLATE — v4.2 Deploy

Use este template para reportar status diariamente durante a Semana 1. Copie a seção do seu dia, preencha, e compartilhe com MN no Slack.

---

## STANDUP — Terça 26 jul (08:00 UTC)

**Responsável:** Você (Claude-Haiku)  
**Checkpoint:** 1.1, 1.2, 1.3  

### O que foi feito ontem
- [ ] Preparação de dados Supabase
- [ ] Validação de credenciais API
- [ ] Alinhamento com especialistas

### Status das tarefas

| Tarefa | Planejado | Realizado | % Pronto | Status |
|--------|-----------|-----------|----------|--------|
| 1.1 (Supabase RAG) | Terça 09:00 | Terça 11:30 | 100% | ✅ Completo |
| 1.2 (Routing rules SP) | Terça 14:00 | [Pendente MN] | 0% | ⏳ Bloqueado |
| 1.3 (Pastas SP) | Terça 15:30 | [Pendente MN] | 0% | ⏳ Bloqueado |

### Bloqueadores
- [ ] Nenhum

### Próximos passos (hoje)
- [ ] Iniciar 2.1 (Skills registry) — 10:00 UTC
- [ ] Aguardar conclusão 1.2 + 1.3 por MN

### Notas adicionais
```
Exemplo:
- Supabase collections criadas com sucesso
- Embedding testado em 1000 docs (média 2.3s/doc)
- Aguardando aprovação MN para routing rules
```

### ETA para conclusão do caminho crítico
Sábado 30 jul 17:00 UTC (on track)

---

## STANDUP — Quarta 27 jul (08:00 UTC)

**Responsável:** Você (Claude-Haiku)  
**Checkpoint:** 2.1, 2.2, 2.3  

### O que foi feito ontem
- [ ] Tarefa X
- [ ] Tarefa Y

### Status das tarefas

| Tarefa | Planejado | Realizado | % Pronto | Status |
|--------|-----------|-----------|----------|--------|
| 2.1 (Skills registry) | Quarta 10:00 | | | [ ] Não iniciado |
| 2.2 (Carga RAG) | Quarta 13:00 | | | [ ] Não iniciado |
| 2.3 (Arquitetura atualizado) | Quarta 16:00 | | | [ ] Não iniciado |

### Bloqueadores
- [ ] Nenhum

### Próximos passos (hoje)
- [ ] Validação de 1.1 + 1.2 + 1.3 (devem estar 100%)
- [ ] Iniciar 2.1 e 2.2 em paralelo

### Notas adicionais
```
[Preencher durante o dia]
```

### ETA para conclusão do caminho crítico
[Atualizar baseado em progresso]

---

## STANDUP — Quinta 28 jul (08:00 UTC)

**Responsável:** Você (Claude-Haiku)  
**Checkpoint:** validação geral  

### O que foi feito ontem
- [ ] Tarefa X
- [ ] Tarefa Y

### Status das tarefas

| Tarefa | Planejado | Realizado | % Pronto | Status |
|--------|-----------|-----------|----------|--------|
| 2.2 (Carga RAG finalizada) | — | | | [ ] Não iniciado |
| 2.3 (Revisão MN) | — | | | [ ] Não iniciado |

### Bloqueadores
- [ ] Nenhum (esperado)

### Próximos passos (hoje)
- [ ] Ajustes finais em 2.2
- [ ] Preparação para testes de sexta (3.1)

### Notas adicionais
```
[Preencher durante o dia]
```

### ETA para conclusão do caminho crítico
[Atualizar baseado em progresso]

---

## STANDUP — Sexta 29 jul (17:00 UTC)

**Responsável:** Você (Claude-Haiku)  
**Checkpoint:** 3.1, 3.2 + preparação gate MN  

### O que foi feito ontem
- [ ] Tarefa X
- [ ] Tarefa Y

### Status das tarefas

| Tarefa | Planejado | Realizado | % Pronto | Status |
|--------|-----------|-----------|----------|--------|
| 3.1 (Testes routing) | Sexta 09:00 | | | [ ] Não iniciado |
| 3.2 (Upload SKILL.md SP) | Sexta 14:00 | | | [ ] Não iniciado |

### Bloqueadores
- [ ] [Crítico] [Descrição] — ETA fix: [data/hora]

### Relatório de testes (3.1)

**Sumário:**
- Total testes: [ ] 
- Testes passaram: [ ] / [ ]
- Testes falharam: [ ] / [ ]
- Taxa de sucesso: [ ]%

**Detalhes por segmento:**

| Segmento | Trigger palavra | Roteado para | Skill ativada | Status |
|----------|-----------------|--------------|---------------|--------|
| Saneamento | "ETA", "SNIS" | agente-saneamento | Sim | ✅ Pass |
| Energia | "ANEEL", "transmissão" | agente-energia | Sim | [ ] |
| Portos | "ANTAQ", "dragagem" | agente-portos | Sim | [ ] |
| Aeroportos | "ANAC", "pista" | agente-aeroportos | Sim | [ ] |
| Barragens | "barragem", "CFRD" | agente-barragens | Sim | [ ] |

**Artefatos de teste:**
- Log completo: `test-logs/routing-validation-2026-07-29.txt`
- Exemplos de fallback (se houver): [lista]

### Notificação para MN
- [ ] Slack message enviada: "Pronto para gate — veja relatório completo em CHECKLIST-SEMANA1-EXEC.md / 3.1"
- [ ] Prazo gate comunicado: Sábado 30 jul 17:00 UTC

### Próximos passos (sábado)
- [ ] Aguardar aprovação MN em 3.3
- [ ] Merge e tag v4.2 após aprovação

### Notas adicionais
```
[Preencher durante os testes de sexta]
```

### ETA para conclusão do caminho crítico
Sábado 30 jul 17:00 UTC (aguardando MN)

---

## FORMATO DE PREENCHIMENTO RÁPIDO

**Copie e adapte para seu dia:**

```markdown
## STANDUP — [DIA] [DATA] ([HORA] UTC)

**Responsável:** [Você / MN / Especialista]
**Checkpoint:** [Tarefas deste checkpoint]

### O que foi feito ontem
- [ ] Item 1
- [ ] Item 2

### Status das tarefas

| Tarefa | Planejado | Realizado | % Pronto | Status |
|--------|-----------|-----------|----------|--------|
| X | [hora] | [resultado] | [%] | [✅/🔄/⏳/❌] |

### Bloqueadores
- [ ] [Descrição — nível crítico]

### Próximos passos (hoje)
- [ ] Ação 1
- [ ] Ação 2

### Notas adicionais
```
Contexto livre
```

### ETA para conclusão do caminho crítico
[Data/hora]
```

---

## ENVIO PARA MN

Paste este report no Slack (#deploy-v4.2 ou equivalente):

```
📊 DAILY STANDUP — [DIA] [DATA]

Tarefa crítica: [X] 
Status: [✅ On track / ⏳ Slight delay / 🔴 Bloqueado]
% Conclusão geral: [X]%

[Copy & paste da tabela de status]

Próximos: [resumo de 1 linha]

Detalhes: [link para este arquivo]
```

---

**Template criado:** 2026-07-25 14:30 UTC  
**Para usar:** Copie a seção do seu dia, preencha, e envie para MN
