# Padrão visual de relatórios — Manta Maestro

Ticket: **MNT-2026-REDESIGN-RELATORIOS**
Status: **proposto — aguardando gate humano MN**
Data: 2026-08-29

## Decisão

A partir deste documento, todo relatório gerado pelos agentes do Manta
Maestro segue o padrão híbrido **"MBB + Engenharia"**: a disciplina de
consultoria (McKinsey/BCG/Bain) combinada com o rigor de tabela/dado de
um relatório técnico de engenharia — sempre dentro das 6 regras
obrigatórias da skill `padrao-manta` (logo, cores, abas numeradas,
tabelas/quadros, rastreabilidade, marca d'água).

Template de referência: **`templates/relatorio-padrao-manta.html`**.

## Por que esse padrão (pesquisa, 2026-08-29)

**Consultoria (McKinsey/BCG/Bain):**
- Pyramid Principle — a conclusão vem primeiro; o detalhe vem depois
- Título de ação — o título da seção já é a conclusão, não o tema
  ("As 6 regras fecham os desvios do diagnóstico", não "Proposta")
- Uma mensagem por página/seção — nada de duas conclusões na mesma tela
- Rótulo direto no dado, legenda separada só quando não há alternativa
- Fontes e notas de rodapé sempre presentes

Fontes: [How McKinsey Consultants Make Presentations](https://slideworks.io/resources/how-mckinsey-consultants-make-presentations) ·
[Consulting Slide Standards — Deckary](https://deckary.com/blog/consulting-slide-standards) ·
[How McKinsey Creates Clear And Insightful Charts](https://www.theanalystacademy.com/mckinsey-report-breakdown/)

**Relatório técnico de engenharia:**
- Cabeçalho/subcabeçalho claros, alinhamento de coluna consistente por
  tipo de dado (texto à esquerda, número à direita/centro)
- Largura de coluna ajustada ao conteúdo — nunca deixada ao acaso
- Toda tabela/figura numerada e referenciada no texto
- Estilo uniforme de borda/fonte/cor entre todas as tabelas do documento

Fontes: [Working with Tables — ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/working-with-tables-effective-content-presentation/) ·
[Tables and Figures — Engineering Writing Center, USU](https://engineering.usu.edu/students/ewc/writing-resources/tables-figures)

## Regras concretas do padrão combinado

Aplicam-se **junto** às 6 regras obrigatórias do padrão Manta, nunca no
lugar delas:

1. **Título de seção = conclusão, não tópico.** Ex.: "Sem template fixo,
   o visual muda a cada relatório gerado", não "Diagnóstico".
2. **Mensagem principal no topo da primeira aba** — uma frase que resume
   a conclusão geral do documento inteiro (o "governing thought" do
   Pyramid Principle), antes do quadro de escopo e de qualquer tabela.
3. **Uma tabela/quadro por ideia** — não empilhar duas conclusões
   diferentes na mesma tabela.
4. **Toda tabela numerada** (`Tabela 1.1`, `2.3`...) e citada no texto que
   a antecede.
5. **Coluna com largura fixa** (`<colgroup>`) e alinhamento por tipo:
   texto à esquerda, número/percentual à direita ou centralizado.
6. **Gráfico, quando houver, com rótulo direto no dado** — evitar
   legenda separada sempre que o rótulo direto couber.
7. **Fontes e ficha técnica sempre na última aba**, numerada em
   sequência com as demais.

## Onde isso vive

| Peça | Caminho |
|---|---|
| Template de referência (produção) | `templates/relatorio-padrao-manta.html` |
| Diagnóstico + mockup comparativo | `docs/mockups/relatorio-diagnostico-manta-maestro.html` |
| Runbook de implementação | `docs/DIAGNOSTICO-DESIGN-RELATORIOS.md` |
| Logo (placeholder até chegar o oficial) | `assets/logo-manta-placeholder.svg`, `assets/README.md` |

## Gate humano

Este padrão fica **proposto** até aprovação MN. Depois de aprovado:
propagar `templates/relatorio-padrao-manta.html` para os demais agentes
do Maestro (ver checklist em `docs/DIAGNOSTICO-DESIGN-RELATORIOS.md`).
