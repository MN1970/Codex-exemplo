# Atualização da Tabela Tarifária — 2026

**Status:** análise concluída, addendum pronto para colar na skill de produção.
**Ainda não aplicado** — mudança de valores/estrutura de tarifa comercial
exige gate humano (MN) antes de publicar no SharePoint, seguindo o mesmo
fluxo já usado em `docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md` (variante M6).

Fonte: planilha de orçamento de projeto fornecida pelo usuário
(`Orçamento_CLIENTE.xlsx`, fechamento com Mauricio em 24/04/26), aba
**"Tarifas"** — tabela oficial de tarifa adotada por Função × Nível.
Nomes de colaboradores e salários individuais (presentes nas abas
"Tabela de Custos" e no orçamento linha a linha) **não são reproduzidos
aqui** — apenas os valores agregados por nível, que é o dado relevante
para a tabela tarifária comercial.

---

## 1. O que a planilha contém

A planilha tem 7 abas:

| Aba | Conteúdo |
|---|---|
| Orçamento | Orçamento de um projeto específico (CLIENTE): equipe alocada por função (Comitê Técnico, Coordenação, Especialistas, Equipe Técnica), horas/mês, custo salarial, BDI aplicado (Contingência 10% + Imposto 17,5% + Overhead 25% + Lucro 15% = 67,5%), fechamento em R$ 431.571,98 (3 meses) / R$ 863.143,96 mensal, tarifa média R$ 297,23/h |
| Visita Técnica | Modelo de custo de viagem (passagem, hospedagem, diária, veículo, pedágio) — zerado neste orçamento |
| Despesas | Modelo de custo de ferramentas (AutoCAD, Civil 3D, MS Project) — zerado neste orçamento |
| BDI | Espelho do fechamento de BDI da aba Orçamento (mesma estrutura 67,5%) |
| Tabela de Custos | Base de custo individual por colaborador (nome, função, nível, R$/mês, R$/hora, BDI, tarifa de venda) — **dado sensível de RH, não replicado neste documento** |
| **Tarifas** | **Tabela oficial de tarifa adotada por Função × Nível — é a fonte da atualização abaixo** |
| Função e Nível | Lista de referência das combinações Função × Nível válidas |

## 2. Nova tabela tarifária (fonte: aba "Tarifas")

Estrutura em 2 eixos — **Função** × **Nível** — diferente da tabela atual
da skill `proposta-comercial`, que é uma lista única de 13 "Perfis" (base
176h/mês). A nova estrutura é mais granular (distingue nível dentro de
Coordenação, Especialista, Engenharia e Analista).

| Função | Nível | Custo Médio (R$/h) | Venda Médio (R$/h, BDI 67,5%) | **Tarifa Adotada (R$/h)** | Equivalente mensal (176h) |
|---|---|---|---|---|---|
| Diretoria | Sócio Diretor | 170,45 | 524,47 | **800,00** | 140.800,00 |
| Coordenação | Máster | 170,45 | 524,46 | **550,00** | 96.800,00 |
| Coordenação | Sênior | – | – | **522,50** | 91.960,00 |
| Coordenação | Pleno | – | – | **496,38** | 87.362,00 |
| Especialista | Máster | 157,66 | 485,12 | **500,00** | 88.000,00 |
| Especialista | Sênior | – | – | **475,00** | 83.600,00 |
| Especialista | Pleno | – | – | **451,25** | 79.420,00 |
| Especialista | Júnior | – | – | **428,69** | 75.449,00 |
| Engenharia | Máster | 182,33 | 561,02 | **561,00** | 98.736,00 |
| Engenharia | Sênior | 141,48 | 435,32 | **532,95** | 93.799,20 |
| Engenharia | Pleno | 93,75 | 288,46 | **506,30** | 89.109,24 |
| Engenharia | Júnior | – | – | **480,99** | 84.653,78 |
| Analista | Sênior | – | – | **150,00** | 26.400,00 |
| Analista | Pleno | 28,86 | 88,80 | **142,50** | 25.080,00 |
| Analista | Júnior | 17,04 | 52,44 | **135,38** | 23.826,00 |
| Estágio | Estagiário | 12,50 | 38,46 | **80,00** | 14.080,00 |

> Observação sobre os níveis dentro de cada Função: os valores seguem uma
> progressão de ~5% de degrau entre níveis adjacentes (ex.: Coordenação
> Sênior = Máster × 0,95; Pleno = Sênior × 0,95), exceto Diretoria e
> Estágio, que têm nível único.

## 3. Comparação com a tabela atual da skill (13 perfis)

| Perfil atual (skill) | R$/h atual | Nível novo mais próximo | R$/h novo | Variação |
|---|---|---|---|---|
| Sócio / Diretor | 1.000 | Diretoria — Sócio Diretor | 800,00 | **-20%** |
| Engenheiro Máster | 392 | Engenharia — Máster | 561,00 | **+43%** |
| Engenheiro Sênior | 347 | Engenharia — Sênior | 532,95 | **+54%** |
| Técnico Máster | 347 | Especialista — Máster | 500,00 | **+44%** |
| Engenheiro Pleno A (>10a) | 290 | Engenharia — Pleno | 506,30 | **+75%** |
| Técnico Sênior | 258 | Especialista — Sênior | 475,00 | **+84%** |
| Engenheiro Pleno B (≤10a) | 234 | Engenharia — Pleno | 506,30 | **+116%** |
| Técnico Pleno | 183 | Especialista — Pleno | 451,25 | **+147%** |
| Engenheiro Júnior | 148 | Engenharia — Júnior | 480,99 | **+225%** |
| Projetista Sênior | 106 | — (sem correspondência direta) | — | — |
| Analista A | 95 | Analista — Sênior/Pleno | 150,00 / 142,50 | **+58% / +50%** |
| Analista B | 64 | Analista — Júnior | 135,38 | **+112%** |
| Estagiário | 34 | Estágio — Estagiário | 80,00 | **+135%** |

**Leitura:** a nova tarifa adotada está, na maioria dos níveis, bem acima
da tabela vigente na skill — exceto Sócio/Diretor, que cai. Isso é
consistente com um projeto real fechado com BDI de 67,5% (Overhead 25% +
Lucro 15% + Imposto 17,5% + Contingência 10%), que aparentemente reflete
uma política de precificação mais atual do que a tabela publicada na
skill. Antes de publicar, **confirmar com o gate humano (MN)** se:

1. A tabela da skill deve migrar para a estrutura em 2 eixos
   (Função × Nível) ou se os novos valores devem apenas substituir os
   `R$/h` da lista de 13 perfis existente, mantendo os nomes atuais.
2. A queda em Sócio/Diretor (-20%) é intencional ou um efeito do BDI
   específico deste projeto (67,5%) que não deve virar tarifa padrão.
3. "Projetista Sênior" (perfil hoje sem correspondência na nova aba
   Tarifas) deve ser mantido, removido ou mapeado para algum nível de
   Especialista/Técnico.

## 4. Addendum pronto para colar na skill de produção

Assim como o addendum M6 (`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`),
o bloco abaixo é **aditivo** — substitui apenas a seção "Tabela Tarifária
Padrão" do arquivo de produção
`Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/02-sub-skills/
skill-proposta-comercial-SKILL.md`. **Não publicar sem aprovação MN.**

```markdown
## Tabela Tarifária Padrão (atualização 2026 — base 176h/mês)

Estrutura por Função × Nível (substitui a tabela de 13 perfis anterior).

| Função | Nível | Tarifa (R$/h) | Tarifa (R$/mês, 176h) |
|---|---|---|---|
| Diretoria | Sócio Diretor | R$ 800 | R$ 140.800 |
| Coordenação | Máster | R$ 550 | R$ 96.800 |
| Coordenação | Sênior | R$ 522,50 | R$ 91.960 |
| Coordenação | Pleno | R$ 496,38 | R$ 87.362 |
| Especialista | Máster | R$ 500 | R$ 88.000 |
| Especialista | Sênior | R$ 475 | R$ 83.600 |
| Especialista | Pleno | R$ 451,25 | R$ 79.420 |
| Especialista | Júnior | R$ 428,69 | R$ 75.449 |
| Engenharia | Máster | R$ 561 | R$ 98.736 |
| Engenharia | Sênior | R$ 532,95 | R$ 93.799,20 |
| Engenharia | Pleno | R$ 506,30 | R$ 89.109,24 |
| Engenharia | Júnior | R$ 480,99 | R$ 84.653,78 |
| Analista | Sênior | R$ 150 | R$ 26.400 |
| Analista | Pleno | R$ 142,50 | R$ 25.080 |
| Analista | Júnior | R$ 135,38 | R$ 23.826 |
| Estágio | Estagiário | R$ 80 | R$ 14.080 |

> Valores já incluem encargos, overhead e margem (BDI de referência:
> Contingência 10% + Imposto 17,5% + Overhead 25% + Lucro 15% = 67,5%).
> Sem custos adicionais exceto deslocamentos. Fonte: fechamento de
> orçamento de projeto em 24/04/2026, tabela "Tarifas" consolidada por
> Função × Nível.
```

### Checklist de aplicação (para quem for publicar no SharePoint)

- [ ] Decidir com o gate humano (MN) os 3 pontos da seção 3 acima.
- [ ] Colar o bloco da seção 4 substituindo "Tabela Tarifária Padrão" no
      arquivo de produção, na posição indicada.
- [ ] Confirmar que a mudança de estrutura (13 perfis → Função × Nível)
      não quebra referências existentes em propostas M1–M6 já emitidas.
- [ ] Registrar a mudança no changelog da skill (nova versão da
      `skill-proposta-comercial-SKILL.md`).
- [ ] Atualizar `CLAUDE.md` (este repositório) quando a publicação for
      confirmada.
