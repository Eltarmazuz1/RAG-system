import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingsService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDINGS_MODEL
        # Simple client for OpenAI. 
        # In a real app with multiple providers, this would be more abstract.
        self.base_url = "https://api.openai.com/v1"

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts using OpenAI API.
        """
        if not self.api_key:
            logger.warning("OpenAI API Key not set. Returning dummy embeddings for testing if needed.")
            # For strict correctness, we should raise or return empty. 
            # But let's raise to fail fast if config is missing.
            raise ValueError("OPENAI_API_KEY is missing via environment variables.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenAI expects newlines to be replaced in some cases, but for 'text-embedding-3' it's usually fine.
        # We'll valid input.
        payload = {
            "input": texts,
            "model": self.model
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract embeddings in order
                # The response.data list usually has index, we assume it's sorted or maps 1:1
                embeddings = [item["embedding"] for item in data["data"]]
                
                logger.info(f"Generated {len(embeddings)} embeddings using {self.model}")
                return embeddings

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

embeddings_service = EmbeddingsService()
