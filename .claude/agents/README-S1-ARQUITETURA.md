# Índice: Manta 03-S1 — Arquitetura Expandida (8 Módulos)

**Status**: v1.0 Completa | **Data**: 2026-08-11 | **Product Owner**: Mauricio Neves

---

## DOCUMENTAÇÃO COMPLETA

### 🏗️ ARQUITETURA MESTRE

**[manta-03-s1-arquitetura-integracao.md](./manta-03-s1-arquitetura-integracao.md)**
- Visão geral dos 8 módulos e suas responsabilidades
- Diagrama de arquitetura (Mermaid)
- Routing automático (Intake Q2)
- 3 fluxos de dados principais (Geotecnia, Hidrologia, Otimização)
- Integração com agentes horizontais (Manta 05, 07, 02, 06, 15)
- Roadmap Q3 2026 - Q2 2027
- Métricas de sucesso

---

### 📋 8 MÓDULOS ESPECIALIZADOS

#### S1.1 — Geotecnia
**[manta-03-s1-geotec.md](./manta-03-s1-geotec.md)**
- CBR, compactação, estabilização com cal/cimento
- Análise de solos problemáticos
- Recomendações de espessura de camadas
- Integração com S1.3 (Materiais) e S1.6 (BIM-Cost)

#### S1.2 — Hidrologia
**[manta-03-s1-hidro.md](./manta-03-s1-hidro.md)**
- Drenagem, bueiros, dimensionamento
- Risco de chuva e impacto em cronograma
- HEC-RAS, modelos de vazão
- Integração com S1.5 (Métodos) e S1.8 (Contratual-Geo)

#### S1.3 — Materiais
**[manta-03-s1-materiais.md](./manta-03-s1-materiais.md)**
- Locação de jazidas (solo, areia, brita)
- Distância Média de Transporte (DMT)
- Ensaios de transportabilidade
- Bota-fora e adequação ambiental

#### S1.4 — Inovação
**[Manta-03-S1-INOVACAO.md](./Manta-03-S1-INOVACAO.md)**
- Warm Mix Asphalt (WMA), RAP, geopolímero
- Pavimento verde, IoT, asfalto inteligente
- Viabilidade técnico-econômica
- Integração com S1.6 (BIM-Cost) e Manta 06 (Modelagem)

#### S1.5 — Métodos
**[manta-03-s1-metodos.md](./manta-03-s1-metodos.md)**
- Sequenciamento de pistas, produtividade
- Equipamentos e frentes de trabalho
- Sazonalidade climática
- Cronograma realista com contingência

#### S1.6 — BIM-Cost
**[manta-03-s1-bim-cost.md](./manta-03-s1-bim-cost.md)**
- Integração Civil 3D ↔ SICRO
- Volumes automáticos (terraplenagem, pavimento)
- Sensibilidade de variantes 3D
- Scripts de simulação de custo

#### S1.7 — Benchmarking
**[manta-03-s1-benchmarking.md](./manta-03-s1-benchmarking.md)**
- Busca de projetos similares (base 50+ rodovias)
- Regressão de custo unitário ($/km, $/m³)
- Validação de estimativas SICRO
- Margem de contingência técnica

#### S1.8 — Contratual-Geo
**[manta-03-s1-contratual-geo.md](./manta-03-s1-contratual-geo.md)**
- Matriz de alocação de risco (Contratante/Contratada/Compartilhado)
- Cláusulas especiais (descoberta, chuva, compactação)
- Redução de disputas contratuais (-40%)
- Co-agente com Manta 02 (Contratual)

---

## FLUXOS DE DADOS PRINCIPAIS

### Fluxo A: Geotecnia → Orçamento
```
S1.1 (CBR, estabilização)
  ↓
S1.3 (localiza jazida)
  ↓
S1.6 (atualiza espessuras)
  ↓
S1.5 (ajusta produtividade)
  ↓
Manta 05 (SICRO final)
```

### Fluxo B: Hidrologia → Cronograma
```
S1.2 (pluviometria, bueiros)
  ↓
S1.5 (dias perdidos por chuva)
  ↓
S1.8 (alocação risco climático)
  ↓
Manta 07 (cronograma com margem)
```

### Fluxo C: Otimização
```
S1.7 (benchmark + similares)
  ↓
S1.4 (inovação aplicável)
  ↓
S1.6 (sensibilidade de variantes)
  ↓
Manta 06 (VPL/TIR cenários)
```

---

## ROUTING AUTOMÁTICO (Intake Q2)

Quando usuário menciona **"rodovia"** + qualquer palavra-chave:

| Palavra-chave | Módulo Ativado |
|---------------|----------------|
| CBR, solo, estabilização | S1.1 Geotecnia |
| drenagem, bueiro, chuva, HEC-RAS | S1.2 Hidrologia |
| jazida, bota-fora, DMT | S1.3 Materiais |
| WMA, RAP, pavimento verde, IoT | S1.4 Inovação |
| equipamentos, cronograma, produtividade | S1.5 Métodos |
| Civil 3D, volumes, sensibilidade | S1.6 BIM-Cost |
| benchmark, similar, custo unitário | S1.7 Benchmarking |
| cláusula, risco geológico, garantia | S1.8 Contratual-Geo |
| **múltiplas** palavras-chave | **múltiplos** módulos + consolidação |

---

## INTEGRAÇÃO COM MANTA HORIZONTAL

| Agente | Input | Output |
|--------|-------|--------|
| **Manta 05** (Orçamento) | Volumes, materiais, alternativas inovação | SICRO otimizado |
| **Manta 07** (Cronograma) | Produtividade, sazonalidade, chuva | Cronograma realista |
| **Manta 02** (Contratual) | Riscos geológicos, cláusulas recomendadas | Contrato com alocação de risco |
| **Manta 06** (Modelagem) | Cenários jazida, tecnologia, variantes | VPL, TIR, sensibilidade |
| **Manta 15** (Advisory) | Benchmarking, inovação, viabilidade | Recomendação estratégica |

---

## RAG CONSOLIDADA (Supabase)

Todas as 8 coleções integradas com busca cruzada:

| Prefixo | Coleção | Fontes |
|---------|---------|--------|
| **geo:** | Geotecnia | NBR 7181, DNER-ME, estudos DNIT |
| **hid:** | Hidrologia | HEC-RAS, ABNT, INMET, ANA |
| **mat:** | Materiais | Manuais DNIT/DER, tabelas jazidas |
| **ino:** | Inovação | WMA técnicos, NAPA, RAP normas |
| **met:** | Métodos | MTG's, manuais planejamento |
| **bim:** | BIM-Cost | Civil 3D, templates, scripts SICRO |
| **ben:** | Benchmarking | Base Manta (50+ projetos), similares |
| **ctg:** | Contratual-Geo | Cláusulas, matriz risco, jurisprudência |

**Exemplo busca cruzada**: "CBR baixo + WMA" → `geo: + ino: + mat:`

---

## ROADMAP INTEGRADO

| Período | Atividade | Status |
|---------|-----------|--------|
| **Q3 2026** (agora) | Deploy 8 módulos, teste routing, validação RAG | 🚀 Em andamento |
| **Q4 2026** | Integração MCP, pipelines automáticos, testes cenários simples | 📋 Planejado |
| **Q1 2027** | Testes complexos (5+ módulos), otimizações performance | 📋 Planejado |
| **Q2 2027** | Lançamento v1.0, publicação case studies | 📋 Planejado |

---

## MÉTRICAS DE SUCESSO

| Métrica | Meta | Validação |
|---------|------|-----------|
| Acurácia de custo | ±10% vs realizado | Baseline 2027 |
| Acurácia de cronograma | ±5% vs realizado | Baseline 2027 |
| Economia média | 25-35% por projeto | Q4 2026 |
| Redução de disputas | -40% vs histórico | Q4 2026 |
| Taxa de adoção | 80%+ (3+ módulos) | Q2 2027 |
| Tempo de análise | 2-3 dias vs 5-7 dias manual | Q4 2026 |

---

## COMO USAR ESTE ÍNDICE

1. **Primeira vez?** Leia [manta-03-s1-arquitetura-integracao.md](./manta-03-s1-arquitetura-integracao.md) para visão 360°.

2. **Módulo específico?** Navegue pela tabela acima e clique no `.md` respectivo.

3. **Fluxo de dados?** Consulte seção "FLUXOS DE DADOS PRINCIPAIS" acima.

4. **Integração com Manta?** Veja tabela "INTEGRAÇÃO COM MANTA HORIZONTAL".

5. **Implementação?** Comece por:
   - S1.1 (Geotecnia) — base técnica
   - S1.6 (BIM-Cost) — integração com SICRO
   - S1.7 (Benchmarking) — validação de custo
   - S1.8 (Contratual-Geo) — alocação risco

---

## CONTATOS

| Papel | Email |
|------|-------|
| **Product Owner** | mneves@mantaassociados.com |
| **Maestro Router** | manta-maestro@mantaassociados.com |
| **Tim Técnica S1** | #manta-s1-infra (Slack) |
| **Escalação Custos** | tim.custo@mantaassociados.com |
| **Escalação Jurídica** | gerente.juridico@mantaassociados.com |

---

**Versão**: 1.0 | **Última atualização**: 2026-08-11  
**Próxima revisão**: Q4 2026 (após v1 alpha testing)  
**Repositório**: `Codex-exemplo/.claude/agents/`
