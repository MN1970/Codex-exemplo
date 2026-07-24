-- MantaBase MCP v2 — Supabase setup migrations
-- Cria função RPC para executar queries read-only com parâmetros

-- Função RPC para executar SELECT com parâmetros
CREATE OR REPLACE FUNCTION execute_select_query(
    p_sql TEXT,
    p_params JSONB DEFAULT NULL
)
RETURNS TABLE (
    rows JSONB,
    count BIGINT,
    error TEXT
) AS $$
DECLARE
    v_result JSONB;
    v_count BIGINT;
    v_error TEXT := NULL;
BEGIN
    BEGIN
        -- Validação básica: query deve começar com SELECT
        IF NOT (UPPER(TRIM(p_sql)) ~ '^SELECT') THEN
            RAISE EXCEPTION 'Only SELECT queries allowed';
        END IF;

        -- Bloquear keywords perigosas
        IF (UPPER(p_sql) ~ '(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE)') THEN
            RAISE EXCEPTION 'Mutation queries are not allowed';
        END IF;

        -- Executar query
        EXECUTE p_sql INTO v_result USING p_params;

        -- Contar linhas (aproximado)
        v_count := COALESCE(JSONB_ARRAY_LENGTH(v_result), 0);

        RETURN QUERY SELECT v_result, v_count, v_error;

    EXCEPTION WHEN OTHERS THEN
        v_error := SQLERRM;
        RETURN QUERY SELECT NULL::JSONB, 0::BIGINT, v_error;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant executar ao usuário anon (cliente)
GRANT EXECUTE ON FUNCTION execute_select_query(TEXT, JSONB) TO anon;
GRANT EXECUTE ON FUNCTION execute_select_query(TEXT, JSONB) TO authenticated;

-- Tabela de auditoria para logging de queries
CREATE TABLE IF NOT EXISTS mcp_query_audit (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    query_hash TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT NOW(),
    duration_ms INTEGER,
    row_count INTEGER,
    error_message TEXT
);

-- Index para rápida lookup
CREATE INDEX idx_mcp_query_audit_user_date ON mcp_query_audit(user_email, executed_at DESC);

-- Função para log de queries
CREATE OR REPLACE FUNCTION log_query(
    p_user_email TEXT,
    p_query_hash TEXT,
    p_duration_ms INTEGER,
    p_row_count INTEGER,
    p_error_message TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO mcp_query_audit (user_email, query_hash, duration_ms, row_count, error_message)
    VALUES (p_user_email, p_query_hash, p_duration_ms, p_row_count, p_error_message);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION log_query(TEXT, TEXT, INTEGER, INTEGER, TEXT) TO authenticated;

-- Política de RLS para auditoria (usuários podem ler apenas suas queries)
ALTER TABLE mcp_query_audit ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own query logs" ON mcp_query_audit
    FOR SELECT
    USING (user_email = current_user_email());

-- ===== Extensão de exemplo: tabela de projects para testes =====

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK (status IN ('active', 'inactive', 'archived')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Projects are viewable by anyone" ON projects FOR SELECT USING (true);

-- ===== Índices para performance =====

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- ===== Triggers para atualizar updated_at =====

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
