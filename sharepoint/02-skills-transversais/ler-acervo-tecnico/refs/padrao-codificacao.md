# refs/padrao-codificacao.md — ler-acervo-tecnico

Método para decifrar o esquema de codificação de documentos de um
acervo técnico recebido de terceiros, e caso de referência (DERSA).

## Template genérico de detecção

A maioria dos grandes projetistas/contratantes de infraestrutura no
Brasil usa uma variação do mesmo esqueleto:

```
TIPO – EMPREENDIMENTO . SUBTRECHO . OBRA – DISCIPLINA / SEQUENCIAL _ REVISÃO
```

Onde, tipicamente:

- **TIPO** — espécie documental (2-3 letras: desenho, relatório,
  memorial descritivo, memória de cálculo, planilha, índice...).
- **EMPREENDIMENTO** — código numérico ou alfanumérico curto do
  empreendimento, constante em todo o acervo.
- **SUBTRECHO** — sub-divisão geográfica/funcional do empreendimento
  (`00` costuma significar "geral/abrangência total").
- **OBRA** — identificador de obra específica (`000` = geral/linear;
  faixas numéricas costumam separar categorias, ex. OAEs vs túneis).
- **DISCIPLINA** — código de 2-4 caracteres (letra + números) por
  especialidade técnica.
- **SEQUENCIAL** — número dentro da disciplina; faixas dentro da mesma
  disciplina costumam ter significado semântico (ex.: 100 = memórias de
  quantidade, 800 = orçamento/gestão) — **não assumir isso sem
  confirmar em um índice ou em uma amostra consistente**.
- **REVISÃO** — letra (A, B, C…), às vezes numérica.

## Procedimento de detecção

1. Nunca aplicar o template acima às cegas — ele é um ponto de partida,
   não uma verdade universal.
2. Procurar primeiro um documento de índice/relação (nomes comuns:
   "índice", "index", "ID-", "relação de documentos", "master
   document list", "MDL"). Se existir, ele quase sempre traz a legenda
   oficial da codificação — usar essa legenda, não a heurística.
3. Sem índice: amostrar nomes de arquivo em pelo menos 5 pastas
   diferentes do acervo e procurar o padrão comum (separadores mais
   frequentes, posição dos blocos alfanuméricos, faixas numéricas
   repetidas).
4. Validar a hipótese de padrão contra pelo menos 10 nomes adicionais
   antes de aplicá-la ao inventário inteiro.
5. Se a validação falhar (padrão inconsistente, múltiplos padrões
   coexistindo — comum em acervos que mesclam emissões de projetistas
   diferentes), **não forçar um único esquema**: inventariar por
   pasta/nome literal e registrar a inconsistência como achado.

## Caso de referência — esquema DERSA (Ferroanel Norte)

Usado como exemplo didático de como o método acima se aplica na
prática (fonte: Nota Técnica "Acervo Técnico do Ferroanel Norte —
Projeto Básico DERSA", v1.0, 27/08/2026):

```
TIPO – 48 . SS . OOO – DDD / NNN _ REV
```

- `TIPO`: DE desenho · RT relatório técnico · MD memorial descritivo ·
  MC memória de cálculo · PL planilha · ID índice de documentos · FD
  folha de desenho (formulário).
- `48`: código do empreendimento (Ferroanel Norte), constante em todo o
  acervo.
- `SS`: sub-trecho (`00` = abrangência geral).
- `OOO`: obra (`000` geral/linear; `001–052` OAEs e passagens
  superiores; `101–113` túneis T01–T13; `100` conjunto de túneis).
- `DDD`: disciplina — ex. `A10` (geral/orçamento/plano de execução),
  `A12` (gestão documental), `C10/C11` (estruturas), `F10` (traçado),
  `G10` (geologia/geotecnia), `H08/H10` (hidrologia/drenagem), `I10`
  (interferências), `O10` (operacional), `P10` (pavimentação), `Q10`
  (terraplenagem), `S10` (acústica).
- `NNN`: sequencial — faixas semânticas por disciplina (ex., em `A10`,
  série 100 = memórias de quantidades, série 800 = orçamento/gestão) —
  confirmado no índice-mestre desse acervo, não assumido a priori.
- `REV`: revisão alfabética (até G observado nesse acervo).

Ponto de atenção recorrente nesse tipo de esquema: a distinção entre a
série que traz **quantidades para orçamento** (ex. `A10`) e a série que
traz **cálculo estrutural/dimensionamento** (ex. `C10`) é a que mais
gera confusão nas equipes — vale sempre explicitar essa diferença no
briefing, não só decifrar o código.

## O que registrar no relatório final

- A tabela `TIPO`/`SS`/`OOO`/`DDD`/`NNN`/`REV` (ou o equivalente
  identificado) com um exemplo real de cada campo.
- A tabela de disciplinas identificadas → onde aparecem com mais peso.
- Um exemplo prático de "tradução" (ex.: "quero a memória de
  quantidades da Obra 12" → código X, pasta Y) — é o que realmente
  acelera o uso do acervo pela equipe.
