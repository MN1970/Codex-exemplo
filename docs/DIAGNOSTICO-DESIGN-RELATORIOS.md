# Diagnóstico de design — Relatórios do Manta Maestro

Ticket: **MNT-2026-REDESIGN-RELATORIOS**
Data: 2026-08-29
ID do documento: `MANTA-REDESIGN-RELATORIOS-20260829-01`

Mockup interativo (antes/depois + causa raiz do logo):
`docs/mockups/relatorio-diagnostico-manta-maestro.html`

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
- [ ] Obter o arquivo oficial do logo (SVG de preferência) — ver
      `assets/README.md`
- [ ] Commitar o logo real em `assets/logo-manta.svg` (ou `.png`)
- [ ] Gerar o base64 a partir do arquivo real e embutir no template
- [ ] Consolidar um template único de relatório (HTML/CSS) com as 6 regras
      obrigatórias do padrão Manta já aplicadas — os agentes passam a
      *preencher* esse template, não recriá-lo a cada chamada
- [ ] Atualizar a skill `padrao-manta` para referenciar o asset real e
      remover o fallback "desenhar SVG inline"
- [ ] Migrar 1 relatório piloto e validar com o time
- [ ] Propagar o template para os demais agentes do Maestro
- [ ] Gate humano: aprovação MN antes de propagar

## 3. Fontes

- Skill `padrao-manta` v2 (regras obrigatórias, paleta, tipografia)
- Varredura do repositório `mn1970/codex-exemplo`, do Google Drive e do
  SharePoint da Manta em 2026-08-29 — nenhum template de relatório ou
  arquivo de logo encontrado
