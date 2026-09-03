# Padrão de Marca — Capa de Propostas Manta Associados

Este diretório guarda os ativos de identidade visual **oficiais** referenciados
pelo CLAUDE.md master e usados por todas as skills/agentes que geram propostas
técnicas e comerciais (`proposta-comercial`, `proposta-tecnica-rod`,
`padrao-manta`, agente A7-bd).

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `logo-manta.jpg` | Logo oficial "Manta Associados" (extraído de `capa-padrao-proposta.pdf`, 249×104px). Usar como referência de marca; solicitar arquivo em resolução maior/vetorial (SVG/AI) quando disponível. |
| `capa-padrao-proposta.pdf` | Capa-modelo de Proposta Técnica (ex.: MNT-2026-COM-1192_A). Define o layout padrão obrigatório de toda capa de proposta Manta. |

## Estrutura obrigatória da capa

1. **Código do documento** no canto superior direito, padrão `MNT-YYYY-TIPO-SEQ`
   (ex.: `MNT-2026-COM-1192_A`) — conforme regra R4 do Manta Maestro.
2. **Título** em duas linhas: tipo em caixa alta grande (`PROPOSTA`) + subtítulo
   em negrito (`Técnica` ou `Comercial`).
3. **Campo "Responsável"** — fundo laranja (`#E8863A` aprox.), nome do
   responsável técnico Manta.
4. **Campo "Empresa"** — fundo preto/cinza-escuro, nome do cliente.
   ⚠️ Regra R1 do Maestro: em artefatos de exemplo/treinamento, nomes de
   empresas devem ser substituídos por placeholder; em propostas reais ao
   cliente, o nome do cliente é exibido normalmente neste campo.
5. **Padrão gráfico** de losangos sobrepostos em tons terracota/marrom nos
   cantos superior-direito e inferior-direito.
6. **Logo Manta Associados** no rodapé, alinhado à esquerda, com linha
   horizontal separando do corpo da capa.

## Uso

Qualquer skill ou agente que gere uma proposta (técnica, comercial ou
econômica) deve:

1. Referenciar este documento como fonte do padrão de capa.
2. Reutilizar `logo-manta.jpg` (ou uma versão vetorial superior, quando
   fornecida) — nunca recriar o logo do zero.
3. Seguir a estrutura descrita acima, alterando apenas: código do documento,
   tipo de proposta, responsável e empresa/cliente.

## Pendência

- [ ] Obter arquivo vetorial do logo (SVG/AI/EPS) em alta resolução — a versão
      atual foi extraída de um PDF e tem resolução baixa (249×104px).
