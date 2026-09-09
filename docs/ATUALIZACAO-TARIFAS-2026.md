# Atualização da Tabela Tarifária — 2026

**Status:** ✅ **PUBLICADO em produção** — a tabela tarifária real de
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` foi atualizada
para a versão **3.3.2** em 2026-09-09 (gate humano MN confirmado
diretamente nesta conversa: "sim para tudo"), substituindo a lista de 13
perfis pela matriz Função × Nível abaixo. Publicação verificada por
releitura do arquivo via `SharePoint_Manta` MCP.

> ⚠️ **Correção de rastreamento (2026-09-09):** a primeira versão deste
> documento assumia, com base numa cópia local desatualizada, que a
> tabela tarifária de produção vivia em
> `04_IA/Manta-Maestro/05-sub-skills/skill-proposta-comercial-SKILL.md`.
> Verificação direta no SharePoint (`SharePoint_Manta` MCP, leitura)
> mostra que esse arquivo hoje é só um stub de 667 bytes apontando para
> `_DEPRECATED.md` — o corpo operacional da skill (numeração, tabela
> tarifária, dados fixos, cláusulas) foi fundido em 2026-09-07 (v3.3.0)
> para dentro de **`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md`**
> (versão atual: **3.3.1**, 2026-09-07). Duas boas notícias dessa
> verificação: (1) a tabela tarifária real de produção ("Tabela
> tarifaria padrao [v3.3.0]", base 176h/mês) é **idêntica** — mesmos 13
> perfis e valores — à usada na comparação da seção 3 abaixo, então a
> análise permanece válida; (2) a variante "Tipo A / Concessão de
> Infraestrutura de Grande Porte" (equivalente ao antigo addendum "M6")
> **já está aplicada em produção**, não mais pendente. O addendum da
> seção 4 abaixo foi corrigido para apontar ao arquivo e à seção reais.

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
skill. Decisão do gate humano (MN, confirmado nesta conversa em
2026-09-09 — "sim para tudo") sobre os 3 pontos abaixo, **já aplicada em
produção**:

1. **Migrar para a estrutura em 2 eixos** (Função × Nível) — decidido:
   sim, substitui a lista de 13 perfis (não é só um reajuste de `R$/h`
   mantendo os nomes antigos).
2. **Queda em Sócio/Diretor (-20%)** — aceita como intencional (reflete
   a tarifa real adotada no fechamento de orçamento de 24/04/2026, não
   um artefato do BDI específico do projeto).
3. **"Projetista Sênior"** (sem correspondência direta na nova aba
   Tarifas) — removido da tabela; nota registrada no arquivo de
   produção instruindo usar o nível "Especialista" mais próximo por
   senioridade até reconciliação futura.

## 4. Addendum aplicado na skill de produção

O bloco abaixo **substituiu** a seção "Tabela tarifaria padrao
[v3.3.1]" do arquivo real de produção
`Engenharia/Documentos Compartilhados/04_IA/Manta-Maestro/02-atividades/
A1-proposta/SKILL.md`, agora na versão **3.3.2** (2026-09-09) — publicado
via `SharePoint_Manta` MCP e confirmado por releitura do arquivo.

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

### Checklist de aplicação (publicado em 2026-09-09)

- [x] Decidir com o gate humano (MN) os 3 pontos da seção 3 acima.
- [x] Colar o bloco da seção 4 substituindo "Tabela tarifaria padrao"
      em `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md`, e
      bump de versão para 3.3.2.
- [ ] Confirmar que a mudança de estrutura (13 perfis → Função × Nível)
      não quebra referências existentes em propostas Tipo A/PRC/variante
      de concessão já emitidas — pendente de checagem manual pela equipe
      Manta contra propostas já emitidas.
- [x] Registrar a mudança no changelog do arquivo (campo `updated`/
      `supersedes` no frontmatter e nota de versão v3.3.2 no corpo).
- [x] Atualizar `CLAUDE.md` (este repositório).
