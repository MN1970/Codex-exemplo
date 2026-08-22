# Governança de Licenças

Toda fonte de `registro-fontes.csv` carrega um campo `licenca` com três valores.

| `licenca` | O que pode entrar na base |
|---|---|
| `publico` | tudo — coeficiente, valor, tabela |
| `licenciado` | coeficiente entra **se** a Manta tiver assinatura vigente; marcar a linha e restringir acesso |
| `cite_only` | **nada numérico.** Só metadado: cobertura, edição, o que entrega, como acessar |

Distribuição atual: 118 públicas, 6 licenciadas, 12 cite-only.

## Regra cite-only

Doze fontes proprietárias estão catalogadas e **nenhum coeficiente delas entra na
base**: RSMeans/Gordian, Spon's, Rawlinsons, Caterpillar Performance Handbook,
Komatsu Handbook, EquipmentWatch Blue Book, ONDAC, Construdata, Revista Costos,
BIMSA/Opus, BKI, Batiprix.

O que **pode** ser registrado sobre elas:

- que existem, o que cobrem, qual edição, qual país;
- como acessar e a ordem de custo do acesso;
- a **metodologia pública** — por exemplo, que o RSMeans expressa produtividade
  como *crew daily output*, e a fórmula de conversão para `hh/unidade`. A fórmula
  é conhecimento de engenharia; a tabela de valores é o produto licenciado.

O que **não** pode:

- copiar coeficiente, produtividade tabelada, custo horário de equipamento ou
  composição, nem em CSV, nem em documento, nem parafraseado com número.

**Isso é regra de build, não recomendação.** O validador reprova qualquer linha
com `licenca = cite_only` e `valor` preenchido:

```
licenca=cite_only com 'valor' preenchido - conteudo licenciado nao entra na base
```

Verificável a qualquer momento:

```bash
python3 tools/validate_consumos.py --selftest
```

## Fontes licenciadas — verificar assinatura antes de usar

Seis fontes onde o uso depende de contrato vigente da Manta:

| Fonte | Por que importa |
|---|---|
| **Sobratema** `F-068` | melhor fonte BR de frota e hora-máquina de equipamento |
| **CII** `F-091` | benchmarking internacional de produtividade |
| **Oxford Global Projects** `F-092` | base de desvio de custo (Flyvbjerg) |
| **PIANC** `F-121` | referência técnica portuária (S6) |
| **ICOLD** `F-122` | barragens (S10) |
| **HDM-4** `F-095` | custo de ciclo de vida rodoviário (licença PIARC) |

**Pendência para MN:** confirmar quais dessas a Manta assina. Sem confirmação,
tratar como cite-only.

## Por que isso é rígido

Esta base alimenta orçamento e claim de cliente. Coeficiente de origem licenciada
dentro de um laudo assinado é exposição contratual e reputacional da Manta, não
só questão de direito autoral. O custo de manter a disciplina é ter menos linhas;
o custo de perdê-la aparece em contraditório técnico.

## Dado de projeto da Manta

Medição, as-built e diário de obra do SharePoint `03_Projetos/*` são a camada de
maior valor — é dado que nenhum concorrente tem. Regras próprias:

- `tier = D` quando vem de um único projeto (não é estatística);
- exige anonimização conforme a regra R1 de sanitização do padrão Manta
  (concessionária vira `[CLIENTE]`) antes de sair de qualquer entregável;
- só entra em faixa P10/P50/P90 com ≥ 3 projetos independentes.

Está no backlog porque depende de acesso ao SharePoint que esta sessão não tem.
