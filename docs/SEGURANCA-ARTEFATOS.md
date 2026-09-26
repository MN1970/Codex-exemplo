# Segurança de Artefatos e Dados — Manta Maestro

Versão 1.0 — 2026-09-26 · Ticket MNT-2026-SEC-RLS-01

Checklist para evitar **vazamento de dados** e **acesso indevido** em
artefatos (portais HTML, dashboards, apresentações), no Supabase, no
SharePoint, no GitHub e nos agentes IA. Vale para todo material Manta,
com atenção redobrada a claims, propostas, dados de cliente (R2J, Régis,
EGTC, ViaQuatro) e dados pessoais.

---

## 1. Achados Supabase — projeto `manta-maestro` (2026-09-26)

Levantamento feito via Security Advisors + consulta a `pg_policies` e
`has_table_privilege`. Nenhuma alteração foi aplicada em produção.

| # | Severidade | Achado | Correção |
|---|-----------|--------|----------|
| 1 | 🔴 Crítico | 19 tabelas `r2j_*` (~85 mil linhas: preços base e unitários, receita, EVTEA, OPEX, parâmetros de edital) com política `SELECT TO anon USING (true)`. Qualquer pessoa com a chave anon, que fica visível no código-fonte dos portais, lê tudo pela REST API. | Migration `2026_09_26_security_rls_hardening.sql` |
| 2 | 🔴 Alto | RAG (`manta_rag_chunks`, `manta_rag_documents`, `manta_rag_cases`, `rag_chunks`), `manta_trace`, `manta_artefatos` e tabelas `pk_*` com leitura anon aberta. | Mesma migration |
| 3 | 🟠 Médio | `pk_queries` e `pk_feedback` aceitam `INSERT` anônimo: permite spam e envenenamento do feedback que alimenta o RAG. As consultas registradas também são legíveis por anon. | Mesma migration (INSERT só de membro) |
| 4 | 🟠 Médio | Políticas `TO authenticated USING (true)` liberam qualquer conta do Supabase Auth, não só a equipe Manta. | `private.is_manta_member()` (e-mail @mantaassociados.com) + desativar cadastro aberto |
| 5 | 🟡 Baixo | Função `SECURITY DEFINER` `get_projeto_status_publico` executável por anon. | Mantida como exceção intencional: só devolve snapshots `aprovado AND publicado`. Revisar se o conteúdo de `payload` pode mesmo ser público. |
| 6 | 🟡 Baixo | Extensões `vector` e `pg_trgm` no schema `public`. | Mover para `extensions` numa janela de manutenção (afeta tipos de coluna; não incluído na migration). |
| — | ℹ️ OK | 17 tabelas com RLS ligada e sem política (ex.: `manta_api_clients`, `manta_projects`, `manta_agent_messages`): bloqueadas para anon/authenticated, o que é o comportamento seguro. Bucket `rag-source-docs` é privado. | — |

### Validação da migration

A migration foi executada no banco real dentro de uma transação abortada
à força (`RAISE EXCEPTION` no fim), sem gravar nada. Resultado:
`anon_select_r2j = false`, `tabelas com política anon = 0`, políticas
`manta_member_read` / `manta_member_insert` criadas. Depois da execução,
o schema `private` e as novas políticas não existiam, o que confirma o
rollback.

### Antes de aplicar (gate MN)

1. **Inventariar os portais que usam a chave anon** (Portal R2J, Portal
   PK, portais de projeto). Depois da migration eles passam a receber
   lista vazia.
2. Migrar cada portal para uma destas opções:
   - **Login Supabase Auth**: provedor Azure/Entra ID (SSO Manta) ou
     magic link, com `signInWithOAuth` / `signInWithOtp`; ou
   - **Edge function** que usa `service_role` só no servidor e devolve ao
     portal apenas o recorte necessário.
3. Em *Auth → Providers*: **desativar cadastro aberto** e manter a
   confirmação de e-mail. Sem isso, qualquer pessoa cria uma conta com
   e-mail no domínio `@mantaassociados.com`.
4. **Rotacionar a chave anon** depois da migração: as chaves antigas
   estão em HTMLs já distribuídos.
5. Aplicar com `supabase db push` e rodar os Security Advisors de novo.

---

## 2. Artefatos (claude.ai, portais HTML)

- [ ] **Privado por padrão.** Compartilhar só com pessoas específicas ou
      com a organização, nunca "qualquer pessoa com o link".
- [ ] **Nada sensível embutido no HTML.** Quem abre a página consegue ler
      o código-fonte. Esconder aba, CSS `display:none` ou "senha em
      JavaScript" **não protege**.
- [ ] **Nenhuma credencial na página**: chaves de API, `service_role`,
      tokens do Graph ou client secrets do Azure. A chave anon do
      Supabase só é aceitável se a RLS estiver correta (seção 1).
- [ ] **Dados vivos em vez de copiados.** Ler do SharePoint ou Supabase
      com a identidade de quem está vendo, para que cada pessoa veja só o
      que já pode ver.
- [ ] **`localStorage` só para conveniência** (aba lembrada, filtro),
      nunca para dados de cliente.
- [ ] **Um artefato por público.** Versão interna (números, fontes,
      margens) separada da versão para cliente. Em portais multi-visão
      (ex.: Manta / ViaQuatro / EGTC), cada visão é um artefato próprio,
      não uma aba do mesmo arquivo.
- [ ] **Rastreabilidade.** Marca d'água com destinatário e data nos
      materiais para cliente (padrão Manta), para identificar a origem
      em caso de vazamento.

## 3. SharePoint / Microsoft 365

- [ ] **Menor privilégio**: grupos por pasta de projeto
      (`03_Projetos/<Segmento>/<Projeto>`); nada de "Todos" nem
      "Everyone except external users".
- [ ] **Rótulos de sensibilidade (Purview)**: Público / Interno /
      Confidencial / Restrito, com criptografia nos dois últimos.
- [ ] **DLP**: bloquear envio externo de CPF, CNPJ e valores contratuais.
- [ ] **Links de compartilhamento** apenas para pessoas específicas, com
      expiração (ex.: 30 dias). Revisão trimestral dos acessos externos.
- [ ] **MFA obrigatório + Acesso Condicional** (Entra ID): bloquear
      dispositivos não gerenciados e login fora de BR/AR/PE.
- [ ] **Integrações** (MCP `SharePoint_Manta`, Zapier, GitHub Action)
      com `Sites.Selected` no Graph, não permissão para o tenant inteiro.
      Escritas feitas por agente passam por gate humano.
- [ ] **Log de auditoria** do Purview ativo; alerta para download em
      massa.

## 4. GitHub e agentes IA

- [ ] Repositórios **privados**; *secret scanning* e *push protection*
      ligados.
- [ ] **Branch protection** em `main`: PR obrigatório + aprovação MN.
- [ ] Credenciais só em GitHub Secrets ou no cofre do ambiente, nunca
      em `CLAUDE.md`, SKILL.md, prompts ou migrations.
- [ ] **Agentes com o mínimo de ferramentas.** S6–S10 são somente
      leitura (Read/Grep/Glob/Bash/WebSearch/WebFetch). Permissão de
      escrita no SharePoint ou Supabase só com gate humano.
- [ ] **Conteúdo externo é dado, não instrução.** PDFs de edital, e-mails
      e páginas web podem trazer *prompt injection*; o agente não executa
      ordens encontradas nesses documentos.

## 5. Base legal e normativa

- **LGPD** (Lei 13.709/2018): art. 46 (medidas de segurança), art. 48
  (comunicação de incidente à ANPD e ao titular).
- **Argentina — Lei 25.326** (proteção de dados pessoais), relevante
  para o projeto AySA.
- **ISO/IEC 27001:2022** (SGSI) e **NIST Cybersecurity Framework 2.0**
  como referência para padronizar controles.
