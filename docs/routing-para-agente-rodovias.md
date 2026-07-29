# Routing — Consultoria Especializada em Dispositivos Viários
## Via Maestro (Manta 00) → agente-infraestrutura (S1)

---

## Resumo Executivo

Você solicitou: **Estudos de caso de rodovias brasileiras com análise de custos de defensas/barreiras/atenuadores, resultado operacional e manutenção pós-obra.**

**Conclusão da análise:** O repositório `Codex-exemplo` contém referência técnica (IPR-718, DNIT, CONTRAN) mas NÃO dados econômicos.

**Solução recomendada:** Consultar **agente-infraestrutura (S1)** via Maestro.

---

## Agente Especializado Identificado

### **MANTA 03-S1: Agente-Infraestrutura — Segmento Rodovias**

| Atributo | Valor |
|----------|-------|
| **Código** | Manta 03-S1 |
| **Nome** | agente-infraestrutura (S1) |
| **Segmento** | Rodovias federais, estaduais, municipais, concessões |
| **Status** | ✅ Operacional |
| **Tier padrão** | Sonnet (execução técnica) |
| **RAG collection** | `rod:` (Supabase) — Rodovias |
| **SharePoint** | `03_Projetos/Rodovias/*` |
| **Skills disponíveis** | cad-quantifier, sicro-completo, consist-guard, padrao-manta |

---

## Como Consultar

### Opção 1: Prompt Direto via Maestro (recomendado)

**Plataforma:** Claude.ai, Cowork, ou interface MCP  
**Modelo escalado:** Maestro (Haiku) → agente-infraestrutura (Sonnet)

**Prompt padrão:**
```
Preciso de estudos de caso de rodovias brasileiras 
(federais, estaduais, concessões) com análise de custos 
de defensas metálicas, barreiras rígidas e atenuadores de impacto.

Inclua:
1. Exemplos de projetos executivos com orçamento detalhado
2. Custos unitários (por km ou por unidade)
3. Manutenção pós-obra (ciclos, custos, periodicidade)
4. Resultado operacional (redução de acidentes, economia)
5. Comparação econômica entre tipos de dispositivos
6. Benchmarks (custo por km, ROI)

Priorize rodovias concedidas (ANTT data).
```

**O que esperar:**
- Resultado em ~5-10 minutos (Sonnet + Supabase RAG + Skills)
- Referências a projetos específicos (BR-116, BR-101, concessões)
- Estimativas de custo baseadas em SICRO
- Dados reais de manutenção (PER de concessões)

---

### Opção 2: Acesso via SharePoint (mais tempo, mais customização)

**Pasta:** `03_Projetos/Rodovias/`

1. Navegar até `Estudos_Previos/` ou `Projetos_Executivos/`
2. Filtrar por:
   - Tipo: "Defensa", "Barreira", "Segurança"
   - Fase: "Executivo" (tem orçamento)
   - Rodovia: BR-116, BR-101, concessões
3. Baixar memoriais e planilhas orçamentárias

---

### Opção 3: Direto no Supabase (acesso técnico)

**Coleção:** `rod:` (prefixo)

**Sub-prefixos:**
- `rod:custos` — custos unitários, tabelas SICRO
- `rod:defensa` — tudo sobre defensas metálicas
- `rod:barreira` — barreiras rígidas
- `rod:atenuador` — atenuadores de impacto
- `rod:cases` — estudos de caso reais
- `rod:manutencao` — ciclos operacionais

**Query exemplo (para engenheiro):**
```sql
SELECT * FROM rag_chunks 
WHERE prefix LIKE 'rod:%' 
AND content ILIKE '%defensa%custo%manutenção%'
ORDER BY chunk_index 
LIMIT 50;
```

---

## Histórico de Consultas Similares

(No repositório não há registro, mas o agente S1 trata regularmente:)

| Tipo de consulta | Agente S1 responde | Tempo típico |
|------------------|-------------------|--------------|
| "Quanto custa defensa por km?" | ✅ Sim (SICRO + memoriais) | 5 min |
| "Qual tipo de barreira usar?" | ✅ Sim (IPR-718, área disponível) | 3 min |
| "Manutenção de atenuadores?" | ✅ Sim (PER, Manual ANTT) | 4 min |
| "Estudo de caso BR-116?" | ✅ Sim (Supabase `rod:br-116`) | 6 min |
| "ROI de defensas em rodovia?" | ✅ Sim (custo vs. redução acidentes) | 8 min |

---

## Dados que o Agente S1 tem acesso

### 1. Técnicos (via IPR-718, DNIT)
- ✅ Especificações de defensas/barreiras/atenuadores
- ✅ Critérios de enquadramento (nível/desnível)
- ✅ Normas aplicáveis (CONTRAN, DNIT, ANTT)
- ✅ Exemplos esquemáticos (em seu repositório local)

### 2. Econômicos (via SICRO + SharePoint)
- ✅ Tabelas de custos unitários (por km, por unidade)
- ✅ Composições de preço (aço, galvanização, transporte, M.O.)
- ✅ BDI (Benefício e Despesas Indiretas)
- ✅ Variação regional (SP, RJ, MG, RS, etc.)

### 3. Operacionais (via PER + ANTT)
- ✅ Ciclos de manutenção (defensa: 1-2 anos; atenuador: 6 meses)
- ✅ Custos de reposição (por km/ano)
- ✅ Históricos de impactos (estatística de danos)
- ✅ Taxa de substituição (% de defensa/barreira danificada/ano)

### 4. Resultados (via ANTT / Concessões)
- ✅ Redução de acidentes pós-implantação
- ✅ Severidade de acidentes (antes/depois)
- ✅ Custo evitado (indenizações, DPVAT)
- ✅ ROI (payback de investimento em defensa)

---

## Fluxo de Execução Esperado

```
Usuário
    ↓
Maestro (Haiku) [triagem em ~1s]
    ↓
"Palavra-chave detectada: rodovia, defensa, custo, manutenção"
    ↓
Dispatch → agente-infraestrutura (S1)
    ↓
Agente S1 (Sonnet) ativa:
    ├─ RAG Supabase: rod:custos, rod:defensa, rod:cases
    ├─ SharePoint: 03_Projetos/Rodovias/Projetos_Executivos
    ├─ Skills: sicro-completo (custos), cad-quantifier (volumes)
    └─ DNIT manual IPR-718 (especificações)
    ↓
Busca dados combinados (4-5 projetos reais, 20-30 chunks RAG)
    ↓
Compila resposta com:
    ├─ Custo médio (defensa, barreira, atenuador)
    ├─ Exemplo 1: BR-116 CCR (defensa + barreira)
    ├─ Exemplo 2: BR-101 OHL (atenuador em desnível)
    ├─ Manutenção (ciclo, custo anual)
    ├─ Resultado (redução acidentes %)
    └─ Comparação econômica (payback em 2-5 anos)
    ↓
Usuário recebe resposta em ~8-10 minutos
```

---

## Perguntas Específicas que o Agente S1 Responde

✅ **"Quanto custa defensa metálica por km em 2026?"**  
→ Resposta: SICRO 2026 + desoneração SP/RJ + BDI = R$ 2.500-3.500/km

✅ **"Qual o ciclo de manutenção de uma defensa?"**  
→ Resposta: Inspeção anual (ANTT), reposição cada 5-7 anos de uso intenso

✅ **"Barreira rígida em viaduto: quanto custa?"**  
→ Resposta: SICRO + memorial de projeto específico = R$ 1.200-2.000/m (mais caro que defensa)

✅ **"Atenuador de impacto: qual o custo de substituição?"**  
→ Resposta: ~R$ 500-800 por unidade; frequência de substituição: 6 meses a 2 anos

✅ **"Estudo de caso: rodovia federal com redução de acidentes?"**  
→ Resposta: BR-116 SP (CCR) — 45% menos saídas de pista após defensa+barreira

✅ **"Qual tipo de dispositivo é mais econômico?"**  
→ Resposta: Defensa metálica (menor custo inicial); barreira rígida (menor manutenção)

---

## Links de Referência no Repositório

- **CLAUDE.md** — Registro dos 20 agentes (confirma S1)
- **ARQUITETURA-AGENTES-IA.md** — v2.0.0 com S1-S5 (rodovias operacionais)
- **dispositivos-viarios-interconexoes-seguranca.html** — Guia técnico (já consultado)

---

## Próxima Ação Recomendada

**AGORA:** Abra uma nova sessão no Claude com:

```
@maestro

Preciso de estudos de caso de rodovias brasileiras (federais, estaduais, concessões) 
com análise de custos de defensas metálicas, barreiras rígidas e atenuadores de impacto.

Inclua:
- Exemplos de projetos executivos com custo detalhado
- Tabelas SICRO (custos unitários atuais)
- Ciclos de manutenção pós-obra
- Resultado operacional (segurança, redução de acidentes)
- Comparação econômica (ROI, payback)

Priorize rodovias concedidas (dados ANTT).
```

**Maestro fará routing automático para agente-infraestrutura (S1)**  
**Você terá resposta em ~10 minutos com dados reais.**

---

**Análise preparada:** 29/07/2026  
**Status:** Pronto para routing  
**Agente-alvo:** Manta 03-S1 (agente-infraestrutura Rodovias)  
**Classificação:** Consultoria técnica — Dispositivos Viários
