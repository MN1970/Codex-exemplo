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

## 2. Correção aplicada em produção (2026-09-07)

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

## 3. O que fica pendente / fora do escopo desta correção

- **Fonte de verdade duplicada**: se existir mesmo uma cópia local mais
  completa da skill (ver `_sync_pending.json` de outra skill,
  `manta-maestro`, como exemplo do padrão), o próximo `Sync-MantaMaestro.ps1`
  rodado a partir da máquina local **pode sobrescrever** esta edição se
  a versão local não tiver sido atualizada com o mesmo conteúdo. Ação
  recomendada: MN atualizar a cópia local equivalente (se existir) para
  não perder esta mudança no próximo sync.
- **Revisão _D da proposta MNT-2026-COM-1183**: não localizada — se
  existir em outra pasta/nome, vale confirmar; caso contrário, toda
  referência a "_D" em versões antigas deste documento e do `CLAUDE.md`
  deste repositório deveria ter sido "_C".
- **Reconciliação arquitetural ampla** (segmentos S1–S13 vs. S1–S11
  reais, "20+ agentes"/RAG Supabase fictícios vs. estrutura real de
  `SKILL.md` por segmento/atividade/disciplina/funcional): registrada
  como gap separado em `docs/GAP-RECONCILIACAO-SHAREPOINT-REAL.md`, não
  resolvida aqui.

---

*Correção feita a partir de leitura real via `SharePoint_Manta` MCP
(site `Engenharia`, biblioteca `Documentos`) em 2026-09-07. Substitui a
análise original deste arquivo, que partia de uma premissa não
verificada — ver nota no topo.*
