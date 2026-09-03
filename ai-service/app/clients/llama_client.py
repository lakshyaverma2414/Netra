import httpx
from app.config import config

class LlamaClient:
    def __init__(self):
        self.base_url = config.QWEN_BASE_URL
        self.model = config.QWEN_MODEL

    async def check_health(self) -> bool:
        """Ping the llama.cpp server to ensure it is up."""
        try:
            # llama.cpp server usually exposes /health or /v1/models
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.base_url}/v1/models")
                return response.status_code == 200
        except Exception:
            return False

    async def generate_json(self, prompt: str) -> dict:
        """Call Qwen model and request JSON output."""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a precise extraction assistant. Always output valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.1
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import json
                return json.loads(content)
        except Exception as e:
            raise Exception(f"Failed to generate JSON from Qwen: {e}")

llama_client = LlamaClient()
