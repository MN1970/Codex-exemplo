# Gap — Reconciliação entre este repositório e o Manta Maestro real (SharePoint)

**Status:** 🔴 aberto, crítico, decisão MN pendente. **Não resolvido nesta
sessão** — escopo grande demais para ser corrigido junto de uma mudança
pontual de skill. Documentado aqui conforme combinado com o usuário em
2026-09-07.

## Como foi descoberto

Até 2026-09-07 esta sessão (e, aparentemente, todas as sessões que
escreveram este repositório antes dela) não tinha acesso real de
leitura/escrita ao SharePoint da Manta (`SharePoint_Manta` MCP). Toda a
arquitetura "Manta Maestro" documentada aqui — segmentos, agentes, RAG,
infraestrutura — foi escrita sem nunca ser checada contra a fonte real.
Ao ganhar acesso real nesta sessão (para corrigir a skill
`proposta-comercial`, ver `docs/MODELO-MESTRE-PROPOSTA.md`), a leitura
de `Documentos Compartilhados/04_IA/Manta-Maestro/09-base-conhecimento/
INDICE-CANONICAL.md` (índice canônico real, gerado 2026-07-11) revelou
divergências estruturais, não só pontuais.

## Divergências confirmadas

| Dimensão | Este repositório (`Codex-exemplo`) | SharePoint real (`INDICE-CANONICAL.md`) |
|---|---|---|
| Segmentos | S1–S13 (+ S11 "Mineração" identificado, S12 Óleo&Gás, S13 Edificações, todos "propostos") | **S1–S11**, sendo S1=Rodovias, S2=OAE, S3=Ferrovia, S4=Metrô, **S5=Imobiliário**, **S6=Edificações**, **S7=Portos**, **S8=Aeroportos**, **S9=Saneamento**, **S10=Energia**, **S11=Barragens** |
| Numeração S6–S11 | "Convenção A" (S6=Portos...S10=Barragens), com "Convenção B" explicitamente descartada nos Gaps abertos | É **exatamente** a "Convenção B" que este repositório descartou — Edificações=S6, Barragens=S11 |
| Atividades | A1–A10 (Proposta, Quantidades, Orçamento, Modelagem, Cronograma, Contratual, Claims, Advisory, Regulatório, Risco) | **Mesma lista e mesma ordem** — este eixo bate |
| Estrutura de skill | "20+ agentes" nomeados "Manta 00–25", cada um um `.claude/agents/*.md` extenso | `SKILL.md` por segmento/atividade/disciplina/funcional/sub-skill, em pastas numeradas (`01-segmentos/`, `02-atividades/`, `03-funcionais/`, `04-disciplinas/`, `05-sub-skills/`) — sem "Manta NN" como identidade central |
| RAG / infraestrutura | Supabase pgvector (projeto `ogxxgvgtulrbbppshjie`), 9 coleções, embedder bge-small/bge-m3, APScheduler, ML routing (XGBoost/NN), consensus voting, disaster recovery (RTO/RPO), Docker/K8s deploy | Nenhuma menção a isso no índice canônico — infraestrutura real parece ser MCP SharePoint + scripts de sync (`Sync-MantaMaestro.ps1`, PowerShell + MS Graph delegado) rodando localmente na máquina do usuário |
| Skill `proposta-comercial` | 18 seções, modos M1–M6, tabela de 13 perfis, ref. MNT-2026-COM-1183_D | 14 seções, modos M1–M5, tabela de 12 níveis, ref. Hope PPP MNT-2025-COM-1104 — corrigido em `docs/MODELO-MESTRE-PROPOSTA.md` |

## O que isso pode significar

Três hipóteses, em ordem decrescente de probabilidade:

1. **Alucinação consolidada**: uma sessão inicial inventou a arquitetura
   "v5.0" (agentes numerados, Supabase, APScheduler, ML) sem nunca
   checar contra o SharePoint real, e sessões seguintes trataram esse
   conteúdo como fato estabelecido, expandindo-o por dezenas de PRs
   (`agente-portos.md`, `agente-oleo-gas.md`, "Maestro OS v6.0" com
   consensus voting e disaster recovery, etc.) sem jamais verificar.
2. **Protótipo/exercício paralelo intencional**: este repositório pode
   ter sido criado como exercício de design ("Codex-exemplo" sugere
   isso pelo nome) para explorar uma arquitetura mais ambiciosa,
   deliberadamente desconectada da produção real — mas, se for esse o
   caso, isso nunca foi declarado explicitamente em nenhum README ou
   CLAUDE.md deste repositório; o texto sempre trata a arquitetura como
   se fosse a real ("Operacional", "produção", "gate humano MN").
3. **SharePoint real está desatualizado**: menos provável — o índice
   canônico tem data recente (2026-07-11) e é descrito como "ponto
   único de consulta" ativo, com script de sync ativo
   (`Sync-MantaMaestro.ps1`).

## Recomendação

Não decidir isso via consolidação automática de CLAUDE.md, como as
versões anteriores fizeram com outras divergências (numeração de
segmento, embedder). Esta é uma decisão de produto/arquitetura que
precisa do MN:

1. **Confirmar qual é o sistema real** — se é o SharePoint
   (`INDICE-CANONICAL.md` + `05-sub-skills/` etc.), então este
   repositório deveria ser reduzido/revisado para refletir isso, não o
   contrário.
2. Se confirmado que o SharePoint é a fonte real, planejar a
   reconciliação em fases (não em um único PR): (a) numeração de
   segmento (adotar S1–S11 real, remover S12/S13 fictícios ou
   reclassificá-los conforme o real), (b) trocar o modelo de "20
   agentes Manta NN" pela estrutura real de pastas/SKILL.md, (c)
   remover ou marcar claramente como "proposta de arquitetura futura,
   não implementada" tudo que hoje se apresenta como operacional sem
   lastro real (Supabase RAG, APScheduler, ML routing, consensus
   voting, disaster recovery).
3. Enquanto isso não for decidido, tratar qualquer alegação deste
   repositório sobre "produção"/"operacional" com ceticismo e, quando
   uma mudança real for necessária (como a da skill
   `proposta-comercial`), **sempre verificar contra o SharePoint real
   primeiro**, não confiar no que já está escrito aqui.

## Não resolvido nesta sessão

Este documento só registra o achado e a recomendação. Nenhuma mudança
estrutural (renumeração de segmentos, remoção de agentes fictícios,
etc.) foi feita no repositório além desta documentação — aguarda
decisão do MN sobre o item 1 acima.
