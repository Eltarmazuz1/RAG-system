import asyncio
from app.services.vector_store import vector_store
from app.services.embeddings import embeddings_service

async def test_search():
    # Ensure collection exists
    await vector_store.ensure_collection()
    
    # Try to search for something
    query = "what is the project"
    print(f"Searching for: {query}")
    
    query_embedding = (await embeddings_service.embed_texts([query]))[0]
    results = await vector_store.search_similar(query_embedding, top_k=5)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Score: {result.score}")
        print(f"Text: {result.text[:200]}...")
        print(f"Metadata: {result.metadata}")

if __name__ == "__main__":
    asyncio.run(test_search())
