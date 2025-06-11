import aiohttp
from typing import Dict, Any, Optional

class LLMService:
    def __init__(self, model_url: str = "http://ollama:11434"):
        self.model_url = model_url
    
    async def generate_content(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate content using the Ollama LLM service
        """
        try:
            params = params or {}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.model_url}/api/generate",
                    json={
                        "model": params.get("model", "llama3.2"),
                        "prompt": prompt,
                        "stream": False,
                        **params
                    }
                ) as response:
                    if response.status != 200:
                        raise Exception(f"LLM request failed with status {response.status}")
                    
                    result = await response.json()
                    return result["response"]
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            raise
