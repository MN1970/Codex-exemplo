# terraplenagem_auditor

Auditor de otimalidade para estudos de movimento de terra (terraplenagem)
em projetos rodoviários. Reconstrói o diagrama de massas (curva de
Brückner) a partir dos volumes de corte/aterro do estudo, resolve o
problema de alocação corte → aterro → jazida → bota-fora como um problema
de transporte via Programação Linear (PuLP), e compara o custo ótimo
calculado contra o custo total proposto no estudo — apontando o gap de
otimalidade e alocações potencialmente subótimas.

## O que a ferramenta faz e o que não faz

- Faz: recalcula, de forma independente, qual seria a alocação de menor
  custo para os volumes informados (execução + transporte, com free-haul
  e sobretransporte/overhaul), e mostra o quanto o estudo proposto se
  distancia desse ótimo.
- Não faz: não substitui o julgamento técnico do engenheiro responsável,
  não é uma ferramenta de conformidade oficial com o SICRO/DNIT, e não
  embute nenhuma tabela real de custos — os custos de execução (SICRO) e
  os parâmetros de transporte (free-haul, overhaul) devem ser fornecidos
  pelo usuário a partir de fontes oficiais atualizadas (Manual de Custos
  Rodoviários DNIT / SICRO vigente). Os arquivos em `exemplos/` usam
  códigos e valores ILUSTRATIVOS, não são referência oficial.
- Simplificação assumida: o custo de execução (escavação/carga/
  compactação) é aplicado como a média das composições informadas a
  todas as alocações, pois o modelo de dados atual não amarra cada
  trecho a um código SICRO específico. Refinar esse mapeamento por
  trecho/material é uma extensão natural.

## Instalação

```bash
pip install -r requirements.txt
```

## Uso via CLI

```bash
python -m terraplenagem_auditor.cli \
  --trechos exemplos/trechos_exemplo.csv \
  --jazidas exemplos/jazidas_exemplo.csv \
  --composicoes exemplos/composicoes_exemplo.csv \
  --custo-proposto 120000 \
  --saida relatorio.md
```

Rode o comando acima a partir do diretório `tools/` (para que
`terraplenagem_auditor` seja importável como pacote), ou instale o
pacote em modo editável.

Sem `--saida`, o relatório é impresso no terminal (stdout).

### Formato dos CSVs de entrada

**Trechos** (`--trechos`, obrigatório):
`estaca_inicial, estaca_final, volume_corte_m3, volume_aterro_m3, tipo_material`

**Jazidas/bota-foras** (`--jazidas`, opcional):
`nome, tipo (jazida|bota_fora), estaca, capacidade_m3, custo_unitario_extra`

**Composições de custo de execução** (`--composicoes`, opcional):
`codigo, descricao, custo_unitario, data_base`

## Uso como biblioteca

```python
from terraplenagem_auditor.io_planilha import carregar_estudo_csv
from terraplenagem_auditor.otimizador_lp import resolver_alocacao_otima
from terraplenagem_auditor.comparador import comparar
from terraplenagem_auditor.relatorio import gerar_relatorio

estudo = carregar_estudo_csv("trechos.csv", "jazidas.csv", "composicoes.csv", custo_total_proposto=120000)
resultado = comparar(estudo, resolver_alocacao_otima(estudo))
print(gerar_relatorio(resultado))
```

## Testes

```bash
pytest tests/ -q
```
