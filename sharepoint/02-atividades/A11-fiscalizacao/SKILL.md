---
name: atividade-A11-fiscalizacao
codigo: A11
camada: L1.7
tipo: atividade
version: 1.0.0
updated: 2026-07-31
origem: portado do SP-native 2026-07-31 (SP-A11-fiscalizacao/SKILL.md v1.0.0 do 2026-07-27, com corpo A8 legado — renomeado consistentemente para A11 nesta porta).
---

# A11 Fiscalizacao e Supervisao de Obras — Metodo

Atividade transversal (celula `*.A11.*` — S1-S14). Alta recorrencia operacional: rotina diaria/semanal de campo, nao um estudo pontual. Inspecao de rotina, medicao mensal, vistoria de etapa, auditoria tecnica; checklists por disciplina; NC leve/grave/critica; RDO e Relatorio de Medicao; integracao com A5 (cronograma) e A7 (claims).

## Sua funcao

1. Identificar o tipo de inspecao solicitado (rotina diaria, medicao mensal, vistoria de etapa, auditoria tecnica) e a disciplina envolvida
2. Levantar os dados de campo disponiveis; se algum dado essencial nao foi fornecido, registrar como `null` com o motivo (R2) — nunca estimar valor de campo nao medido
3. Aplicar checklist da disciplina correspondente, comparando valor medido vs criterio de aceitacao normativo/de projeto
4. Classificar toda nao-conformidade em NC leve, grave ou critica usando criterios objetivos
5. Gerar RDO (Relatorio Diario de Obra) estruturado
6. Quando o pedido for de medicao, gerar Relatorio de Medicao com quantitativo executado vs planejado
7. Alimentar integracao com A5 (avanco fisico) e A7 (evidencias para pleito)
8. Aplicar R1-R5 e submeter output ao F7 antes de entregar
9. Sinalizar normas nao cadastradas na KB (nao afirmar como fundamentacao formal ate a KB ser atualizada)

## 1. Tipos de inspecao

| Tipo | Periodicidade | Escopo | Output principal |
|---|---|---|---|
| Rotina diaria | Diaria | Efetivo, equipamentos, clima, servicos, ocorrencias | RDO |
| Medicao mensal | Mensal (ou ciclo contratual) | Quantitativo executado acumulado vs planejado, % avanco fisico | Relatorio de Medicao |
| Vistoria de etapa | Por marco/gate | Verificacao formal antes de liberar etapa seguinte | Termo de liberacao + NC pendente |
| Auditoria tecnica | Eventual | Revisao aprofundada de conformidade e rastreabilidade | Relatorio de auditoria com achados |

## 2. Checklist por disciplina

Para cada item: valor medido, criterio de aceitacao, e classificacao automatica de NC.

### 2.1 Concreto
- Slump (cone de Abrams): dentro da faixa especificada em projeto/traco. NC leve se desvio ≤ tolerancia +30%; NC grave se acima.
- Moldagem CPs: conjunto minimo coletado e identificado por betonada. Ausencia = NC grave.
- Cura: metodo e tempo aplicado conforme plano de qualidade. Interrupcao antes do prazo = NC leve ou grave.
- Resistencia a compressao: fc_medido ≥ fck de projeto. Abaixo = NC critica se peca carregada.

### 2.2 Terraplenagem
- Grau de compactacao (GC%): (γd,campo / γd,max,Proctor) × 100. Conforme especificacao de projeto.
- Umidade de compactacao: dentro da faixa vs umidade otima do Proctor. Fora = NC leve.
- Espessura de camada: controle topografico. Alem do limite sem verificacao = NC grave.
- CBR: CBR_medido ≥ CBR_projeto. Abaixo = NC grave a critica.

### 2.3 Pavimentacao
- Espessura de camada: sondagem/testemunho/georadar. Deficit sistematico = NC grave.
- Textura superficial (macrotextura): mancha de areia HS. Fora da faixa = NC leve a grave.
- IRI: perfilometria. Acima do limite = NC grave a critica.
- Compactacao asfaltica: Gmb/Gmm em testemunho. Abaixo do minimo = NC grave.

### 2.4 Estrutural
- Flechas: medicao topografica. Acima do limite de projeto = NC grave; com fissuracao progressiva = NC critica.
- Fissuras: fissurometro wk. Acima do limite estavel = NC grave; progressiva = NC critica.
- Alinhamento/verticalidade: prumo/nivel/estacao total. Fora da tolerancia sem comprometer estabilidade = NC grave.

Nota R2: os limites numericos sao especificos do projeto executivo e contrato. Se nao informado, registrar `criterio_projeto: null` com o motivo.

## 3. Classificacao de nao-conformidade (NC)

| Classificacao | Criterio | Acao | Prazo |
|---|---|---|---|
| NC leve | Desvio recuperavel em rotina, sem risco a seguranca ou durabilidade | Registro no RDO + verificacao seguinte | Ate 5 dias uteis |
| NC grave | Excede tolerancia, compromete durabilidade/desempenho, sem risco imediato | RNC formal + paralisacao do subitem + comunicar A7 se potencial claim | Ate 15 dias corridos |
| NC critica | Risco iminente a seguranca, colapso potencial, ou violacao de NR de seguranca do trabalho | Embargo imediato + SESMT em 2h + TRACE obrigatorio | Sem prazo — retomada apos verificacao formal |

Fluxo: toda NC grave ou critica registrada com evidencia fotografica; valor economico associado aplica R5 (BRL + data + TRACE); avaliar A7 se configura pleito.

## 4. Relatorio Diario de Obra (RDO)

Estrutura minima (schema completo em `manta-tools/schemas/rdo-schema.json`):

- Cabecalho: data, celula S.A.D, obra/trecho (sanitizado R1), fiscal (iniciais R1)
- Clima: condicao por turno, precipitacao, paralisacao
- Efetivo: por funcao/categoria, empresa executora sanitizada R1
- Equipamentos: tipo, quantidade, horas trabalhadas/paradas + motivo
- Servicos executados: disciplina, descricao, localizacao, quantidade, unidade
- Ocorrencias: descricao, disciplina, classificacao NC, evidencia fotografica (referencia)
- Assinatura: fiscal (iniciais) + data/hora fechamento

Gerar sempre em JSON antes da prosa — prosa e derivada do JSON.

## 5. Relatorio de Medicao

Estrutura minima:

- Cabecalho: periodo, celula S.A.D, obra/trecho (sanitizado), contrato/item
- Itens de medicao: codigo (SICRO/SINAPI/contrato), descricao, unidade, qty planejada, qty executada no periodo, qty acumulada, % avanco fisico
- Calculo:
  ```
  % avanco fisico (item) = qty executada acumulada / qty planejada total × 100
  % avanco fisico (obra) = Σ (peso do item no orcamento × % avanco do item)
  ```
- Valores: BRL sempre com data de referencia + TRACE (R5)
- Evidencia fotografica: array de referencias por item
- Comparacao planejado vs executado: sinalizar desvio por item e disciplina
- Aprovacao: fiscal + data

R4: se fonte de quantitativo estiver apenas em `.xlsx`, buscar `.pdf`/`.docx` equivalente antes de citar como fonte definitiva.

## 6. Integracao com A5 e A7

- **Com A5 (cronograma)**: % avanco fisico medido e input para atualizar earned value; SPI/CPI recalculados; toda NC grave/critica com impacto de prazo reportada a A5 com dias de atraso + atividade/WBS afetada.
- **Com A7 (claims)**: RDOs e medicoes sao evidencia primaria de campo para pleitos (clima, interferencia, retrabalho por NC nao atribuivel). Sinalizar `potencial_claim: true` com referencia cruzada (data, item, disciplina, evidencia).

## 7. Celulas S.A.D e observacao R2

- Celulas: `*.A11.*` transversal a todos os S (S1-S14) e D (D01-D23); celula completa e.g. `S1.A11.D06` (fiscalizacao de pavimentacao em rodovia), `S6.A11.D08` (fiscalizacao estrutural em edificacao).
- Normas tecnicas citadas nos checklists refletem pratica de mercado consolidada. Antes de citar como fundamentacao formal em laudo/RNC/claim, confirmar existencia em `manta-kb/referencias-engenharia.json`; se nao constar, tratar como lacuna R2.

## Regras invioaveis (L4 Kernel)

- R1: sanitizacao (empresa → `[CONCESS.]`; pessoas → iniciais)
- R2: nao inventar (criterio nao informado = `null` + motivo)
- R3: alertas NC critica via Twilio, nao WhatsApp pessoal
- R4: xlsx → buscar `.pdf`/`.docx` equivalente antes de tratar como fonte
- R5: BRL sempre com data-base + TRACE

## Metadados

```
Skill        : fiscalizacao-obras
Codigo       : A11-FISCALIZACAO
Eixo         : A11 (Atividade — Fiscalizacao/Supervisao, transversal S1-S14)
Versao       : 1.0.0
Schemas      : manta-tools/schemas/rdo-schema.json ; manta-tools/schemas/medicao-schema.json
Atualizado   : 2026-07-31
Origem       : portado do SP-native SKILL.md v1.0.0 (2026-07-27, corpo A8 legado renomeado para A11)
```
