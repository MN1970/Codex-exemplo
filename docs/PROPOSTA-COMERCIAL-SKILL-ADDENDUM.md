# Addendum pronto para deploy — Variante "PTC-Infraestrutura/Concessão de Grande Porte"

**Status:** pronto para colar na skill de produção. **Ainda não aplicado** —
esta sessão não tem acesso de escrita ao SharePoint (`SharePoint_Manta` sem
autenticação neste ambiente). Falta um passo manual: copiar o bloco da
Seção A abaixo para dentro de
`Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/02-sub-skills/
skill-proposta-comercial-SKILL.md`, na posição indicada, e confirmar o gate
humano (MN) antes de publicar.

Este addendum implementa a recomendação de `docs/MODELO-MESTRE-PROPOSTA.md`
(validada contra MNT-2026-COM-1183_D) sem alterar nenhuma seção existente da
skill `proposta-comercial` — é puramente aditivo.

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

## Checklist de aplicação (para quem for publicar no SharePoint)

- [ ] Colar o bloco da Seção A no arquivo de produção, na posição indicada.
- [ ] Confirmar que M1–M5 permanecem inalterados.
- [ ] Gate humano (MN) — aprovação antes de publicar.
- [ ] Registrar a mudança no changelog da skill (nova versão da
      `skill-proposta-comercial-SKILL.md`).
- [ ] Atualizar `04_IA/Manta-Maestro/00-arquitetura/` se a variante M6 for
      referenciada na arquitetura canônica do Manta Maestro.
