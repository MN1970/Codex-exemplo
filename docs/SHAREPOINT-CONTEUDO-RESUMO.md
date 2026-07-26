# Conteúdo SharePoint por Segmento — Resumo Executivo

**Versão**: Maestro v1.0 (2026-07-24)  
**Status**: ✅ Estrutura esperada definida e validada  
**Próximo passo**: Sincronizar SharePoint real e comparar

---

## 📊 VISÃO GERAL

Maestro (Manta 00) mapeou a **estrutura esperada completa** de conteúdo para os **5 segmentos NOVOS** (S6-S10):

| Segmento | Nome | RAG Prefix | Subpastas | Arquivos Ex. | Reguladores |
|----------|------|-----------|-----------|--------------|-------------|
| **S6** | Portos | `por:` | 18 | 52 | ANTAQ, PIANC, BNDES |
| **S7** | Aeroportos | `aer:` | 18 | 50 | ANAC, ICAO, FAA, DECEA |
| **S8** | Saneamento 🔴 AySA | `san:` | 18 | 52 | ANA, SNIS, AySA, ERAS |
| **S9** | Energia 🔴 ANEEL | `ene:` | 18 | 51 | ANEEL, ONS, EPE, State Grid |
| **S10** | Barragens | `bar:` | 18 | 50 | ICOLD, CBDB, Lei 12.334, PNSB |
| **TOTAL** | — | — | **90** | **255 exemplos** | — |

---

## 🎯 ESTRUTURA HIERÁRQUICA

### Nível 1: Pastas Principais (5 por segmento)
```
03_Projetos/{Segmento}/
├── 01_Projetos_Executados
├── 02_Estudos_Tecnicos
├── 03_Normas_Referencias
├── 04_Templates_Documentos
└── 05_Licitacoes_Editais
```

### Nível 2: Subpastas por Tipologia (18 por segmento)

**S6 Portos** (exemplo):
- Terminais_Portuarios
- Obras_Costeiras
- Dragagem
- Sistemas_Carga_Descarga
- Hidrodinamica
- Geotecnia_Portuaria
- Estruturas
- Ambiental

**S7 Aeroportos** (exemplo):
- Pistas_Taxiways
- Terminal_Passageiros
- Terminal_Cargas
- Sistemas_Balizamento
- Infraestrutura_Servicos
- Pavimentacao_Aeroportuaria
- Drenagem_Aviacao
- Seguranca_Operacional

**S8 Saneamento** (exemplo):
- ETA
- ETE
- Redes_Distribuicao
- Drenagem_Urbana
- Coleta_Esgoto
- Tratamento_Agua
- Tratamento_Esgoto
- Economia

**S9 Energia** (exemplo):
- Linhas_Transmissao
- Subestacoes
- Redes_Distribuicao
- Usinas
- Fluxo_Potencia
- Curto_Circuito
- Economia_Energia
- Risco_Confiabilidade

**S10 Barragens** (exemplo):
- Barragem_Principal
- Vertedouro
- Sistema_Rejeitos
- Sistemas_Vazao_Transvase
- Hidrologia
- Geotecnia_Fundacoes
- Hidraulica_Estrutural
- Estrutural

### Nível 3: Arquivos de Exemplo

Cada subpasta contém 2-3 arquivos exemplares com nomenclatura padrão:

```
[CODIGO]_[NUMERO]_[DESCRICAO]_[VERSAO].[EXT]

Exemplos:
TP_01_Terminal_Conteineres_Santos_2024_Relatorio_Executivo.pdf
DG_01_Dragagem_Aprofundamento_Calado_13m_Santarém.pdf
HD_01_Modelo_Hidrodinamico_Porto_Fortaleza_MIKE_21.pdf
```

---

## 📁 ARQUIVOS DE REFERÊNCIA

### Arquivo Maestro: `sharepoint_structure_s6_s10.yaml`
- ✅ Formato canônico YAML
- ✅ Hierarquia completa (3 níveis)
- ✅ Descrições em português
- ✅ Exemplos de arquivos para cada subpasta
- **Uso**: Referência técnica, automação de criação de pastas

### Arquivo Integração: `sharepoint_structure_s6_s10.json`
- ✅ Formato JSON estruturado
- ✅ Mesmo conteúdo que YAML
- **Uso**: Importar em sistemas, APIs, scripts Python/Node

---

## 🔄 PRÓXIMAS ETAPAS

### Fase 1: Validação da Estrutura (esta semana)
- [ ] Sincronizar SharePoint real (rclone/Graph API/OneDrive)
- [ ] Comparar estrutura real vs esperada
- [ ] Identificar arquivos que JÁ existem
- [ ] Listar gaps (o que está faltando)
- [ ] Gerar relatório de divergências

### Fase 2: Preenchimento de Gaps (próxima semana)
- [ ] Criar pastas faltantes em SP (baseado em YAML)
- [ ] Fazer upload de normas primárias (TIER 1)
- [ ] Ingestar projetos executados Manta (TIER 2)
- [ ] Completar templates padrão (TIER 3)
- [ ] Catalogar editais/licitações (TIER 4)

### Fase 3: Ativação RAG (Fase 1 do plano)
- [ ] Rodar `ingest_rag_batch.py` para cada segmento
- [ ] Validar chunks gerados (acurácia, relevância)
- [ ] Testar routing Maestro com prompts de teste
- [ ] Deploy v4.2 com RAG operacional

---

## 🎬 COMANDOS ÚTEIS

### Criar pastas localmente (antes de upload)
```bash
# Gerar pastas baseado em YAML
python3 scripts/create_sharepoint_folders.py \
  --structure docs/sharepoint_structure_s6_s10.yaml \
  --target /path/to/03_Projetos

# Ou via rclone (direto no SP)
rclone mkdir sharepoint:'/{site}/{library}/03_Projetos/Portos/01_Projetos_Executados'
rclone mkdir sharepoint:'/{site}/{library}/03_Projetos/Portos/02_Estudos_Tecnicos'
# ... (90 pastas × 18 subpastas)
```

### Validar estrutura criada
```bash
python3 scripts/audit_sharepoint_projects.py

# Gera: AUDIT-SHAREPOINT.csv com comparação esperado vs real
```

### Ingestar conteúdo para RAG (após sincronizar)
```bash
python3 scripts/ingest_rag_batch.py \
  --segment S6 \
  --tier T1 \
  --source /home/user/Codex-exemplo/sharepoint/03_Projetos/Portos

# Processa PDFs → chunks → Supabase rag_chunks
```

---

## 📋 RESUMO

**Estrutura esperada**: ✅ Definida (90 subpastas, 255 arquivos exemplo)  
**Arquivo master**: ✅ Maestro YAML + JSON  
**Status SharePoint real**: ❌ Vazio (0 arquivos, aguardando sincronização)  
**Roadmap**: Fase 1 (90d) → Consolidação & Automação

**Quando sincronizar o SharePoint real, a auditoria automática vai:**
1. Escanear 03_Projetos completo
2. Comparar com estrutura esperada
3. Identificar gaps por segmento
4. Gerar matriz de prioridades (Tier 1-4)
5. Sugerir ordem de ingestion para RAG

---

**Próximo passo**: Sincronize o SharePoint e rode `python3 scripts/audit_sharepoint_projects.py` para gerar relatório consolidado! 🚀

**Arquivos de referência**:
- 📄 `docs/sharepoint_structure_s6_s10.yaml` — Maestro estrutura canônica
- 📄 `docs/sharepoint_structure_s6_s10.json` — Formato integração
- 📄 `docs/SYNC-SHAREPOINT-GUIDE.md` — Como sincronizar (4 opções)
- 📄 `scripts/audit_sharepoint_projects.py` — Script de auditoria
