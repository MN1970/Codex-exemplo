# Base de Consumos por Receita Setorial

Quanto de insumo físico é consumido por unidade de receita/investimento em cada
segmento de construção pesada — mão de obra, equipamentos, aço, concreto,
cimento, agregados e combustível.

Não é orçamento de serviço. É intensidade macro, do tipo *"para cada R$ 1 milhão
de obra de infraestrutura, consomem-se X homem-hora e Y toneladas de aço"*.

Serve para dimensionar mercado, conferir ordem de grandeza de CAPEX, sustentar
business development e dar sanidade a orçamento bottom-up.

## Estado atual — leia antes de usar

**Nenhuma linha desta base foi verificada contra a fonte primária.** A sessão que
a construiu teve todo o acesso externo bloqueado pela política de egress
(IBGE, SNIC, Instituto Aço Brasil, Banco Mundial e demais). Os 8 valores
existentes vieram de **resultados de busca**, não da leitura dos documentos, e
estão marcados `verificacao = snippet_busca` e `tier = D`.

Consequências práticas:

- **Nenhum valor daqui vai para orçamento de cliente** antes de ser promovido a
  `fonte_primaria_lida`.
- Os **segmentos S1–S10 estão vazios**. O dado disponível só existe no recorte
  agregado da CNAE (41 edificações, 42 obras de infraestrutura, 43 serviços
  especializados). Descer ao segmento exige o SIDRA, que está bloqueado.
- O que **está** pronto e é reaproveitável: o método, o schema, o validador com
  autoteste, o catálogo de 171 fontes e o crosswalk CNAE ↔ NAICS com o grau de aderência
  de cada segmento.

Ver `validacao/relatorio.md` para o registro completo do que foi bloqueado e
o que falta para fechar o piloto.

## Estrutura

```
docs/pesquisa-consumos/
├── README.md                      este arquivo
├── 00-PLANO-PESQUISA.md           escopo, fases, matriz de cobertura
├── 01-METODO-INTENSIDADE.md       método direto x indireto, com exemplo trabalhado
├── 02-FONTES-BRASIL.md            fontes BR nas 7 camadas
├── 03-FONTES-INTERNACIONAIS.md    multilaterais e agências
├── 04-GOVERNANCA-LICENCAS.md      matriz de licença, regra cite-only
├── 05-BACKLOG.md                  Fase 2 e itens diferidos
└── 06-FONTES-EUA.md               mercado americano, ENR e o par CNAE 42 <-> NAICS 237

data/consumos/
├── schema/intensidade.schema.json
├── schema/fonte.schema.json
├── registro-fontes.csv            171 fontes catalogadas
├── crosswalk-cnae-setores.csv     CNAE 2.0 <-> S1..S10 Manta <-> NAICS
├── intensidades-setor.csv         produto principal
├── estrutura-custo-setor.csv      participação % por família
└── validacao/relatorio.md

tools/validate_consumos.py
```

## Como consultar

```bash
python3 tools/validate_consumos.py --stats     # valida e mostra a matriz de cobertura
python3 tools/validate_consumos.py --selftest  # prova que as regras duras reprovam
```

## Como contribuir

1. Abra a fonte, leia o número **no documento**, anote onde
   (`fonte_localizacao`: tabela, página, código do agregado SIDRA).
2. Se a fonte não estiver em `registro-fontes.csv`, cadastre-a primeiro — o
   validador exige a chave estrangeira.
3. Se o valor for calculado, `metodo = indireto` e `memoria_calculo` com a conta
   reproduzível. Toda premissa que não vem da fonte vai em `premissas`.
4. `verificacao = fonte_primaria_lida` **só** se você abriu o documento.
5. Rode o validador. Ele precisa sair com código 0.
