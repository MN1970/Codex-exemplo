#!/usr/bin/env python3
"""
Manta Maestro v5.0.2 — RAG Indexing Pipeline
Ticket: MNT-2026-INFRASTRUCTURE-RAG-PGVECTOR
Date: 2026-08-08

This script provides utilities for:
1. Loading documents (PDF, DOCX, TXT) from disk or URLs
2. Chunking text into semantic units
3. Embedding chunks using BAAI/bge-small-en-v1.5 (384d)
4. Storing embeddings + metadata in Supabase pgvector
5. Testing similarity search

Requirements:
  pip install supabase python-dotenv sentence-transformers pymupdf pypdf
  export SUPABASE_URL="https://..."
  export SUPABASE_KEY="eyJ0..."
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

# Third-party
import dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@dataclass
class DocumentChunk:
    """Represents a text chunk to be embedded"""
    collection_slug: str
    document_title: str
    document_url: Optional[str]
    chunk_index: int
    chunk_text: str
    metadata: Dict


class RAGIndexer:
    """Main RAG indexing orchestrator"""

    def __init__(self, model_name: str = 'BAAI/bge-small-en-v1.5'):
        """Initialize embeddings model"""
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384
        logger.info(f"Loaded embedding model: {model_name} (dim={self.embedding_dim})")

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks using simple size-based strategy.
        For production, consider semantic chunking (e.g., by sentence boundaries).

        Args:
            text: Input text to chunk
            chunk_size: Target size of each chunk (tokens, approximate)
            overlap: Overlap between chunks (characters)

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            # Adjust end to word boundary
            if end < len(text) and text[end] != ' ':
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            chunks.append(text[start:end].strip())
            start = end - overlap
        return [c for c in chunks if c]  # Filter empty chunks

    def embed_text(self, text: str) -> List[float]:
        """Generate 384-dimensional embedding for text"""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def index_chunk(self, chunk: DocumentChunk) -> bool:
        """
        Store a single chunk + embedding in Supabase.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Embed the chunk
            embedding = self.embed_text(chunk.chunk_text)

            # Prepare row for database
            row = {
                'collection_slug': chunk.collection_slug,
                'prefix': f"{chunk.collection_slug}_{chunk.chunk_index:04d}",
                'document_title': chunk.document_title,
                'document_url': chunk.document_url,
                'chunk_index': chunk.chunk_index,
                'chunk_text': chunk.chunk_text,
                'chunk_length': len(chunk.chunk_text),
                'embedding': embedding,
                'metadata': chunk.metadata,
            }

            # Insert into rag_chunks table
            response = supabase.table('rag_chunks').insert(row).execute()
            logger.info(f"Indexed chunk {chunk.prefix}: {chunk.document_title[:50]}")
            return True

        except Exception as e:
            logger.error(f"Error indexing chunk: {e}")
            return False

    def index_document(
        self,
        collection_slug: str,
        document_title: str,
        text: str,
        document_url: Optional[str] = None,
        metadata_extra: Optional[Dict] = None,
        chunk_size: int = 512,
    ) -> int:
        """
        Index a full document by chunking and embedding.

        Args:
            collection_slug: e.g., 'saneamento', 'energia'
            document_title: e.g., 'Lei 14.026/2020'
            text: Full document text
            document_url: Optional source URL
            metadata_extra: Additional metadata (regulatory_status, source_type, etc.)
            chunk_size: Approximate chunk size

        Returns:
            Number of chunks successfully indexed
        """
        # Split into chunks
        chunks_text = self.chunk_text(text, chunk_size=chunk_size)
        logger.info(f"Splitting '{document_title}' into {len(chunks_text)} chunks")

        # Index each chunk
        success_count = 0
        for i, chunk_text in enumerate(chunks_text):
            metadata = {
                'source_type': 'regulatory',
                'language': 'pt-br',
                'document_section': i,
                **(metadata_extra or {})
            }
            chunk = DocumentChunk(
                collection_slug=collection_slug,
                document_title=document_title,
                document_url=document_url,
                chunk_index=i,
                chunk_text=chunk_text,
                metadata=metadata,
            )
            if self.index_chunk(chunk):
                success_count += 1

        logger.info(f"Successfully indexed {success_count}/{len(chunks_text)} chunks for '{document_title}'")
        return success_count

    def search_similar(self, query: str, collection_slug: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query: Search query (natural language)
            collection_slug: Collection to search ('saneamento', etc.)
            top_k: Number of results to return

        Returns:
            List of matching chunks with similarity scores
        """
        # Embed query
        query_embedding = self.embed_text(query)

        # Call Supabase RPC for vector similarity search
        # Note: This assumes a stored procedure exists on Supabase
        # Alternative: Use HTTP API directly for vector search
        try:
            response = supabase.rpc(
                'search_similar_chunks',
                {
                    'query_embedding': query_embedding,
                    'collection_filter': collection_slug,
                    'k': top_k
                }
            ).execute()
            return response.data
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []


def load_seed_documents() -> List[Tuple[str, str, str]]:
    """
    Returns a list of (collection_slug, document_title, sample_text) for initial seeding.
    In production, these would be loaded from files/URLs.

    Returns:
        List of (collection_slug, document_title, text)
    """
    seed_docs = [
        # Saneamento (S8)
        (
            'saneamento',
            'Lei 14.026/2020 — Marco Regulatório do Saneamento',
            """
            Lei 14.026/2020 — Marco Regulatório do Saneamento

            A Lei 14.026 de 26 de julho de 2020 é o novo marco regulatório
            do saneamento básico no Brasil. Ela traz mudanças significativas
            no setor, incluindo:

            1. Universalização do saneamento até 2033
            2. Abertura para concessões privadas
            3. Regulação por entidade reguladora (ANA)
            4. Tarifas baseadas em custo efetivo
            5. Transparência de dados operacionais (SNIS)

            Artigo 1: Aplicação a abastecimento de água, esgotamento sanitário,
            limpeza urbana, manejo de resíduos sólidos.

            [Additional regulatory content would be added here...]
            """
        ),
        # Energia (S9)
        (
            'energia',
            'Decreto 5.163/2004 — Ambiente de Contratação de Energia',
            """
            Decreto 5.163/2004 — Leilões e Contratos de Energia

            Este decreto regulamenta o ambiente de contratação de energia
            elétrica no Brasil, estabelecendo:

            1. Dois ambientes: ACL (Ambiente de Contratação Livre) e ACR (Ambiente de Contratação Regulada)
            2. Leilões competitivos para concessões (A-5, A-3)
            3. Tarifa de referência (RAP — Receita Anual Permitida)
            4. Reajuste tarifário com Fator X (produtividade)

            Artigo 5: Concessões serão outorgadas a título oneroso, por prazo
            de até 35 anos, em regime de concorrência.

            [Additional regulatory content...]
            """
        ),
        # Portos (S6)
        (
            'portos',
            'Lei 12.815/2013 — Modernização dos Portos',
            """
            Lei 12.815/2013 — Lei de Modernização dos Portos

            A Lei de Modernização dos Portos estabelece as diretrizes
            para operação de portos brasileiros:

            1. Autoridades Portuárias (APs) para administração de portos públicos
            2. Terminais de Uso Privado (TUPs) para operadores privados
            3. Arrendamentos simplificados para terminais
            4. Tarifas baseadas em custo + margem

            Artigo 2: Portos são bens públicos de uso comum.

            [Additional regulatory content...]
            """
        ),
        # Aeroportos (S7)
        (
            'aeroportos',
            'Lei 11.182/2005 — Infraestrutura de Aviação Civil',
            """
            Lei 11.182/2005 — Criação da INFRAERO e Estrutura de Aviação Civil

            Esta lei estabelece a estrutura de aviação civil no Brasil:

            1. Criação da INFRAERO para gestão de aeroportos federais
            2. Estrutura de concessões para aeroportos regionais
            3. Autoridade reguladora (ANAC)
            4. Tarifas de pouso, estacionamento e armazenagem

            Artigo 1: INFRAERO é empresa pública para explorar infraestrutura aeroportuária.

            [Additional regulatory content...]
            """
        ),
        # Barragens (S10)
        (
            'barragens',
            'Lei 12.334/2010 — Segurança de Barragens',
            """
            Lei 12.334/2010 — Segurança de Barragens

            Lei que estabelece a Política Nacional de Segurança de Barragens:

            1. Registro obrigatório de barragens (SIGBM/SNISB)
            2. Classificação por risco e dano potencial
            3. Inspeções periódicas (mínimo anual para alto risco)
            4. Planos de ação de emergência (PAE)
            5. Responsabilidade civil do empreendedor

            Artigo 1: Esta Lei institui a Política Nacional de Segurança de Barragens.

            [Additional regulatory content...]
            """
        ),
    ]
    return seed_docs


def main():
    """Main entry point for seeding RAG collections"""
    indexer = RAGIndexer()

    # Load and index seed documents
    seed_docs = load_seed_documents()
    total_chunks = 0

    for collection_slug, document_title, text in seed_docs:
        logger.info(f"\n--- Indexing: {document_title} ---")
        chunks = indexer.index_document(
            collection_slug=collection_slug,
            document_title=document_title,
            text=text,
            metadata_extra={
                'regulatory_status': 'current',
                'source_type': 'regulatory',
            },
            chunk_size=512
        )
        total_chunks += chunks

    logger.info(f"\n=== Seeding Complete ===")
    logger.info(f"Total chunks indexed: {total_chunks}")

    # Test search
    logger.info("\n--- Testing Vector Search ---")
    test_queries = [
        ('saneamento', 'Qual é o prazo de universalização do saneamento?'),
        ('energia', 'Como funciona a tarifação de transmissão de energia?'),
        ('portos', 'Quais são os tipos de terminais portuários?'),
        ('aeroportos', 'Como funcionam as tarifas aeroportuárias?'),
        ('barragens', 'Qual é a importância da segurança de barragens?'),
    ]

    for collection, query in test_queries:
        logger.info(f"\nQuery: '{query}' (collection: {collection})")
        results = indexer.search_similar(query, collection, top_k=3)
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. {result.get('document_title')} - Similarity: {result.get('similarity'):.4f}")


if __name__ == '__main__':
    main()
