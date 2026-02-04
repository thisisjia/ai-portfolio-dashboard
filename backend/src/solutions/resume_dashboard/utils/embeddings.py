"""Embedding and RAG utilities for semantic search using Ollama.

NOTE: This module is NOT currently used in production.

ORIGINAL DESIGN:
    Hybrid search with embeddings + BM25 + RRF:
    - Semantic search via cosine similarity on Ollama embeddings
    - BM25-like keyword matching for exact term matching
    - Reciprocal Rank Fusion (RRF) for combining results

WHY NOT DEPLOYED:
    Memory constraints on AWS t2.micro (1GB total RAM):
    - nomic-embed-text model: ~500MB
    - Ollama service overhead: ~300MB
    - FastAPI + SQLite + OS: ~400MB
    Total required: ~1.2GB > 1GB available

    Even lighter alternatives (EmbeddingGemma-300M <200MB, all-MiniLM-L6-v2 43MB)
    still require embedding infrastructure exceeding free tier constraints.

CURRENT APPROACH:
    Direct context injection to Groq LLM (llama-3.3-70b-versatile).
    Single resume (~5KB) fits in 8K context window.
    Multi-agent routing handles query classification without embeddings.

TRADE-OFFS:
    - Works for current scale (single document)
    - Not scalable to 100+ documents without RAG
    - Forced by memory constraints, acceptable for MVP/demo

KEPT AS REFERENCE:
    Demonstrates knowledge of RAG, vector search, and hybrid retrieval.
    Would be activated if scaling up (requires t2.medium+).

See ARCHITECTURE.md section "No RAG/Vector Search" for detailed analysis.
"""

import numpy as np
import aiosqlite
import pickle
import httpx
from typing import List, Dict, Any, Tuple
from pathlib import Path


class EmbeddingManager:
    """Manages embeddings for RAG-based resume querying using Ollama."""

    def __init__(self, db_path: str = None, model_name: str = "nomic-embed-text", ollama_url: str = "http://localhost:11434"):
        """
        Initialize embedding manager with Ollama.

        Args:
            db_path: Path to SQLite database
            model_name: Name of Ollama embedding model (nomic-embed-text, mxbai-embed-large)
            ollama_url: Ollama API endpoint
        """
        if db_path is None:
            import os
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            db_path = os.path.join(backend_dir, "resume_dashboard.db")

        self.db_path = db_path
        self.model_name = model_name
        self.ollama_url = ollama_url
        print(f"✅ Using Ollama embedding model: {self.model_name}")

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector for given text using Ollama."""
        import requests

        response = requests.post(
            f"{self.ollama_url}/api/embeddings",
            json={
                "model": self.model_name,
                "prompt": text
            }
        )

        if response.status_code == 200:
            embedding = np.array(response.json()["embedding"])
            return embedding
        else:
            raise Exception(f"Failed to generate embedding: {response.text}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts efficiently."""
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings

    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        return dot_product / norm_product if norm_product > 0 else 0.0

    async def store_embedding(
        self,
        content_type: str,
        content_id: int,
        content_text: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any] = None
    ):
        """Store an embedding in the database."""
        import json

        # Convert numpy array to bytes for storage
        embedding_bytes = pickle.dumps(embedding)
        metadata_json = json.dumps(metadata) if metadata else None

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO embeddings
                (content_type, content_id, content_text, embedding, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (content_type, content_id, content_text, embedding_bytes, metadata_json))
            await db.commit()

    async def retrieve_similar(
        self,
        query: str,
        content_type: str = None,
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most similar content using semantic search.

        Args:
            query: The search query
            content_type: Filter by content type (optional)
            top_k: Number of results to return
            threshold: Minimum similarity score

        Returns:
            List of dictionaries with content and similarity scores
        """
        import json

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Retrieve all embeddings from database
        async with aiosqlite.connect(self.db_path) as db:
            if content_type:
                cursor = await db.execute("""
                    SELECT id, content_type, content_id, content_text, embedding, metadata
                    FROM embeddings WHERE content_type = ?
                """, (content_type,))
            else:
                cursor = await db.execute("""
                    SELECT id, content_type, content_id, content_text, embedding, metadata
                    FROM embeddings
                """)

            rows = await cursor.fetchall()

        # Calculate similarities
        results = []
        for row in rows:
            embedding_id, content_type, content_id, content_text, embedding_bytes, metadata_json = row

            # Deserialize embedding
            embedding = pickle.loads(embedding_bytes)

            # Calculate similarity
            similarity = self.cosine_similarity(query_embedding, embedding)

            if similarity >= threshold:
                metadata = json.loads(metadata_json) if metadata_json else {}
                results.append({
                    "id": embedding_id,
                    "content_type": content_type,
                    "content_id": content_id,
                    "content": content_text,
                    "similarity": float(similarity),
                    "metadata": metadata
                })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    async def hybrid_search(
        self,
        query: str,
        content_type: str = None,
        top_k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword matching.

        Args:
            query: The search query
            content_type: Filter by content type (optional)
            top_k: Number of results to return
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)

        Returns:
            List of dictionaries with content and combined scores
        """
        # Get semantic results
        semantic_results = await self.retrieve_similar(query, content_type, top_k=top_k*2)

        # Simple keyword matching (case-insensitive)
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        # Combine scores
        for result in semantic_results:
            # Keyword score (BM25-like simple version)
            content_lower = result["content"].lower()
            content_terms = set(content_lower.split())
            term_matches = len(query_terms & content_terms)
            keyword_score = term_matches / len(query_terms) if query_terms else 0

            # Combined score
            result["keyword_score"] = keyword_score
            result["combined_score"] = (
                semantic_weight * result["similarity"] +
                keyword_weight * keyword_score
            )

        # Re-sort by combined score
        semantic_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return semantic_results[:top_k]

    async def clear_embeddings(self, content_type: str = None):
        """Clear all embeddings or embeddings of a specific type."""
        async with aiosqlite.connect(self.db_path) as db:
            if content_type:
                await db.execute("DELETE FROM embeddings WHERE content_type = ?", (content_type,))
            else:
                await db.execute("DELETE FROM embeddings")
            await db.commit()

    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about stored embeddings."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT content_type, COUNT(*) as count
                FROM embeddings
                GROUP BY content_type
            """)
            rows = await cursor.fetchall()

            stats = {
                "total": sum(row[1] for row in rows),
                "by_type": {row[0]: row[1] for row in rows}
            }

            return stats
