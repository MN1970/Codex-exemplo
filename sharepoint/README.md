# `sharepoint/` — espelhos do SharePoint no repositório

Atualizado na auditoria de 2026-09-22 (`docs/PLANO-AUDITORIA-v1.md`).

## Onde fica o Manta Maestro de verdade

A árvore canônica é a do SharePoint:

```text
mnassociados.sharepoint.com/sites/Engenharia
  └── Documentos Compartilhados/04_IA/Manta-Maestro/
      ├── 01-segmentos/   S1–S14 (numeração oficial, decisão D2)
      ├── 02-atividades/  A1–A11
      ├── 03-funcionais/  F1–F10
      ├── 04-disciplinas/ D01–D22
      ├── 06-exemplares/  exemplares L3 por célula S.A
      └── 09-base-conhecimento/INDICE-CANONICAL.md   ← ponto de entrada
```

A biblioteca solta `04_IA` (Drive B) tem cópias antigas: `Manta-Maestro/` e
`01-agentes-fundamentais/` estão marcadas com `_DEPRECATED.md`.

## O que existe nesta pasta

| Caminho | O que é | Direção |
|---|---|---|
| `Manta-Maestro/` | Espelho **parcial** da árvore canônica: só arquivos sem dado comercial nem nome de cliente/pessoa (hoje `INDICE-CANONICAL.md`, `template-prt-rodovias-v1.md` e `03-exemplares/_DEPRECATED.md`) | repo → SP |
| `avisos-drive-b/` | Avisos `_DEPRECATED.md` publicados na biblioteca `04_IA` | repo → SP |
| `00-arquitetura/`, `ARQUITETURA-AGENTES-IA-v5.0.0.md`, `CONSOLIDACAO-SHAREPOINT-v5.0.1.md`, `UPLOAD-MANUAL-v5.0.1.md` | Documentos históricos da v5.0 | — (histórico) |
| `01-agentes-fundamentais/` | Espelho antigo (v4.2) dos agentes verticais, usado pela Routine de sync de julho–agosto | histórico; numeração de agente já corrigida para D2, mas o destino no SP (`04_IA/01-agentes-fundamentais/`) está descontinuado |

## Regras

1. **O repositório é público.** Nada que tenha tabela de preço, dado bancário,
   contato pessoal, nome de cliente ou de profissional entra aqui (regra R1).
   Esses arquivos ficam com edição só no SharePoint — por exemplo,
   `02-atividades/A1-proposta/SKILL.md`.
2. Arquivo espelhado em `Manta-Maestro/` é editado **aqui** e publicado no SP;
   edição feita direto no SP é sobrescrita na próxima publicação.
3. Antes de publicar, reler a versão do SP (há vários escritores — achado P-17)
   e conferir tamanho e `quickXorHash` depois do upload.
4. A importação completa da árvore canônica para cá (onda W2 do plano) está
   **suspensa** até MN decidir como tratar o conteúdo confidencial num
   repositório público.
