# Relatório de Validação — Piloto de Consumos por Receita Setorial

Data: 2026-08-22
Branch: `claude/pesquisa-consumos-construcao-5e2qtm`
Validador: `tools/validate_consumos.py`

## Resultado

```
OK - 8 intensidades, 136 fontes, 2 linhas de estrutura de custo, 14 mapeamentos CNAE
```

Exit code 0. Autoteste do validador: 8 de 8 regras duras disparam corretamente,
e linha válida passa limpa.

## Contra a meta do plano

| Item | Meta | Entregue | Situação |
|---|---|---|---|
| Intensidades nos 5 setores prioritários | 40–60 linhas | **0** | não atingida |
| Intensidades em recorte agregado CNAE | — | 8 linhas | fora da meta original, foi o que o acesso permitiu |
| Estrutura de custo por setor | 6 blocos | 1 bloco, 81,9% não decomposto | não atingida |
| Comparação internacional | 2 setores | 0 | não atingida |
| Catálogo de fontes | 100–130 | **136** | atingida |
| Crosswalk CNAE | — | 14 mapeamentos, com grau de aderência | atingido |
| Método, schema, validador | — | completos e testados | atingido |

Matriz de cobertura: **6 de 112 células**. Os dez segmentos S1–S10 estão
inteiramente vazios.

## Causa: bloqueio de egress

A política de rede desta sessão negou o acesso às fontes. Confirmado
explicitamente pelo proxy, com erro `EGRESS_BLOCKED`, nestes domínios:

| Domínio | O que se buscava |
|---|---|
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
|---|---|---|---|
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

## O que falta para fechar o piloto

Por ordem de retorno:

1. **SIDRA/PAIC por classe CNAE** (F-004) — desbloqueia S6 (42.91-0, classe
   própria), S8 (42.22-7) e S9 (42.21-9) de uma vez.
2. **Matriz de insumo-produto** (F-002) — elimina a ressalva da autoconstrução.
3. **Pesos do INCC** (F-079) — fecha os 81,9% não decompostos da estrutura de
   custo.
4. **Sobratema** (F-068) — única fonte séria de hora-máquina de equipamento no
   Brasil; a família `equipamentos` está hoje 100% vazia. Confirmar assinatura.
5. **CONCLA** (F-007) — validar os 14 mapeamentos CNAE.
6. **S7 e S10** — sem classe CNAE dedicada; só saem por fonte setorial
   (ANAC F-026; CBDB F-074 e SNISB F-041).
7. **Internacional** — OECD ICIO (F-012) e INFRALATAM (F-100).

Nada disso é limitação de método. O método está pronto, testado e roda no recorte
agregado. É limitação de acesso à rede.
