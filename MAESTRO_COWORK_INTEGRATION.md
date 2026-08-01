# 🤖 Maestro (Manta 00) — Integração Cowork

Guia de configuração para ativar o Maestro com skill `youtube-transcript` no Claude Cowork.

---

## 📋 Resumo Executivo

| Item | Status |
|------|--------|
| **Maestro Version** | v4.3 (2026-08-01) |
| **Plataforma** | Claude Cowork |
| **Skill C1** | youtube-transcript ✅ |
| **Agentes** | 20 (15 horizontais + 5 verticais) |
| **Routing** | Automático por trigger |

---

## 🚀 Setup no Cowork

### 1. Ativar o Maestro

```
/maestro

Ou mencione qualquer agente/skill que ativa o router automaticamente:
- "Extraia a transcrição de [link YouTube]"
- "Analise este vídeo: [link]"
- "O que fala neste vídeo?"
```

### 2. Triggers Automáticos Disponíveis

#### **Skill: youtube-transcript**
```
Ativa quando você menciona:
✅ youtube.com/...
✅ youtu.be/...
✅ "transcrição do vídeo"
✅ "legenda"
✅ "o que fala nesse vídeo"
✅ Link com "video" ou "vídeo"
```

**Exemplo:**
```
"Maestro, extraia a transcrição de https://www.youtube.com/watch?v=QoQBzR1NIqI"

→ Maestro detecta YouTube
→ Aciona skill: youtube-transcript
→ Retorna transcrição em texto/JSON com timestamps
```

---

## 📊 Routing Maestro (v4.3)

### Skills Horizontais (C1)
- **youtube-transcript**: Extrai legendas de vídeos YouTube

### Agentes Verticais (S1–S10)
| Segmento | Agente | Trigger |
|----------|--------|---------|
| **Rodovias** | agente-infraestrutura (S1) | rodovia, pavimento, SICRO |
| **Pontes/OAE** | agente-infraestrutura (S2) | ponte, viaduto, OAE |
| **Ferrovia** | agente-infraestrutura (S3) | ferrovia, trilho, dormente |
| **Metrô** | agente-infraestrutura (S4) | metrô, estação, NATM |
| **Saneamento** | agente-saneamento (S8) | ETA, ETE, adutora |
| **Energia** | agente-energia (S9) | transmissão, LT, ANEEL |
| **Portos** | agente-portos (S6) | porto, terminal, ANTAQ |
| **Aeroportos** | agente-aeroportos (S7) | aeroporto, pista, ANAC |
| **Barragens** | agente-barragens (S10) | barragem, vertedouro, ICOLD |

---

## 💡 Use Cases no Cowork

### 1. **Extrair Transcrição de Palestra**
```
📹 Vídeo: Palestra sobre Claude Code
🎯 Ação: "Extraia a transcrição e resuma"
✅ Resultado: Texto + timestamps
```

### 2. **Análise de Conteúdo Técnico**
```
📹 Vídeo: Tutorial de IA/Engenharia
🎯 Ação: "O que fala sobre [tópico]?"
✅ Resultado: Seções com timestamps
```

### 3. **Pesquisa Evolutiva (Gap G007)**
```
📹 Vídeo: Webinar/Conferência
🎯 Ação: "Alimente a EVOLUTION.md com insights"
✅ Resultado: Conteúdo textual para RAG
```

### 4. **Roteamento Inteligente**
```
📝 Pergunta: "Projeto de estrada com análise de vídeo"
→ Detecta: rodovia + vídeo
→ Aciona: skill youtube-transcript + agente-infraestrutura (S1)
✅ Resultado: Transcrição + análise estrutural
```

---

## 🔑 Comandos Rápidos no Cowork

```bash
# Ativar Maestro explicitamente
/maestro

# Extrair transcrição (ativa skill automaticamente)
"Transcrição de https://youtu.be/..."

# Rodar agente específico
/agente-saneamento "Analise este projeto"
/agente-energia "Transmissão ou distribuição?"

# Combinação: skill + agente
"Vídeo sobre rodovia: [link] + análise estrutural"
→ Maestro aciona skill + agente-infraestrutura (S1)
```

---

## 📁 Arquivos de Referência

```
Codex-exemplo/
├── CLAUDE.md                           # Master registry (v4.3)
├── MAESTRO_COWORK_INTEGRATION.md       # Este arquivo
├── youtube_transcript_extractor.py     # Script local
├── requirements-youtube.txt            # Dependências
├── YOUTUBE_TRANSCRIPT_README.md        # Docs completas
└── QUICK_START.md                      # Início rápido
```

---

## ⚙️ Configuração Avançada

### Personalizar Triggers
Edite `CLAUDE.md` seção `## ROUTING`:
```
IF menção a [seu_trigger]
   → skill: youtube-transcript
```

### Adicionar Novo Agente
1. Crie `.claude/agents/seu-agente.md`
2. Atualize `CLAUDE.md` com routing
3. Commit e push

---

## 🎓 Exemplos Reais no Cowork

### Exemplo 1: Extrair Claude Code Tutorial
```
Usuário: "Quero aprender Claude Code. Extraia o vídeo do Nick Saraev"

Maestro responde:
✅ Detecta YouTube (link ou nome do criador)
✅ Aciona skill: youtube-transcript
✅ Retorna:
   - transcript.txt (4 horas de conteúdo)
   - transcript.json (com timestamps)
   - Resumo dos tópicos principais
```

### Exemplo 2: Análise com Routing
```
Usuário: "Tenho um vídeo sobre transmissão de energia. 
         Extraia e analise com o agente-energia"

Maestro responde:
✅ Detecta: YouTube + "transmissão" + "energia"
✅ Aciona: skill youtube-transcript + agente-energia (S9)
✅ Retorna:
   - Transcrição do vídeo
   - Análise técnica (ANEEL, LT, RAP, etc)
   - Insights sobre leilão/ONS
```

---

## 🔗 Links Úteis

- **Maestro Registry**: CLAUDE.md (este repo)
- **Skill youtube-transcript**: `/root/.claude/skills/youtube-transcript/`
- **PR #45**: Integração completa documentada
- **Claude Cowork Docs**: https://claude.ai/cowork

---

## 📞 Suporte

**Problemas comuns:**

| Problema | Solução |
|----------|---------|
| "Vídeo sem legenda" | Use vídeo com captions ativadas |
| "Skill não ativa" | Mencione YouTube explicitamente |
| "Proxy bloqueando" | Use Cowork (não ambiente remote) |

**Contato**: mneves@mantaassociados.com

---

## ✅ Checklist de Ativação

- [x] Maestro v4.3 configurado
- [x] Skill youtube-transcript integrada
- [x] Routing rules definidas
- [x] Documentação completa
- [x] Exemplos fornecidos
- [x] PR #45 aprovada
- [ ] Deploy em produção (aguardando Gate MN)

---

**Versão**: 1.0.0  
**Data**: 2026-08-01  
**Status**: ✅ Pronto para Cowork

_Generated by [Claude Code](https://claude.ai/code)_
