# Área de Apresentação e Retenção de Conhecimento — Pessoas Manta

Registro das pessoas da Manta Associados que usam o Manta Maestro e do
conhecimento que cada uso agrega ao ecossistema (agentes, skills, RAG,
routing). Referenciado pelo `CLAUDE.md` master.

Versão: **v1.0** (template) — estrutura vazia, pronta para ser
preenchida pelo time. Ver seção "Como preencher" antes de adicionar
linhas.

---

## 1. Objetivo

Duas coisas que hoje não têm um lugar único:

1. **Apresentação** — quem usa o Maestro, com qual papel, e quais
   agentes/segmentos usa mais. Serve de diretório vivo do time.
2. **Retenção de conhecimento** — quando um uso do Maestro gera
   conhecimento novo (uma fonte validada, uma regra de routing, uma
   lição aprendida, uma correção de erro), esse conhecimento precisa
   ser capturado aqui — com um critério explícito — em vez de morrer
   na conversa que o gerou.

Sem critério, "conhecimento agregado" vira um passa-livre para qualquer
anotação. A seção 3 define o critério antes de qualquer registro.

---

## 2. Cadastro de pessoas (template)

Preencher uma linha por pessoa na primeira vez que ela usa o Maestro.

| Nome | E-mail | Papel na Manta | Segmento(s) que atende | Agentes/skills mais usados | Nível | Data 1º uso |
|------|--------|----------------|-------------------------|------------------------------|-------|-------------|
| _(a preencher)_ | | | | | | |

**Nível** — uma das três opções, reavaliada a cada trimestre:
- `usuário` — usa agentes prontos, não cria/edita.
- `power-user` — usa vários agentes/skills, contribui casos de uso.
- `mantenedor` — cria/edita agentes, skills, routing ou RAG.

---

## 3. Critério de classificação do conhecimento agregado

Todo registro na seção 4 precisa se encaixar em **um** dos tipos
abaixo. Se não encaixar em nenhum, não é conhecimento retido — é
conversa e fica só no histórico do chat.

| Tipo | O que é | Onde o artefato final mora | Critério mínimo para validar |
|------|---------|------------------------------|-------------------------------|
| Fonte RAG nova | Documento/norma/dado incorporado a uma coleção Supabase | `rag_chunks` (coleção do segmento) | Fonte oficial, datada, com origem rastreável |
| Regra de routing | Nova entrada ou ajuste no bloco `ROUTING` do `CLAUDE.md` | `CLAUDE.md` / `sp_agent_routing` | Testada com ≥3 prompts reais do segmento |
| Skill ou agente (novo/atualizado) | Novo `.md` de agente ou skill, ou revisão de um existente | `.claude/agents/`, catálogo de skills | Passou por gate humano (MN) |
| Caso de uso documentado | Prompt + resultado validado, lição aprendida reaproveitável | Seção 4 deste arquivo | Replicável por outra pessoa sem reexplicar contexto |
| Correção de erro / alucinação | Erro identificado (ex.: via `aluci-guard`) e corrigido na fonte | Seção 4 + registry da skill afetada | Causa raiz identificada, não só o sintoma |
| Processo / SOP | Runbook ou checklist operacional novo | `docs/` | Testado em uma execução real, não só desenhado |

**Nível de impacto** (obrigatório em cada linha da seção 4):
- `Baixo` — útil para o caso pontual que gerou o registro.
- `Médio` — reaproveitável dentro do mesmo segmento/agente.
- `Alto` — transversal, muda routing, RAG ou skill usada por vários agentes.

**Status** (ciclo de vida do registro):
`Proposto` → `Em revisão` → `Validado (gate MN)` → `Publicado`

---

## 4. Registro de conhecimento retido (template)

Uma linha por contribuição, na ordem em que acontece. Não editar
retroativamente uma linha `Publicado` — abrir uma nova linha
referenciando a anterior.

| Data | Pessoa | Agente/Segmento | Tipo (seção 3) | Descrição resumida | Impacto | Status | Fonte / link / commit |
|------|--------|------------------|------------------|----------------------|---------|--------|--------------------------|
| _(a preencher)_ | | | | | | | |

---

## 5. Como preencher

1. Ao usar um agente do Maestro pela primeira vez, adicionar a pessoa
   na seção 2.
2. Sempre que o uso gerar algo que se encaixe na seção 3, abrir uma
   linha na seção 4 no mesmo dia (não depois, de memória).
3. Registros com impacto `Alto` seguem o mesmo gate humano do
   `DEPLOY CHECKLIST` do `CLAUDE.md` antes de virar `Publicado`.
4. Este arquivo é apêndice do `CLAUDE.md` master — mudanças de versão
   aqui devem ser refletidas no histórico de versões do `CLAUDE.md`.

---

## Histórico de versões

- **v1.0** (2026-08-13) — criação da estrutura/template. Sem dados de
  pessoas ou conhecimento ainda — aguardando preenchimento pelo time.
