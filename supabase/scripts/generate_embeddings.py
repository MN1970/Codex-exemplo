#!/usr/bin/env python3
"""
Generate embeddings para SICRO Similaridade Integration
Usa BAAI/bge-small-en-v1.5 (384-dim) para indexação vetorial em Supabase pgvector
"""

import os
import sys
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração
MODEL_NAME = "BAAI/bge-small-en-v1.5"
DB_URL = os.getenv("SICRO_DB_URL")
BATCH_SIZE = 50

def load_model():
    """Carrega modelo de embeddings"""
    logger.info(f"Carregando modelo {MODEL_NAME}...")
    return SentenceTransformer(MODEL_NAME)

def connect_db():
    """Conecta ao Supabase PostgreSQL"""
    logger.info("Conectando ao Supabase...")
    conn = psycopg2.connect(DB_URL)
    register_vector(conn)
    return conn

def fetch_sicro_items(conn):
    """Fetch itens SICRO que precisam de embeddings"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, descricao
            FROM sicro_insumos
            WHERE embedding IS NULL
            ORDER BY created_at DESC
            LIMIT 1000
        """)
        return cur.fetchall()

def generate_and_store_embeddings(model, conn):
    """Gera embeddings e armazena em Supabase"""
    items = fetch_sicro_items(conn)

    if not items:
        logger.info("Nenhum item para processar.")
        return

    logger.info(f"Processando {len(items)} itens...")

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i+BATCH_SIZE]
        ids = [item[0] for item in batch]
        texts = [item[1] for item in batch]

        # Gera embeddings
        logger.info(f"Batch {i//BATCH_SIZE + 1}: Gerando embeddings para {len(texts)} itens...")
        embeddings = model.encode(texts, show_progress_bar=True)

        # Armazena em Supabase
        with conn.cursor() as cur:
            query = """
                UPDATE sicro_insumos
                SET embedding = %s, updated_at = NOW()
                WHERE id = %s
            """
            data = [(emb.tolist(), id_) for emb, id_ in zip(embeddings, ids)]
            execute_values(cur, query, data, page_size=BATCH_SIZE)
            conn.commit()

        logger.info(f"Batch salvo: {len(data)} embeddings")

    logger.info("✅ Embeddings gerados e armazenados com sucesso!")

if __name__ == "__main__":
    try:
        model = load_model()
        conn = connect_db()
        generate_and_store_embeddings(model, conn)
        conn.close()
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)
