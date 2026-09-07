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
| **Tarifas × Success Fee segregados** | Na Seção 12 (Preço), apresentar em tabelas separadas: (a) **Tarifas** — remuneração fixa por perfil/hora do escopo-base (tabela tarifária padrão, 13 perfis); (b) **Success Fee** — remuneração contingente, com o(s) critério(s) de sucesso definido(s) proposta a proposta (economia de custo, conquista, cronograma etc.) e o percentual/valor aplicável a cada um | Sempre que a proposta tiver componente de remuneração contingente — nunca somar success fee à tarifa em uma única linha |
| **Método do Paramétrico em Etapas** | Descrever o método de CAPEX/OPEX em etapas numeradas (leitura do MEF/edital → estruturação do escopo físico → aplicação do banco de custos Manta → curva ABC → cenários e comparação), com pelo menos 1 exemplo numérico real (desvio de custo vs. tabela oficial, curva ABC por insumo) | Propostas que envolvam paramétrico de CAPEX/OPEX como entregável central |
| **Infraestrutura e Ferramentas Incluídas** | Tabela explícita do que está incluso no preço (plataformas de IA, tokens/mês, AutoCAD, Civil 3D, SharePoint, Office 365) | Sempre, quando a proposta incluir Portal Manta ou ferramentas de produtividade como parte do escopo |
| **Controle de Revisão** | No topo do documento, antes da Seção 1: o que mudou desta revisão para a anterior, e por quê | Toda revisão (`_B`, `_C`, `_D`...) de uma proposta já emitida |

### Exigibilidade do Success Fee (gatilho de pagamento)

O success fee só se torna exigível a partir da **formalização documentada**
do evento que caracteriza o sucesso definido na proposta — nunca a partir
de uma percepção informal de resultado. O gatilho varia conforme o
critério de sucesso adotado na Seção 12:

| Critério de sucesso da proposta | Evento que torna o success fee exigível |
|---|---|
| Melhoria/economia de custos (CAPEX/OPEX) | Formalização da **aprovação do orçamento** pelo cliente incorporando a economia identificada (ata, ofício ou aprovação equivalente do órgão/instância competente) |
| Conquista (ex.: vencer o leilão/licitação, obter aprovação regulatória) | Formalização da **conquista** (ex.: homologação do resultado do leilão, assinatura do contrato de concessão, publicação da aprovação regulatória) |
| Cumprimento de cronograma / marco contratual | Formalização do **marco de cronograma atingido e aprovado** pelo cliente (ateste/aceite do marco) |
| Outro critério específico definido na proposta | Aplicar a mesma lógica: exigibilidade nasce do evento-gatilho formalizado e documentado equivalente, descrito na própria proposta |

Em todos os casos mantém-se a cláusula-mãe já prevista em "Cenários de
Contratação": **sem a formalização do evento-gatilho, não há success fee
devido** — a mera expectativa de sucesso, sem documento de formalização,
não gera exigibilidade nem vencimento de prazo de pagamento.

### Juros e Encargos por Atraso no Pagamento

Cláusula adicional a inserir na Seção 13 (Medição e Pagamento), aplicável
tanto às Tarifas quanto ao Success Fee: em caso de atraso no pagamento de
qualquer fatura além do prazo de vencimento acordado, incidirão, sobre o
valor em aberto e sem necessidade de aviso ou notificação prévia:

- **Multa moratória** de 2% (dois por cento) sobre o valor da fatura em
  atraso;
- **Juros de mora** de 1% (um por cento) ao mês, pro rata die, calculados
  desde a data de vencimento até a data do efetivo pagamento;
- **Atualização monetária** pelo IPCA (ou índice equivalente pactuado no
  contrato), aplicada sobre o saldo devedor no mesmo período.

Os percentuais acima são o padrão de referência do modelo mestre — a
proposta pode ajustá-los conforme negociação específica com o cliente,
mantendo a estrutura de três parcelas (multa + juros + correção
monetária). Esta cláusula não substitui, mas complementa, os prazos e
condições já definidos na Seção 13 quanto à forma de faturamento e
aprovação de medições.

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
- [ ] Revisar com jurídico os percentuais padrão de multa/juros/correção
      monetária da cláusula de atraso de pagamento antes de publicar.
- [ ] Gate humano (MN) — aprovação antes de publicar.
- [ ] Registrar a mudança no changelog da skill (nova versão da
      `skill-proposta-comercial-SKILL.md`).
- [ ] Atualizar `04_IA/Manta-Maestro/00-arquitetura/` se a variante M6 for
      referenciada na arquitetura canônica do Manta Maestro.
