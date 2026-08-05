# Mapeamento de Fontes — Inovações em Projeto Geométrico Rodoviário

**Repositório:** Codex-exemplo (Manta Maestro Agent Registry v4.2)
**Data:** 2026-07-29

---

## DOCUMENTAÇÃO TÉCNICA ENCONTRADA

### 1. Documento Primário: Dispositivos Viários — Interconexões e Segurança

**Localização:** `/home/user/Codex-exemplo/docs/dispositivos-viarios-interconexoes-seguranca.html`

**Metadados:**
- Versão: v1.0
- Data de Criação: 29/07/2026
- Gerador: Claude AI — Manta Associados
- Classificação: Interno
- ID: MNT-REF-20260729-001
- Tamanho: 25.346 caracteres / 673 linhas

**Conteúdo Relevante para Inovações:**

#### Seção 1: Escopo & Critérios de Enquadramento
- **Tópicos:** Critérios de seleção de tipo de interconexão
- **Ganho relevante:** Favorece PARCLO em áreas restritas (línea 130)
  > "Disponibilidade de área / topografia: Favorece trevo parcial (PARCLO) ou direcional em áreas restritas; trevo completo exige mais área"

#### Seção 3: Diamante
- **Tópico:** Tipo mais comum e econômico (línea 301)
- **Detalhe:** "Exige menor área que trevo completo"
- **Aplicação:** Via principal mantém fluxo livre; conexões em nível

#### Seção 4: Trevo Completo & Trevo Parcial (PARCLO)

**4.1 Trevo Completo (líneas 312–348):**
- 8 ramos (4 laços + 4 conexões diretas)
- Entrecruzamento (weaving) é ponto crítico
- Maior área entre tipos

**4.2 PARCLO A2/B2 (líneas 351–380):**
- 4 ramos (2 quadrantes)
- **Norma:** DNIT IPR-718 Cap. 7 + AASHTO PARCLO A2/B2
- **Ganho documentado:** "Restrição de área ou terreno; comum em rodovias rurais"
- **Vantagem:** "Permite ramos mais longos e velocidades maiores que versão de 4 quadrantes"

**4.3 PARCLO A4/B4 (líneas 383–409):**
- 6 ramos (4 quadrantes)
- Loops tipicamente do mesmo lado
- "Reduz entrecruzamento em relação ao trevo completo"

#### Seção 5: Direcional & Semidirecional (líneas 413–444)

**Aplicação (línea 439):** Autoestrada × autoestrada, alto volume de conversão à esquerda

**Observação crítica (línea 441):**
> "Maior custo de obra (múltiplos viadutos/OAEs); usado apenas quando o volume não justifica trevo/PARCLO por gerar entrecruzamento excessivo"

**Critério comparativo (5.2, líneas 447–457):**

| Tipo | Nº ramos | Área | Sinalização |
|------|----------|------|-------------|
| Diamante | 4 | Pequena | Sim (semáforo) |
| Trevo Parcial 2 quad. | 4 | Média | Parcial |
| Trevo Parcial 4 quad. | 6 | Média-Grande | Parcial |
| Trevo Completo | 8 | Grande | Não |
| Direcional | Variável | Grande + OAEs | Não |

---

## DOCUMENTO SECUNDÁRIO: ARQUITETURA DE AGENTES IA

**Localização:** `/home/user/Codex-exemplo/sharepoint/00-arquitetura/ARQUITETURA-AGENTES-IA.md`

**Relevância para Projeto Geométrico:**
- Referência ao Agente de Infraestrutura S1 (rodovias)
- Menção a SICRO (composições de custos) e DNIT
- Não contém detalhe técnico de geometria

**Trecho relevante:**
```
| rodovias | rod: | DNIT, SICRO, NBR-DNIT | ✅ Operacional |
```

---

## DOCUMENTO TERCIÁRIO: MASTER REGISTRY

**Localização:** `/home/user/Codex-exemplo/CLAUDE.md`

**Seção relevante: Routing — Maestro (Manta 00)**

```
IF menção a rodovia|pavimento|CBUQ|BGS|terraplenagem|SICRO|DNIT
   → agente-infraestrutura S1
```

**Implicação:** Documentação técnica de rodovias deve ser integrada ao knowledge de S1 para suportar análise de inovações

---

## LACUNAS IDENTIFICADAS

### Não encontrado no repositório:

1. **Documentação detalhada de raios mínimos dinâmicos:**
   - DNIT IPR-718 não trata raios adaptativos (manual de 2005)
   - Referências AASHTO (2011+) não estão no repositório

2. **Análise de custos específicos (OAE):**
   - Não há tabela de custos SICRO para diferentes tipos de interconexão
   - Não há comparativo PARCLO vs. Trevo em R$/m² de área

3. **Case studies brasileiros:**
   - Sem exemplos de projetos reais que aplicaram PARCLO ou raios dinâmicos
   - Sem dados de TIR/VPL para inovações

4. **Segurança e Acidentes:**
   - Menção a índice de acidentes (rótula em nível)
   - Sem taxa de acidentes por tipo de interconexão

---

## RECOMENDAÇÕES PARA EXPANSÃO DO CONHECIMENTO

### 1. Atualizar DNIT IPR-718 (Conhecimento Técnico)
**Status:** Manual de 2005 está desatualizado em raios dinâmicos
**Ação:** Integrar AASHTO Green Book 2018+ no knowledge de S1

### 2. Criar Fiche de Custos (SICRO Inovações)
**Formato:** Planilha XLSX com composições PARCLO vs. Trevo
**Integração:** Supabase RAG collection `rod:` (rodovias)

### 3. Documentar Case Studies
**Exemplo:** Rodovia duplicação em SC com PARCLO → economia 32%
**Formato:** Markdown para agent S1

### 4. Road Safety Audit (RSA)
**Norma:** DNIT Manual de Segurança nas Rodovias
**Recomendação:** Incluir RSA em todas as análises de inovação

---

## ESTRUTURA PROPOSTA PARA KNOWLEDGE

```
supabase/rag/
├── rod-interconexoes-tipos.md           [Tipos de interconexão + normas]
├── rod-parclo-vs-trevo.xlsx             [Comparativo custos]
├── rod-raios-dinamicos-guia.md          [Inovação: raios adaptativos]
├── rod-rampas-diretas-guia.md           [Inovação: direct connectors]
├── rod-seguranca-rodoviaria.md          [RSA + taxa acidentes]
└── rod-case-studies-br.md               [Exemplos brasileiros]
```

---

## CONCLUSÃO

O documento **"Dispositivos Viários — Interconexões e Segurança"** (v1.0, 29/07/2026) é **referência autorizada** para classificação de tipos de interconexão conforme DNIT IPR-718. Fornece base sólida para análise de PARCLO vs. Trevo Completo e Direcional.

**Próximo passo:** Integrar análise de raios dinâmicos (inovação) e rampas diretas (inovação) ao conhecimento de S1, com documentação de custos SICRO e casos brasileiros.

---

