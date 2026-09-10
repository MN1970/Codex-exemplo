# Addendum pronto para deploy — Variante "PTC-Infraestrutura/Concessão de Grande Porte"

**Status:** ✅ **gate humano (MN) aprovado em 2026-09-10.** Ainda **não
aplicado** na skill de produção — falta só o passo mecânico: colar o
bloco da Seção A abaixo dentro de
`Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/02-sub-skills/
skill-proposta-comercial-SKILL.md`, na posição indicada. Bloqueado nesta
sessão porque o conector `SharePoint_Manta` está desconectado (MCP
server disconnected) — precisa ser feito por uma sessão/pessoa com
acesso de escrita ao SharePoint.

**⚠️ Confirmar antes de publicar:** a "Fonte de validação" abaixo cita
`MNT-2026-COM-1183_D`. Um levantamento completo do SharePoint em
2026-09-10 (118 propostas catalogadas + leitura integral do documento)
**não encontrou nenhum arquivo `_D`** — apenas a revisão `_C`
(`MNT-2026-COM-1183_C_3.pdf`, 21 páginas, 24/08/2026), cujo próprio
controle de revisão interno diz substituir a `_B`, sem mencionar uma
`_D`. Antes de colar este addendum na skill de produção, confirmar se a
`_D` existe em algum outro lugar (ex.: rascunho local, e-mail, versão
ainda não subida) ou corrigir a referência de fonte para `_C` nos dois
lugares abaixo (nesta seção e na "Fonte de validação" dentro do bloco a
colar).

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

- [x] Gate humano (MN) — aprovado em 2026-09-10.
- [ ] Confirmar fonte de validação (_C vs. _D — ver aviso acima) antes de
      colar o bloco.
- [ ] Colar o bloco da Seção A no arquivo de produção, na posição indicada.
- [ ] Confirmar que M1–M5 permanecem inalterados.
- [ ] Registrar a mudança no changelog da skill (nova versão da
      `skill-proposta-comercial-SKILL.md`).
- [ ] Atualizar `04_IA/Manta-Maestro/00-arquitetura/` se a variante M6 for
      referenciada na arquitetura canônica do Manta Maestro.
