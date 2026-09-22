---
name: template-prt-rodovias
celula: S1.A1
tipo: template de atividade
version: 1.0.1
created: 2026-07-09
fontes: [EX-001, EX-002, EX-003]
corpus: manta_propostas_index.json v2.0 (8 propostas Tipo B catalogadas)
mantenedor: Manta 11 (A1) + Manta 99
---

# Template — Proposta Técnica Rodoviária (Tipo B)

Template canônico para elaboração de propostas técnicas em que a Manta é **autora em nome do cliente** (Tipo B), no segmento rodovias (S1) e adjacências (S2 OAE). Sintetizado a partir de 3 exemplares reais entregues (2023–2026), estruturas completas em `06-exemplares/S1.A1/`.

## 1. Variantes reconhecidas

| Variante | Natureza | Exemplar | Estrutura externa |
|---|---|---|---|
| **B1 — Obra** | Proposta de execução de obra para concorrência de concessionária (empreitada) | EX-001 (duplicação ~9 km), EX-003 (adequação de 6 OAEs) | Livre (EX-001) ou **imposta pelo edital** (EX-003: OIR→PIR→RIR→EIR / ISO 19650) |
| **B2 — Concessão/CAPEX** | Estudo técnico de obras, riscos e CAPEX para licitação de concessão (ARTESP/ANTT) | EX-002 (lote ~90 km, concorrência internacional) | Livre, orientada a análise (entendimento → plano de ataque → premissas de orçamento → parametrização → riscos) |

**PASSO 0 obrigatório (antes de qualquer redação):** extrair do edital/carta-convite a estrutura de resposta exigida. Se houver taxonomia imposta (TR, OIR/PIR/RIR/EIR, IAP, anexos numerados), ela comanda o esqueleto externo e os blocos abaixo são **mapeados** para dentro dela — nunca ignorados.

## 2. Blocos canônicos de conteúdo

Os 3 exemplares usam os mesmos blocos, em pesos semelhantes. O bloco 4 é sempre o núcleo (37–45% do documento).

| # | Bloco | Conteúdo mínimo | Elementos gráficos típicos | Peso típico |
|---|---|---|---|---|
| 1 | **Carta de apresentação** | Encaminhamento formal, declaração de visita ao local e conhecimento das condições, referência ao certame | — | 1-2 pág. |
| 2 | **Apresentação da empresa / equipe** | Portfólio, experiências análogas (obras semelhantes), organograma do proponente | Fotos de obras, organograma | 5-8% |
| 3 | **Entendimento do escopo** | Localização e trechos (km a km), objeto, detalhamento por segmento, premissas geométricas, documentos do edital, sobreposições com concessões existentes, condições precedentes, quantitativos macro | Mapas, tabelas de datas-marco, tabelas de quantitativos | 10-25% |
| 4 | **Plano de Ataque** ★núcleo | Premissas do planejamento estratégico; frentes de trabalho com lógica executiva (descrição → desafios → serviços/quantitativos → mitigações); diagrama Tempo×Caminho e/ou retigráficos; cronograma (MS Project nível 3+, inline ou anexo); praticabilidade (Köppen, pluviometria, calendário, turnos, fatores de retomada); histogramas de equipamentos e mão de obra; mobilização/desmobilização; canteiro (layout); desvios de tráfego por etapa (projetos-tipo); desapropriações; interferências; logística de materiais e subcontratados | Tempo×Caminho, retigráficos, Gantt, histogramas, layout de canteiro, projetos-tipo de desvio | **37-45%** |
| 5 | **Metodologia executiva** | Por serviço (terraplenagem, drenagem, pavimentação, contenções, OAE, sinalização...) ou por estrutura (OAE a OAE): passo a passo executivo, seções-tipo, controle tecnológico e ensaios | Seções-tipo, plantas, cortes, fotos de situação | 10-20% |
| 6 | **Gestão QSMS** | Planos de Qualidade (SGQ/ISO 9001, PIT, databook/as-built), Ambiental (ISO 14001, controles operacionais), Segurança (procedimentos por risco) e Saúde. Boilerplate corporativo do proponente **adaptado à obra** — reaproveitável entre propostas do mesmo cliente | Organograma da obra, matrizes de responsabilidade | 15-45% (B1); ausente ou mínimo em B2 |
| 7 | **Equipe do contrato** | Organograma nominal, mini-CVs da liderança, dimensionamento, matriz RACI, subcontratadas | Organograma, tabela RACI | 3-8% |
| 8 | **Riscos e qualificações comerciais** | Matriz de riscos (P×I ou identificação); hipóteses/premissas assumidas (condições impostas à contratante); exclusões de escopo; regime de preço e ressalvas (ex.: itens por preço unitário); eventos de desequilíbrio (B2); análise de maturidade FEL da informação do edital (B2) | Matriz de risco, tabelas de premissas | 3-10% |
| 9 | **Formais e anexos** | Atestado de visita, termo de encerramento, anexos: cronograma MSP, currículos, curva S/eventograma, planilhas | — | conforme edital |

## 3. Mapeamento blocos → variantes

- **B1 estrutura livre (EX-001):** Carta → 2 → 3 → 4 → 5 (dentro do 4) → 6 (Q/A/S/S como capítulos próprios) → 8 ("Considerações Finais") → 9.
- **B1 estrutura imposta (EX-003):** OIR recebe blocos 2+6(qualidade)+critérios de medição; PIR recebe 3+4+5+7; RIR recebe normas/aprovações; EIR recebe EAP/entregáveis/fluxos de informação; Conclusão recebe síntese + visita. Blocos 8 distribuídos como "premissas/hipóteses" e "itens fora do escopo".
- **B2 (EX-002):** 2 → 3 (expandido: edital+contrato+anexos, POI, sequenciamento, riscos contratuais) → 4 → 5 (por tipologia de serviço) → premissas de orçamento (FEL, classes de estimativa, matriz de responsabilidades) → parametrização por estrutura → alternativas → 10 riscos → anexos. QSMS ausente.

## 4. Checklist de completude (usar antes do DELIVER)

- [ ] Estrutura externa confere com a exigida pelo edital (PASSO 0)
- [ ] Plano de ataque tem: frentes + Tempo×Caminho/retigráfico + cronograma + praticabilidade + histogramas
- [ ] Metodologia executiva cobre TODOS os serviços/estruturas do escopo, com controle tecnológico
- [ ] Quantitativos citados são rastreáveis à fonte (edital, POI, CAD) — R2: lacuna vira `null`+motivo, não chute
- [ ] Premissas/hipóteses e exclusões de escopo explicitadas (proteção comercial)
- [ ] Matriz de riscos presente
- [ ] Equipe: organograma + RACI + CVs (ou anexo)
- [ ] Elementos formais: carta, atestado de visita, termo de encerramento
- [ ] **Lacunas recorrentes do corpus a superar:** curva S inline (ausente em 3/3 exemplares — incluir quando o edital pontuar), EAP formal (rara), quantitativos consolidados em tabela única

## 5. Regras invioáveis aplicáveis

- **R1** — em exemplares e materiais de treino: empresas → `[CONCESS.]`/`[CONSTRUTORA]`, pessoas → iniciais. Na proposta real entregue, obviamente, nomes verdadeiros.
- **R2** — quantitativo sem fonte = `null` + motivo + pergunta ao usuário. Nunca inventar produtividade, prazo ou quantidade.
- **R4** — planilhas de apoio: buscar PDF/DOCX equivalente antes de xlsx da biblioteca Engenharia.
- **R5** — valores em BRL @hoje com INCC-DI registrado; TRACE desde o INTAKE.

## 6. Ciclo de atualização (loop L2→L3)

1. Nova proposta Tipo B entregue → depositar no projeto (`02_CLIENTE/{cliente}/{projeto}/03_DOC_ELA/03_ENTREGA/`).
2. Registrar no `manta_propostas_index.json` (`06-exemplares/_indices/`; até 2026-09-22 vivia em `03-exemplares/bd/`) com `celula_sad` e `status_catalogacao`.
3. Se nota auto-juiz >= 4 **e** triagem humana = 'exemplar' → gerar `EX-NNN.md` sanitizado (R1) em `06-exemplares/S1.A1/`.
4. Revisar este template quando um exemplar novo contradisser os blocos canônicos (mantenedor: Manta 99).
