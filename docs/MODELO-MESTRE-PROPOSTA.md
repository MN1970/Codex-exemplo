# Modelo Mestre de Proposta — correção de premissa + segregação Tarifa×Success Fee

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
| Orçamentista | Sênior | 285,00 | 50.160,00 | 427,50 |
| Orçamentista | Pleno | 176,00 | 30.976,00 | 264,00 |
| Orçamentista | Júnior | 135,38 | 23.826,88 | 203,07 |
| Estágio | Estagiário | 80,00 | 14.080,00 | 120,00 |

Notas (fonte: ficha técnica da revB, dentro da própria skill real):

1. Perfis de produtos de software ligados a IA usam as mesmas
   maturidades e tarifas de "Analista (Engenharia/Software)" — sem
   tabela específica.
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

## 5. O que fica pendente / fora do escopo desta correção

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
