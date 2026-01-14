import logging
import httpx
import json
from typing import AsyncIterator
from app.config import settings
from app.models.schemas import ChatMessage

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_key = self._get_api_key()
        self.base_url = "https://api.openai.com/v1" # Simplification for OpenAI-compatible
        
    def _get_api_key(self):
        if self.provider == "openai":
            return settings.OPENAI_API_KEY
        elif self.provider == "anthropic":
            return settings.ANTHROPIC_API_KEY
        elif self.provider == "gemini":
            return settings.GEMINI_API_KEY
        return None

    async def stream_chat(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """
        Stream chat response from the LLM.
        """
        if not self.api_key:
            yield "Error: API Key missing."
            return

        logger.info(f"Streaming chat with {len(messages)} messages using {self.model}")

        # OpenAI-compatible payload
        payload = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", 
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.read()
                        logger.error(f"LLM Error {response.status_code}: {error_text}")
                        yield f"Error from LLM: {response.status_code}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0]["delta"]
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                pass
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield f"Error: {str(e)}"

llm_provider = LLMProvider()
