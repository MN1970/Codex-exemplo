---
name: atividade-A9-regulatorio
codigo: A9
camada: L1.7
tipo: atividade
version: 3.0.0
updated: 2026-07-09
origem: portado do SP-native 2026-07-31 para v6.1 taxonomia reconciliada
---

# A9 Assessoria regulatoria — Metodo

Racional metodologico para interface tecnica com orgaos reguladores e ambientais: peticoes administrativas, notas tecnicas ao regulador, defesa em processo sancionador, requerimentos de licenca, recursos administrativos, audiencias publicas, consultas normativas. Slot preenchido em 2026-07-09 (antes reservado, extracao migrou para F4).

Distincao vs A8: A8 produz parecer/laudo (produto tecnico-juridico interno ou para terceiros); A9 conduz o processo administrativo perante o regulador (protocolo, prazo, contraditorio, recurso). A8 opina, A9 protocola.

## Pipeline
```
intake        -> mapeia orgao competente, rito, prazo, autos
diagnose      -> le auto de infracao / oficio / edital de consulta
estrategia    -> define tese processual e linha argumentativa
tecnico       -> monta fundamentacao tecnica (chama disciplinas)
peca          -> redige peticao/nota/defesa/recurso no rito exigido
protocolo     -> checklist de anexos, procuracao, guias, GRU
follow-up     -> monitora andamento, prazos de manifestacao
publica       -> DOCX peca protocolavel + anexos + comprovante
```

## Proposta de output canonica
- Tipo: peca administrativa protocolavel
- Formato: DOCX no rito do orgao (ARTESP tem template proprio, ANTT outro, CETESB outro) + PDF assinado + anexos indexados
- Estrutura: 1. Enderecamento e qualificacao, 2. Sintese dos fatos, 3. Do direito / do rito, 4. Fundamentacao tecnica, 5. Pedido, 6. Rol de anexos, 7. Requerimentos de producao de prova.
- Paginas: 15-120 + anexos tecnicos volumosos
- Funcionais: F1 (Opus + judge), F4 (evidencia processual), F7 (R1-R5), F8, F2, F6.

## Rubrica auto-juiz L2
- Recomenda: tese principal + tese subsidiaria (se principal cair)
- Compara: precedentes do proprio orgao em casos analogos
- Antecipa: contra-manifestacao do regulador / fiscal
- Quantifica: valor da multa contestada, BRL @hoje, prazo de reducao (30% em 30d)
- Ponto cego: prazo processual perdido, competencia recursal, efeito suspensivo nao pedido

## Verificacao adversarial (default)
Sempre 2-3 verificadores paralelos: (a) tempestividade (prazo), (b) competencia e rito, (c) coerencia tecnica com evidencia primaria, (d) alinhamento com precedente do proprio regulador.

## Composicoes com disciplinas
A9.D13 licenciamento ambiental (CETESB/IBAMA), A9.D14 desapropriacao (defesa em processo expropriatorio), A9.D07 outorga hidrica (DAEE/ANA), A9.D12 interferencias (concessionarias), A9.D01 trafego (defesa em auto de fiscalizacao ARTESP/ANTT).

## Reguladores tipicos por segmento
- S1 rodovias: ARTESP, ANTT, DER, DNIT, PRF (auto de infracao operacional)
- S2 metro/S3 ferrovia: ANTT, STM, ANTAQ (multimodal), CPTM/Metro (contratante-fiscal)
- S4 OAE: DER, ARTESP (interdicoes)
- S5 imobiliario: Prefeituras, CETESB, GRAPROHAB, corpo de bombeiros
- S6 energia: ANEEL, IBAMA, orgaos estaduais de meio ambiente

## Sub-skills L1 chamadas
reg-intake, reg-tese, reg-peca (a criar), docx, pdf, artefato.

## Ver tambem
[[A6-contratual]] (fundamento contratual pode virar tese regulatoria), [[A8-advisory]] (parecer tecnico vira anexo de peca A9), [[A10-risco]] (risco regulatorio pre-materializado), [[D13-meio-ambiente]], [[D14-desapropriacao]].
