# Addendum pronto para deploy — Variante "PTC-Infraestrutura/Concessão de Grande Porte"

**Status: ✅ SUPERSEDIDO — já implementado na skill de produção, por
caminho independente.** Este arquivo vira registro histórico; nenhuma
ação de publicação resta.

Confirmado em 2026-09-13: `skill-proposta-comercial-SKILL.md` (caminho
citado abaixo) é hoje um stub "DEPRECATED". A fonte de verdade da
proposta técnico-comercial passou a ser
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.9,
2026-09-11), que já contém uma variante equivalente aos 5 blocos deste
addendum, sob o nome **"Tipo A / Concessão de Infraestrutura de Grande
Porte"** (a numeração de modos mudou de M1–M6 para Tipo A/B/PRC — não é
uma seção "M6" separada, é um perfil do Tipo A).

A pendência `_C`/`_D` sinalizada abaixo **também já foi resolvida na
fonte, de forma independente**: o changelog da skill nova (v3.3.7,
2026-09-10) removeu a alegação de validação contra "MNT-2026-COM-1183_D"
por não corresponder a documento real (só existe `_C_3`) — mesma
divergência encontrada no levantamento do acervo desta sessão. A versão
em produção é mais conservadora que o texto abaixo: marca a variante
como "pendente de validação contra uma proposta real específica antes de
uso em cliente", em vez de alegar uma validação inexistente. Um segundo
caso do mesmo padrão (citação a "MNT-2026-COM-1301" não encontrada no
SharePoint) foi achado e corrigido na v3.3.9.

O conteúdo abaixo (Seção A e checklist) fica mantido **apenas como
registro do racional original** — não deve mais ser colado em lugar
nenhum; a skill em produção já superou este texto.

---

Este addendum implementava a recomendação de `docs/MODELO-MESTRE-PROPOSTA.md`
(validada contra MNT-2026-COM-1183_D) sem alterar nenhuma seção existente da
skill `proposta-comercial` — era puramente aditivo.

---

## Onde inserir

No arquivo `skill-proposta-comercial-SKILL.md`, inserir o bloco da **Seção A**
como uma nova seção **imediatamente depois** de "## 5 Modos de Operação
(M1–M5)" e **antes** de "## Workflow de Geração". Nenhum texto existente
precisa ser removido ou renumerado — M1 a M5 continuam exatamente como estão.

---

## SEÇÃO A — Conteúdo a colar

```markdown
## M6 — Variante PTC-Infraestrutura/Concessão de Grande Porte

Extensão do modo **M1 (Proposta Completa)** para propostas de avaliação
técnica, paramétrico de CAPEX/OPEX e gestão integrada em concessões de
infraestrutura de grande porte (rodovias, ferrovias, portos, aeroportos,
saneamento, energia, barragens). Validada contra a proposta real
MNT-2026-COM-1183_D (Concessão Rota 2 de Julho). Usar quando o cliente for
um investidor/concessionária avaliando participação em leilão ou já
concessionária de um ativo de grande porte — não substitui M1 genérico para
propostas menores ou de outra natureza.

### Blocos adicionais (inserir dentro da Seção 3 — Escopo dos Serviços, ou
como sub-seções 2.1/2.2 quando o objeto envolver decisão de investimento)

| Bloco | Conteúdo | Quando usar |
|---|---|---|
| **Dados Oficiais do Empreendimento** | Quadro físico do ativo (extensão, CAPEX, OPEX, prazo, TIR se disponível) extraído de fonte primária (edital, PER, audiência pública, MEF) com rastreabilidade número-a-número à tabela/documento de origem | Sempre que a proposta responder a um edital publicado ou processo de audiência pública em andamento |
| **Cenários de Contratação** | Separar objeto em Cenário 1 (escopo-base, preço fixo) e Cenário(s) opcionais (módulo de engenharia de valor, success fee), com cláusula explícita "sem acordo, sem success fee" — a adesão ao módulo opcional nunca gera ônus se recusada | Sempre que houver upsell de engenharia de valor / otimização não incluído no preço fixo do escopo-base |
| **Método do Paramétrico em Etapas** | Descrever o método de CAPEX/OPEX em etapas numeradas (leitura do MEF/edital → estruturação do escopo físico → aplicação do banco de custos Manta → curva ABC → cenários e comparação), com pelo menos 1 exemplo numérico real (desvio de custo vs. tabela oficial, curva ABC por insumo) | Propostas que envolvam paramétrico de CAPEX/OPEX como entregável central |
| **Infraestrutura e Ferramentas Incluídas** | Tabela explícita do que está incluso no preço (plataformas de IA, tokens/mês, AutoCAD, Civil 3D, SharePoint, Office 365) | Sempre, quando a proposta incluir Portal Manta ou ferramentas de produtividade como parte do escopo |
| **Controle de Revisão** | No topo do documento, antes da Seção 1: o que mudou desta revisão para a anterior, e por quê | Toda revisão (`_B`, `_C`, `_D`...) de uma proposta já emitida |

### Convenção de versionamento (variante M6)

Propostas M6 usam sufixo de letra para revisões substanciais em resposta a
processo regulatório público (`MNT-YYYY-COM-NNNN_A`, `_B`, `_C`...), em vez
do `REV_00/REV_01` padrão do M1 — porque a numeração acompanha o calendário
do processo (audiência pública, publicação de edital, leilão), não um ciclo
de revisão interna da Manta. Fora da variante M6, manter `REV_NN`.

### Fusão de cláusulas finais (opcional, só na variante M6)

Para propostas M6, as seções 6 (Fora do Escopo), 8 (Casos Omissos), 15
(Validade), 16 (Contato/Dados da Empresa), 17 (Limitação de
Responsabilidade) e 18 (Disclaimer) PODEM ser condensadas em uma única
seção final "Propriedade Intelectual e Cláusulas Finais", em formato de
tabela compacta, seguida de uma **Ficha Técnica do Documento** (cliente,
projeto, documento, código, versão, data de emissão, classificação,
responsável, contato comercial, fontes primárias, repositório). Fora da
variante M6, manter as 18 seções numeradas individualmente — a fusão é
opcional e específica deste perfil de cliente/proposta.

### Fonte de validação

Proposta real: MNT-2026-COM-1183_D (Concessão Rota 2 de Julho —
BR-116/324/BA, Nova Infra Invest, 26/08/2026). Análise completa em
`docs/MODELO-MESTRE-PROPOSTA.md` no repositório `Codex-exemplo`.
```

---

## Checklist de aplicação (histórico — já superado, ver status no topo)

- [x] Gate humano (MN) — aprovado em 2026-09-10.
- [x] Fonte de validação corrigida — resolvido na skill de produção
      (v3.3.7), independentemente deste addendum.
- [x] Conteúdo equivalente já publicado — como variante "Tipo A /
      Concessão de Infraestrutura de Grande Porte" em
      `02-atividades/A1-proposta/SKILL.md`.
- [x] M1–M5 (hoje Tipo A/B/PRC) permanecem inalterados como estrutura
      genérica — a variante é um perfil adicional, não substituição.
- [x] Mudança registrada no changelog da skill de produção (v3.3.0,
      v3.3.7, v3.3.9).
- [ ] Atualizar `04_IA/Manta-Maestro/00-arquitetura/` se a variante ainda
      não estiver referenciada na arquitetura canônica do Manta Maestro
      (não verificado nesta sessão).
