import logging
from qdrant_client import AsyncQdrantClient, models
from app.config import settings
from app.models.schemas import Chunk, SearchResult

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        if settings.VECTOR_DB_URL:
            logger.info(f"Connecting to Qdrant at {settings.VECTOR_DB_URL}")
            self.client = AsyncQdrantClient(url=settings.VECTOR_DB_URL)
        else:
            logger.info(f"Using local Qdrant at {settings.VECTOR_DB_PATH}")
            self.client = AsyncQdrantClient(path=settings.VECTOR_DB_PATH)
            
        self.collection_name = settings.VECTOR_DB_COLLECTION

    async def ensure_collection(self):
        """
        Ensure the collection exists. If not, create it.
        We assume a default vector size for 'text-embedding-3-small' which is 1536.
        """
        # Note: In a real app, you might want to make vector_size configurable
        # OpenAI text-embedding-3-small is 1536 dim
        VECTOR_SIZE = 1536 
        
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection '{self.collection_name}'...")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created.")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")

    async def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]):
        if not chunks or not embeddings:
            return
        
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings count mismatch")

        points = [
            models.PointStruct(
                id=chunk.id,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "document_id": chunk.document_id,
                    **chunk.metadata
                }
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        logger.info(f"Upserting {len(points)} points to {self.collection_name}...")
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search_similar(self, query_embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        try:
            results = await self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True
            )
            
            return [
                SearchResult(
                    text=point.payload.get("text", ""),
                    score=point.score,
                    metadata=point.payload or {}
                )
                for point in results.points
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

# Global instance could be used, or dependency injection
vector_store = VectorStore()
