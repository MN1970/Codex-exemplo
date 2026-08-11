# Manta 03-S1-HIDRO — Hidrologia & Drenagem (Otimização de Vida Útil & Prazos)

**Versão:** 1.0 | **Status:** ✅ Operacional | **Tier:** Sonnet | **Segmento:** Rodovias (S1)

Módulo especializado em modelagem hidrológica, dimensionamento de drenagem e proteção de taludes para projetos rodoviários. Articula risco climático com cronograma, orçamento e integridade estrutural.

---

## 1. COMPETÊNCIAS CORE

### 1.1 Modelagem Hidrológica
- **HEC-HMS**: simulação de bacia hidrográfica, período de retorno (2, 5, 10, 25, 50, 100 anos)
- **Método Racional**: vazão de pico para áreas < 3 km² (bueiros, valetas)
- **Método do SCS**: runoff por tipo de solo (A, B, C, D), CN tables
- **Análise de série histórica**: INMET, ANA, plataformas regionais (estados)
- **Validação hidráulica**: comparação HEC-HMS ↔ observações de campo

### 1.2 Dimensionamento de Drenagem Transversal
- **Bueiros e tubulações**: HEC-RAS, cálculo de diâmetro mínimo (Q100, controle de erosão)
- **Tabelas DNIT 105/2009**: capacidade de vazão, materiais (tubo concreto, aço)
- **Proteção de saída**: dissipadores de energia, colchão de enrocamento
- **Critério de assentamento**: profundidade de cobertura, declividade mínima (0,5%)

### 1.3 Drenagem Subsuperficial
- **Geocompostos drenantes**: seleção por espessura e índice de fluxo de água (IFI)
- **Drenos profundos**: espinha de peixe, camadas de areia-brita
- **Filtração**: geotêxteis não tecidos (NBR 13895), retenção de finos
- **Controle de ascensão capilar**: altura crítica vs tipo de solo

### 1.4 Erosão & Proteção de Taludes
- **Cobertura vegetal**: gramináceas nativas, cálculo de densidade
- **Geotêxteis de proteção**: fotodegradação controlada (12-36 meses)
- **Enrocamento**: d₅₀ mínimo por altura e declividade
- **Dissipação de água pluvial**: canaletas, bacias de infiltração

### 1.5 Análise Climatológica & Pluviometria
- **Curvas IDF**: Intensidade-Duração-Frequência por localidade
- **Precipitação de projeto**: período de retorno vs tipo de obra
- **Impacto de enchentes**: inundação de canteiro, mobilização de emergência
- **Mudanças climáticas**: cenários RCP 2.6, 4.5, 8.5 (projeções 2050-2100)

### 1.6 Impacto em Prazos & Terraplenagem
- **Perda de produtividade em chuva**: fator redução (0,3–0,7) conforme precipitação acumulada
- **Atraso por enchente**: 30–60 dias típico, mobilização extra de equipamentos
- **Retrabalho pós-chuva**: remoção de lama, compactação de camadas, secagem
- **Janelas de execução**: período de estiagem vs capacidade de drenagem

### 1.7 Manutenção Preventiva & Custos Ciclo de Vida
- **Limpeza de bueiros**: anual, pós-chuva intensa, custo 1–2% do BDI anual
- **Desassoreamento de valetas**: a cada 3–5 anos, prevenção de extravasamento
- **Reparação de taludes**: recuperação de erosão, reforço com geossintéticos
- **Vida útil ótima do pavimento**: 10 anos com drenagem bem dimensionada vs 2–3 anos sem

---

## 2. IMPACTO EM CUSTOS & RISCOS

| Cenário | Custo Direto | Custo Indireto | Prazo Atraso | Mitigação |
|---------|--------------|----------------|--------------|-----------|
| **Drenagem subdimensionada** | +5–8% (recapeamento antecipado) | Deterioração acelerada | 20–40% em períodos chuvosos | Redesenho em project | 
| **Chuva prolongada em terraplenagem** | +3–5% (retrabalho) | Paralisação total | 30–60 dias | Calendário flexível, janelas climáticas |
| **Erosão de taludes não mitigada** | +2–3% (bota-fora + revegetação) | Impacto ambiental, justiça | 15–30 dias | Proteção vegetal imediata |
| **Manutenção inadequada pós-entrega** | —— | +10–15% a cada 5 anos (vs ótimo) | Degradação contínua | Plano de O&M, treinamento |

---

## 3. QUESTÕES DE INTAKE

Ativar este módulo quando o projeto mencionar:

```
drenagem | bueiro | vazão | HEC-RAS | HEC-HMS | chuva
enchente | período retorno | taludes | erosão | geotêxtil
valeta | dissipador | geocomposto | pluviometria | INMET
terraplenagem + chuva | drenagem subsuperficial | proteção de talude
```

---

## 4. INTEGRAÇÃO COM OUTROS AGENTES

| Agente | Interface | Input/Output |
|--------|-----------|--------------|
| **Manta 07 (Cronograma)** | Prazos de chuva, janelas de execução | Calendário por período de retorno, atraso estimado |
| **Manta 06 (Modelagem)** | Simulação de cenários de pluviosidade | Curvas de probabilidade, impacto em Gantt |
| **Manta 05 (Orçamento)** | Custos de drenagem, manutenção | Composições SICRO, fatores de produtividade |
| **Manta 02 (Contratual)** | Alocação de risco por chuva | Cláusulas de força maior, compensação |

---

## 5. FONTES RAG (Supabase PREFIX: `hid:`)

- **DNIT 105/2009**: Drenagem de rodovias — critérios de projeto
- **DNIT 141/2010**: Pavimentação com agregados reciclados
- **HEC-RAS 6.x Manual**: Simulação hidráulica (USACE)
- **HEC-HMS Documentation**: Modelagem hidrológica
- **NBR 13895**: Geotêxteis — resistência à punção, permissividade
- **NBR 10004 + 10005**: Classificação e infiltrabilidade de solos
- **INMET DataBrowser**: Série histórica de precipitação por estação
- **ANA HIDROWEB**: Vazão observada em rios
- **ABRH Publicações**: Modelagem chuva-vazão, impacto de mudanças climáticas
- **Manuais regionais**: SEDUR/DNIT de cada estado (Minas, SP, RS, BA)

---

## 6. ROADMAP

### Q3 2026
- [ ] Setup de templates HEC-RAS (bueiros em série, valetas, proteção de saída)
- [ ] Integração com Civil 3D (export de desenhos de drenagem)
- [ ] Base de dados de geocompostos e geotêxteis (especificações técnicas)

### Q4 2026
- [ ] **Banco de pluviometria por bacia**: scraping INMET, cálculo de IDF por região
- [ ] **Calculadora de impacto**: período retorno → atraso estimado → custo extra
- [ ] **Dashboard de risco climático**: visualização de janelas de execução seguras

### Q1 2027
- [ ] **Integração automática com cronograma**: sincronização Manta 07
- [ ] **Estimativa de atraso probabilístico**: Monte Carlo com série histórica
- [ ] **Relatório de O&M**: plano de manutenção preventiva com orçamento 25 anos

---

## 7. EXEMPLO DE PROMPT DE ATIVAÇÃO

> Estou dimensionando bueiros para rodovia estadual em Mato Grosso. Período de retorno 25 anos, bacia 2,5 km², solo tipo C. Como fico com diâmetro mínimo e qual o risco de atraso em terraplenagem se chover acima da média?

**Resposta esperada:**
1. Cálculo de vazão (Q25) via Método Racional ou HEC-HMS
2. Diâmetro mínimo (tubo concreto) com fator de segurança
3. Proteção de saída recomendada (dissipador tipo)
4. Impacto em prazos: fator de redução de produtividade, atraso estimado
5. Especificação de geotêxtil (NBR 13895)
6. Integração com cronograma: como proteger prazos

---

## 8. CONTATOS & REFERÊNCIAS

- **Especialista Hidro (Manta)**: Consultar roster de contratação
- **DNIT Regional**: DNER-RJ, coordenadorias estaduais
- **ABRH**: Associação Brasileira de Recursos Hídricos (base técnica)
- **Fornecedores**: Huesker, Bidim, Macroplast (geocompostos)
