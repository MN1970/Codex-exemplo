#!/usr/bin/env python3
"""
Parallel KE Embeddings Indexer for Manta Maestro.

Orchestrates discovery → sharding → parallel indexing → verification.
Used with Claude Code Task tool to spawn subagents per shard.

Model: BAAI/bge-small-en-v1.5 (384d, normalized L2)
Project: ogxxgvgtulrbbppshjie (Manta Maestro Supabase)
"""

import json
from typing import List, Dict, Tuple

class KeIndexerOrchestrator:
    """Main orchestrator for parallel KE embedding indexing."""

    def __init__(self, project_id: str = "ogxxgvgtulrbbppshjie"):
        self.project_id = project_id
        self.pending_kes = []
        self.shards = []

    def discover(self, kes_result: List[Tuple[str, str]]) -> int:
        """
        Ingest discovery query result.

        Args:
            kes_result: [("KE-XXX", "description"), ...]

        Returns:
            Number of KEs pending indexing.
        """
        self.pending_kes = kes_result
        return len(kes_result)

    def shard(self, shard_size: int = 15) -> int:
        """
        Divide pending KEs into shards.

        Args:
            shard_size: KEs per shard (15-20 recommended).

        Returns:
            Number of shards created.
        """
        import math
        num_shards = math.ceil(len(self.pending_kes) / shard_size)

        for i in range(num_shards):
            start = i * shard_size
            end = start + shard_size
            shard = {code: desc for code, desc in self.pending_kes[start:end]}
            self.shards.append(shard)

        return len(self.shards)

    def gen_subagent_prompts(self) -> List[Tuple[int, str]]:
        """
        Generate subagent prompts for each shard.

        Returns:
            [(shard_number, prompt), ...]
        """
        prompts = []
        for i, shard in enumerate(self.shards, 1):
            prompt = self._mk_prompt(shard, i, len(self.shards))
            prompts.append((i, prompt))
        return prompts

    def _mk_prompt(self, shard: Dict[str, str], num: int, total: int) -> str:
        """Generate a subagent prompt for one shard."""
        ke_json = json.dumps(shard, indent=2, ensure_ascii=False)

        return f"""Você vai indexar o shard {num}/{total} de KEs no Manta Maestro.

**Procedimento (exatamente como abaixo):**

1. Instale a dependência:
   pip install sentence-transformers --break-system-packages

2. Em Python, gere os embeddings:
   ```python
   from sentence_transformers import SentenceTransformer
   import json

   kes = {ke_json}

   model = SentenceTransformer('BAAI/bge-small-en-v1.5')

   def vec_literal(vec):
       return "[" + ",".join(f"{{x:.6f}}" for x in vec) + "]"

   def esc(s):
       return s.replace("'", "''")

   codes = list(kes.keys())
   texts = list(kes.values())
   embeddings = model.encode(texts, normalize_embeddings=True)

   rows = []
   for code, text, emb in zip(codes, texts, embeddings):
       vec_str = vec_literal(emb)
       row = f"('{{code}}', '{{vec_str}}'::vector, 'BAAI/bge-small-en-v1.5', '{{esc(text)}}')"
       rows.append(row)

   sql = (
       "INSERT INTO public.ke_embeddings (ke_codigo, embedding, model, chunk_text)\\n"
       "VALUES\\n" + ",\\n".join(rows) + "\\nON CONFLICT DO NOTHING;"
   )
   print(sql)
   ```

3. Execute o SQL gerado via Supabase MCP (project_id: ogxxgvgtulrbbppshjie).

4. Confirme a gravação:
   ```sql
   SELECT ke_codigo FROM public.ke_embeddings
   WHERE ke_codigo = ANY(ARRAY[{', '.join(f"'{k}'" for k in shard.keys())}]);
   ```

5. Reporte:
   - ✅ Lista de ke_codigo gravados com sucesso
   - ❌ Lista de falhas (se houver) com o erro

**Modelo:** BAAI/bge-small-en-v1.5 (sempre; não altere)
**Normalize:** sempre com normalize_embeddings=True
**Conflito:** use ON CONFLICT DO NOTHING (não sobrescreva existentes)

KEs deste shard ({len(shard)} items):
{json.dumps(shard, indent=2, ensure_ascii=False)}
"""

    def gen_verification_sql(self) -> str:
        """Generate final verification query."""
        return """SELECT COUNT(*) AS total_kes,
       COUNT(emb.ke_codigo) AS com_embedding,
       COUNT(*) - COUNT(emb.ke_codigo) AS sem_embedding
FROM public.knowledge_extractions ke
LEFT JOIN public.ke_embeddings emb ON emb.ke_codigo = ke.ke_codigo;"""

    def summary(self) -> str:
        """Generate execution summary."""
        total_kes = sum(len(s) for s in self.shards)
        return f"""
╔════════════════════════════════════════════╗
║ Parallel KE Embeddings Indexer Summary     ║
╠════════════════════════════════════════════╣
║ Total KEs pending:      {len(self.pending_kes):>20} ║
║ Shards created:         {len(self.shards):>20} ║
║ Total items in shards:  {total_kes:>20} ║
║ Shard size:             {len(self.shards[0]) if self.shards else 0:>20} (avg) ║
║ Model:                  BAAI/bge-small-en-v1.5 ║
║ Project ID:             ogxxgvgtulrbbppshjie ║
╚════════════════════════════════════════════╝

Next: dispatch each shard to a subagent (via Claude Code Task tool).
All subagents run in parallel.
Finally: run verification query and report.
"""


if __name__ == "__main__":
    # Demo: 3 KEs → 2 shards
    demo = KeIndexerOrchestrator()
    demo.discover([
        ("KE-100", "Procedimento de escavação em solos coesivos com SPT > 25"),
        ("KE-101", "Compactação de aterro com energia Proctor intermediária"),
        ("KE-102", "Fundação profunda tipo estaca raiz em argila muito mole"),
    ])
    demo.shard(shard_size=2)

    print(demo.summary())
    print("\n" + "="*50)
    for shard_num, prompt in demo.gen_subagent_prompts():
        print(f"\n[SHARD {shard_num}]")
        print(prompt[:500] + "...")

    print("\n" + "="*50)
    print("\n[VERIFICATION SQL]")
    print(demo.gen_verification_sql())
