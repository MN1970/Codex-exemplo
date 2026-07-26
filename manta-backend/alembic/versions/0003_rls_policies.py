"""RLS policies multi-org

Habilita Row-Level Security nas tabelas por-organização: organizations,
agents, rag_chunks, sessions, feedback, ml_models.

`users` e `roles` ficam DE FORA de propósito:

  * o fluxo de login precisa localizar o `User` pelo e-mail ANTES de
    saber qual é a "organização ativa" da conexão — com RLS ligada
    nessa tabela, `SELECT * FROM users WHERE email = ...` sem o GUC
    `app.current_org_id` já setado devolveria zero linhas sempre
    (fail-closed), quebrando o próprio login;
  * `roles` é catálogo global (não tem `org_id`), não há o que isolar.

Se no futuro o login precisar rodar sob RLS, o padrão recomendado é uma
função `SECURITY DEFINER` (bypassa RLS por definição, roda com os
privilégios de quem a criou) que faz só o lookup de credenciais, em vez
de abrir mão da RLS na tabela inteira.

Mecanismo: cada policy lê `current_setting('app.current_org_id', true)`
— o `true` final é o `missing_ok`, então se a GUC não estiver setada a
função devolve NULL em vez de lançar erro, e a comparação
`org_id = NULL` é sempre falsa. Ou seja, o padrão é NEGAR (fail-closed),
nunca vazar dados de outra organização por esquecimento de setar o
contexto. Quem seta a GUC é `database.set_org_context()`, via
`SELECT set_config('app.current_org_id', :org_id, true)` — o terceiro
argumento (`is_local=true`) dá o mesmo escopo de `SET LOCAL`: o valor
vale só até o fim da transação atual.

IMPORTANTE — RLS e o dono da tabela: por padrão, o Postgres ISENTA o
dono da tabela (e superusers) das próprias policies de RLS. Como o
papel que roda `alembic upgrade` tipicamente também é quem cria as
tabelas (logo, o dono), aplicamos `FORCE ROW LEVEL SECURITY` em cada
uma — isso faz a policy valer mesmo para o dono (superusers continuam
isentos, sempre). Em produção, o ideal ainda é ter um papel de
aplicação distinto do papel de migração (ex.: migrations rodam como
`manta_migrator`, a app conecta como `manta_app`, sem `BYPASSRLS`) — no
Supabase isso é exatamente `service_role` (bypassa RLS, uso
server-side/admin) vs. `authenticated`/`anon` (respeitam RLS).

`ml_models.org_id` é nullable (catálogo global quando NULL) — a policy
reflete isso: linhas com `org_id IS NULL` são visíveis a qualquer
organização; linhas com `org_id` preenchido só à própria organização.

`organizations` tem uma pegadinha proposital: a policy de INSERT é
permissiva (`WITH CHECK (true)`), diferente de SELECT/UPDATE/DELETE
(restritos à própria org). Motivo — "ovo e galinha": para criar uma
Organization nova (signup/onboarding) seria preciso já ter
`app.current_org_id` setado para o id da organização que ainda nem
existe, o que é impossível. A autorização de QUEM pode criar uma
organização continua sendo responsabilidade da aplicação (endpoint de
signup); a RLS aqui protege leitura/alteração pós-criação, não o
cadastro inicial.

Revision ID: 0003_rls_policies
Revises: 0002_initial_schema
Create Date: 2026-07-26
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_rls_policies"
down_revision: Union[str, None] = "0002_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Tabelas com FK org_id NOT NULL — isolamento estrito (só a própria org).
_STRICT_ORG_TABLES: tuple[str, ...] = ("agents", "rag_chunks", "sessions", "feedback")


def _enable_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")


def _disable_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    # organizations: SELECT/UPDATE/DELETE restritos à própria org; INSERT
    # é deliberadamente permissivo (ver docstring do módulo — sem isso,
    # nenhuma organização nova poderia ser criada).
    _enable_rls("organizations")
    op.execute(
        """
        CREATE POLICY organizations_insert_any ON organizations
        FOR INSERT
        WITH CHECK (true)
        """
    )
    op.execute(
        """
        CREATE POLICY organizations_select_isolation ON organizations
        FOR SELECT
        USING (id = current_setting('app.current_org_id', true))
        """
    )
    op.execute(
        """
        CREATE POLICY organizations_update_isolation ON organizations
        FOR UPDATE
        USING (id = current_setting('app.current_org_id', true))
        WITH CHECK (id = current_setting('app.current_org_id', true))
        """
    )
    op.execute(
        """
        CREATE POLICY organizations_delete_isolation ON organizations
        FOR DELETE
        USING (id = current_setting('app.current_org_id', true))
        """
    )

    # agents, rag_chunks, sessions, feedback: org_id NOT NULL.
    for table in _STRICT_ORG_TABLES:
        _enable_rls(table)
        op.execute(
            f"""
            CREATE POLICY {table}_org_isolation ON {table}
            USING (org_id = current_setting('app.current_org_id', true))
            WITH CHECK (org_id = current_setting('app.current_org_id', true))
            """
        )

    # ml_models: org_id nullable — NULL = catálogo global visível a todas.
    _enable_rls("ml_models")
    op.execute(
        """
        CREATE POLICY ml_models_org_isolation ON ml_models
        USING (org_id IS NULL OR org_id = current_setting('app.current_org_id', true))
        WITH CHECK (org_id IS NULL OR org_id = current_setting('app.current_org_id', true))
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS ml_models_org_isolation ON ml_models")
    _disable_rls("ml_models")

    for table in reversed(_STRICT_ORG_TABLES):
        op.execute(f"DROP POLICY IF EXISTS {table}_org_isolation ON {table}")
        _disable_rls(table)

    op.execute("DROP POLICY IF EXISTS organizations_delete_isolation ON organizations")
    op.execute("DROP POLICY IF EXISTS organizations_update_isolation ON organizations")
    op.execute("DROP POLICY IF EXISTS organizations_select_isolation ON organizations")
    op.execute("DROP POLICY IF EXISTS organizations_insert_any ON organizations")
    _disable_rls("organizations")
