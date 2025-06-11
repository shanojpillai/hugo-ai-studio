from typing import Dict, Any
import aiohttp
import os

class ContentService:
    def __init__(self):
        self.generated_sites_path = os.path.join(os.path.dirname(__file__), "..", "generated_sites")
        os.makedirs(self.generated_sites_path, exist_ok=True)
    
    async def save_content(self, site_id: str, content: Dict[str, Any]) -> bool:
        """
        Save generated content to the appropriate location in the Hugo site structure
        """
        try:
            site_path = os.path.join(self.generated_sites_path, site_id)
            content_path = os.path.join(site_path, "content")
            os.makedirs(content_path, exist_ok=True)
            
            # Save content based on its type and section
            for section, section_content in content.items():
                section_path = os.path.join(content_path, section)
                os.makedirs(section_path, exist_ok=True)
                
                if isinstance(section_content, str):
                    with open(os.path.join(section_path, "_index.md"), "w") as f:
                        f.write(section_content)
                elif isinstance(section_content, dict):
                    for page, page_content in section_content.items():
                        with open(os.path.join(section_path, f"{page}.md"), "w") as f:
                            f.write(page_content)
            
            return True
        except Exception as e:
            print(f"Error saving content: {str(e)}")
            return False
