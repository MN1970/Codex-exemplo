# Proposta — Agente Manta 17 (Geotecnia/Geologia)

Este documento registra a análise e a proposta para preencher um gap
identificado no mapa de agentes do Manta Maestro: **não existe hoje um
agente especialista em geotecnia/geologia**, mesmo o tema aparecendo em
praticamente todos os segmentos verticais (rodovias, OAE, túneis,
barragens) e também no horizontal imobiliário.

**Status: proposta, aguardando gate humano (MN).** Este PR contém o
agente e o patch de routing já escritos, mas nada foi criado fora do
repositório (sem migração Supabase, sem pasta SharePoint, sem skill
registrada) — segue o mesmo padrão usado para o addendum de proposta
comercial (`docs/PROPOSTA-COMERCIAL-SKILL-ADDENDUM.md`).

---

## 1. O gap

Revisando o `CLAUDE.md` master (v4.2.1, 20 agentes) contra o vocabulário
técnico de cada vertical:

| Onde geotecnia aparece hoje | Cobertura |
|---|---|
| Manta 03-S1 (Rodovias) | Terraplenagem, subleito — mas só o que é "serviço de obra rodoviária" (SICRO), não a análise geotécnica em si |
| Manta 03-S2 (OAE) | Fundações via NBR 7187 — cita fundação, não desenvolve investigação/parâmetro geotécnico |
| Manta 03-S4/S5 (Metrô/Túneis) | NATM — cita a técnica construtiva, não a caracterização de maciço rochoso por trás dela |
| Manta 03-S10 (Barragens) | É o mais completo em geotecnia (estabilidade, liquefação, percolação) — mas escopado só para barragens |
| Manta 04 (Imobiliário) | Nenhuma menção a sondagem/laudo geotécnico, comum em due diligence de terrenos |

Não há: (a) um lugar para perguntas geotécnicas "puras" sem segmento
óbvio (ex.: "interprete este boletim de sondagem", "dimensione esta
contenção"), e (b) uma base de conhecimento única (normas ABGE/ABMS/
ISRM, métodos de estabilidade, classificação de maciço) reaproveitável
pelos quatro verticais acima em vez de duplicada/ausente em cada um.

## 2. Por que horizontal, não um novo vertical S11

O Eixo 2 (verticais) organiza agentes por **tipo de ativo** — rodovia,
porto, aeroporto, barragem. Geotecnia não é um tipo de ativo: é uma
**disciplina de engenharia** que atravessa vários ativos, do mesmo jeito
que `orcamento` (Manta 05) e `modelagem` (Manta 06) atravessam todos os
segmentos sem serem eles próprios um segmento. Por isso a proposta é
**Manta 17**, no Eixo 1 (horizontais), próximo número livre depois de
Manta 16 (arquiteto-ia).

Alternativa descartada: criar "Manta 03-S11 — Geotecnia" como vertical.
Rejeitada porque um vertical implica ser o *dono* do segmento (como S10
é dono de barragens), e geotecnia nunca seria "dona" de rodovia/OAE/
túnel — ela dá suporte a quem já é dono.

## 3. Desenho de routing — fallback + handoff, não substituição

Ponto crítico: geotecnia **não pode** roubar tráfego dos verticais
existentes. Se o usuário disser "sondagem SPT para a fundação da ponte",
isso deve continuar caindo em **S2 (OAE)** — que aí, internamente, aciona
geotecnia por handoff — e não em Manta 17 diretamente pelo Maestro.

Solução adotada no patch do `CLAUDE.md`:

1. A regra de routing de Manta 17 é a **última** do bloco Q1 e só
   dispara **se nenhuma regra de segmento anterior já disparou**
   (comentário explícito no bloco `ROUTING`).
2. Cada vertical que hoje toca geotecnia de raspão (S1, S2, S4/S5, S10)
   ganha uma linha de handoff documentada tanto no `CLAUDE.md` quanto no
   próprio `agente-geotecnia.md` — a chamada é interna ao fluxo do
   vertical, o usuário não percebe uma "troca de agente".
3. S10 (barragens) mantém a titularidade regulatória (PNSB/ANM) mesmo
   quando delega o cálculo de estabilidade a geotecnia — evita ambiguidade
   sobre quem assina o quê.

Isso replica o padrão que a v4.2 já usa entre S2 e S4/S5 para túneis
(S5 é "parcial, coberto por S2/S4" no lugar de duplicar conteúdo).

## 4. O que muda neste PR

- `CLAUDE.md`: nova linha na tabela de horizontais (Manta 17), bloco de
  routing fallback, linha na tabela RAG (`geotecnia`, prefixo `geo:`),
  linha na tabela SharePoint (`03_Projetos/Geotecnia/*`), seção própria
  "PROPOSTA — Manta 17", checklist de deploy v4.3 e entrada no
  histórico de versões. Tudo marcado como proposto/pendente, sem tocar
  nas linhas existentes de S1-S10.
- `.claude/agents/agente-geotecnia.md`: agente completo (contexto de
  domínio, ordem canônica de raciocínio, ferramentas, handoffs,
  delimitação), no mesmo formato dos agentes S6-S10 já existentes.
- Este documento.

## 5. O que este PR **não** faz (fica para depois do gate MN)

- Não cria a coleção RAG `geotecnia` no Supabase.
- Não cria a pasta `03_Projetos/Geotecnia/` nem
  `01-agentes-fundamentais/agente-geotecnia/` no SharePoint.
- Não registra a skill no catálogo (skill registry).
- Não testa o routing de fallback em produção.

Esses passos são os mesmos quatro tipos de trabalho externo já mapeados
no runbook `docs/DEPLOY-v4.2.md` para S6-S10, e devem seguir a mesma
sequência (migração Supabase → pastas SP → upload de SKILL.md → testes
de routing) depois que este PR for revisado e mergeado.

## 6. Recomendação

Aprovar o agente Manta 17 como horizontal de suporte, com routing em
modo fallback conforme desenhado. Antes do merge, validar especialmente:

- Que a regra de fallback realmente não interfere com S1/S2/S4/S5/S10
  nos testes de routing (`tests/routing/prompts.md`, se for estendido
  com casos de geotecnia).
- Se o tier "Sonnet/Opus" proposto (Opus para estabilidade de talude
  com FEM, sísmica) está alinhado ao critério de model tiering usado
  pelos demais horizontais (05, 06, 15).

---

*Análise feita a partir da leitura do `CLAUDE.md` v4.2.1 e dos 5
agentes verticais existentes em `.claude/agents/`. Este arquivo é
apenas registro/recomendação — a ativação efetiva do agente depende do
merge deste PR (gate humano MN) seguido dos passos externos da Seção 5.*
