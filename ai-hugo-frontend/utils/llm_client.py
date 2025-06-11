import requests
from typing import Dict, Any

class LLMClient:
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url
    
    async def generate_content(self, prompt: str, params: Dict[str, Any] = None) -> str:
        """
        Generate content using the LLM service
        """
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "prompt": prompt,
                    "params": params or {}
                }
            )
            response.raise_for_status()
            return response.json()["content"]
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")
