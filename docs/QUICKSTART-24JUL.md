# GUIA RÁPIDO — Comece AGORA (24-Jul-2026)

**Duração**: ~2 horas (hoje)
**Objetivo**: Preparar ambiente + iniciar sincronização TIER 1

---

## PASSO 1: VERIFICAR PRÉ-REQUISITOS (5 MIN)

Executar:
```bash
# 1. rclone instalado?
rclone version

# 2. Acesso ao SharePoint?
rclone listremotes
# Deve exibir um remote (ex: "sharepoint", "onedrive", etc.)

# 3. Espaço em disco?
df -h ~
# Deve ter >5 GB disponível
```

Se algum falhar:
- **rclone não instalado**: `brew install rclone` (Mac) ou `apt install rclone` (Linux)
- **Remote não existe**: Configurar com `rclone config`
  - Tipo: `Microsoft Graph`
  - Client ID: Deixar em branco (usa padrão)
  - Seguir prompts até obter acesso ao SharePoint
- **Espaço insuficiente**: Limpar pasta `~/Downloads` ou usar HD externo

---

## PASSO 2: COPIAR SCRIPTS (2 MIN)

Ler o arquivo `/tmp/claude-0/-home-user-Codex-exemplo/47a02d8e-8b20-58af-9e2f-c1a14322497b/scratchpad/SCRIPTS-PRONTOS-S6-S10.sh`

Executar (uma única vez):
```bash
bash /tmp/claude-0/-home-user-Codex-exemplo/47a02d8e-8b20-58af-9e2f-c1a14322497b/scratchpad/SCRIPTS-PRONTOS-S6-S10.sh
```

Isso vai criar ~7 scripts em `~/` :
- `setup-sync-s6-s10.sh`
- `sync-tier1.sh`
- `validate-tier1.sh`
- `sync-tier2.sh`
- `generate-gaps-report.sh`
- `checklist-s*.sh` (5 versões)
- `generate-consolidation-report.sh`

Verificar:
```bash
ls -lh ~/*s6-s10.sh ~/*tier*.sh ~/*checklist*.sh
```

---

## PASSO 3: EXECUTAR SETUP (2 MIN)

```bash
bash ~/setup-sync-s6-s10.sh
```

Esperado:
```
Setup: Sincronização SharePoint S6-S10
Diretório: /home/user/Manta-S6-S10-Sync
✓ Setup completo!
```

Verificar:
```bash
ls -lh ~/Manta-S6-S10-Sync/03_Projetos/
# Deve exibir: Saneamento/ Energia/ Portos/ Barragens/ Aeroportos/
```

---

## PASSO 4: SINCRONIZAR TIER 1 (45-60 MIN)

⚠️ **ESTE PASSO DEMORA** — pode sair e deixar rodando

```bash
time bash ~/sync-tier1.sh
# Vai exibir progresso + tempo total no final

# Alternativa: rodar em background
nohup bash ~/sync-tier1.sh > ~/Manta-S6-S10-Sync/logs/tier1.out 2>&1 &

# Acompanhar progresso:
tail -f ~/Manta-S6-S10-Sync/logs/tier1.out
```

Esperado:
```
[10:15:20] Sincronizando Saneamento/00-Normativos...
  ✓ Sucesso: 45 arquivos, 320 MB

[10:20:15] Sincronizando Energia/00-Normativos...
  ✓ Sucesso: 52 arquivos, 280 MB

... (continua para outros 3 segmentos)

✓ TIER 1 sincronização completo
Próximo passo: ./validate-tier1.sh
```

**Tamanho total esperado TIER 1**: 1.1–1.6 GB

---

## PASSO 5: VALIDAR TIER 1 (5 MIN)

Após conclusão de PASSO 4:

```bash
bash ~/validate-tier1.sh
```

Esperado:
```
[✓] Saneamento: 45 arquivos, 320 MB
[✓] Energia: 52 arquivos, 280 MB
[✓] Portos: 38 arquivos, 210 MB
[✓] Barragens: 42 arquivos, 240 MB
[✓] Aeroportos: 35 arquivos, 185 MB

TOTAL: 212 arquivos em TIER 1

✓ Relatório salvo: .../validate-tier1-*.txt
```

Se aparecer `[⚠] PASTA VAZIA` para algum segmento:
- Verificar se pasta existe em SharePoint: `rclone lsd sharepoint:...`
- Se não existe, criar manualmente no SharePoint e sincronizar novamente

---

## PASSO 6: ANALISAR GAPS (3 MIN)

```bash
bash ~/generate-gaps-report.sh
```

Revisar relatório. Se tudo OK:
```
[✓] Saneamento/00-Normativos: 45 arquivos
[✓] Saneamento/01-Projetos-Executados: 15 arquivos
[✓] Saneamento/02-Estudos-Primarios: 8 arquivos
... (etc)

STATUS: OK para continuar com TIER 2
```

Se muitos `[⚠]` ou `[✗]`:
- Verificar manualmente no SharePoint: https://manta.sharepoint.com/sites/...
- Fazer upload de documentos faltantes
- Rodar `sync-tier1.sh` novamente

---

## PASSO 7: SINCRONIZAR TIER 2 (45-90 MIN) — AMANHÃ OU HOJE À NOITE

Deixar TIER 1 validado. Depois:

```bash
# Deixar rodando (pode sair)
nohup bash ~/sync-tier2.sh > ~/Manta-S6-S10-Sync/logs/tier2.out 2>&1 &

# Acompanhar
tail -f ~/Manta-S6-S10-Sync/logs/tier2.out
```

Esperado (após 1-2 horas):
```
[✓] Saneamento/01-Projetos-Executados: 500 MB
[✓] Saneamento/02-Estudos-Primarios: 200 MB
[✓] Energia/01-Projetos-Executados: 600 MB
... (etc)

✓ TIER 2 sincronizado
Próximo passo: Executar checklists por segmento
```

---

## PASSO 8: VALIDAR POR SEGMENTO (25-JUL)

Executar um de cada vez:

```bash
bash ~/checklist-s8.sh   # Saneamento
bash ~/checklist-s9.sh   # Energia
bash ~/checklist-s6.sh   # Portos
bash ~/checklist-s10.sh  # Barragens
bash ~/checklist-s7.sh   # Aeroportos
```

Esperado (exemplo S8):
```
=== CHECKLIST S8 - SANEAMENTO ===
Data: Jul 25 2026

[TIER 1 - Normativos]
  [✓] Lei 14.026/2020
  [✓] NBR 12211-12218

[TIER 2 - Projetos]
  Projetos encontrados: 18
  [✓] Mínimo 3 projetos
```

---

## PASSO 9: RELATÓRIO CONSOLIDADO (25-JUL)

```bash
bash ~/generate-consolidation-report.sh
```

Esperado:
```
=== CONSOLIDAÇÃO S6-S10 ===

--- Saneamento ---
Arquivos: 68
Tamanho: 720 MB

--- Energia ---
Arquivos: 92
Tamanho: 880 MB

... (etc)

TOTAL GERAL: 650+ arquivos
Tamanho: 3.5–4.5 GB

STATUS: Pronto para FASE 2 (RAG Ingestion)
```

---

## ✅ CHECKLIST HOJE (24-JUL)

- [ ] rclone verificado e funcionando
- [ ] Scripts copiados para ~/
- [ ] `setup-sync-s6-s10.sh` executado
- [ ] `sync-tier1.sh` iniciado (deixa rodando)
- [ ] Parar aqui por hoje

---

## ✅ CHECKLIST AMANHÃ (25-JUL)

- [ ] `validate-tier1.sh` executado
- [ ] `generate-gaps-report.sh` revisado
- [ ] Gaps corrigidos (se houver)
- [ ] `sync-tier2.sh` iniciado (deixa rodando)
- [ ] Enquanto aguarda, revisar PLANO-SINCRONIZACAO-S6-S10.md

---

## ✅ CHECKLIST 26-JUL (SEMANA)

- [ ] TIER 2 validado
- [ ] Checklists (S6-S10) todos passando
- [ ] Consolidation report gerado
- [ ] SINAL VERDE para FASE 2 (RAG)

---

## PROBLEMAS COMUNS + SOLUÇÕES

### Problema 1: "rclone: not found"
```bash
# Solução: instalar
brew install rclone  # Mac
apt install rclone   # Linux
```

### Problema 2: "No remote found"
```bash
# Solução: configurar rclone
rclone config
# Selecionar "n" (new remote)
# Nome: "sharepoint"
# Tipo: "Microsoft Graph"
# Seguir instruções
```

### Problema 3: "Permission denied" ao sincronizar
```bash
# Solução: verificar acesso ao SharePoint
rclone lsd sharepoint:
# Se falhar, reauthenticar:
rclone config
# Editar remote existente, fazer reauth
```

### Problema 4: "Pasta vazia após sincronização"
```bash
# Solução: verificar se existe no SharePoint
rclone lsd sharepoint:"Manta Associados/Documentos Compartilhados/03_Projetos/Saneamento/00-Normativos"

# Se mostrar nada, a pasta não existe — criar no SharePoint web
```

### Problema 5: "Sync lento"
```bash
# Normal — TIER 1 = 1-2 horas, TIER 2 = 1-3 horas
# Deixa rodando em background:
nohup bash ~/sync-tier1.sh > ~/Manta-S6-S10-Sync/logs/sync.out 2>&1 &

# Acompanhar:
tail -f ~/Manta-S6-S10-Sync/logs/sync.out
```

---

## PRÓXIMAS FASES (SEM AÇÃO HOJE)

### FASE 2 (31-Jul a 04-Ago): Preparar RAG Supabase
- Criar table `rag_chunks` em Supabase
- Chunking/embedding de documentos
- Bulk insert com metadata

### FASE 3 (07-Jul a 11-Ago): Validar Agentes
- Testar routing (Maestro → agentes corretos)
- Testar respostas fundadas em RAG

### FASE 4 (14-Ago): Go-live
- Deploy público
- Comunicado ao time

---

## DOCUMENTAÇÃO COMPLETA

Arquivos referência (em scratchpad):
1. **PLANO-SINCRONIZACAO-S6-S10.md** — Plano detalhado (50+ páginas, todos os scripts)
2. **SUMARIO-EXECUTIVO-S6-S10.md** — Sumário 1-página (visão executiva)
3. **SCRIPTS-PRONTOS-S6-S10.sh** — Gerador de scripts (copiar/colar)
4. **QUICKSTART-24JUL.md** — Este arquivo

---

## SUPORTE

Se algo der errado:
1. Revisar "PROBLEMAS COMUNS" acima
2. Ler logs em `~/Manta-S6-S10-Sync/logs/*.log`
3. Revisar PLANO-SINCRONIZACAO-S6-S10.md seção 2.2 (Script de Sincronização)
4. Contactar Maestro (mneves@mantaassociados.com)

---

## TL;DR — 3 COMANDOS PARA COMEÇAR

```bash
# 1. Uma única vez: copiar scripts
bash /tmp/claude-0/-home-user-Codex-exemplo/47a02d8e-8b20-58af-9e2f-c1a14322497b/scratchpad/SCRIPTS-PRONTOS-S6-S10.sh

# 2. Setup local (2 min)
bash ~/setup-sync-s6-s10.sh

# 3. Sincronizar TIER 1 (deixa rodando, 1h)
time bash ~/sync-tier1.sh
```

**Esperado ao final do dia**: 1.1-1.6 GB de normativos sincronizados em `~/Manta-S6-S10-Sync/`.

---

**Maestro | v1.0 | 2026-07-24**
