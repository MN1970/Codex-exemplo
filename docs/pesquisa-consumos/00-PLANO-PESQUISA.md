# Plano de Pesquisa — Consumos por Receita Setorial

Ticket: **MNT-2026-CONSUMOS-SETORIAIS**
Branch: `claude/pesquisa-consumos-construcao-5e2qtm`
Base: `CLAUDE.md` v4.3 (Manta Maestro)

## Escopo

**Dentro:** intensidade de consumo de 8 famílias de insumo por unidade de
receita/investimento setorial, Brasil e comparação internacional, para os
segmentos de construção pesada do registro Manta.

**Fora desta rodada:** coeficiente bottom-up por serviço (`hm/m3` de dragagem,
`hh/m` de rede, `kg cimento/m3` de CCR). Isso é a Fase 2, descrita em
`05-BACKLOG.md`. Foi decisão explícita de MN: pouca granularidade, poucas
famílias de insumo.

**Setores prioritários:** S6 Portos, S7 Aeroportos, S10 Barragens, S8 Saneamento
(prioridade AySA), S9 Energia/transmissão. S1/S2 rodovias entra como âncora de
calibração metodológica, não como alvo de coleta.

## Fases

| Fase | Conteúdo | Estado |
|---|---|---|
| 0 | Método, schema, validador, crosswalk CNAE, catálogo de fontes | **concluída** |
| 1 | Extração no recorte agregado CNAE 41/42/43 | **parcial** — 8 linhas, nenhuma verificada na fonte primária |
| 2 | Descida ao segmento S1–S13 via SIDRA por classe CNAE | **bloqueada** — egress |
| 3 | Comparação internacional (Economic Census/NAICS 237, BEA, OECD ICIO, Eurostat, INFRALATAM) | **tentada, não concluída** — numerador americano obtido, denominador bloqueado |
| 4 | Estrutura de custo completa por setor (INCC, custos e despesas da PAIC) | **parcial** — 1 bloco, 81,9% não decomposto |

## Matriz de cobertura

Gerada pelo validador, não mantida à mão:

```bash
python3 tools/validate_consumos.py --stats
```

Estado atual: **6 de 136 células** preenchidas. Todas no recorte agregado
(C41, C42, C43, CF). Os treze segmentos S1–S13 estão **inteiramente vazios**.

Meta do piloto era 40 a 60 linhas cobrindo os 5 setores prioritários. Não foi
atingida, e o motivo está em `../../data/consumos/validacao/relatorio.md`.

## O gargalo real

A PAIC publica, em release aberto, apenas os três grandes segmentos da seção F.
Para chegar a portos, saneamento ou energia é preciso consultar o **SIDRA por
classe CNAE** — e o SIDRA está bloqueado pela política de egress desta sessão,
junto com o resto do domínio `ibge.gov.br`.

Não é limitação de método. O método está pronto e testado no recorte agregado.
É limitação de acesso, e se resolve rodando a mesma coleta de um ambiente com
egress liberado para os domínios listados no relatório.

## Ordem de trabalho quando o acesso abrir

1. **SIDRA/PAIC por classe CNAE** (F-004) — desbloqueia S6 (42.91-0, classe
   própria), S8 (42.22-7) e S9 (42.21-9) de uma vez. Maior retorno por hora.
2. **Matriz de insumo-produto** (F-002) — resolve aço e cimento sem a ressalva
   da autoconstrução, porque numerador e denominador vêm do mesmo sistema.
3. **Pesos do INCC** (F-079) — fecha a estrutura de custo e habilita a rota
   indireta para as famílias sem dado físico direto.
4. **Sobratema** (F-068) — a única fonte brasileira séria de frota e
   hora-máquina. Verificar se a Manta tem assinatura.
5. **S7 e S10** — não têm classe CNAE dedicada. Só saem por fonte setorial:
   estudos de concessão da ANAC (F-026) e CBDB + SNISB (F-074, F-041).
6. **Internacional** — OECD ICIO (F-012) e INFRALATAM (F-100).

## Gates de qualidade

1. `python3 tools/validate_consumos.py` com código de saída 0.
2. Toda linha com `denominador`, `ano_base`, `deflator`, `fonte_id` e
   `fonte_localizacao`. Todo `metodo = indireto` com `memoria_calculo`.
3. Zero valor sob `licenca = cite_only`.
4. `aluci-guard` nos documentos (norma, lei, URL, sigla de fonte).
5. `consist-guard` na coerência numérica.
6. Nenhum valor `snippet_busca` em entregável de cliente.

## Checagens de sanidade de ordem de grandeza

O teste que de fato pega erro de método — multiplicar a intensidade pelo
denominador nacional e comparar com o total do país:

- **Cimento**: intensidade × valor das obras do país vs. consumo aparente do SNIC.
  Estourar o consumo nacional significa denominador errado.
- **Aço**: idem contra o consumo de laminados na construção (Instituto Aço Brasil).
- **Mão de obra**: idem contra o pessoal ocupado da PAIC e do CAGED.
- **Estrutura de custo**: participações somam 100% ± 2 pp (cobrado pelo validador)
  e a ordem de grandeza bate com os pesos do INCC.

Checagens internas que **já passaram** nos dados atuais:

- soma dos três segmentos 2022 = R$ 439,0 bi, igual ao total divulgado;
- soma do pessoal ocupado 2022 = 2.317,8 mil, coerente com os "2,3 milhões";
- participação de obras de infraestrutura em 2023 = 175,7/484,2 = 36,3%, igual ao
  percentual divulgado;
- salário médio implícito 2022 = R$ 79,6 bi / 2,3178 mi = R$ 34.343 por
  pessoa-ano, ~R$ 2.582/mês equivalente — plausível para a construção em 2022,
  o que valida numerador e denominador simultaneamente.
