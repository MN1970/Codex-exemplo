# KB Evoluído — Manta Maestro 2.0

**Status**: 🔨 Em construção (4 agentes paralelos trabalhando)

Sistema de Knowledge Base evolutivo com **aprendizado contínuo**, machine learning e feedback automático para o Manta Maestro.

## 🎯 Objetivo

Transformar o KB do Manta Maestro de **estático** (v4.2) para **evolutivo** — atualizando constantes técnicas, templates e padrões automaticamente diariamente a partir de:
- Projetos finalizados
- Validação de agentes especializados
- Machine learning (clustering, pattern matching, anomaly detection)
- Feedback humano (aprovação/rejeição de mudanças)

## 📦 O que está sendo construído

Em paralelo, 4 agentes estão criando:

1. **ARCHITECTURE.md** — Arquitetura completa do sistema (3 camadas: Ingestion → Processing → Knowledge)
2. **schemas.sql** — Estrutura Supabase (versionamento, auditoria, feedback, ML)
3. **ml-pipeline.md** — Algoritmos e modelos de aprendizado
4. **orchestration.md** — DAG de automação (Airflow/n8n, triggers, alerts)

## 📊 Estrutura do Repositório

```
kb-evoluido/
├── README.md                    # este arquivo
├── PRIORITY_MAP.md             # segmentos prioritários (S8, S9, S6)
│
├── architecture/               # documentação
│   └── ARCHITECTURE.md         # (Agent 1 gerando)
│
├── supabase/                   # schemas e migrações
│   ├── schema.sql             # (Agent 2 gerando)
│   ├── migrations/
│   └── seed-data.sql
│
├── ml-pipeline/                # modelos e processamento
│   ├── pipeline.md            # (Agent 3 gerando)
│   ├── feature-engineering/
│   ├── models/
│   └── validation/
│
├── orchestration/              # automação e workflows
│   ├── orchestration.md       # (Agent 4 gerando)
│   ├── airflow-dag.py        # DAG principal
│   ├── triggers.py            # triggers de automação
│   └── alerts.py
│
└── scripts/
    ├── ingest.py             # coleta de dados
    ├── validate.py           # validação de insights
    └── update-kb.py          # atualização de constantes
```

## 🚀 Fluxo de Evolução

```
Projeto Finalizado
       ↓
Extração de Features (diário)
       ↓
Clustering & Pattern Matching (ML)
       ↓
Validação por Agentes (semanal)
       ↓
Consenso (2 de 3 agentes)
       ↓
Atualização KB + Versionamento
       ↓
Publicação de Changelog
       ↓
Novo projeto já usa constantes atualizadas ✅
```

## 📋 Segmentos Prioritários

### Tier 1 (Máxima Prioridade)
- **Saneamento (S8)** — AySA, ETA/ETE, constantes K1/K2
- **Energia (S9)** — ANEEL, transmissão, subestações
- **Portos (S6)** — ANTAQ, tarifas dinâmicas, PIANC

### Tier 2
- **Aeroportos (S7)**, **Barragens (S10)**

Ver [PRIORITY_MAP.md](./PRIORITY_MAP.md) para detalhes.

## 🔄 Próximas Etapas

- [ ] Agent 1 completa ARCHITECTURE.md
- [ ] Agent 2 completa schemas.sql (deploy em Supabase)
- [ ] Agent 3 completa pipeline.md (treino de modelos)
- [ ] Agent 4 completa orchestration.md (deploy Airflow)
- [ ] Integração com projeto existente (CLAUDE.md, agentes S6-S10)
- [ ] Teste end-to-end com 1 projeto piloto
- [ ] Ativar evolução automática diária

## 🔐 Considerações de Segurança

- ✅ Versionamento completo (rollback sempre possível)
- ✅ Auditoria de todas mudanças (quem/quando/por quê)
- ✅ Gate humano para mudanças críticas (normas, leis)
- ✅ Threshold de confiança para auto-update (> 85%)
- ✅ Políticas RLS em Supabase por role (agente, humano, admin)

## 📞 Contato & Escalation

- **Contradições entre agentes** → slack alert, escalação para MN
- **Model drift detectado** → retraining automático
- **Falha crítica** → rollback automático + análise

---

**Versão**: v1.0-alpha | **Data**: 2026-07-30 | **Branch**: `claude/kb-evoluido-manta-maestro-167734`
