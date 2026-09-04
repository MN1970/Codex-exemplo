# Drenagem em Rodovias — Base de Conhecimento

**Agente responsável**: Manta 03-S1 (Infraestrutura — Rodovias)  
**Versão**: 1.0  
**Última atualização**: 2026-08-04

---

## Visão Geral

Esta pasta contém a **base de conhecimento técnico completo** sobre drenagem em projetos rodoviários brasileiros. Cobre desde fundamentos hidrológicos até operação e manutenção, com foco em aplicabilidade prática e conformidade normativa (DNIT, NBR, padrões internacionais).

---

## Estrutura de Arquivos

```
drenagem/
├── README.md                                    # Este arquivo
├── 00-indice-maestro.md                         # Índice geral + roteiro de consulta
├── 01-fundamentos-hidrologicos.md               # TÓPICO 1: Ciclo hidrológico, vazão
├── 02-drenagem-superficial.md                   # TÓPICO 2: Sarjetas, valetas (planejado)
├── 03-drenagem-subsuperficial.md                # TÓPICO 3: Camadas drenantes, drenos (planejado)
├── 04-taludes-trincheiras.md                    # TÓPICO 4: Proteção de encostas (planejado)
├── 05-bueiros-galerias.md                       # TÓPICO 5: Dimensionamento (planejado)
├── 06-intersecoes-dispositivos.md               # TÓPICO 6: Interseções especiais (planejado)
└── 07-manutencao-inspecao.md                    # TÓPICO 7: Operação & manutenção (planejado)
```

---

## Tópicos Disponíveis

### Tópico 1: Fundamentos Hidrológicos ✅ COMPLETO

**Arquivo**: `01-fundamentos-hidrologicos.md`

Aborda:
- Ciclo da água e componentes (precipitação, infiltração, evapotranspiração, escoamento)
- Bacias hidrográficas e delimitação de áreas de drenagem
- **Tempo de concentração** (Kirpich, Giandotti)
- **Cálculo de vazão** pelo Método Racional
- **Coeficientes de escoamento** por tipo de solo/cobertura
- Evapotranspiração (Penman-Monteith, valores típicos)
- **Infiltração**: capacidade por tipo de solo (DNIT ES 131/86)
- Exemplos com valores reais (Federal Vd=100)
- 3 casos reais nacionais (BR-116, rodovia sertaneja, duplicação)
- Tabelas normativas DNIT ES 131/86, NBR 10844:2020
- **27 referências** técnicas e normativas

**Quando consultar**: Sempre como primeira leitura para dimensionamento de drenagem; base para cálculos de vazão.

---

### Tópicos 2–7: Planejados

| Tópico | Tema | Status | Data prevista |
|--------|------|--------|---|
| 2 | Drenagem Superficial | 🔄 Em desenvolvimento | 2026-08-15 |
| 3 | Drenagem Subsuperficial | 🔄 Planejado | 2026-08-22 |
| 4 | Proteção de Taludes | 🔄 Planejado | 2026-08-29 |
| 5 | Bueiros e Galerias | 🔄 Planejado | 2026-09-05 |
| 6 | Intersecções Especiais | 🔄 Planejado | 2026-09-12 |
| 7 | Manutenção & Inspeção | 🔄 Planejado | 2026-09-19 |

---

## Como Usar Esta Base

### Para Engenheiros em Projeto

1. **Comece pelo Índice** (`00-indice-maestro.md`): Oferece roteiro de consulta por problema específico.
2. **Tópico 1** (Fundamentos): Leia completamente na primeira vez; depois consulte conforme necessário.
3. **Tópicos 2–5**: Consulte conforme fase do projeto (básico, executivo).
4. **Tópico 7**: Use em operação/manutenção.

### Para Equipes de Fiscal

1. Consulte **Tópico 7** (Manutenção) para cronograma de inspeção.
2. Use **Tópico 1** para entender parâmetros de projeto e revisão de conformidade.

### Para Assistentes de IA (Agentes)

1. **Skill `rodovias`**: Quando menção de drenagem, precipitação, escoamento → carregue `01-fundamentos-hidrologicos.md`
2. **Skill `rodovias-geotecnia`**: Quando menção de infiltração, lençol freático → carregue `03-drenagem-subsuperficial.md` (quando pronto)
3. **Maestro**: Use `00-indice-maestro.md` para roteamento de queries.

---

## Normas Técnicas Integradas

Esta base é **100% alinhada** com:

- **DNIT ES 131/86** — Drenagem Superficial de Rodovias
- **DNIT ES 132/86** — Drenagem Subsuperficial de Rodovias
- **DNIT ES 133/86** — Drenagem de Cortes e Aterros
- **NBR 10844:2020** — Instalações Prediais de Águas Pluviais
- **Padrões internacionais** (ASCE, USDA, FAA) para compatibilidade

---

## Valores de Referência — Federal Vd=100

### Precipitação Máxima

| Período de retorno | Altura (mm) | Intensidade (mm/h) |
|--------------------|------------|-------------------|
| Tr = 5 anos | 100 | 155 |
| **Tr = 25 anos** | **160** | **245** |
| Tr = 50 anos | 185 | 270 |

### Coeficiente de Escoamento (C)

- Pavimento asfáltico: **0,95–1,00**
- Grama/pasto: **0,15–0,30**
- Solo nu: **0,20–0,40**
- Bosque: **0,05–0,15**

### Infiltração (f_c)

- Cascalho bem graduado (GW): **50–100 mm/h** ← Preferido para drenagem
- Areia: **5–20 mm/h**
- Argila: **< 0,2 mm/h** ← Impermeável

---

## Integração com Outros Módulos Rodoviários

```
GEOMETRIA           PAVIMENTAÇÃO        DRENAGEM            OAE
├─ Traçado         ├─ Estrutura        ├─ Hidrologia       ├─ Ponte
├─ Alinhamento     ├─ Materiais        ├─ Superficial      ├─ Viaduto
├─ Interseções     ├─ Dimensionamento  ├─ Subsuperficial   └─ Túnel
└─ Dispositivos    └─ Camada drenante  ├─ Bueiros          
                                        └─ Manutenção
```

**Conexão**: Drenagem depende de geometria (áreas de bacia), integra com pavimentação (camada drenante) e é crítica para OAE.

---

## Casos de Estudo Documentados

### Tópico 1

1. **BR-116 (Mantiqueira, MG)** — Serra com alta precipitação, OAE críticas
2. **Rodovia Federal (Sertão, CE)** — Semiárido, baixa infiltração, ET elevada
3. **Duplicação (Vale do Paraíba, SP)** — Bacia de infiltração como inovação

Cada caso apresenta:
- Contexto hidrológico
- Dados de chuva e capacidade de infiltração
- Solução implementada
- Resultado e desempenho

---

## Fórmulas Críticas

### Vazão (Método Racional)

$$Q = 0,278 \times C \times i \times A$$

- Q = vazão (m³/s)
- C = coeficiente de escoamento
- i = intensidade de chuva (mm/h)
- A = área de bacia (ha)

### Tempo de Concentração (Kirpich)

$$t_c = 57 \times \left(\frac{L^3}{H}\right)^{0,385}$$

- L = comprimento talvegue (km)
- H = desnível (m)
- t_c = minutos

---

## Checklist para Dimensionamento

- [ ] Dados climáticos: série histórica (≥20 anos) disponível
- [ ] Período de retorno: definido conforme tipo de drenagem
- [ ] Topografia: mapa com curvas de nível em escala apropriada
- [ ] Bacias: delimitadas e calculadas
- [ ] Tempo de concentração: escolhida fórmula apropriada
- [ ] Coeficiente C: estimado por tipo de cobertura
- [ ] Intensidade IDF: obtida de estação regional
- [ ] Infiltração: teste realizado ou material especificado
- [ ] Lençol freático: profundidade mapeada
- [ ] Referências: normas DNIT consultadas

---

## Suporte Técnico

**Dúvidas ou sugestões?**

- Consulte o **Índice Maestro** (`00-indice-maestro.md`) para roteiro de problema específico.
- Se precisar de variação regional, consulte:
  - **INMET** — Instituto Nacional de Meteorologia (séries de precipitação)
  - **ANA** — Agência Nacional de Águas (Portal HidroWeb)
  - **CPRM** — Serviço Geológico do Brasil (mapas de risco)

---

## Versionamento

| Versão | Data | Alterações principais |
|--------|------|----------------------|
| **1.0** | 2026-08-04 | Criação inicial; Tópico 1 completo |

**Próxima revisão**: 2026-12-31

---

**Agente responsável**: Manta 03-S1 (Infraestrutura — Rodovias)  
**Status**: ✅ Produção  
**Licença**: Uso interno Manta Associados
