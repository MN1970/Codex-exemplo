# Checklist de Projeto — Drenagem Rodoviária

**Referência**: Tópico 1 — Fundamentos Hidrológicos  
**Normas**: DNIT ES 131/86, DNIT ES 132/86, NBR 10844:2020  
**Data**: 2026-08-04  
**Uso**: Projeto Básico e Executivo

---

## FASE 1: COLETA DE DADOS

### 1.1 Dados Climáticos

- [ ] **Série histórica de precipitação máxima anual**
  - [ ] Mínimo 20 anos de dados
  - [ ] Fonte: INMET, ANA, estação regional
  - [ ] Verificado com órgão gestor local
  
- [ ] **Equação IDF (Intensidade-Duração-Frequência)**
  - [ ] Obtida de estação meteorológica próxima
  - [ ] Validada para o tipo de clima regional
  - [ ] Constantes K, a, b, c documentadas
  
- [ ] **Período de retorno definido**
  - [ ] Conforme tipo de drenagem (DNIT ES 131)
  - [ ] Justificativa registrada

### 1.2 Topografia

- [ ] **Mapa topográfico em escala apropriada**
  - [ ] Escala mínima: 1:2.000 (projeto básico) ou 1:500–1:1.000 (executivo)
  - [ ] Curvas de nível: intervalos 1–2 m
  - [ ] Sistema de coordenadas definido (UTM, SIRGAS 2000)
  
- [ ] **Pontos cotados em seções críticas**
  - [ ] Entrada e saída de bueiros
  - [ ] Fundo de talvegues naturais
  - [ ] Pontos de divergência de água

### 1.3 Geotecnia

- [ ] **Sondagem de solo (SPT ou similiar)**
  - [ ] Mapeamento do lençol freático
  - [ ] Classificação SUCS dos solos
  - [ ] Profundidade de lençol estimada
  
- [ ] **Teste de infiltração (cilindro duplo — DNIT ES 132/86)**
  - [ ] Realizado em camadas de provável drenagem
  - [ ] Mínimo 3 pontos por tipo de solo
  - [ ] Taxa de infiltração (f_c) documentada em mm/h

### 1.4 Levantamento de Campo

- [ ] **Reconhecimento visual do terreno**
  - [ ] Tipo de cobertura vegetal (percentuais)
  - [ ] Áreas impermeáveis (pavimento, estruturas)
  - [ ] Áreas de alagamento ou retenção natural
  - [ ] Fotografias (data, localização, legenda)

---

## FASE 2: DELIMITAÇÃO DE BACIAS

### 2.1 Divisor de Águas

- [ ] **Mapa de bacias desenhado**
  - [ ] Cada ponto de drenagem identificado
  - [ ] Divisor de águas traçado com base em topografia
  - [ ] Validação em campo (opcional, recomendado)

### 2.2 Cálculo de Áreas

- [ ] **Áreas de drenagem (A) em hectares**
  - [ ] Medidas por planímetro ou software CAD
  - [ ] Unidades: hectares (ha) ou km²
  - [ ] Planilha com todas as bacias

### 2.3 Parâmetros da Bacia

- [ ] **Para cada bacia:**
  - [ ] Comprimento do talvegue (L) em metros
  - [ ] Desnível (H) em metros
  - [ ] Declive médio (I_m) em m/m (calculado como H/L)
  - [ ] Tipo predominante de cobertura

---

## FASE 3: CÁLCULO HIDROLÓGICO

### 3.1 Tempo de Concentração (t_c)

- [ ] **Fórmula selecionada justificada**
  - [ ] Kirpich: para bacias pequenas (A < 1 km²)
  - [ ] Giandotti: para bacias maiores (A > 1 km²)
  - [ ] Outra fórmula regional documentada

- [ ] **Cálculo de t_c realizado**
  - [ ] t_c em minutos
  - [ ] Planilha de cálculo apresentada
  - [ ] Resultado revisado (verificação de realismo)

### 3.2 Intensidade de Chuva (i)

- [ ] **Intensidade obtida via equação IDF**
  - [ ] Valor de Tr (período de retorno) inserido
  - [ ] Duração = t_c (duração crítica)
  - [ ] Resultado: intensidade em mm/h
  
- [ ] **Documento apresentado com cálculo**
  - [ ] Equação IDF completa
  - [ ] Gráfico IDF como referência (se disponível)

### 3.3 Coeficiente de Escoamento (C)

- [ ] **Mapa de cobertura de solo preparado**
  - [ ] Percentuais de cada tipo (pavimento, grama, rocha, etc.)
  - [ ] Área de cada tipo calculada
  
- [ ] **Coeficiente C ponderado calculado**
  - [ ] Fórmula: C = Σ(C_i × A_i) / Σ A_i
  - [ ] Valores C conforme tabela DNIT
  - [ ] Resultado em 2 ou 3 casas decimais

### 3.4 Vazão (Método Racional)

- [ ] **Fórmula aplicada: Q = 0,278 × C × i × A**
  - [ ] Q = vazão em m³/s
  - [ ] Unidades verificadas (C adimensional, i em mm/h, A em ha)
  - [ ] Resultado com 1 ou 2 casas decimais

- [ ] **Vazão por tipo de drenagem (se aplicável)**
  - [ ] Superficial (valeta, sarjeta)
  - [ ] Subsuperficial (dreno)
  - [ ] Bueiro / passagem hídrida
  - [ ] Cada uma com seu Tr e C apropriado

- [ ] **Planilha-resumo de vazões**
  - [ ] Todas as bacias
  - [ ] Valores utilizados de C, i, A, Tr
  - [ ] Q resultante em m³/s

---

## FASE 4: INFILTRAÇÃO E PERMEABILIDADE

### 4.1 Teste de Infiltração Realizado

- [ ] **Teste de cilindro duplo executado (DNIT ES 132/86)**
  - [ ] Localização: coordenadas UTM
  - [ ] Profundidade de teste: documento
  - [ ] Duração mínima: 30 minutos por ponto
  - [ ] Taxa final (f_c) em mm/h
  - [ ] Foto ou sketch do local

### 4.2 Classificação de Solos

- [ ] **Solos classificados segundo SUCS**
  - [ ] Camada 1 (0–0,5 m): símbolo SUCS, f_c
  - [ ] Camada 2 (0,5–1,5 m): símbolo SUCS, f_c
  - [ ] Camada 3+ se aplicável

- [ ] **Avaliação de adequação para drenagem**
  - [ ] GW, GP, SW: recomendado ✅
  - [ ] SP, SM: aceitável com ressalvas ⚠️
  - [ ] SC, CL, ML: não recomendado ❌

### 4.3 Especificação de Material Drenante

- [ ] **Se necessário camada drenante:**
  - [ ] Material: GW ou GP conforme disponibilidade
  - [ ] f_c mínimo exigido em mm/h
  - [ ] Geotêxtil especificado (se aplicável)
  - [ ] Espessura mínima em cm

---

## FASE 5: LENÇOL FREÁTICO

### 5.1 Profundidade Mapeada

- [ ] **Profundidade de lençol freático**
  - [ ] Em metros abaixo da superfície
  - [ ] Mapeado em seções longitudinais
  - [ ] Indicação de zona saturada vs. insaturada

### 5.2 Risco Estrutural

- [ ] **Risco avaliado**
  - [ ] Profundidade > 1,5 m: Baixo ✅
  - [ ] Profundidade 1,0–1,5 m: Moderado ⚠️
  - [ ] Profundidade 0,5–1,0 m: Alto ❌
  - [ ] Profundidade < 0,5 m: Crítico ❌❌

### 5.3 Medidas Mitigadoras (se necessário)

- [ ] **Se risco moderado ou alto:**
  - [ ] Dreno perimetral especificado
  - [ ] Camada drenante sob pavimento
  - [ ] Bombeamento ou rebaixamento considerado

---

## FASE 6: PROJETO DE DRENAGEM

### 6.1 Drenagem Superficial

- [ ] **Sarjetas / canaletas dimensionadas**
  - [ ] Seção transversal desenhada
  - [ ] Capacidade verificada (Manning)
  - [ ] Velocidade máxima dentro de limites (proteção erosão)
  
- [ ] **Valetas laterais**
  - [ ] Profundidade e largura definidas
  - [ ] Revestimento especificado (grama, concreto)
  - [ ] Declividade longitudinal mínima 0,5%

### 6.2 Drenagem Subsuperficial

- [ ] **Camada drenante sob pavimento**
  - [ ] Espessura definida (tipicamente 10–15 cm)
  - [ ] Material especificado (GW, permeabilidade)
  - [ ] Descarga para dreno perimetral detalhado

- [ ] **Dreno perimetral**
  - [ ] Localização (ao pé de aterro)
  - [ ] Tubo ou trincheira especificado
  - [ ] Material filtrante (geotêxtil + areia)
  - [ ] Descarga para drenagem superficial

### 6.3 Bueiros e Galerias

- [ ] **Para cada bueiro:**
  - [ ] Vazão de projeto Q (m³/s)
  - [ ] Tipo de bueiro (circular, celular, retangular)
  - [ ] Dimensões (diâmetro ou vãos)
  - [ ] Verificação de capacidade (altura de remanso < limite)
  - [ ] Fundação especificada
  - [ ] Revestimento especificado
  - [ ] Detalhe construtivo em seção

### 6.4 Proteção de Taludes

- [ ] **Se corte ou aterro instável:**
  - [ ] Drenagem de encosta especificada
  - [ ] Trincheira drenante detalhada
  - [ ] Proteção superficial (grass, gabião, concreto)

---

## FASE 7: DOCUMENTAÇÃO E APRESENTAÇÃO

### 7.1 Relatório de Hidrologia

- [ ] **Seções obrigatórias:**
  - [ ] 1. Introdução (objetivo, local, metodologia)
  - [ ] 2. Dados climáticos e hidrológicos (fonte, serie utilizada)
  - [ ] 3. Bacias de drenagem (mapa, áreas, parâmetros)
  - [ ] 4. Cálculo de vazão (método racional, planilhas)
  - [ ] 5. Infiltração e permeabilidade (testes, solos)
  - [ ] 6. Lençol freático e risco estrutural
  - [ ] 7. Projeto de drenagem (descrição geral)
  - [ ] 8. Referências normativas (DNIT, NBR, outros)

- [ ] **Anexos técnicos:**
  - [ ] Cópia de série de chuva máxima anual (20+ anos)
  - [ ] Equação IDF com constantes K, a, b, c
  - [ ] Mapa de bacias (em escala apropriada)
  - [ ] Mapa de cobertura de solo
  - [ ] Mapa de lençol freático (perfil geológico)
  - [ ] Planilha de vazões (Q por bacia e Tr)
  - [ ] Resultados de testes de infiltração (campo)
  - [ ] Fotos do levantamento

### 7.2 Desenhos Técnicos

- [ ] **Plantas**
  - [ ] Planta geral de drenagem (escala 1:5.000 ou 1:10.000)
  - [ ] Identificação de pontos de drenagem
  - [ ] Bacias delimitadas e cotadas

- [ ] **Seções longitudinais**
  - [ ] Seção tipo com camadas drenantes
  - [ ] Seção crítica (corte profundo, lençol alto)
  - [ ] Drenagem subsuperficial detalhada

- [ ] **Detalhes construtivos**
  - [ ] Detalhe de sarjeta/canaleta
  - [ ] Detalhe de dreno perimetral
  - [ ] Detalhe de camada drenante
  - [ ] Detalhe de bueiro (seção e elevação)

### 7.3 Especificações Técnicas

- [ ] **Materiais para drenagem**
  - [ ] Agregados (GW, GP, areia — tamanho, gradação)
  - [ ] Geotêxtil (tipo, gramatura, permeabilidade)
  - [ ] Revestimento de superfícies (grama, concreto, alvenaria)

- [ ] **Serviços de drenagem**
  - [ ] Limpeza de áreas
  - [ ] Escavação de valetas e trincheiras
  - [ ] Assentamento de bueiros
  - [ ] Teste de infiltração em campo (recebimento)

---

## FASE 8: REVISÃO E VALIDAÇÃO

### 8.1 Verificação Interna (Engenheiro)

- [ ] **Consistência de cálculos**
  - [ ] Vazões verificadas com calculadora independente
  - [ ] Unidades conferidas (m³/s, não m³/min ou L/s)
  - [ ] Interpolação de IDF revisada

- [ ] **Conformidade normativa**
  - [ ] Período de retorno conforme DNIT
  - [ ] Materiais conforme especificação DNIT
  - [ ] Metodologia alinhada com NBR 10844:2020

- [ ] **Realismo técnico**
  - [ ] Vazões condizentes com tipo de bacia
  - [ ] Tempo de concentração realista
  - [ ] Coeficiente C apropriado para cobertura mapeada

### 8.2 Revisão por Gestor de Projeto

- [ ] **Aprovação de dados de entrada**
  - [ ] Período de retorno aprovado
  - [ ] Fontes de dados climáticos validadas

- [ ] **Conformidade com DNIT**
  - [ ] Comparação com projetos similares (série histórica)
  - [ ] Consulta com concedente/órgão gestor se necessário

### 8.3 Aprovação Final

- [ ] **Documento assinado**
  - [ ] Engenheiro responsável (CREA)
  - [ ] Responsável técnico do projeto
  - [ ] Data de aprovação registrada

---

## FASE 9: EXECUÇÃO

### 9.1 Recebimento de Materiais

- [ ] **Agregados para drenagem**
  - [ ] Curva granulométrica verificada vs. especificação
  - [ ] Amostra de aceitação testada (permeabilidade)

- [ ] **Geotêxtil**
  - [ ] Certificado de fabricante apresentado
  - [ ] Tipo e gramatura conforme projeto

- [ ] **Bueiros (pré-moldados)**
  - [ ] Inspeção visual (fissuras, defeitos)
  - [ ] Dimensões confirmadas

### 9.2 Controle de Execução

- [ ] **Teste de infiltração in situ**
  - [ ] Realizado conforme DNIT ES 132/86
  - [ ] Mínimo 1 ponto por 100 m de drenagem
  - [ ] Taxa ≥ valor de projeto
  - [ ] Laudo de teste assinado

- [ ] **Inspeção visual**
  - [ ] Assentamento de bueiros correto
  - [ ] Compactação de material drenante
  - [ ] Geotêxtil sem rasgo ou deslocamento

- [ ] **Relatório de execução (as-built)**
  - [ ] Fotos de execução
  - [ ] Testes de infiltração
  - [ ] Divergências vs. projeto documentadas

---

## FASE 10: OPERAÇÃO E MANUTENÇÃO

### 10.1 Cronograma de Inspeção

- [ ] **Inspeção inicial**
  - [ ] Período: até 3 meses após conclusão
  - [ ] Verificação de funcionamento
  - [ ] Foto-documentação

- [ ] **Inspeção periódica**
  - [ ] Semestral nos primeiros 2 anos
  - [ ] Anual após 2 anos (ou conforme plano operacional)

### 10.2 Limpeza Preventiva

- [ ] **Limpeza de bueiros**
  - [ ] Frequência: conforme sedimentação (tipicamente anual)
  - [ ] Remoção de sedimento e vegetação

- [ ] **Limpeza de valetas**
  - [ ] Frequência: conforme vegetação (tipicamente 2×/ano)
  - [ ] Mantém profundidade e seção livre

### 10.3 Reparos

- [ ] **Protocolo de reparação**
  - [ ] Erosão em valeta: revestimento com grama/concreto
  - [ ] Colapso de bueiro: substituição ou reforço
  - [ ] Entupimento: limpeza e investigação de causa raiz

---

## Assinatura de Aprovação

```
_________________________________     ____/____/______
Engenheiro Responsável               Data
CREA nº ___________


_________________________________     ____/____/______
Responsável Técnico do Projeto       Data


_________________________________     ____/____/______
Órgão Gestor / Concedente            Data
```

---

**Referência**: Tópico 1 — Fundamentos Hidrológicos / Manta Associados  
**Última revisão**: 2026-08-04  
**Próxima revisão**: 2027-08-04
