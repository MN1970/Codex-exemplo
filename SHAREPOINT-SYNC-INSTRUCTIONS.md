# Sincronização com SharePoint — Instruções Manuais

## ⚠️ Status: Autenticação Required

Os arquivos foram commitados no branch `claude/manta-mes-em-paaleo-iewro0` e estão prontos para sincronização com SharePoint.

Porém, a sessão atual não tem autenticação OAuth interativa para SharePoint. 

---

## 📁 Arquivos a Sincronizar

```
Codex-exemplo/
├── CLAUDE.md (atualizado com nova seção AUTOSCALING)
├── maestro-autoscaling-policy.html (26 KB)
├── manta-maestro-orquestracao-v5.html (34 KB)
└── quando-usar-claude-ai-cowork-code.html (23 KB)
```

---

## 🔗 Localização no SharePoint

Destino recomendado:

```
Site: Engenharia
Library: Documentos
Path: /04_IA/Manta-Maestro/00-arquitetura/
```

---

## ✅ Checklist de Sincronização Manual

Peça ao administrador do SharePoint (ou execute você mesmo em sessão interativa):

### Passo 1: Upload dos documentos HTML

1. Abra SharePoint → `/04_IA/Manta-Maestro/00-arquitetura/`
2. Faça upload dos 3 arquivos:
   - `maestro-autoscaling-policy.html`
   - `manta-maestro-orquestracao-v5.html`
   - `quando-usar-claude-ai-cowork-code.html`
3. Marque cada um com tag: `manta-maestro-v5` e `2026-08-08`

### Passo 2: Atualizar CLAUDE.md no SharePoint

1. Baixe o atual `CLAUDE.md` do SP (pasta `00-arquitetura/`)
2. Merge com a versão local (nova seção AUTOSCALING já está incluída)
3. Upload da versão merged, versão 5.0.2 (foi 5.0.1)
4. Marque como "Master Registry — Versão Oficial"

### Passo 3: Criar índice de documentos

Crie um arquivo `INDEX-autoscaling.md` no SP:

```markdown
# Índice — Manta Maestro Autoscaling v1.0

## Documentos

1. **CLAUDE.md** (v5.0.2 em diante)
   - Seção: AUTOSCALING — Política de Escalagem Automática
   - Status: ✅ Operacional
   - Data: 2026-08-08

2. **maestro-autoscaling-policy.html**
   - 4 Volume Bands, matriz de seleção de modelo
   - Algoritmo de decisão automática
   - Status: ✅ Reference
   - Audiência: Arquitetos IA, Maestro maintainers

3. **manta-maestro-orquestracao-v5.html**
   - 4 padrões de orquestração (pipeline, parallel, fan-out, lotes)
   - Limites técnicos e SLA
   - Status: ✅ Reference
   - Audiência: Desenvolvedores, DevOps

4. **quando-usar-claude-ai-cowork-code.html**
   - Matriz de decisão Claude AI vs Cowork vs Claude Code
   - Stack recomendado para Manta (3 modos)
   - Status: ✅ Reference
   - Audiência: PMs, stakeholders

## Implementação

Fase 1 — Setup infraestrutura (Semana 1)
Fase 2 — Routing e orquestração (Semana 2)
Fase 3 — Padrões de orquestração (Semana 2–3)
Fase 4 — Validação e deploy (Semana 3–4)

Ver maestro-autoscaling-policy.html → Seção 7: Implementação
```

### Passo 4: Notificar equipe

- Mensagem no Slack (canal #manta-maestro):
  ```
  🚀 Manta Maestro v5.0.2 — Política de Escalagem Automática implementada!
  
  ✅ Maestro agora escolhe automaticamente múltiplos agentes baseado em volume
  ✅ Sonnet + Haiku como padrão (não Opus)
  ✅ 3 documentos novos no SharePoint
  ✅ 4 fases de implementação prontas
  
  Docs: /04_IA/Manta-Maestro/00-arquitetura/
  ```

---

## 🔐 Autenticação SharePoint (para próximas vezes)

Quando quiser sincronizar do Claude Code diretamente:

```bash
# Em sessão interativa:
claude mcp add --transport oauth SharePoint_Manta https://your-org.sharepoint.com

# Ou em Claude Code com autenticação Cowork:
/mcp
# → selecionar SharePoint_Manta
# → completar OAuth flow
```

---

## 📊 Status de Sincronização

| Artefato | Status | Localização | Data |
|----------|--------|------------|------|
| maestro-autoscaling-policy.html | ⏳ Aguardando sync manual | SP / 00-arquitetura/ | 2026-08-08 |
| manta-maestro-orquestracao-v5.html | ⏳ Aguardando sync manual | SP / 00-arquitetura/ | 2026-08-08 |
| quando-usar-claude-ai-cowork-code.html | ⏳ Aguardando sync manual | SP / 00-arquitetura/ | 2026-08-08 |
| CLAUDE.md (v5.0.2) | ⏳ Aguardando merge com SP | GitHub + SP | 2026-08-08 |
| GitHub PR | ✅ Criada (draft) | `/MN1970/Codex-exemplo/pull/new/...` | 2026-08-08 |

---

## 📝 Próximos Passos

1. **Você (ou admin):** Execute checklist acima
2. **Maestro:** Monitor `rag_learning_log` semanal para ajustes
3. **Semana 2:** Iniciar Phase 2 de implementação (routing + orquestração)
4. **Semana 3:** Validar wall-clock real vs SLA estimado

---

**Documento gerado:** 2026-08-08  
**Criado por:** Manta Maestro v5.0.1  
**Próxima atualização:** Após sync com SP
