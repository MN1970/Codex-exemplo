# Extensão do registry aluci-guard — Portos (Manta 03-S6)

Fonte extraída: `sharepoint/01-agentes-fundamentais/agente-portos/SKILL.md`
(agente vertical de Portos, Manta 03-S6, v1.0.0, 2026-07-05).

## Compatível com schema atual (normas_abnt.py / leis_federais.py)

- **NBR 9782**
  - Descrição curta (conforme SKILL.md, seção V2/axes/01-normas.md): "ações portuárias"
  - Status: a confirmar (não verificado contra base oficial ABNT)
  - Entrada sugerida para `normas_abnt.py`:
    ```python
    {
        "codigo": "NBR 9782",
        "descricao": "Ações portuárias (citada em agente-portos como norma de ações em cais/estruturas marítimas)",
        "status": "a confirmar",
        "ano": None,  # não informado no SKILL.md
    }
    ```

- **NBR 6122**
  - Descrição curta: citada no SKILL.md junto de NBR 9782, na mesma linha de `axes/01-normas.md`, sem título explícito associado no texto (contexto geral: fundações — inferido apenas pelo agrupamento com o eixo de normas do agente-portos, já que o próprio agente cobre "fundações profundas em água" como disciplina D05)
  - Status: a confirmar (não verificado contra base oficial ABNT)
  - Entrada sugerida para `normas_abnt.py`:
    ```python
    {
        "codigo": "NBR 6122",
        "descricao": "Citada em agente-portos (eixo de normas), sem título explícito no SKILL.md; possível relação com fundações",
        "status": "a confirmar",
        "ano": None,  # não informado no SKILL.md
    }
    ```

Nenhuma **lei federal brasileira com número** foi encontrada explicitamente citada no SKILL.md do agente-portos (não há menção a "Lei nº ..." neste arquivo).

## Fora do schema atual (requer nova categoria de registry)

Todas as entradas abaixo requerem categoria nova (ex.: `normas_internacionais.py` ou `normas_setoriais.py`), pois não são normas ABNT nem leis federais brasileiras numeradas.

- **ANTAQ** — Agência Nacional de Transportes Aquaviários. Citada repetidamente: como fonte regulatória (V2 Inteligência Setorial, `axes/02-regulatorio.md`), fonte de dados RAG ("ANTAQ resoluções + editais de arrendamento (2018-2026)"), integração/handoff ("Cláusula de arrendamento ANTAQ" → `agente-contratual`), e regra de sanitização (R1: "ANTAQ pode ficar (regulador)"). Requer categoria de "resoluções normativas / regulador setorial".

- **PIANC** — organização internacional (reports/guidance). Citada como:
  - MarCom 121 (defensas)
  - MarCom 158 (dragagem)
  - MarCom 165 (canais)
  - "PIANC guidance" (eixo indicadores)
  - "publicações PIANC" (eixo academia)
  - "PIANC bulletin correto?" (checagem do aluci-guard) e "PIANC bulletin existe?" (regra 6)
  Requer categoria de "normas/relatórios técnicos internacionais".

- **ROM 0.2** — recomendação técnica (ações), citada em `axes/01-normas.md` e nas fontes RAG do Knowledge Engine. Requer categoria internacional/setorial.

- **ROM 2.0** — recomendação técnica (marítimo civil), mesma origem que ROM 0.2, também citada na regra 6 ("ROM está atualizado?"). Requer categoria internacional/setorial.

- **NORMAM** — Normas da Autoridade Marítima (Marinha do Brasil), citada em `axes/02-regulatorio.md` como "Marinha (NORMAM)". Requer categoria de norma regulatória setorial brasileira (não é ABNT nem lei federal numerada).

- **IBAMA** — órgão federal de licenciamento ambiental, citado em `axes/02-regulatorio.md` junto com ANTAQ e Marinha. Não há norma/lei numerada associada no texto — apenas o órgão. Requer categoria setorial/regulatória (ou tratamento como "órgão", não como norma).

- **SICRO adaptado** — citado em `axes/04-indicadores.md` como "SICRO adaptado + PIANC guidance". Já existe categoria `sicro.py` no registry, mas o SKILL.md não cita nenhum código SICRO específico — apenas a menção genérica "SICRO adaptado" (indicando adaptação, não um código do banco padrão). Não há código extraível para o schema `sicro.py` atual; mantido aqui apenas para registro da menção.

- **DHN** — Diretoria de Hidrografia e Navegação (Marinha do Brasil), citada em `por-doc-batimetria.md` como fonte de "carta náutica DHN". É uma fonte de dado/autoridade, não uma norma técnica numerada — mas foi incluída aqui por ser referência institucional citada no SKILL.md.

- **EIA/RIMA** — Estudo de Impacto Ambiental / Relatório de Impacto Ambiental, citado em `disciplines/D10-ambiental-costeiro.md` ("EIA/RIMA, disposição dragagem"). É um instrumento de licenciamento ambiental brasileiro, mas o SKILL.md não cita a lei/resolução CONAMA que o rege — não há número de norma/lei associável.

- **Manuais brasileiros CDP, EMAP, Codesa, Codeba** — citados nas "Fontes iniciais" do Knowledge Engine como fontes documentais (manuais de autoridades portuárias: Companhia Docas do Pará, Empresa Maranhense de Administração Portuária, Companhia Docas do Espírito Santo, Companhia Docas da Bahia). Não são normas técnicas com código/número — são nomes de instituições/manuais institucionais. Incluídos aqui apenas para registro; não recomendável tratar como "norma" em nenhuma categoria de registry sem mais detalhe (edição, ano, título do manual).

## Observações

- O SKILL.md não fornece ano de publicação para NBR 9782 nem para NBR 6122, nem título completo — a descrição acima é a única informação textual disponível no arquivo.
- Nenhuma lei federal brasileira numerada foi encontrada neste SKILL.md especificamente (diferente do CLAUDE.md master, que cita "Lei 14.026" para saneamento em outro contexto).
- Itens como ANTAQ e IBAMA são órgãos/reguladores, não "normas" no sentido estrito — foram listados na seção "fora do schema" porque o pedido da tarefa pede para capturar toda menção normativa/regulatória/técnica presente no SKILL.md, mas a categorização final de registry (se serão tratados como norma, como entidade reguladora, ou ignorados) é uma decisão de produto a ser tomada por quem define o schema de `normas_setoriais.py` / `normas_internacionais.py`.
- Nenhuma verificação de existência real ou vigência foi realizada — todas as entradas estão marcadas como "status a confirmar" e nenhuma consulta externa (ABNT, Planalto, PIANC, ANTAQ) foi feita, conforme escopo da tarefa.
- Todas as referências acima foram extraídas literalmente do texto do SKILL.md; nenhuma norma foi inferida ou adicionada além do que está escrito no arquivo.
