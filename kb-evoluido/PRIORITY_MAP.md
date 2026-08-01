# Mapa de Prioridades — KB Evoluído

## Segmentos Prioritários para Evolução Contínua

### 🥇 Tier 1 — Máxima Prioridade

| Segmento | Agente | Foco | Razão |
|----------|--------|------|-------|
| **Saneamento** | agente-saneamento (S8) | AySA (Argentina), ETA/ETE, adução | Projeto recorrente, alta complexidade hidráulica, regulação dinâmica (Lei 14.026) |
| **Energia** | agente-energia (S9) | Transmissão (ANEEL), subestações, leilões | Setor altamente regulado, constantes técnicas que evoluem (resolução ANEEL), projetos de larga escala |
| **Portos** | agente-portos (S6) | Terminais, dragagem, concessões (ANTAQ) | Grande volume de dados, padrões internacionais (PIANC), índices tarifários dinâmicos |

### 🥈 Tier 2 — Secundária

| Segmento | Agente | Foco |
|----------|--------|------|
| **Aeroportos** | agente-aeroportos (S7) | Infraestrutura, balizamento, TPS/TECA |
| **Barragens** | agente-barragens (S10) | Estudos prévios, segurança, regulação (Lei 12.334) |

---

## Dados Disponíveis por Segmento

```
sharepoint/01-agentes-fundamentais/
├── agente-saneamento/
│   ├── README.md           # Contexto de domínio
│   ├── SKILL.md            # Skills disponíveis
│   ├── refs/               # Referências (normas, leis)
│   └── prompts/starters.md # Prompts de inicialização
├── agente-energia/
├── agente-portos/
├── agente-aeroportos/
└── agente-barragens/
```

---

## Constantes Técnicas Iniciais a Rastrear

### Saneamento (agente-saneamento)
- K1 (coef. dia máximo): 1.2–1.5 BR, variável por região
- K2 (coef. hora máxima): 1.5–2.0 BR
- Per capita: 150–250 L/hab.dia BR, 200–350 AR
- Taxas de aplicação ETA (m³/m².dia)
- Métodos ETE (UASB, MBR, lodo ativado)
- Índices SNIS (perda %, atendimento %)

### Energia (agente-energia)
- Parâmetros de transmissão (R, X por km)
- Capacidade de subestações (VA)
- Resolução ANEEL vigente (taxa, fator X/R)
- Custos de torre estaiada vs convencional
- Critérios de seleção de rota (faixa, segurança)

### Portos (agente-portos)
- Calado operacional por berço
- Padrões PIANC (forças de atracação)
- Dragagem (produtividade, profundidade)
- Índices de movimentação (TEU/dia, ton/dia)
- Tarifas portuárias (dinâmicas por região)

---

## Cadência de Atualização

| Frequência | Tipo | Segmentos |
|-----------|------|----------|
| **Diária** | Ingestion de projetos finalizados | Todos |
| **Semanal** | Validação de constantes por agente | S8, S9, S6 |
| **Mensal** | Publicação de changelog KB | Todos |
| **Trimestral** | Atualização de normas/resoluções | S8 (Lei 14.026), S9 (ANEEL), S6 (ANTAQ) |

---

## Acesso a Dados Externos (para ML)

- **SNIS (BR)**: API pública, KPIs por concessionária
- **ERAS/AySA (AR)**: Relatórios trimestrais, dados de consumo
- **ANEEL**: Editais, resoluções normativas, leilões
- **ANTAQ**: Estatísticas portuárias, tarifas
- **SharePoint Manta**: Projetos finalizados (memoriais, orçamentos, cronogramas)

---

## Próximos Passos

1. ✅ Criar schemas Supabase para rastreamento
2. ✅ Definir pipeline de ingestion (diário)
3. ✅ Treinar modelos de padrão recognition
4. ✅ Implementar feedback loop
5. ✅ Rodar evolução automática 1x/semana (depois escalar para diário)
