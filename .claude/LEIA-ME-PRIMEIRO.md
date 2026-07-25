# LEIA-ME PRIMEIRO — Execução v4.2 Semana 1

**Bem-vindo ao Deploy v4.2!** Este é seu hub de controle para a semana 1 (25–31 jul 2026).

---

## NAVEGAÇÃO RÁPIDA

### 📋 Seu Dia-a-Dia

1. **Comece aqui:** [`CHECKLIST-SEMANA1-EXEC.md`](./CHECKLIST-SEMANA1-EXEC.md)
   - ✅ Checklist completo com prazos hora-a-hora
   - 🎯 Dependências e caminho crítico
   - 👥 Matriz de responsabilidades
   - ⏰ Cronograma visual (seg–dom)
   - 📞 Contatos de escalação

2. **Acompanhe desvios:** [`DESVIOS.md`](./DESVIOS.md)
   - 🚨 Se algo atrasar > 30 min
   - 🔒 Se há bloqueador técnico
   - 📝 Lições aprendidas (ao final)

3. **Report diário:** [`STANDUP-DAILY-TEMPLATE.md`](./STANDUP-DAILY-TEMPLATE.md)
   - 📊 Template para daily standup com MN
   - 📋 Tabelas prontas para preencher
   - 🔔 Formato para Slack

### 🔧 Arquivos de Referência

- **Agentes novos:** `.claude/agents/` (5 SKILL.md)
  - `agente-saneamento.md`
  - `agente-energia.md`
  - `agente-portos.md`
  - `agente-aeroportos.md`
  - `agente-barragens.md`

- **Instruções mestras:** `CLAUDE.md` (v4.2)
  - Tabelas de segmentos (Eixo 2)
  - Regras de routing (seção Routing)
  - Colections RAG (seção RAG)
  - Checklist original (para comparação)

---

## SUA SEMANA EM 3 FASES

### 🔴 FASE 1 — Seg–Ter (25–26 jul): Infra & Base
**Seu papel:** Criar coleções Supabase + validar
**MN role:** Criar routing rules + pastas SharePoint

**Tarefas:**
1. `1.1` → Supabase RAG collections (você)
2. `1.2` → Routing SharePoint (MN)
3. `1.3` → Pastas SharePoint (MN)

**Checkpoint:** Terça 08:00 UTC

---

### 🟡 FASE 2 — Qua–Qui (27–28 jul): Config & Docs
**Seu papel:** Registrar skills + carregar dados
**MN role:** Review arquitetura

**Tarefas:**
1. `2.1` → Skills registry (você)
2. `2.2` → Carga RAG (você + especialista)
3. `2.3` → Arquitetura updated (você + MN review)

**Checkpoint:** Quarta 08:00 UTC

---

### 🟢 FASE 3 — Sex–Sab (29–30 jul): Testes & Aprovação
**Seu papel:** Testar routing + upload SKILL.md
**MN role:** Gate final + merge

**Tarefas:**
1. `3.1` → Testes routing (você + especialista Maestro)
2. `3.2` → Upload SKILL.md SharePoint (MN)
3. `3.3` → Aprovação final MN (gate)

**Checkpoint:** Sexta 17:00 UTC (notifique MN 24h antes)

---

## COMO USAR ESTE CHECKLIST

### ✅ Marcando Progresso

**No CHECKLIST-SEMANA1-EXEC.md:**

```markdown
- [ ] Item não iniciado
- [🔄] Item em progresso
- [✅] Item completo
```

**Faça commit a cada atualização:**
```bash
git add CHECKLIST-SEMANA1-EXEC.md DESVIOS.md
git commit -m "Update: tarefa 1.1 completa com sucesso"
```

### 📊 Daily Standup (com MN)

**Cada dia às 08:00 UTC (ou à hora ajustada):**

1. Abra [`STANDUP-DAILY-TEMPLATE.md`](./STANDUP-DAILY-TEMPLATE.md)
2. Copie a seção do seu dia
3. Preencha as informações
4. Envie para MN no Slack (#deploy-v4.2 ou equivalente)

**Formato Slack:**
```
📊 DAILY STANDUP — Quarta 27 jul

Tarefa crítica: 2.2 (Carga RAG)
Status: ✅ On track
% Conclusão geral: 45%

| 2.2 (Carga RAG) | Quarta 13:00 | Quarta 15:30 | 75% | 🔄 Em progresso |

Próximos: Finalizar 2.2 + iniciar 2.3

Detalhes: .claude/STANDUP-DAILY-TEMPLATE.md
```

### 🚨 Registrando Bloqueadores

**Se algo atrassar:**

1. Abra [`DESVIOS.md`](./DESVIOS.md)
2. Adicione uma linha em "Bloqueadores Técnicos"
3. Notifique MN no Slack (se > 1h)

**Exemplo:**
```
| 2026-07-26 | 1.1 | API Supabase timeout em 5000 docs | Reduza batch size + retry | especialista-bd | 2026-07-26 15:00 |
```

### 📝 Lições Aprendidas

**Ao final de cada tarefa, registre em DESVIOS.md:**

```
| 2026-07-26 | Carga RAG | Documentos SNIS com XML aninhado demoram embedding | Pré-processar antes de carregar | 
```

---

## CAMINHO CRÍTICO (Não deixar atrasar!)

```
1.1 (Supabase)
  ↓ deve estar 100% antes de 2.2
2.2 (Carga RAG)
  ↓ deve estar 100% antes de 3.1
3.1 (Testes routing)
  ↓ deve estar 100% antes de 3.3
3.3 (Gate MN) ← DEADLINE SÁBADO 17:00 UTC
```

**Se 1.1 atrasar em 1h → 3.3 atrasa em 1h.**

---

## CRONOGRAMA COMPRIMIDO

```
SEG 25  | Prepare-se, leia este documento
TER 26  | 1.1 + 1.2 + 1.3 (infra) + checkpoint
QUA 27  | 2.1 + 2.2 + 2.3 (config) + checkpoint
QUI 28  | Ajustes finais
SEX 29  | 3.1 + 3.2 (testes) + notifique MN
SÁB 30  | 3.3 (gate MN) + merge + tag v4.2
DOM 31  | Buffer & lições aprendidas
```

---

## CONTATOS DE EMERGÊNCIA

| Papel | Nome | Email | Slack | Quando contatar |
|-------|------|-------|-------|-----------------|
| Product Owner | MN | mneves@mantaassociados.com | @mneves | Desvio > 2h, gate final |
| Você (Lead) | Claude-Haiku | — | — | Daily standup 08:00 UTC |
| Esp. Supabase | [TBD] | — | — | Bloqueador BD |
| Esp. SharePoint | [TBD] | — | — | Bloqueador SP |
| Esp. Maestro | [TBD] | — | — | Bloqueador routing |

**Escalação:**
- 🟢 Tudo bem → continue
- 🟡 Atraso < 1h → log em DESVIOS
- 🟠 Atraso 1–2h → notifique MN + Slack
- 🔴 Bloqueador crítico → chamada com MN + especialista

---

## CHECKLIST DE LEITURA (Faça agora)

- [ ] Li `LEIA-ME-PRIMEIRO.md` (este arquivo)
- [ ] Li `CHECKLIST-SEMANA1-EXEC.md` completamente
- [ ] Identifiquei meu papel (você vs MN vs especialista)
- [ ] Entendi o caminho crítico (1.1 → 2.2 → 3.1 → 3.3)
- [ ] Salvei contatos de emergência
- [ ] Baixei/imprimi o cronograma visual
- [ ] Agendei checkpoints diários (08:00 UTC)
- [ ] Configurei notificação para MN (sexta 17:00 → notify at 16:00)

---

## ARTEFATOS AO FINAL

Ao sábado 30 jul 17:00 UTC, você deve ter:

- ✅ `CHECKLIST-SEMANA1-EXEC.md` 100% preenchido
- ✅ `DESVIOS.md` com histórico de mudanças
- ✅ 5 coleções RAG em Supabase (san, ene, por, aer, bar)
- ✅ 5 pastas SharePoint criadas
- ✅ 5 SKILL.md uploadados para SP
- ✅ `ARQUITETURA-AGENTES-IA.md` atualizado (v1.0.0 → v2.0.0)
- ✅ Testes de routing passando 100%
- ✅ Git tag `v4.2` com changelog
- ✅ Aprovação final de MN

---

## PERGUNTAS FREQUENTES

### P: E se algo atrasar?
**R:** Log em `DESVIOS.md` + notifique MN. Ele ajudará a replanejear.

### P: Qual é o prazo mais crítico?
**R:** Sábado 30 jul 17:00 UTC (gate MN). Tudo antes disso é preparação.

### P: Posso fazer tarefas em paralelo?
**R:** Sim! 1.1, 1.2, 1.3, 2.1 podem ser paralelos, mas respeite as dependências no CHECKLIST.

### P: E se eu não conseguir Supabase no prazo?
**R:** Notifique MN imediatamente. Ele acionará especialista BD ou ajustará timeline.

### P: Como reporto testes de 3.1?
**R:** Use tabela em STANDUP-DAILY-TEMPLATE.md seção "Relatório de testes (3.1)".

---

## PRÓXIMOS PASSOS

1. **Agora:** Leia `CHECKLIST-SEMANA1-EXEC.md` completamente
2. **Hoje (seg 25):** Prepare Supabase + alerte especialistas
3. **Amanhã (ter 26):** Primeira tarefa 1.1 de manhã
4. **Após 1.1:** Daily standup com MN em `STANDUP-DAILY-TEMPLATE.md`

---

## SUPORTE

- **Dúvida no checklist?** → MN no Slack
- **Bloqueador técnico?** → Log em `DESVIOS.md` + especialista
- **Lição aprendida?** → Registre em `DESVIOS.md` para post-mortem

---

**Documento criado:** 2026-07-25 14:30 UTC  
**Válido para:** Semana 1 do Deploy v4.2 (25–31 jul 2026)  
**Última atualização:** 2026-07-25 14:30 UTC  

**Status global:** 🟢 **PRONTO PARA COMEÇAR**

---

## Lembrete Final

> "Um checklist bem estruturado evita 80% dos atrasos. Use-o como companheiro, não como punição."
> — Filosofia de execução Manta

**Você consegue! 💪**
