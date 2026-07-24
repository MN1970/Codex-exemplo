"""Testes de query read-only e validação SQL."""

import pytest

try:
    from supabase_client import SupabaseQueryValidator
except ImportError:
    SupabaseQueryValidator = None


@pytest.mark.skipif(SupabaseQueryValidator is None, reason="supabase not installed")
class TestQueryValidation:
    """Testes de validação SQL."""

    def test_valid_select_query(self):
        """Query SELECT válida."""
        sql = "SELECT * FROM projects WHERE id = 1"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is True
        assert error is None

    def test_valid_select_with_join(self):
        """SELECT com JOIN válido."""
        sql = """
        SELECT p.id, p.name, t.title
        FROM projects p
        JOIN tasks t ON p.id = t.project_id
        WHERE p.status = 'active'
        """
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is True
        assert error is None

    def test_valid_select_with_aggregation(self):
        """SELECT com agregação válido."""
        sql = "SELECT COUNT(*) as total FROM projects GROUP BY status"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is True
        assert error is None

    def test_block_insert(self):
        """Bloqueia INSERT."""
        sql = "INSERT INTO projects (name) VALUES ('test')"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "INSERT" in error

    def test_block_update(self):
        """Bloqueia UPDATE."""
        sql = "UPDATE projects SET name = 'test' WHERE id = 1"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "UPDATE" in error

    def test_block_delete(self):
        """Bloqueia DELETE."""
        sql = "DELETE FROM projects WHERE id = 1"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "DELETE" in error

    def test_block_drop(self):
        """Bloqueia DROP."""
        sql = "DROP TABLE projects"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "DROP" in error

    def test_block_comment_injection(self):
        """Bloqueia comentários (potential injection)."""
        sql = "SELECT * FROM projects -- WHERE id = 1"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "Comments" in error

    def test_block_block_comment_injection(self):
        """Bloqueia block comments (/* */)."""
        sql = "SELECT * FROM projects /* WHERE id = 1 */"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "Comments" in error

    def test_block_non_select(self):
        """Bloqueia queries que não começam com SELECT."""
        sql = "WITH cte AS (SELECT * FROM projects) SELECT * FROM cte"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        # CTEs começam com WITH, não SELECT — deve bloquear
        assert is_safe is False
        assert "Only SELECT" in error

    def test_case_insensitive(self):
        """Validação é case-insensitive."""
        sql = "select * from projects where id = 1"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is True

    def test_block_function_copy(self):
        """Bloqueia função COPY (I/O)."""
        sql = "COPY projects TO STDOUT"
        is_safe, error = SupabaseQueryValidator.is_safe(sql)
        assert is_safe is False
        assert "COPY" in error
