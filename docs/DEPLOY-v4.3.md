# Deploy runbook — Manta Maestro v4.3

Origem: pedido do usuário para generalizar, como skill do Manta
Maestro, o processo manual usado na Nota Técnica "Acervo Técnico do
Ferroanel Norte — Projeto Básico DERSA" (projeto MRS, 27/08/2026) —
ler a estrutura de um acervo técnico recebido de Cliente (SharePoint,
OneDrive ou diretório local) e montar o mesmo tipo de briefing, de
forma repetível para qualquer projeto/segmento.

Este runbook cobre o que precisa ser feito **fora deste repo git** para
concluir a v4.3.

---

## 1. Merge do PR (gate humano MN)

- [ ] Revisar o PR da branch `claude/ferroanel-norte-acervo-3wadva`.
- [ ] Approve + merge (draft → ready → merged).

Não seguir para os próximos passos até o merge estar no `main`.

---

## 2. Skill registry do Maestro operacional

O skill vive hoje só neste repositório de referência. Para ficar
disponível em runtime:

- [ ] Copiar `.claude/skills/ler-acervo-tecnico/` para o repositório
      operacional do Maestro (mesmo caminho relativo).
- [ ] Registrar o skill no catálogo interno (skill registry), se o
      Maestro operacional mantiver um catálogo separado do
      `.claude/skills/`.
- [ ] Confirmar se este skill deve receber um código Manta formal
      (hoje registrado no `CLAUDE.md` como "sem código Manta
      dedicado" — Eixo 4) ou permanece como utilitário sem código.

---

## 3. SharePoint

- [ ] Criar a pasta `02-skills-transversais/ler-acervo-tecnico/` em
      `04_IA/Manta-Maestro/` no SharePoint (ver `sharepoint/README.md`).
- [ ] Fazer upload do conteúdo de
      `sharepoint/02-skills-transversais/ler-acervo-tecnico/` (SKILL.md,
      README.md, refs/, prompts/).

---

## 4. Teste do pipeline

Antes de considerar o skill operacional, testar o pipeline descrito no
`SKILL.md` com pelo menos:

- [ ] Um acervo real (ou de teste) via SharePoint.
- [ ] Um acervo real (ou de teste) via OneDrive.
- [ ] Uma estrutura de pastas local (diretório de computador).
- [ ] Um caso com múltiplas fontes combinadas (checar deduplicação de
      volume).
- [ ] Um caso sem índice-mestre e sem padrão de codificação
      identificável (checar que o skill não força um esquema
      inventado).

---

## 5. Verificação pós-deploy

- [ ] Confirmar que o entregável (Nota Técnica) segue
      `refs/template-nota-tecnica.md` e a identidade visual
      `padrao-manta`.
- [ ] Confirmar que a planilha de inventário tem uma aba por
      disciplina/pasta, conforme a seção "Entregáveis" do `SKILL.md`.
- [ ] Confirmar que `aluci-guard` e `consist-guard` rodaram antes do
      fechamento do entregável de teste.

---

## Referências

- `CLAUDE.md` — Eixo 4 (Skills transversais).
- `.claude/skills/ler-acervo-tecnico/SKILL.md` — canônico.
- `sharepoint/02-skills-transversais/ler-acervo-tecnico/` — mirror para
  upload.
