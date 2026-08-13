#!/usr/bin/env python3
"""
Demo executável da infraestrutura de indexação paralela de KEs.

Simula o fluxo completo:
1. Discovery (dados demo de KEs pendentes)
2. Sharding
3. Geração de prompts de subagent
4. Geração de embeddings locais (demo com 2 KEs)
5. Geração de SQL INSERT
6. (Opcional) Inserção no Supabase MCP

Uso:
  python3 scripts/run_ke_indexing_demo.py [--no-embeddings]
"""

import json
import sys
from pathlib import Path

# Adiciona scripts/ ao path para imports
sys.path.insert(0, str(Path(__file__).parent))

from parallel_ke_embeddings_indexer import KeIndexerOrchestrator


def demo_discovery():
    """Simula discovery: KEs que faltam embeddings."""
    print("\n" + "="*70)
    print("STEP 1: DISCOVERY — KEs sem embeddings")
    print("="*70)

    # Em produção, viria de:
    # SELECT ke.ke_codigo, ke.descricao FROM knowledge_extractions ke
    # LEFT JOIN ke_embeddings emb USING(ke_codigo) WHERE emb.ke_codigo IS NULL

    demo_kes = [
        ("KE-100", "Especificação de fundação profunda em solos coesivos com SPT > 25"),
        ("KE-101", "Procedimento de compactação de aterro com energia Proctor intermediária e CBR ≥ 80%"),
        ("KE-102", "Método de execução de estaca raiz em argila muito mole com micromotor"),
        ("KE-103", "Critério de aceitação para drenagem em obra de contenção com geotêxtil"),
        ("KE-104", "Especificação de concreto usinado com resistência característica 35 MPa e slump 12 cm"),
    ]

    print(f"\n✅ Descobertos {len(demo_kes)} KEs sem embeddings:")
    for code, desc in demo_kes:
        print(f"  {code}: {desc[:60]}...")

    return demo_kes


def demo_sharding(kes):
    """Divide KEs em shards para paralelismo."""
    print("\n" + "="*70)
    print("STEP 2: SHARDING — Divisão em N shards para paralelo")
    print("="*70)

    orchestrator = KeIndexerOrchestrator()
    orchestrator.discover(kes)
    num_shards = orchestrator.shard(shard_size=3)  # 3 KEs por shard para demo

    print(orchestrator.summary())

    return orchestrator


def demo_subagent_prompts(orchestrator):
    """Mostra prompts prontos para disparar para subagents."""
    print("\n" + "="*70)
    print("STEP 3: SUBAGENT PROMPTS — Prontos para dispatch paralelo")
    print("="*70)

    prompts = orchestrator.gen_subagent_prompts()

    for shard_num, prompt in prompts:
        print(f"\n{'─'*70}")
        print(f"[SHARD {shard_num}]")
        print(f"{'─'*70}")
        print(prompt[:600] + "\n...[truncado para demo]")


def demo_generate_embeddings(orchestrator, skip=False):
    """Gera embeddings locais para uma amostra de KEs."""
    if skip:
        print("\n" + "="*70)
        print("STEP 4: GENERATE EMBEDDINGS — Skipped (--no-embeddings)")
        print("="*70)
        return None

    print("\n" + "="*70)
    print("STEP 4: GENERATE EMBEDDINGS — Usando SentenceTransformer")
    print("="*70)

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("\n⚠️  sentence-transformers não instalado. Instalando...")
        import subprocess
        subprocess.run(
            ["pip", "install", "sentence-transformers", "--break-system-packages"],
            check=True
        )
        from sentence_transformers import SentenceTransformer

    print("\n📥 Carregando modelo BAAI/bge-small-en-v1.5...")
    print("   (primeira execução baixa ~120 MB do HuggingFace Hub)")

    model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    # Pega o primeiro shard para demo
    first_shard = orchestrator.shards[0]
    codes = list(first_shard.keys())
    texts = list(first_shard.values())

    print(f"\n⚙️  Codificando {len(codes)} KEs com normalize_embeddings=True...")
    embeddings = model.encode(texts, normalize_embeddings=True)

    print(f"✅ Embeddings gerados (384 dims, L2-normalized)")

    # Mostra sample
    for code, emb in zip(codes[:2], embeddings[:2]):
        vec_norm = sum(x**2 for x in emb) ** 0.5  # Verifica norma L2
        print(f"  {code}: norm={vec_norm:.6f}, dims={len(emb)}")

    return {
        'model': model,
        'shard': first_shard,
        'embeddings': embeddings,
        'codes': codes,
        'texts': texts
    }


def demo_generate_sql(embeddings_data):
    """Gera SQL INSERT para inserção no Supabase."""
    print("\n" + "="*70)
    print("STEP 5: GENERATE SQL INSERT")
    print("="*70)

    if not embeddings_data:
        print("\n(Skipped due to --no-embeddings)")
        return

    codes = embeddings_data['codes']
    texts = embeddings_data['texts']
    embeddings = embeddings_data['embeddings']

    def vec_literal(vec):
        return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"

    def esc(s):
        return s.replace("'", "''")

    rows = []
    for code, text, emb in zip(codes, texts, embeddings):
        vec_str = vec_literal(emb)
        row = f"('{code}', '{vec_str}'::vector, 'BAAI/bge-small-en-v1.5', '{esc(text)}')"
        rows.append(row)

    sql = (
        "INSERT INTO public.ke_embeddings (ke_codigo, embedding, model, chunk_text)\n"
        "VALUES\n"
        + ",\n".join(rows)
        + "\nON CONFLICT DO NOTHING;"
    )

    print(f"\n✅ SQL gerado para {len(codes)} KEs:")
    print(f"\n{sql[:500]}...")

    return sql


def demo_verify(orchestrator):
    """Mostra query de verificação final."""
    print("\n" + "="*70)
    print("STEP 6: VERIFICATION — Query final de auditoria")
    print("="*70)

    verify_sql = orchestrator.gen_verification_sql()
    print(f"\n{verify_sql}")

    print("\n✅ Resultado esperado: sem_embedding = 0")


def main():
    skip_embeddings = "--no-embeddings" in sys.argv

    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║  Parallel KE Embeddings Indexer — Demo End-to-End                  ║")
    print("║  (infraestrutura completa: discovery → sharding → embeddings → SQL) ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # Step 1: Discovery
    kes = demo_discovery()

    # Step 2: Sharding
    orchestrator = demo_sharding(kes)

    # Step 3: Subagent Prompts
    demo_subagent_prompts(orchestrator)

    # Step 4: Generate Embeddings
    embeddings_data = demo_generate_embeddings(orchestrator, skip=skip_embeddings)

    # Step 5: Generate SQL
    sql = demo_generate_sql(embeddings_data)

    # Step 6: Verification
    demo_verify(orchestrator)

    print("\n" + "="*70)
    print("✅ DEMO COMPLETO")
    print("="*70)
    print("""
Próximos passos em produção:

1. Rodar discovery query via Supabase MCP
   → obtém lista real de KEs sem embeddings

2. Usar KeIndexerOrchestrator para sharding
   → gera N shards de ~15 KEs cada

3. Disparar cada shard como um subagent em paralelo
   → via Claude Code Task tool
   → cada subagent rooda steps 4-5 localmente
   → insere no Supabase MCP via execute_sql

4. Rodar verification query final
   → confirma sem_embedding = 0

Documentação completa: PARALLEL_KE_EMBEDDINGS.md
""")


if __name__ == "__main__":
    main()
