import requests
from typing import Dict, Any
import os

class LLMClient:
    def __init__(self, ollama_url: str = None):
        # Use direct Ollama connection for better reliability
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://43.192.149.110:11434")
        self.backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

    def generate_content(self, prompt: str, model: str = "llama3.2") -> str:
        """
        Generate content using Ollama directly
        """
        try:
            # Try direct Ollama connection first
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2048
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            # Fallback to backend API
            try:
                response = requests.post(
                    f"{self.backend_url}/generate",
                    json={
                        "prompt": prompt,
                        "params": {"model": model}
                    },
                    timeout=60
                )
                response.raise_for_status()
                return response.json().get("content", "")
            except Exception as backend_error:
                raise Exception(f"Both Ollama and backend failed. Ollama: {str(e)}, Backend: {str(backend_error)}")
