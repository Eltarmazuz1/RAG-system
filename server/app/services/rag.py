import logging
from app.models.schemas import SearchResult
from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

async def retrieve_context(query: str, top_k: int = 5) -> list[SearchResult]:
    """
    Retrieve relevant documents for a query.
    1. Embed query.
    2. Search vector store.
    """
    logger.info(f"Retrieving context for query: {query}")
    try:
        query_embedding = (await embeddings_service.embed_texts([query]))[0]
        results = await vector_store.search_similar(query_embedding, top_k=top_k)
        logger.info(f"Retrieved {len(results)} chunks.")
        return results
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return []
