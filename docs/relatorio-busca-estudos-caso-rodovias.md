# Busca de Estudos de Caso — Dispositivos Viários em Rodovias Brasileiras
## Status: Análise do repositório Codex-exemplo

**Data da busca:** 29/07/2026  
**Repositório analisado:** `/home/user/Codex-exemplo` (Manta Associados)  
**Conclusão:** Repositório contém arquitetura de agentes IA, não estudos de caso econômicos.

---

## 1. O que foi encontrado

### 1.1 Documento Técnico de Referência (disponível)

**Arquivo:** `/home/user/Codex-exemplo/docs/dispositivos-viarios-interconexoes-seguranca.html`  
**Versão:** v1.0 (29/07/2026)  
**Tipo:** Referência técnica interna Manta Associados

**Conteúdo:**
- Guia ilustrado (SVG/CAD) de 9 tipos de interconexões rodoviárias (nível e desnível)
- Classificação de 4 dispositivos de segurança viária:
  - Defensa metálica (semiflexível)
  - Barreira rígida (tipo New Jersey)
  - Atenuador de impacto
  - Dispositivos auxiliares (tachas, balizadores, anti-ofuscante)
- Normas aplicáveis: DNIT IPR-718, DNIT manuais, CONTRAN Vol. I-VII, Manual ANTT
- Critérios de enquadramento (VMD, classe da via, velocidade projeto, disponibilidade de área)
- **NÃO contém:** dados de custos, estudos de caso, análise econômica, manutenção pós-obra

**Normas base referenciadas:**
| Norma | Órgão | Cobertura |
|-------|-------|-----------|
| IPR-718, 2ª ed. (2005) | DNIT | Projeto de Interseções — critérios de seleção |
| Manual Brasileiro de Sinalização | CONTRAN | Vol. I a VII — sinalização e dispositivos |
| Manual de Segurança nas Rodovias | DNIT | Defensas, barreiras, atenuadores |
| Manual ANTT Rodovias Federais Concedidas | ANTT | Fiscalização, manutenção, recuperação |
| PER (Programa Exploração Rodovia) | Ministério Transportes | Modelo de operação e manutenção |
| IPR-740 | DNIT | Travessias urbanas |

---

## 2. Tipos de dispositivos documentados

### Dispositivos de Contenção e Segurança

**6.1 Defensa Metálica (Guard-Rail)**
- Aplicação: Todo o comprimento da rodovia, áreas com espaço livre insuficiente
- Norma: DNIT / Manual ANTT
- Espaçamento entre postes: 2,00-4,00 m
- Altura nominal: ~0,70 m
- Características: Semiflexível, reorienta veículos
- **Custo:** NÃO documentado

**6.2 Barreira Rígida (New Jersey / Single Slope)**
- Aplicação: Canteiro central estreito, viadutos, pistas adjacentes
- Norma: DNIT IPR-718 / Manual ANTT
- Altura: 0,81-1,07 m
- Base: ~0,60 m
- Características: Estrutura de concreto, indeformável, disposta longitudinalmente
- **Custo:** NÃO documentado

**7.1 Atenuador de Impacto**
- Aplicação: Nariz de bifurcações, pilares de viaduto próximos à pista
- Predominante em desnível
- Padrão real: módulos chevron preto/amarelo
- Comprimento: conforme velocidade de projeto
- Observação: "Requer manutenção e substituição pós-impacto"
- **Custo:** NÃO documentado
- **Manutenção:** Mencionada, mas sem detalhes

---

## 3. Referências a resultados operacionais

O documento menciona (no item 2.2 — Rótula):  
> "Estudo de caso citado nas referências aponta rótula como um dos tipos com maior índice de acidentes quando mal dimensionada — atenção a raios e sinalização de aproximação."

**Observação:** Nenhum estudo de caso específico é citado ou referenciado no documento.

---

## 4. O que NÃO está no repositório

❌ **Estudos de caso de rodovias federais/estaduais/concessões brasileiras**  
❌ **Análise de custos de implantação de defensas/barreiras/atenuadores**  
❌ **Dados de manutenção pós-obra (periodicidade, custos, volume de serviços)**  
❌ **Resultado operacional (segurança: redução de acidentes, severidade)**  
❌ **Comparação econômica entre tipos de dispositivos**  
❌ **Benchmarks de desempenho (custo por km, custo por dispositivo)**  
❌ **Casos específicos de BR-116, BR-101, concessões privadas**  

---

## 5. Onde tais dados podem estar

De acordo com CLAUDE.md, este é um repositório de exemplo (`Codex-exemplo`) da arquitetura de agentes. Estudos de caso econômicos/operacionais devem estar em:

1. **SharePoint da Manta** (mencionado em CLAUDE.md):
   - Pasta: `03_Projetos/Rodovias/*`
   - Documentação: `01-agentes-fundamentais/agente-infraestrutura-S1/`
   - Referências técnicas em `refs/`

2. **Repositório operacional "manta-hub"** (versionado em `viniciusmagnos/manta-hub`):
   - Agente vertical S1 (agente-infraestrutura — Rodovias)
   - RAG collection `rod:` em Supabase
   - Fontes iniciais: DNIT, SICRO, NBR-DNIT

3. **Banco de dados Supabase**:
   - Coleção: `rod:` (rodovias)
   - Chunks com análises técnicas e econômicas

4. **Fontes externas** (não incluídas neste repo):
   - ANTT — Processos licitatórios e relatórios de concessões
   - DNIT — Manuais e estudos de caso operacionais
   - Concessionárias privadas — Relatórios de sustentabilidade e operação
   - SICRO — Banco de dados de custos

---

## 6. Recomendações para próximas etapas

### Para buscar estudos de caso com análise econômica:

1. **Acessar SharePoint da Manta** → pasta `03_Projetos/Rodovias/`
2. **Consultar agente-infraestrutura (S1)** via Maestro (Manta 00):
   - Prompt recomendado: "Preciso de estudos de caso de defensas e barreiras em rodovias federais/estaduais com análise de custos e manutenção"
3. **Supabase RAG** → buscar em coleção `rod:` por:
   - Keywords: "custo defensa", "barreira rígida econômico", "atenuador manutenção"
   - Prefixo: `rod:custos`, `rod:cases`, `rod:manutencao`
4. **Consultar fontes externas**:
   - SICRO (tabelas de custos DNIT)
   - Editais e contratos de concessão no site ANTT
   - Relatórios de operadores (CCR, OHL, Odebrecht)

---

## 7. Documentos técnicos disponíveis neste repo

| Arquivo | Tipo | Conteúdo | Uso |
|---------|------|----------|-----|
| `dispositivos-viarios-interconexoes-seguranca.html` | Referência | Normas, tipos, critérios | Apoio a decisão de enquadramento geométrico |
| `CLAUDE.md` | Registro | Mapa de 20 agentes (horizontais + verticais) | Routing, identificar agente-infraestrutura S1 |
| `ARQUITETURA-AGENTES-IA.md` | Guia | 5 camadas, hub-and-spoke, model tiering | Entender como consultar agentes |
| Agentes `.claude/agents/*.md` | Specs | 5 novos agentes (S6-S10) | Saneamento, Energia, Portos, Aeroportos, Barragens |

---

## 8. Conclusão

O repositório `Codex-exemplo` é um **registro de exemplo da arquitetura de agentes IA** da Manta Associados, não um repositório de dados econômicos ou estudos de caso. 

O **documento técnico disponível** (`dispositivos-viarios-interconexoes-seguranca.html`) fornece:
- ✅ Classificação normativa completa de dispositivos viários
- ✅ Critérios de enquadramento (nível/desnível)
- ✅ Referências a normas DNIT, ANTT, CONTRAN
- ❌ Nenhum dado de custos, manutenção ou resultados operacionais

**Para obter estudos de caso com análise econômica**, consulte:
1. **SharePoint Manta** — projetos reais com memoriais técnicos
2. **Agente-infraestrutura (S1)** via Maestro — com acesso à coleção RAG `rod:`
3. **Fontes externas** — SICRO, ANTT, editais de concessão

---

**ID Documento:** MNT-BUSCA-CASOS-RODOVIAS-20260729  
**Status:** Consultoria Preparatória  
**Próximo passo:** Routing para agente-infraestrutura S1 via Maestro
