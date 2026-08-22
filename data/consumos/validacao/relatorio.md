# Relatório de Validação — Piloto de Consumos por Receita Setorial

Data: 2026-08-22
Branch: `claude/pesquisa-consumos-construcao-5e2qtm`
Validador: `tools/validate_consumos.py`

## Resultado

```text
OK - 8 intensidades, 171 fontes, 8 linhas de estrutura de custo, 17 mapeamentos CNAE
```

Exit code 0. Autoteste do validador: 8 de 8 regras duras disparam corretamente,
e linha válida passa limpa.

## Contra a meta do plano

| Item | Meta | Entregue | Situação |
| --- | --- | --- | --- |
| Intensidades nos 5 setores prioritários | 40–60 linhas | **0** | não atingida |
| Intensidades em recorte agregado CNAE | — | 8 linhas | fora da meta original, foi o que o acesso permitiu |
| Estrutura de custo por setor | 6 blocos | 3 blocos, 8 linhas, todos fechando 100% | parcial — só no recorte agregado |
| Comparação internacional | 2 setores | 0 | não atingida |
| Catálogo de fontes | 100–130 | **171** | superada |
| Crosswalk CNAE ↔ NAICS | — | 17 mapeamentos (S1–S13 + 4 recortes), com grau de aderência | atingido |
| Método, schema, validador | — | completos e testados | atingido |

Matriz de cobertura: **6 de 136 células**. Os treze segmentos S1–S13 estão
inteiramente vazios.

## Causa: bloqueio de egress

A política de rede desta sessão negou o acesso às fontes. Confirmado
explicitamente pelo proxy, com erro `EGRESS_BLOCKED`, nestes domínios:

| Domínio | O que se buscava |
| --- | --- |
| `agenciadenoticias.ibge.gov.br` | PDF de divulgação da PAIC 2023 |
| `biblioteca.ibge.gov.br` | informativo PAIC 2022 (tabelas por CNAE) |
| `concla.ibge.gov.br` | tabela oficial CNAE 2.0, divisão 42 |
| `en.wikipedia.org` | teste de controle |

O teste de controle é o dado relevante: **até a Wikipédia foi negada**, o que
indica bloqueio amplo e não uma restrição a domínios `.gov.br`.

`curl` não tem saída de rede alguma no sandbox (código 000 em 20 domínios
testados, incluindo os quatro acima), então os outros 16 — `sidra.ibge.gov.br`,
`snic.org.br`, `acobrasil.org.br`, `cbicdados.com.br`, `portal.fgv.br`,
`ppi.gov.br`, `worldbank.org`, `infralatam.info`, `stats.oecd.org`,
`ec.europa.eu`, `ofwat.gov.uk`, entre outros — **não foram individualmente
confirmados como negados pelo proxy**. São presumidos inacessíveis, e estão
catalogados como `catalogada_nao_verificada`, não como bloqueados.

## O que foi feito em vez disso

Os 8 valores existentes vieram de **resultados de busca** (a única via de rede
funcional), não da leitura dos documentos. Estão todos marcados
`verificacao = snippet_busca` e `tier = D`.

**Nenhum deles pode ir para orçamento ou laudo de cliente** antes de ser
promovido a `fonte_primaria_lida`.

### Linhas produzidas

| id | valor | unidade | ano |
| --- | --- | --- | --- |
| `INT-C42-MAO_DE_OBRA-001` | 4,633 | pessoas-ano/R$ mi | 2022 |
| `INT-C41-MAO_DE_OBRA-001` | 4,636 | pessoas-ano/R$ mi | 2022 |
| `INT-C43-MAO_DE_OBRA-001` | 7,329 | pessoas-ano/R$ mi | 2022 |
| `INT-CF-MAO_DE_OBRA-001` | 5,280 | pessoas-ano/R$ mi | 2022 |
| `INT-C42-MAO_DE_OBRA-002` | 8.339 | hh/R$ mi | 2022 |
| `INT-CF-MAO_DE_OBRA-002` | 9.504 | hh/R$ mi | 2022 |
| `INT-CF-CIMENTO-001` | 123,9 | t/R$ mi | 2024 |
| `INT-CF-ACO-001` | 18,63 | t/R$ mi | 2024 |

Geradas por `scripts` de cálculo explícito, com `memoria_calculo` em cada linha.

## Checagens de consistência que passaram

Estas dão confiança nos agregados de entrada, apesar de não substituírem a
leitura da fonte primária:

1. **Soma dos segmentos 2022** — 186,1 + 147,8 + 105,1 = **R$ 439,0 bi**, igual
   ao total divulgado. Se um dos três estivesse errado, não fecharia.
2. **Soma do pessoal ocupado 2022** — 862,8 + 684,7 + 770,3 = **2.317,8 mil**,
   coerente com os "2,3 milhões" divulgados.
3. **Participação de infraestrutura em 2023** — 175,7 / 484,2 = **36,3%**, igual
   ao percentual divulgado de forma independente.
4. **Salário médio implícito 2022** — R$ 79,6 bi / 2,3178 mi = **R$ 34.343 por
   pessoa-ano**, ~R$ 2.582/mês equivalente. Plausível para a construção em 2022,
   e valida numerador e denominador ao mesmo tempo.
5. **Estrutura de custo** — bloco soma exatamente 100,0%.

## Ressalvas técnicas registradas nos dados

1. **Autoconstrução.** As linhas de cimento e aço dividem consumo nacional
   aparente por receita da PAIC. O consumo nacional inclui autoconstrução e obra
   fora do universo de empresas formais; a receita da PAIC não. As duas linhas
   portanto **superestimam** a intensidade da construção formal e são **limite
   superior**, não valor central. Está no campo `premissas` de cada uma.
   Correção: usar a matriz de insumo-produto (F-002).
2. **Numerador e denominador de fontes distintas.** Cimento vem do SNIC, aço do
   Instituto Aço Brasil, denominador da PAIC. Recortes possivelmente
   incompatíveis. Registrado em `notas`.
3. **Ano diferente entre famílias.** Mão de obra em 2022 (dado preciso por
   segmento), material em 2024 (o dado de 2023/2024 de pessoal só existe
   arredondado em "2,5 milhões", o que geraria falsa precisão). Não comparar
   famílias entre si sem trazer ao mesmo ano.
4. **Premissa de 1.800 h/ano.** É premissa Manta, não dado do IBGE. Trocá-la
   reescala todas as linhas em `hh/R$ mi`. Substituível por dado observado do
   CAGED/RAIS (F-008, F-009).
5. **Códigos CNAE não verificados.** O crosswalk foi montado sem acesso ao
   CONCLA. Um resultado de busca sugeriu a atribuição de 42.21 e 42.22 (energia
   x água/esgoto) **invertida** em relação à adotada. Todas as 14 linhas estão
   `status_verificacao = nao_verificado_concla`. **Conferir antes de usar.**

## Tentativa de comparação internacional (EUA) — não concluída

Depois da primeira rodada, o catálogo foi ampliado com 35 fontes americanas
(`F-137`–`F-171`, ver `../../docs/pesquisa-consumos/06-FONTES-EUA.md`), com o
objetivo de fechar o par **CNAE 42 ↔ NAICS 237** — o recorte de menor atrito
entre as duas estatísticas.

**Numerador obtido:** 1.097,1 mil postos de trabalho em NAICS 237 (heavy and
civil engineering construction) em 2022.

**Denominador não obtido.** As duas candidatas que apareceram não servem:

| Candidata | Por que não serve |
| --- | --- |
| *Value of construction put in place* (Census `F-016`) — US$ 133,6 bi de rodovia em 2022 | é **gasto por categoria de obra**, não receita de estabelecimento, e cobre só parte do escopo de NAICS 237 |
| Receita de NAICS 237 no Economic Census (`F-137`) | é **a base correta** — tabela `EC2223KOB`, *value of business done* — e não veio nos resultados de busca |

Cruzar emprego de NAICS 237 com gasto do VIP seria exatamente o erro de
denominador que este projeto existe para evitar. **Não foi calculado.**

Com acesso à rede resolve-se em minutos: `data.census.gov`, tabela `EC2223KOB`
ou `EC2223BASIC`, recorte NAICS 237. A linha resultante sairia com
`metodo = direto`, `tier = A` e `verificacao = fonte_primaria_lida` — qualidade
superior a de qualquer linha brasileira desta base hoje.

### Sobre a premissa de 1.800 h/ano

O **BLS CES** (`F-139`) resolve isso com dado observado do lado americano. Obtive
apenas valores estaduais — 38,3 h/semana em Nova York e 37,6 h/semana em
Washington, 2024 — e **não extrapolei de dois estados**. Sugere algo próximo de
1.950–1.980 h/ano, acima das 1.800 h adotadas, mas o regime de trabalho
americano não é o brasileiro: a premissa brasileira tem de sair do CAGED/RAIS
(`F-008`, `F-009`).

### Armadilha registrada no catálogo

A cesta do **ENR Construction Cost Index** (`F-162`) — 200 h de mão de obra
comum, 25 cwt de aço estrutural, 1,128 t de cimento portland, 1.088 board feet
de 2x4 — *parece* um coeficiente de consumo e **não é**: a ENR mantém as
quantidades constantes por construção, para que o índice reflita só preço. A
razão 200 h ÷ 1,128 t ≈ 177 hh por tonelada de cimento é artefato do índice, não
produtividade. Cadastrado como `indice_macro` e `cite_only`, com a advertência no
campo `notas` do próprio CSV.

## Segunda rodada de pesquisa (2026-08-22) — web scraping tentado e negado

Antes de qualquer coleta, testei acesso direto às fontes, incluindo **APIs
públicas** que dispensariam scraping de HTML:

| Alvo | Resultado |
| --- | --- |
| `servicodados.ibge.gov.br` (API de agregados) | `EGRESS_BLOCKED` |
| `apisidra.ibge.gov.br` (API SIDRA) | `EGRESS_BLOCKED` |
| `api.worldbank.org` (API do Banco Mundial) | `EGRESS_BLOCKED` |
| `www.enr.com` | `EGRESS_BLOCKED` |

Somado aos quatro domínios negados na primeira rodada, e ao fato de que `curl`
não tem saída de rede alguma no sandbox, a conclusão é firme: **web scraping é
impossível nesta sessão**, e não por falta de tentativa. O proxy nega todo host,
inclusive API pública e inclusive a Wikipédia usada como controle. O único canal
de rede funcional é a busca web.

### O que a busca rendeu

**1. Estrutura de custos e despesas da PAIC — dois anos, ambos fechando 100%.**
Este é o ganho principal da rodada: fecha os 81,9% que estavam indecompostos.

| Componente | 2022 | 2023 |
| --- | --- | --- |
| Despesas de pessoal | 48,3% | 49,0% |
| Custo dos materiais de construção | 37,4% | 35,9% |
| Obras e serviços de terceiros | 14,3% | 15,1% |
| **soma** | **100,0%** | **100,0%** |

Duas leituras que o dado impõe:

- O denominador aqui é **custos e despesas**, não valor das obras. Os 48,3% e os
  18,1% de remunerações sobre valor das obras (bloco anterior) **não são
  comparáveis**. Por isso `estrutura-custo-setor.csv` ganhou coluna
  `denominador`, e o validador passou a incluí-la na chave do bloco — sem isso,
  os dois blocos de 2022 somariam 200%.
- Parte da mão de obra real do setor está em **terceiros** (14–15%), não em
  despesas de pessoal. Ler o 48,3% como intensidade de trabalho subestima.

**2. Correção no crosswalk — barragem não está no residual.** A nota explicativa
da classe **42.91-0** inclui, além de portos, "enrocamentos, obras de dragagem,
aterro hidráulico, **barragens, diques** (exceto para geração de energia
hidroelétrica), instalação de cabo submarino". Consequências:

- **S10 Barragens** sai de `agregado`/42.99-5 para `parcial`/**42.91-0**.
- **S6 e S10 compartilham a mesma classe CNAE** — a PAIC não os separa. Isso
  substitui a suposição anterior de que portos era o único segmento prioritário
  com classe própria e limpa.
- Barragem **hidroelétrica** fica fora da 42.91 e provavelmente cai em 42.21-9
  (energia), o que mistura S10 com S9 nesse recorte.

**3. A tabela do SIDRA é a 1761, não a 1757.** A tabela da PAIC por classe CNAE
é a **1761**. Corrigido em `registro-fontes.csv` (F-004). É o desbloqueio de
S6/S10, S8 e S9 de uma só vez.

**4. Sobratema — dado de mercado obtido, mas não vira intensidade.** 58,2 mil
máquinas vendidas em 2024 (+9% sobre 53,5 mil em 2023), das quais 36,6 mil de
linha amarela (+14%); estimativa de 56,7 mil para 2025 (−2%). **Frota parada:
18% em 2025 contra 11% em 2024.**

Venda de máquina é **fluxo de investimento**, não consumo de hora-máquina —
não gera linha de intensidade, e forçá-la seria o mesmo erro de denominador que
o projeto evita. O dado de **frota parada** é o mais útil dos quatro: é medida
de utilização, e alimenta diretamente a discussão de FIC/FIT na Fase 2.

**5. Reforço quantitativo da ressalva da autoconstrução.** O SNIC publica a
distribuição de cimento por canal de venda. O dado localizado (**2006**, antigo e
citado apenas como ordem de grandeza) aponta 66,4% em revendas, 18,1% em
industrial/construtoras, 12,9% em concreteiras e 2,6% em exportação. Se a maior
parte do cimento sai por revenda, a intensidade da construção **formal** medida
pela PAIC é bem menor que o limite superior de 123,9 t/R$ mi registrado na base.
Confirma que aquela linha é teto, não valor central.

### O que a busca não rendeu

| Alvo | Situação |
| --- | --- |
| **Pesos do INCC** (F-079) | só a estrutura em dois grupos e as 7 capitais; **percentuais não obtidos** |
| **PAIC por classe CNAE** | inacessível sem o SIDRA 1761 |
| **Receita de NAICS 237** (F-137) | tentada em 3 formulações; exige `data.census.gov` |
| **Valor absoluto de custos e despesas da PAIC** | só percentuais, sem os R$ |

Sem o valor absoluto de custos e despesas, **não** dá para converter os 37,4% de
materiais em quantidade física. Tentar seria inventar. As linhas de intensidade
seguem em 8.

## Terceira rodada — conectores contornam o egress

Constatação central: **os conectores MCP não passam pelo proxy de egress da
web.** SharePoint (Microsoft 365) e Supabase respondem normalmente, enquanto
todo `WebFetch` é negado. Isso abre um caminho de dado que as duas primeiras
rodadas não tinham.

### Primeira fonte efetivamente lida na origem

O **Manual de Custos de Infraestrutura de Transportes (MCIT/DNIT)** está no
SharePoint da Manta e foi lido. É a **primeira e única fonte do projeto com
`verificacao = fonte_primaria_lida`** — as outras 169 seguem catalogadas ou
vindas de busca.

Identificação verificada no documento: 2ª edição, Brasília 2025, 111 p., aprovado
pela Diretoria Colegiada do DNIT em 21/10/2025 (Relato nº 191/2025), revisão pela
FGV sob contratos 490/2021-00 e 647/2024-00. **Oito volumes:**

| Vol | Título |
| --- | --- |
| 01 | Metodologia e Conceitos |
| 02 | Mão de Obra |
| 03 | Preços Referenciais |
| 04 | **FIC — Fator de Influência de Chuvas** (Tomo 1 intensidade; Tomo 2 etapas) |
| 05 | **FIT — Fator de Interferência de Tráfego** |
| 06 | Canteiro de Obras |
| 07 | Administração Local |
| 08 | Mobilização e Desmobilização |

### Erro próprio corrigido

As duas primeiras rodadas afirmavam, em quatro documentos e no registro de
fontes, que o SICRO separa hora produtiva de improdutiva "via **FIT/FIU**".
**"FIU" não existe no SICRO.** Os fatores reais são **FIC** (chuvas, Volume 04) e
**FIT** (tráfego, Volume 05), e a produtividade sai da **PEM — Produção de Equipe
Mecânica** (§3.3.4 do Volume 01). Corrigido em todos os pontos.

É precisamente a classe de erro que o `aluci-guard` existe para pegar: sigla
plausível, propagada por repetição, que só cai quando alguém abre o documento.

### Onde os coeficientes de consumo realmente estão

O próprio manual responde: "os **cadernos técnicos** apresentam as condições de
contorno adotadas nos cálculos dos **consumos dos materiais** e da **produção
horária dos serviços**, suas respectivas memórias e as produções de equipes
mecânicas".

Ou seja, o coeficiente não está no manual — está nos **memoriais de cálculo /
cadernos técnicos**. Endereço concreto para a Fase 2. O Volume 01 traz ainda a
Tabela 4, com massas específicas referenciais de materiais, solos e agregados.

### Supabase de produção — o que tem e o que não tem

Tabela **`public.servicos`**, 143 linhas, descrita como "SICRO/SINAPI —
composições de custo". Estrutura real conferida:

`banco`, `mes_ano`, `codigo`, `descricao`, `unidade`, `grupo`, `custo_mg`,
`custo_sp`, `custo_pr`, `custo_sc`, `embedding`.

**Não há coluna de coeficiente nem de insumo.** É tabela de **preço unitário de
serviço** por estado (SICRO 10-2025; ex.: código 0705199, "Corpo de BSCC
2,50 × 2,50 m — moldado no local — altura do aterro 1,00 a 2,50 m", unidade `m`,
grupo `G07-Bueiros-Celulares`, R$ 4.271,49 em MG). Pela regra dura do projeto —
preço não entra na base — **não gera nenhuma linha de intensidade**.

Também presentes: `sp258_drenagem_mapa` (12 linhas, quantidades de um projeto real
mapeadas para códigos SICRO — bottom-up, projeto único) e `field_measurements`
("medições reais de obra pós-execução"), que **existe mas está vazia** — a camada
proprietária de maior valor segue sem dado.

### Gaps do CLAUDE.md que estes acessos resolvem

Fora do escopo desta base, mas verificado de passagem e vale registrar:

| Gap | Achado |
| --- | --- |
| RLS desabilitado em 3 tabelas (AI-6) | **resolvido** — as 38 tabelas retornam `rls_enabled: true` |
| Projeto `xgluoaa…` (G012) | **confirmado morto** — não aparece na organização; só existem 4 projetos |
| 3 projetos INACTIVE | confirmado: `manta-tocantins`, `manta-rodovias`, `manta-portal-piloto` |
| Embedder (G010) | divergência **é real e agora precisa**: `manta_rag_chunks` = 1024d bge-m3; `servicos` = 1536d OpenAI text-embedding-3-small. Dois embedders coexistindo, decisão MN pendente |
| Contagens do registro | desatualizadas: `rag_collections` = 10 (não 9), `maestro_routing_keywords` = 61 (não 50), `manta_rag_chunks` = 292 (não 204), `manta_rag_documents` = 119 (não 111) |

## O que falta para fechar o piloto

Por ordem de retorno:

1. **SIDRA/PAIC por classe CNAE** (F-004) — desbloqueia S6 (42.91-0, classe
   própria), S8 (42.22-7) e S9 (42.21-9) de uma vez.
2. **Matriz de insumo-produto** (F-002) — elimina a ressalva da autoconstrução.
3. **Pesos do INCC** (F-079) — decompõe os 37,4% de materiais por família física.
   Os percentuais não saíram por busca.
4. **Sobratema** (F-068) — única fonte séria de hora-máquina de equipamento no
   Brasil; a família `equipamentos` está hoje 100% vazia. Confirmar assinatura.
5. **CONCLA** (F-007) — validar os 17 mapeamentos CNAE.
6. **S7 e S10** — sem classe CNAE dedicada; só saem por fonte setorial
   (ANAC F-026; CBDB F-074 e SNISB F-041).
7. **Comparação internacional** — Economic Census `EC2223KOB` (F-137) para
   fechar CNAE 42 ↔ NAICS 237; BEA Input-Output (F-138) como par da matriz do
   IBGE; depois OECD ICIO (F-012) e INFRALATAM (F-100).

Nada disso é limitação de método. O método está pronto, testado e roda no recorte
agregado. É limitação de acesso à rede.
