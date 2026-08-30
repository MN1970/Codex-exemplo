# Diagnóstico de design — Relatórios do Manta Maestro

Ticket: **MNT-2026-REDESIGN-RELATORIOS**
Data: 2026-08-29
ID do documento: `MANTA-REDESIGN-RELATORIOS-20260829-01`

Mockup interativo (antes/depois + causa raiz do logo):
`docs/mockups/relatorio-diagnostico-manta-maestro.html`

Padrão visual definido a partir deste diagnóstico ("MBB + Engenharia"):
`docs/PADRAO-VISUAL-RELATORIOS-MAESTRO.md`

Template de produção pronto para uso pelos agentes:
`templates/relatorio-padrao-manta.html`

---

## 1. Diagnóstico

Não existe, neste repositório nem em qualquer outro local acessível
(Google Drive, SharePoint) durante esta auditoria, um **template fixo de
relatório** nem um **arquivo real do logo Manta**. Cada relatório do
Maestro é gerado do zero a partir da descrição em texto da skill
`padrao-manta` — isso é a causa raiz de dois problemas relatados:

1. A casca visual (cards, badges, cores) varia de geração para geração,
   mesmo seguindo a mesma especificação.
2. O logo nunca sai idêntico entre relatórios: sem um arquivo de
   referência, o modelo desenha o monograma "M" de memória a cada vez.

Ver o mockup para a reconstrução lado a lado dos desvios mais comuns
(cards com sombra, gradiente fora da paleta, badges coloridos, ausência de
numeração/ficha técnica/marca d'água) contra o padrão Manta.

## 2. Proposta

- [x] Diagnóstico registrado (este documento + mockup)
- [x] Padrão visual combinado "MBB + Engenharia" definido — ver
      `docs/PADRAO-VISUAL-RELATORIOS-MAESTRO.md`
- [x] Template único de relatório (HTML/CSS) consolidado, com as 6 regras
      obrigatórias do padrão Manta + o padrão MBB + Engenharia já
      aplicados — `templates/relatorio-padrao-manta.html`. Os agentes
      passam a *preencher* os tokens `{{ASSIM}}` desse template, não
      recriá-lo a cada chamada
- [ ] Obter o arquivo oficial do logo (SVG de preferência) — ver
      `assets/README.md`
- [ ] Commitar o logo real em `assets/logo-manta.svg` (ou `.png`)
- [ ] Gerar o base64 a partir do arquivo real e embutir no template
- [ ] Atualizar a skill `padrao-manta` para referenciar o asset real e
      remover o fallback "desenhar SVG inline"
- [ ] Migrar 1 relatório piloto usando `templates/relatorio-padrao-manta.html`
      e validar com o time
- [x] Propagar a referência ao template para os 5 agentes verticais deste
      repositório (`.claude/agents/agente-{portos,aeroportos,saneamento,
      energia,barragens}.md` — seção "Formato de saída (relatórios)")
- [ ] Propagar para os demais ~15 agentes (Manta 00-02, 04-07, 13-16,
      S1-S4) — vivem no repositório operacional do Maestro (`manta-hub` ou
      equivalente), não acessível nesta sessão. Precisa de `add_repo` com
      o nome real do repositório, ou aplicação manual pelo time
- [ ] Gate humano: aprovação MN antes de propagar

## 3. Fontes

- Skill `padrao-manta` v2 (regras obrigatórias, paleta, tipografia)
- Varredura do repositório `mn1970/codex-exemplo`, do Google Drive e do
  SharePoint da Manta em 2026-08-29 — nenhum template de relatório ou
  arquivo de logo encontrado
