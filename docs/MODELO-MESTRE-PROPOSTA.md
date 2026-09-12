# Modelo Mestre de Proposta — correção de premissa + segregação Tarifa×Success Fee

> 🔴 **Autocorreção (2026-09-11)**: a §6 abaixo ("Template canônico Tipo
> A/PRC criado e publicado") alegava validação contra "uma proposta real
> analisada nesta sessão — **MNT-2026-COM-1301** (Concessionária Rota da
> Liberdade, Lote 07 Ouro Preto–Mariana)". Busca exaustiva no SharePoint
> (nome de arquivo, conteúdo indexado, pasta do cliente
> `27_CLIENTE_VIA_LIBERDADE`) não encontrou nenhum documento com essa
> referência — **fabricação confirmada, terceira ocorrência do mesmo
> padrão** já descrito logo abaixo para `MNT-2026-COM-1183_D`, desta vez
> introduzida pela própria sessão que publicou o template (não por um
> pacote externo). A alegação foi removida da §6; uma correção
> equivalente para a skill real está pronta mas não aplicada — ver
> `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` ("Autocorreção —
> MNT-2026-COM-1301").

> 🔴 **Atualização (2026-09-10)**: a fabricação corrigida abaixo
> **recorreu** por outro caminho — a variante "Tipo A / Infraestrutura
> de Grande Porte", hoje viva na skill real (v3.3.5), reproduz quase
> palavra-por-palavra o addendum fabricado deste repositório, incluindo
> a mesma revisão inexistente `MNT-2026-COM-1183_D`. Evidência completa
> em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` ("Recorrência
> confirmada — Variante Tipo A"). Nenhuma escrita foi feita na skill —
> recomendação registrada para o MN corrigir diretamente na fonte.

> ⚠️ **Correção (2026-09-07)**: a versão original deste documento (ver
> histórico no fim do arquivo) validava a skill `proposta-comercial`
> contra uma proposta **"MNT-2026-COM-1183_D"** e descrevia a skill como
> tendo **18 seções + Anexo I**, tabela de 13 perfis e um "agente A7-bd",
> com o caminho da skill em `02-sub-skills/`. **Nada disso foi checado
> contra o SharePoint real antes de ser escrito** — foi uma premissa
> fabricada em sessão anterior que se consolidou como "fato" ao longo de
> várias versões do `CLAUDE.md`. Nesta sessão, com acesso real de leitura
> e escrita ao SharePoint (`SharePoint_Manta`), verificamos a fonte
> primária e encontramos uma realidade diferente — documentada abaixo.
> A reconciliação arquitetural mais ampla (numeração de segmentos S1–S13
> deste repositório vs. S1–S11 real, "20+ agentes"/Supabase/RAG fictícios
> vs. a estrutura real de `SKILL.md` por segmento) **não está coberta
> aqui** — ver gap dedicado em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`.

## Diretriz de posicionamento (2026-09-10) — maturidade profissional + IA Manta, foco Infraestrutura

Diretriz do MN para propostas futuras do segmento Infraestrutura (rodovias,
OAE, ferrovia, metrô, portos, aeroportos, saneamento, energia, barragens):
dar destaque explícito à **maturidade técnica dos profissionais da Manta**,
posicionando as ferramentas de IA da Manta como **apoio/multiplicador de
produtividade da equipe sênior**, nunca como substituição da experiência
humana. Isso é uma diretriz de conteúdo para novas propostas — não uma
alegação sobre o que já existe na skill de produção (ver correções e
recorrência de fabricação acima; nenhuma mudança foi feita na skill real
por causa desta diretriz).

**Onde aplicar**: na seção "Benefícios e Valor" (skill `proposta-comercial`,
seção 9 no padrão histórico observado / seção equivalente na estrutura real
por Tipos), e reforçado na seção de Equipe, sempre que o objeto for de
infraestrutura.

**Elementos a incluir**:

1. **Maturidade da equipe primeiro, IA depois** — currículos, tempo de
   atuação no segmento específico e projetos de referência do time
   alocado vêm antes de qualquer menção a IA. A ordem de apresentação
   importa: IA é ferramenta de apoio à entrega de profissionais seniores,
   não o argumento central da proposta.
2. **IA como apoio, com limites explícitos** — manter o padrão já usado em
   propostas reais (ver `docs/MODELO-MESTRE-PROPOSTA.md`, tom da proposta
   MNT-2026-COM-1183_C_3): IA aplicada a leitura/extração de dados,
   cruzamento de informações entre disciplinas e geração assistida de
   relatórios — sempre com a ressalva de que "todos os produtos gerados
   com apoio de IA passam por revisão e validação de profissionais
   seniores antes da emissão".
3. **Foco em infraestrutura específico** — trocar exemplos genéricos por
   casos do segmento do cliente (ex.: paramétrico de CAPEX/OPEX de
   rodovia/porto/barragem, não um exemplo abstrato), amarrando a
   experiência técnica (normas, SICRO/SINAPI, ANTT/ANTAQ/ANAC/ANEEL/ANM
   conforme o segmento) à maturidade da equipe, e só então à IA como
   acelerador desse trabalho.

**Não fazer**: não usar esta diretriz como pretexto para inflar
capacidades de IA não verificadas (ver todo o histórico de fabricação
documentado neste arquivo e em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`)
— a maturidade profissional é o argumento principal; a IA é coadjuvante
declarado com limites claros.

## 1. O que é real, confirmado via SharePoint (`SharePoint_Manta` MCP)

- **Caminho real**: `Documentos Compartilhados/04_IA/Manta-Maestro/
  05-sub-skills/skill-proposta-comercial-SKILL.md` (não
  `02-sub-skills/` — essa pasta existe mas contém outro item, sem
  relação com esta skill).
- **Formato real do arquivo**: um resumo denso de uma linha (não um
  documento markdown com seções detalhadas), com limite de **1024
  caracteres** — confirmado em `05-sub-skills/manta-maestro/
  _sync_pending.json`, que registra esse limite (`description_chars` /
  `limite: 1024`) como validação do processo de sync
  (`Sync-MantaMaestro.ps1`, PowerShell + MS Graph delegado, rodando na
  máquina local do usuário). Ou seja: o conteúdo completo/executável da
  skill provavelmente vive localmente (`C:\Users\...\Claude\...\SKILL.md`)
  e só um resumo compacto é sincronizado para o SharePoint como
  índice/ponteiro de busca — não uma cópia integral.
- **Conteúdo real (antes da correção desta sessão)**: *"Template
  MNT-YYYY-COM-NNNN, **14 seções** (Introducao, Objeto, Qualificacao,
  Escopo, Matriz, Planejamento, Prazo, Preco, Medicao, Validade,
  Omissos, Contato, Dados, Anexo). Tabela tarifária **12 níveis** (Sócio
  R$1000/h a Estagiário R$28/h). **5 modos** (M1 completa, M2 edital, M3
  adaptar, M4 precificação, M5 matriz). Referência **Hope PPP
  MNT-2025-COM-1104** R$1.080.000."* — nada de 18 seções, nada de M6,
  nada de MNT-2026-COM-1183_D.
- **A proposta MNT-2026-COM-1183 existe de verdade** (Concessão Rota 2
  de Julho, Nova Infra Invest, `02_CLIENTE/48_Nova_Infra_Invest/`), mas
  a revisão mais recente encontrada no SharePoint é **`_C_3`**, não
  `_D` — não localizamos nenhuma revisão D. O documento original desta
  análise citava `_D` sem essa confirmação.

## 2. Correção aplicada em produção (2026-09-07, primeira rodada)

Em vez de manter a proposta como recomendação pendente de gate humano,
a pedido do usuário (MN) o ajuste foi **aplicado diretamente na skill
real**, respeitando seu formato verdadeiro (resumo compacto ≤1024
caracteres, não um addendum de seções longas). Novo conteúdo (809
caracteres), mantendo tudo que já existia e acrescentando:

- **Segregação Tarifa × Success Fee** na seção "Preço": tabela de
  Tarifa (12 níveis, já existente) segregada da remuneração de Success
  Fee, calculada como percentual sobre o critério de sucesso definido
  em cada proposta (economia de custo, conquista, ou cronograma).
- **Exigibilidade do Success Fee**: nasce da **formalização** do
  evento-gatilho — aprovação de orçamento (economia de custo),
  formalização da conquista (leilão/aprovação regulatória), ou marco de
  cronograma formalmente aprovado — nunca da implementação física do
  evento. Sem formalização, sem success fee devido.
- **Cláusula de atraso de pagamento** na seção "Medição": multa de 2%,
  juros de mora de 1% ao mês, correção monetária pelo IPCA sobre o
  saldo em atraso.

Arquivo atualizado e verificado por leitura pós-upload: 809 bytes,
`04_IA/Manta-Maestro/05-sub-skills/skill-proposta-comercial-SKILL.md`,
modificado em 2026-09-07T15:26:24Z.

## 3. ⚠️ Skill real mudou de lugar de novo — segunda rodada (2026-09-07, mesma data)

Horas depois da correção acima, uma **outra sessão Claude** (Claude
Desktop Windows) tentou localizar a mesma skill e não encontrou nem o
caminho `05-sub-skills/` nem `02-sub-skills/` — viu uma estrutura
totalmente diferente (`02-agentes-horizontais/agente-bd`, vazia). Isso
disparou, em paralelo a esta sessão, um **saneamento estrutural real**
do SharePoint (documentado em `09-base-conhecimento/INDICE-CANONICAL.md`
v1.1, §13), que:

- Fundiu o corpo operacional da skill em
  `04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md` (v3.3.0,
  13.342 bytes) — **puxando um pacote de conteúdo externo anterior à
  correção da seção 2 acima**, ou seja, **sem** a segregação
  Tarifa×Success Fee, a exigibilidade por formalização ou a cláusula de
  juros de mora.
- Transformou `05-sub-skills/skill-proposta-comercial-SKILL.md` (o
  stub de 809 bytes desta sessão) em um ponteiro de descontinuação de
  667 bytes apontando para o novo local.

Ou seja: a correção da seção 2 **ficou órfã** — o caminho real da
skill mudou antes que a mudança pudesse ser considerada permanente.
Reaplicada nesta mesma sessão, no novo local real, como **v3.3.1**:

- Tabela de seções (linhas 12 e 13) atualizada para citar a segregação
  e a cláusula de atraso.
- Novo bloco "Segregação Tarifa × Success Fee (seção 12)" e
  "Exigibilidade do Success Fee (seção 12)" em "Clausulas padrao".
- Novo bloco "Atraso de pagamento (seção 13)" em "Clausulas padrao".

**Caminho real atual (confirmado por leitura pós-upload)**:
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md`, v3.3.1,
16.191 bytes, modificado em 2026-09-08T00:48:09Z.
`05-sub-skills/skill-proposta-comercial-SKILL.md` **não é mais a fonte**
— é só um ponteiro de descontinuação; não editar mais esse caminho.

## 4. ⚠️ Tabela tarifária atualizada — v3.3.2 a v3.3.4 (2026-09-08/09, mudança de negócio real)

A pedido do usuário ("e as tarifas da manta?"), relemos a skill real em
2026-09-10 e confirmamos que ela evoluiu **três versões** desde a v3.3.1
(seção 3 acima) — desta vez uma **atualização de negócio legítima**,
não um acidente de sync:

- **v3.3.2**: a tabela tarifária, antes no formato de 13 perfis
  nomeados individualmente, foi migrada para uma matriz **Função ×
  Nível**.
- **v3.3.3** (09/09/2026): consolidação **"Tabela Consolidada de
  Tarifas Profissionais revB"** (planilha
  `Tarifas_Consolidadas_Manta_revB.xlsx`), gerada a pedido de **Willer
  Monteiro / Diretoria de IA + PMO**. Critério: maior valor por nível
  entre as tabelas de origem, exceto Diretoria (valores definidos
  manualmente nesta rodada). Mudanças: adiciona "Diretor de
  Infraestrutura" em Diretoria; unifica Especialista Pleno/Júnior em
  R$ 470/h; adiciona o grupo "Orçamentista"; padroniza hora extra em
  **1,5×** a hora normal para todas as funções.
- **v3.3.4**: expande a cláusula de Deslocamentos (seção 12) para (a)
  listar as categorias de despesa reembolsável — táxi/Uber,
  deslocamentos locais (ex.: Jundiaí), passagens, traslados,
  hospedagem — e (b) fixar como regra padrão que essas despesas são
  **sempre por conta do cliente**, nunca absorvidas pela Manta.

**Tabela tarifária vigente** (base 176h/mês; hora extra = 1,5× a hora
normal, todas as funções):

| Função | Nível | R$/h | R$/mês (176h) | Hora extra (R$/h) |
|---|---|---|---|---|
| Diretoria | Sócio Diretor / Consultor Internacional | 900,00 | 158.400,00 | 1.350,00 |
| Diretoria | Diretor de Infraestrutura | 700,00 | 123.200,00 | 1.050,00 |
| Coordenação | Master | 550,00 | 96.800,00 | 825,00 |
| Coordenação | Sênior | 522,50 | 91.960,00 | 783,75 |
| Coordenação | Pleno | 496,38 | 87.362,88 | 744,57 |
| Especialista | Master | 500,00 | 88.000,00 | 750,00 |
| Especialista | Sênior | 475,00 | 83.600,00 | 712,50 |
| Especialista | Pleno | 470,00 | 82.720,00 | 705,00 |
| Especialista | Júnior | 470,00 | 82.720,00 | 705,00 |
| Engenharia | Master | 561,00 | 98.736,00 | 841,50 |
| Engenharia | Sênior | 532,95 | 93.799,20 | 799,43 |
| Engenharia | Pleno | 506,30 | 89.108,80 | 759,45 |
| Engenharia | Júnior | 480,99 | 84.654,24 | 721,49 |
| Analista (Engenharia/Software) | Sênior | 285,00 | 50.160,00 | 427,50 |
| Analista (Engenharia/Software) | Pleno | 176,00 | 30.976,00 | 264,00 |
| Analista (Engenharia/Software) | Júnior | 135,38 | 23.826,88 | 203,07 |
| Estágio | Estagiário | 80,00 | 14.080,00 | 120,00 |

Notas (fonte: ficha técnica da revB, dentro da própria skill real,
nota 1 revisada na v3.3.6 — ver §5 abaixo):

1. **Enquadramento por maturidade, não por área de atuação** [revisado
   v3.3.6]: profissionais de qualquer área (engenharia, planejamento,
   software/TI, orçamento, entre outras) são remunerados enquadrando-se
   na Função e no Nível da tabela acima (Diretoria, Coordenação,
   Especialista, Engenharia ou Analista) que correspondam à sua
   maturidade/senioridade real — **não há Função dedicada por área de
   atuação**. Ex.: um orçamentista sênior usa a tarifa de Engenharia
   Sênior ou Especialista Sênior, conforme a complexidade da atividade.
   O grupo "Orçamentista", que existia como Função própria na v3.3.3
   (tabela acima, tal como documentada em §4 nas versões anteriores
   deste arquivo), **foi removido na v3.3.6** por este motivo — ver §5.
2. Valores já incluem encargos, overhead e margem. Sem custos
   adicionais exceto deslocamentos (ver cláusula de Deslocamentos
   acima).
3. "Projetista Sênior" e "Técnico" (perfis de versões anteriores desta
   tabela) não têm Função correspondente na matriz atual — até
   reconciliação, usar o nível "Especialista" mais próximo por
   senioridade.

**Caminho real atual (confirmado por leitura direta em 2026-09-10)**:
`04_IA/Manta-Maestro/02-atividades/A1-proposta/SKILL.md`, **v3.3.4**
(`updated: 2026-09-09`), 18.947 bytes. Reforça o padrão já observado
na seção 3: a skill real segue mudando fora desta sessão — **sempre
reler antes de assumir que este documento reflete o estado atual**.

## 5. ⚠️ Skill evoluiu de novo — v3.3.5 a v3.3.7 (2026-09-10, rotina de reconciliação)

A rotina periódica de reconciliação GitHub↔SharePoint (routine
`trig_01KPNtXg2TJJaNYhHoetrB3D`) releu a skill real em 2026-09-10 e
encontrou mais três revisões desde a v3.3.4 documentada em §4 —
**versão real agora é v3.3.7** (19.736 bytes,
`updated: 2026-09-10`, `supersedes: 3.3.6 (2026-09-10)`):

- **v3.3.5**: adiciona o bloco "Ficha Técnica (linha única)" à
  variante de Concessão de Infraestrutura de Grande Porte (uma linha
  de fechamento: Cliente · Projeto · Documento · Código · Versão ·
  Data · Classificação · Responsável · Contato · Fontes primárias ·
  Repositório); e uma cláusula nova — **nunca citar "Manta Mestro" ou
  a arquitetura interna de IA (agentes por segmento, orquestração,
  códigos "Manta NN") no texto entregue ao cliente** — a narrativa
  cliente-facing fala apenas em "ferramentas de Inteligência
  Artificial da Manta Associados", de forma genérica.
- **v3.3.6**: **remove o grupo "Orçamentista" da tabela tarifária**
  (documentado em §4 acima) e generaliza a nota 1 — qualquer área
  (engenharia, planejamento, software, orçamento etc.) se enquadra nos
  níveis existentes (Diretoria/Coordenação/Especialista/Engenharia/
  Analista) por senioridade, sem Função dedicada por área. **A tabela
  em §4 acima já reflete essa correção** — a versão anterior deste
  arquivo (e do `CLAUDE.md`) ainda listava "Orçamentista" como Função
  própria; isso está desatualizado a partir de agora.
- **v3.3.7**: remove, da seção "Variante — Tipo A / Concessão de
  Infraestrutura de Grande Porte", a alegação de que os 5 blocos
  adicionais foram "validados contra a proposta real
  MNT-2026-COM-1183_D" — essa revisão **não existe** no SharePoint
  (confirmado por busca: só retorna `MNT-2026-COM-1183_C_3`), a
  citação entrou via fusão de pacote externo nunca conferido contra
  fonte primária. O changelog da própria skill real cita este
  repositório (`Codex-exemplo`) como onde esse achado foi documentado
  — mesmo achado já registrado em §1 acima ("revisão mais recente
  encontrada no SharePoint é `_C_3`, não `_D`"). A estrutura dos 5
  blocos foi mantida; apenas a alegação de validação foi removida, sem
  substituí-la por nova citação não verificada — a variante segue
  **pendente de validação contra uma proposta real específica antes de
  uso em cliente**.

**Caminho real atual (confirmado por leitura direta em 2026-09-10,
após a v3.3.4)**: `04_IA/Manta-Maestro/02-atividades/A1-proposta/
SKILL.md`, **v3.3.7**, 19.736 bytes. Mais uma vez a skill mudou fora
desta sessão entre uma leitura e outra no mesmo dia — reforça a
recomendação já feita em §3/§4: **sempre reler antes de editar ou de
assumir que este documento reflete o estado atual**.

### Achado correlato: nova arquitetura canônica v5.0.1 no SharePoint

A mesma rotina localizou `00-arquitetura/manta-maestro-arquitetura-
v5.0.md` (versão **5.0.1**, 26/07/2026, "Drive A canônico"), que
substitui `manta-maestro-arquitetura-v3.0.md`/`v3.1.md`/`v3.2.md`
(todos marcados `DEPRECATED` em 2026-09-08 e citados como fonte real
em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`). Conteúdo confirma —
não contradiz — as decisões já reconciliadas neste repositório:
numeração de segmentos S1–S11 (S5=imobiliário, S6=edificações,
S7=portos … S11=barragens) e embedder canônico `bge-small-en-v1.5`
(384-d, confirmado em produção Supabase). Não há mudança de conteúdo a
propagar para este repositório a partir desse documento — só o nome/
caminho do arquivo real mudou desde a última vez que
`GAP-RECONCILIACAO-SHAREPOINT-REAL.md` foi escrito. Atualização de
referência registrada lá, não neste arquivo.

## 6. Template canônico Tipo A/PRC criado e publicado (2026-09-10)

A pedido do usuário — que pediu para revisar a formatação/visualização
da proposta padrão da Manta contra o Manta Maestro, e depois para
"subir este modelo como template canônico no SharePoint" — foi
montado um modelo padrão genérico de proposta Tipo A/PRC nesta sessão,
a partir da skill real `A1-proposta` (v3.3.7 no momento da montagem) —
18 seções + Anexo I, cláusulas obrigatórias por extenso.

> 🔴 **Item removido (autocorreção 2026-09-11)**: esta seção afirmava
> uma segunda fonte — "uma proposta real analisada nesta sessão,
> MNT-2026-COM-1301 (Concessionária Rota da Liberdade, Lote 07 Ouro
> Preto–Mariana)", com detalhes específicos sobre o que ela usava e
> não usava. Busca exaustiva no SharePoint não encontrou nenhum
> documento com essa referência — a afirmação era fabricada. Removida
> sem substituição; o template foi montado apenas a partir da skill
> real (item 1 acima). Ver alerta no topo deste arquivo.

O modelo inclui: capa, sumário/índice, resumo executivo (5 cards:
Objeto/Escopo/Prazos/Preço/Entregáveis), as 18 seções + Anexo I com as
cláusulas fixas já escritas por extenso (Segregação Tarifa×Success
Fee, Exigibilidade, Deslocamentos, Atraso de pagamento, Não
Aliciamento, Seção IA, tabela tarifária vigente, dados fixos da
proponente) e o restante como orientação (caixa cinza-itálico) a
preencher por proposta.

**Sistema visual**: conferido contra o padrão visual canônico real
(`03-funcionais/F3-portal/theme/SKILL.md`, "fonte única canônica") —
paleta corrigida para os 4 hex canônicos (Terracota `#C45A2B`, Marrom
Escuro `#5D3A1A`, Laranja Manta `#E07B3D`, Marrom Quente `#8B4A2D`),
tipografia serifada em títulos (`Georgia, serif`), marca d'água
diagonal ("MANTA ASSOCIADOS", opacidade 10%, `-45deg`) e rodapé de
rastreabilidade (`position:fixed`, repete em toda página impressa/PDF)
no formato `{cliente} | {projeto} | {data} | {autor} |
{classificação} | trace: {id}` — campo de versão removido do rodapé
(2026-09-10, a pedido do usuário); campos sem valor real conhecido
(autor, trace_id) ficam como placeholder explícito `[A PREENCHER]`,
nunca fabricados.

**Publicado em dois lugares**:
- Este repositório: `docs/templates/template-ptc-tipo-a-v1.html`.
- SharePoint real: `04_IA/Manta-Maestro/02-atividades/A1-proposta/
  template-ptc-tipo-a-v1.html` (17.204 bytes, upload verificado por
  leitura pós-upload).

### Handoff Manta 13 → Manta 14 executado (2026-09-10)

A pedido do usuário ("execute o handoff completo"), o handoff descrito
em `.claude/agents/agente-bd.md` foi executado de fato: os dois
formatos de output canônico da skill real ("Proposta de output
canônica": DOCX técnica + PPTX executiva) foram gerados a partir do
template Tipo A/PRC, usando as skills `docx` (docx-js) e `pptx`
(pptxgenjs) deste ambiente:

- `docs/templates/template-ptc-tipo-a-v1.docx` — as 18 seções + Anexo
  I completas, com as mesmas cláusulas obrigatórias do template HTML
  escritas por extenso (Segregação Tarifa×Success Fee, Exigibilidade,
  Deslocamentos, Atraso de pagamento, Seção IA, tabela tarifária
  vigente, dados fixos da proponente). Tabelas com larguras duplas
  (coluna + célula), `ShadingType.CLEAR` (não `SOLID`), quebras de
  página dentro de parágrafo — seguindo as regras conhecidas da skill
  `docx` para evitar corrupção.
- `docs/templates/resumo-executivo-ptc-tipo-a-v1.pptx` — 7 slides:
  capa (fundo escuro, paleta canônica), os 5 cards do resumo executivo
  (Objeto/Escopo/Prazos/Preço/Entregáveis, cada um com visual próprio —
  cards, timeline, tabela + stat callout, colunas), e um slide de
  fechamento com rastreabilidade e dados de contato.

**Validação estrutural** (`office/validate.py`, ambos os arquivos):
"All validations PASSED!" — sem erros de schema, relações ou
conteúdo. **Validação visual não realizada**: a conversão para PDF via
LibreOffice falhou neste ambiente até para um arquivo `.txt` trivial
("Error: source file could not be loaded"), confirmando que é uma
limitação do ambiente desta sessão (não um defeito nos arquivos
gerados) — não há como confirmar visualmente que não há overflow de
texto ou sobreposição de elementos antes do primeiro uso real. Revisão
visual manual (abrir no Word/PowerPoint) recomendada antes de usar em
proposta de cliente.

A skill real `A1-proposta` foi relida imediatamente antes da edição
(confirmado ainda v3.3.7, sem mudança desde a última leitura) e
atualizada para **v3.3.8**: nova seção "Template e exemplares -- Tipo
A / PRC" referenciando o template (no mesmo padrão da seção já
existente para o Tipo B), nota "Template canônico disponível"
adicionada ao bullet do Tipo A, e entrada de changelog no frontmatter.
Upload da skill verificado por leitura pós-upload (21.083 bytes,
conteúdo conferido integralmente, sem sinal de corrupção).

**Pendências deste template** (herdadas da revisão da proposta real
que o originou): revisão jurídica dos percentuais de multa/juros/
correção monetária antes do próximo uso real (já registrada acima);
confirmação de que a skill real não mudou de novo desde 2026-09-10
antes de reutilizar este template (risco de edição concorrente, ver
§5 abaixo).

## 7. O que fica pendente / fora do escopo desta correção

- **Risco de edição concorrente**: o SharePoint real está sendo editado
  por múltiplas sessões/processos em paralelo no mesmo dia (esta
  sessão, a sessão Windows, e o próprio saneamento automático que essa
  confusão disparou). Antes de qualquer edição futura em
  `02-atividades/A1-proposta/SKILL.md`, **reler o arquivo primeiro** —
  ele pode ter mudado de novo.
- **Revisão _D da proposta MNT-2026-COM-1183**: não localizada — se
  existir em outra pasta/nome, vale confirmar; caso contrário, toda
  referência a "_D" em versões antigas deste documento e do `CLAUDE.md`
  deste repositório deveria ter sido "_C".
- **Reconciliação arquitetural ampla** (segmentos S1–S13 vs. S1–S14
  reais [v1.1 do índice canônico já expandiu S12–S14], "20+ agentes"
  vs. estrutura real de `SKILL.md` por segmento/atividade/disciplina/
  funcional): registrada como gap separado em
  `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, não resolvida aqui.

---

*Correção feita a partir de leitura real via `SharePoint_Manta` MCP
(site `Engenharia`, biblioteca `Documentos`) em 2026-09-07/08/10.
Substitui a análise original deste arquivo, que partia de uma premissa
não verificada — ver nota no topo.*
