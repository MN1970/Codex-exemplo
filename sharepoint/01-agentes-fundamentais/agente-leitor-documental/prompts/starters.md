# prompts/starters.md — agente-leitor-documental

Prompts amostrais organizados por caso de uso. Servem como
conversation starters no chat do Maestro e como material de teste.

## 1. Classificação/organização de lote

- "Tenho uma pasta no SharePoint com PDF, DWG e Excel de um projeto de
  saneamento — organiza a leitura disso antes de eu pedir a análise
  técnica."
- "Chegaram 40 arquivos do edital novo, formatos misturados — separa
  por tipo antes de eu mandar pro agente certo."

## 2. Extração de um formato específico

- "Esse PDF é um edital ANEEL de transmissão — extrai os dados
  estruturados."
- "Essa planilha Excel tem os quantitativos de terraplenagem — estrutura
  em JSON pra eu cruzar com o orçamento."
- "Esse DWG é a planta de um cais — manda pro autodesk-toolkit e depois
  quantifica."

## 3. Pipeline ponta a ponta

- "Recebi PDF + DWG + XLSX de um mesmo projeto de aeroporto — quero o
  pacote inteiro lido, normalizado e entregue pro agente-aeroportos."
- "Esse .xer é o cronograma do contrato — converte e já manda pro
  manta-07."

## 4. Formato não coberto

- "Recebi um arquivo .rvt de um modelo Revit — quem processa isso?"
  (esperado: dispara `autodesk-toolkit`; se skill não cobrir o caso,
  registra em `doc:pending:*` e aciona `manta-16`.)

## 5. Handoff

- "Depois de extrair os dados desse memorial em Word, já manda pro
  agente-saneamento — é um projeto de ETE."
- "A planilha extraída é orçamento — passa pro manta-05 conferir os
  valores."
