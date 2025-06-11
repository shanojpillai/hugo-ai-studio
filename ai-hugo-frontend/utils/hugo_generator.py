import os
import requests
from typing import Dict, Any

class HugoGenerator:
    def __init__(self, base_url: str = "http://backend:8000"):
        self.base_url = base_url
    
    async def create_site(self, config: Dict[str, Any]) -> str:
        """
        Create a new Hugo site with the given configuration
        """
        try:
            response = requests.post(
                f"{self.base_url}/sites",
                json=config
            )
            response.raise_for_status()
            return response.json()["site_id"]
        except Exception as e:
            raise Exception(f"Error creating site: {str(e)}")
    
    async def update_content(self, site_id: str, content: Dict[str, Any]) -> bool:
        """
        Update content in an existing Hugo site
        """
        try:
            response = requests.put(
                f"{self.base_url}/sites/{site_id}/content",
                json=content
            )
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Error updating content: {str(e)}")
