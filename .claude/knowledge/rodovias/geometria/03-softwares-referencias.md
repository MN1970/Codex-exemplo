# Geometria de Rodovias — Softwares, Ferramentas & Referências Técnicas

**Versão**: 1.0  
**Data**: 2026-08-03  
**Agente**: Manta 03-S1 (agente-infraestrutura)  
**Prefixo RAG**: `rod:geom:tools`

---

## 1. Softwares Padrão Manta Associados

### 1.1 MX Road (Bentley)

**Status**: ✅ Padrão ouro para geometria rodoviária  
**Versão**: 2024 (última)  
**Licença**: Enterprise (Manta)

#### Funcionalidades Principais

| Função | Descrição | Output |
|--------|-----------|--------|
| **Horizontal Design** | Alinhamento H com espirais | DWG + XML |
| **Vertical Design** | Perfil vertical (rampas/parábolas) | DWG + relatório |
| **Superelevation** | Cálculo automático de inclinação transversal | Seção transversal |
| **Cross Section** | Seção transversal tipo + variações | DWG + quantitativos |
| **Corridor Modeling** | Superfície de projeto 3D | Surface file |
| **Volume Calculation** | Terraplenagem (corte/aterro) | Relatório PDF |
| **Reports** | Memoriais técnicos formatados | Documento DNIT |

#### Workflow Típico

```
1. Importar topografia
   └─ Entrada: levantamento topográfico (nuvem de pontos ou raster)
   
2. Criar alinhamento horizontal
   └─ Entrada: tangentes + raios
   └─ Saída: estacas, coordenadas, ângulos
   
3. Criar perfil vertical
   └─ Entrada: rampas + raios de parábola
   └─ Saída: cotas, comprimentos, inclinações
   
4. Definir seção transversal padrão
   └─ Entrada: largura faixa, acostamento, taludes
   └─ Saída: template reutilizável
   
5. Gerar corridors (modelo 3D)
   └─ Cálculo automático de volume de corte/aterro
   └─ Exporta superfície de projeto
   
6. Extrair quantitativos
   └─ Pavimento, terraplenagem, drenagem
   └─ Integra com SICRO para orçamentação
   
7. Exportar documentação
   └─ DWG (plantas, perfis, seções)
   └─ PDF (memoriais, tabelas)
```

#### Comandos Essenciais

```
Horizontal:
- Horizontal > New Project > Import Alignment
- Spiral Design (Clotóide automática)
- Curvature Diagram (verifica R_mín)

Vertical:
- Vertical > Create Profile
- Parabolic Curve (automática conforme DNIT)
- Grade Review (verifica d_parada, visibilidade)

Section:
- Template > Create Standard Section
- Material Estimation
- Volume Report

Export:
- Export > Corridor Surface (*.dwg)
- Generate Report (DNIT-formatted)
```

#### Exemplo de Saída

```
RELATÓRIO DE GEOMETRIA — MX Road
================================

Alinhamento Horizontal:
- PC: Est. 0+000, Cota 450.00m
- TC: Est. 0+110, Cota 451.54m
- CT: Est. 0+380, Cota 457.32m
- PT: Est. 0+490, Cota 459.18m

Curva Circular:
- Raio: 350 m
- Ângulo Central: 42°30'
- Comprimento: 259 m
- Superelevação: 7.5%
- Clotóide A: 196.2 m

Perfil Vertical:
- Rampa 1: +5.0% (Est. 0-200)
- Curva Vertical: Parábola 140m (Est. 200-340)
- Rampa 2: -4.0% (Est. 340-500)

Seção Transversal:
- Faixa: 3.60m × 2 = 7.20m
- Acostamento: 2.50m × 2 = 5.00m
- Taludes: 1:1.5 (corte), 1:2 (aterro)

Volumes (1 km):
- Corte: 145,000 m³
- Aterro: 95,000 m³
- Empréstimo: 15,000 m³
```

---

### 1.2 AutoCAD Civil 3D (Autodesk)

**Status**: ✅ Alternativa/complemento ao MX Road  
**Versão**: 2024  
**Licença**: Educacional/Comercial

#### Funcionalidades Principais

```
Alignment:
- Desenho de alinhamento H em 2D
- Conversão automática para parâmetros (raio, ângulo, tangente)

Profile:
- Perfil vertical (seções transversais do levantamento)
- Curvas de projeto (parábolas/linhas)
- Grade Elevation (cotas de projeto)

Corridor:
- Superfícies de projeto 3D
- Associativa: altera alinhamento → atualiza volume automaticamente

Volume Calculation:
- Análise de seções (corte/aterro)
- Relatório de movimento de terra

Drawing Tools:
- Profile View (seção longitudinal completa)
- Sections (seção transversal em qualquer estaca)
```

#### Workflow

```
Civil 3D Workflow:

1. Importar topografia
   [Dwg/LandXML] → Insert Surface
   
2. Criar alinhamento
   Ribbon: Home > Create Design > Alignment
   Define: tangentes > radii > curves
   
3. Criar perfil (Grade)
   Profile > New Profile View
   Profile > Create by Layout
   (Digitar cotas e rampas manualmente ou importar)
   
4. Criar seção padrão (Assembly)
   Corridor > Create Corridor
   Define Assembly (subassemblies: faixa, acostamento, talude)
   
5. Gerar superfícies
   Corridor > Corridor Surface
   (Automático: seções × alinhamento)
   
6. Extrair volumes
   Sample > Sample from Surface
   Compute Cut/Fill
   Generate Volume Report
```

#### Vantagens vs MX Road

| Aspecto | MX Road | Civil 3D |
|--------|---------|---------|
| Especificidade rodovia | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Integração AutoCAD | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Curva de aprendizado | ⭐⭐ | ⭐⭐⭐ |
| Saída DNIT nativa | ✅ | Parcial |
| Custo | Alto | Médio |

---

## 2. Softwares de Orçamento

### 2.1 SICRO DNIT (Sistema Integrado de Custos de Obras)

**Acesso**: https://sicro.dnit.gov.br  
**Atualização**: Mensal (com defasagem ~1 mês)

#### Estrutura de Codificação

```
Código SICRO: XX.YY.ZZ

Exemplo: 01.05.02

01 = Classe
   01 → Mobilização e Desmobilização
   02 → Serviços Geotécnicos
   03 → Movimento de Terra
   04 → Drenagem
   05 → Pavimentação
   06 → Ponte/OAE

05 = Subclasse (Pavimentação)
   02 → Base Granular

ZZ = Item Específico

Exemplo Real:
05.02.01 = Base Granular 15cm (m²) → R$ 35.00/m²
```

#### Composições Típicas Rodovia

```
COMPOSIÇÃO SICRO — Pavimento CBUQ 5cm

Insumos:
- Concreto Betuminoso 5cm: 0.6 t → R$ 950/t = R$ 570.00
- Equipamento (Vibroacabadora): 0.25 h → R$ 200/h = R$ 50.00
- Mão de obra (Operador): 0.25 h → R$ 45/h = R$ 11.25
- Combustível: 5 L → R$ 6/L = R$ 30.00

Total: R$ 661.25/m² (sem margem)

Com margem de 15%: R$ 761.00/m²
```

#### Acesso Programático

```python
# Script para integração SICRO
import requests

def obter_preco_sicro(codigo):
    """Busca preço unitário SICRO"""
    url = f"https://sicro.dnit.gov.br/api/item/{codigo}"
    resp = requests.get(url)
    return resp.json()['preco']

# Cálculo de orçamento
pavimento_m2 = 7200
preco_cbuq_5cm = obter_preco_sicro("05.02.03")  # CBUQ 5cm
custo_total = pavimento_m2 * preco_cbuq_5cm

print(f"Pavimento: {pavimento_m2}m² × R${preco_cbuq_5cm:.2f}/m² = R${custo_total:,.2f}")
```

---

## 3. Softwares de Topografia

### 3.1 Drone Mapping + Processamento

```
Fluxo:
1. Captura DJI Phantom/M300 (voo 50m, sobreposição 80%)
2. Processamento:
   - Pix4Dmapper ou Metashape → nuvem de pontos
   - Densidade: 1 ponto/10cm²
3. Geração:
   - Ortofoto (georeferenciada)
   - MDE (Modelo Digital de Elevação)
   - Nuvem de pontos XYZ
4. Exportação para Civil 3D/MX Road:
   - DEM raster (.tif georeferenciado)
   - Point cloud (.las/.laz)
```

### 3.2 Google Earth Pro + Fusion

```
Levantamento inicial (sem drone):
1. Google Earth Pro > Ferramentas > Régua
2. Medir distâncias / áreas
3. Ver curvas de nível (SRTM 30m)
4. Exportar caminho (.kml)

Limitações:
- Resolução altimétrica: 30m (insuficiente para projeto)
- Uso: reconhecimento inicial apenas
```

---

## 4. Softwares CAD & Design

### 4.1 AutoCAD + Plugins Rodovia

```
Plugins úteis:
- Infraworks (análise 3D terrain)
- Revit (BIM, coordenação)
- Plant 3D (layout de canteiro)

Fluxo CAD:
1. Importar topografia (DEM raster como base)
2. Desenhar alinhamento horizontal (polyline)
3. Anotação: raios, ângulos, tangentes
4. Seções transversais (blocos dinâmicos)
5. Exportar para MX Road/Civil 3D
```

---

## 5. Softwares de Simulação & Análise

### 5.1 Simulação de Tráfego

```
PTV Vissim / Microsimulation:
- Modelar comportamento de veículos
- Testar capacidade em curvas
- Distância de visibilidade interativa
```

### 5.2 Análise de Acidentes

```
Analítica de Risco (Curvatura × Velocidade):
- Correlacionar R_atual com d_parada teórica
- Identificar pontos críticos
- Recomendações de redução de velocidade
```

---

## 6. Referências Técnicas Canônicas

### 6.1 Normas DNIT Essenciais

| Norma | Título | Arquivo |
|-------|--------|--------|
| **ES 101/97** | Projeto Geométrico — Elementos de Rodovia | [DNIT ES 101/97.pdf] |
| **ES 131/86** | Projeto de Drenagem de Rodovias | [DNIT ES 131/86.pdf] |
| **IPR 702/97** | Avaliação Funcional de Pavimentos | [DNIT IPR 702.pdf] |
| **IPR 726/94** | Visibilidade em Curvas Horizontais | [DNIT IPR 726.pdf] |

### 6.2 NBR Relevantes

| NBR | Título |
|-----|--------|
| **NBR 6123** | Forças Devidas ao Vento em Edificações (OAE) |
| **NBR 7187** | Projeto de Pontes de Concreto (interfaces) |
| **NBR 15895** | Sinalização Horizontal de Trânsito |
| **NBR 14644** | Balizamento de Pistas |

### 6.3 Guias ABNT & ICCC

```
- ABNT EB-1046: Projeto de Drenagem
- ICCC (Instituto Cent. Conc.): Manutenção
- EPE (Empresa Pesq. Energética): Classificação Estradas
```

---

## 7. Templates & Checklists

### 7.1 Template de Projeto Geométrico (MX Road)

```
Estrutura de Projeto:

projeto_br116_sp_mg/
├── 01_topografia/
│   ├── levantamento.dwg
│   └── mde_drone.tif
├── 02_geometria/
│   ├── alinhamento_h.xml
│   ├── perfil_v.xml
│   └── secoes.dwg
├── 03_memoriais/
│   ├── memorial_descritivo.docx
│   ├── memorial_geometrico.pdf
│   └── tabelas_estacas.xlsx
├── 04_quantitativos/
│   ├── terraplenagem.xlsx
│   ├── sicro_budget.xlsx
│   └── cronograma_obra.mpp
└── 05_desenhosfinais/
    ├── planta_geral.dwg
    ├── perfil_longitudinal.dwg
    ├── secoes_transversais.dwg
    └── detalhe_superelevacao.dwg
```

### 7.2 Checklist Geométrico Final

```
VALIDAÇÃO GEOMÉTRICA

□ Velocidade de projeto (Vd) definida e documentada
□ Classe de rodovia conforme DNIT
□ Raio mínimo (R_mín) ≥ calculado para todas as curvas
□ Superelevação máxima ≤ 8% (ou 10% em montanha)
□ Comprimento de clotóide ≥ L_mín
□ Tangentes: L_mín ≤ L ≤ L_máx
□ Distância de visibilidade de parada verificada
□ Curvas verticais em parábola (não linear)
□ Declividade mínima 0.5% (drenagem)
□ Rampa máxima dentro do permitido
□ Seção transversal dimensionada
□ Inclinação de taludes por geotecnia
□ Memoriais em conformidade DNIT ES 101/97
□ Desenhos técnicos (DWG + PDF)
□ Quantitativos SICRO ligados a orçamento
□ Aprovação de PM (Project Manager)

Data: _____  Responsável: _________________
```

---

## 8. Integração com Agente-infraestrutura S1

### 8.1 Intake Automático (Questões do Agente)

Quando usuário menciona "geometria de rodovia", o agente faz:

```
Q1. Velocidade de projeto? (40-120 km/h)
Q2. Classe? (BR, BR-e, estadual, municipal)
Q3. Topografia? (plana, ondulada, montanhosa)
Q4. Dados disponíveis?
    □ Levantamento topográfico (DWG/LAS)
    □ Só reconhecimento (Google Earth)
    □ Nenhum (precisa levantar)
Q5. Objetivo?
    □ Projeto (novo traçado)
    □ Reabilitação (ajustes de alinhamento)
    □ Análise de risco
    □ Orçamento SICRO
```

### 8.2 Outputs Padrão

```
1. Relatório Geométrico
   - Alinhamento H (raios, tangentes, estacas)
   - Perfil V (rampas, parábolas, cotas)
   - Seção transversal tipo
   - Visibilidade verificada

2. Desenhos Técnicos (DWG/PDF)
   - Planta (escala 1:2000)
   - Perfil (escala 1:200/1:2000)
   - Seções (a cada 100m)

3. Quantitativos
   - Terraplenagem (m³)
   - Pavimento (m²)
   - Acostamento (m²)

4. Orçamento SICRO
   - Integrado com tabelas atualizadas
   - Margem de erro ±10%
```

---

## 9. Referências Externas (URLs Confiáveis)

```
DNIT:
- https://www.dnit.gov.br/
- SICRO: https://sicro.dnit.gov.br
- Manuais: /normas-e-documentacoes

Autodesk:
- Civil 3D Help: https://help.autodesk.com/view/civil3d/
- University Network: https://www.autodesk.com/education/

Bentley (MX Road):
- https://www.bentley.com/en/products/brands/mxroad
- Documentation: /help/mxroad
```

---

## 10. Glossário Rápido

| Termo | Definição | Sigla |
|-------|-----------|-------|
| Alinhamento | Traço/rota da rodovia (H e V) | — |
| Clotóide | Curva de transição (espiral) | — |
| Superelevação | Inclinação transversal em curva | e |
| Raio mínimo | Menor raio permitido para Vd | R_mín |
| Velocidade de projeto | Velocidade teórica de dimensionamento | Vd |
| Visibilidade | Distância visual mínima segura | d |
| Talude | Inclinação de corte/aterro | 1:m |
| Estaca | Ponto a cada 20m ao longo do eixo | Est. |
| Defensa | Barreira de proteção lateral | — |
| CBUQ | Concreto Betuminoso Usinado Quente | — |
| BGS | Brita Graduada Simples | — |
| SICRO | Sistema de Custos DNIT | — |

