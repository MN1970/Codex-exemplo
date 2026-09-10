# Modelo Mestre de Proposta — correção de premissa + segregação Tarifa×Success Fee

> 🔴 **Atualização (2026-09-10)**: a fabricação corrigida abaixo
> **recorreu** por outro caminho — a variante "Tipo A / Infraestrutura
> de Grande Porte", hoje viva na skill real (v3.3.5), reproduz quase
> palavra-por-palavra o addendum fabricado deste repositório, incluindo
> a mesma revisão inexistente `MNT-2026-COM-1183_D`. Evidência completa
> em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md` ("Recorrência
> confirmada — Variante Tipo A"). Nenhuma escrita foi feita na skill —
> recomendação registrada para o MN corrigir diretamente na fonte.

> ✅ **Atualização (2026-09-10, mesmo dia, sessão seguinte)**: a
> recorrência acima já foi corrigida em produção, fora deste
> repositório — skill avançou v3.3.5 → v3.3.6 (esta sessão, tabela
> tarifária) → **v3.3.7** (removeu a alegação de validação contra
> `MNT-2026-COM-1183_D`, sem substituí-la por citação não verificada) →
> **v3.3.8** (template canônico Tipo A/PRC, conferido contra
> `MNT-2026-COM-1301`/Concessionária Rota da Liberdade — ressalva: esse
> número específico não foi confirmado por busca independente, ver
> `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`). Detalhe em `CLAUDE.md`
> v5.4.11.

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

## 4. O que fica pendente / fora do escopo desta correção

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
(site `Engenharia`, biblioteca `Documentos`) em 2026-09-07/08. Substitui
a análise original deste arquivo, que partia de uma premissa não
verificada — ver nota no topo.*
