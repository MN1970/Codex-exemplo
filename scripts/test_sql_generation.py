#!/usr/bin/env python3
"""
Test SQL generation sem precisar baixar o modelo.
Mostra como fica o SQL INSERT pronto para Supabase MCP.
"""

import json


def test_sql_generation():
    """Demonstra geração de SQL com dados mock."""

    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║  Test: SQL INSERT Generation (mock embeddings)                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")

    # Mock de KE e embeddings (vetores de 384 dims como BAAI/bge-small-en-v1.5)
    kes_shard = {
        "KE-100": "Especificação de fundação profunda em solos coesivos com SPT > 25",
        "KE-101": "Procedimento de compactação de aterro com energia Proctor intermediária",
    }

    # Mock: dois embeddings normalizados (384 dims cada)
    # Em produção viria de: model.encode(texts, normalize_embeddings=True)
    mock_embeddings = [
        [0.123456] * 384,  # vetor 1, normalize L2
        [0.234567] * 384,  # vetor 2, normalized L2
    ]

    def vec_literal(vec):
        """Converte vetor numpy para literal PostgreSQL vector."""
        return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

    def esc(s):
        """Escapa quotes para SQL."""
        return s.replace("'", "''")

    # Gera SQL
    codes = list(kes_shard.keys())
    texts = list(kes_shard.values())

    rows = []
    for code, text, emb in zip(codes, texts, mock_embeddings):
        vec_str = vec_literal(emb)
        row = f"('{code}', '{vec_str}'::vector, 'BAAI/bge-small-en-v1.5', '{esc(text)}')"
        rows.append(row)

    sql = (
        "INSERT INTO public.ke_embeddings (ke_codigo, embedding, model, chunk_text)\n"
        "VALUES\n"
        + ",\n".join(rows)
        + "\nON CONFLICT DO NOTHING;"
    )

    print("✅ SQL INSERT gerado para 2 KEs (mock):\n")
    print(sql)

    print("\n" + "="*70)
    print("Análise:")
    print("="*70)
    print(f"  • Total de KEs: {len(codes)}")
    print(f"  • Dimensões do embedding: 384 (BAAI/bge-small-en-v1.5)")
    print(f"  • Modelo registrado: 'BAAI/bge-small-en-v1.5'")
    print(f"  • ON CONFLICT: DO NOTHING (nunca sobrescreve existente)")

    print("\n✅ Este SQL é executável diretamente via:")
    print("   Supabase MCP → execute_sql (project_id: ogxxgvgtulrbbppshjie)")

    print("\n📋 Em produção, para N KEs:")
    print("  1. Rodar discovery → lista de KEs sem embedding")
    print("  2. Sharding → dividir em N shards (~15 KEs cada)")
    print("  3. Disparar cada shard para um subagent em paralelo")
    print("  4. Cada subagent:")
    print("     - Gera embeddings (SentenceTransformer)")
    print("     - Monta SQL INSERT (como acima)")
    print("     - Executa no Supabase MCP")
    print("  5. Verification query final")


if __name__ == "__main__":
    test_sql_generation()
