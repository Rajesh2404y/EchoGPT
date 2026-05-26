from collections.abc import AsyncIterator

import httpx

from app.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(self, prompt: str, system: str) -> str:
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        async with httpx.AsyncClient(base_url=self.settings.ollama_host, timeout=120) as client:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json().get("response", "")

    async def stream(self, prompt: str, system: str) -> AsyncIterator[str]:
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "system": system,
            "stream": True,
        }
        async with httpx.AsyncClient(base_url=self.settings.ollama_host, timeout=None) as client:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json

                        data = json.loads(line)
                        yield data.get("response", "")
