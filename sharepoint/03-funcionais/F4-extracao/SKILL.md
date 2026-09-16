---
name: funcional-F4-extracao
codigo: F4
camada: L1.6
tipo: funcional
version: 3.0.0
updated: 2026-07-09
---

# F4 Extracao — Servico Transversal

Extracao de PDF/DWG/DXF/XLSX/DOCX/imagens em JSON estruturado. Primeira coisa a rodar em qualquer fluxo com input documental.

## Interface — 3 sub-modulos
- `F4.a.extract_inline(anexo)` -> anexo direto na mensagem do usuario
- `F4.b.fetch_reference(ponteiro)` -> resolve ponteiro (SharePoint path / URL / `portfolio://S{n}/PROJ-NNN`)
- `F4.c.navigate_portfolio(projeto)` -> navegacao completa em `01-segmentos/S{n}/portfolio/PROJ-NNN/`

Modo **hibrido**: combinacao dos tres para pedidos que citam multiplas fontes.

## Formatos suportados
- **PDF** — texto + tabelas + memoriais (via extratores)
- **DOCX/DOC** — texto + estrutura de titulos
- **XLSX/XLS** — abas + celulas + formulas (respeita R4 se do SharePoint Engenharia)
- **DWG/DXF** — geometria CAD, quantitativos via cad-quantifier
- **PPTX** — slides + texto + imagens
- **JPG/PNG/imagens** — visao computacional para plantas escaneadas, fotos de obra
- **Text/MD** — direto

## Output canonico
JSON estruturado por tipo:
```
{ tipo, path_origem, extraido_em, campos: {...}, texto_bruto, tabelas: [], anexos: [] }
```

## Chain com F7 Guardrails
Apos extracao, F7 aplica R1 sanitizacao imediatamente (nomes reais viram `[CONCESS.]`).

## Clients
Todo fluxo inicia por F4. Sem excecao para pedidos com anexos.

## Sub-skills L1 chamados
pdf, docx, xlsx, pptx, projeto-scanner-universal, cad-quantifier, projeto-rodovias-cad, ler-edital, ler-edital-aneel, evtea-extractor, evtea-quantifier.
