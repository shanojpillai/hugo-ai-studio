import os
import shutil
from typing import Dict, Any
import yaml
import subprocess
from models.site_config import SiteConfig

class HugoService:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "..")
        self.templates_path = os.path.join(self.base_path, "templates")
        self.sites_path = os.path.join(self.base_path, "generated_sites")
        os.makedirs(self.sites_path, exist_ok=True)
    
    async def create_site(self, site_id: str, config: SiteConfig) -> bool:
        """
        Create a new Hugo site with the specified configuration
        """
        try:
            site_path = os.path.join(self.sites_path, site_id)
            
            # Copy template based on theme type
            template_path = os.path.join(self.templates_path, config.theme_type)
            shutil.copytree(template_path, site_path)
            
            # Create Hugo config file
            config_data = {
                "baseURL": config.base_url or f"http://localhost:8080/sites/{site_id}",
                "languageCode": config.language_code,
                "title": config.site_name,
                "params": {
                    "description": config.site_description
                }
            }
            
            with open(os.path.join(site_path, "config.yaml"), "w") as f:
                yaml.dump(config_data, f)
            
            # Initialize content directories
            for section in config.main_sections:
                section_path = os.path.join(site_path, "content", section.lower())
                os.makedirs(section_path, exist_ok=True)
                
                # Create section index
                with open(os.path.join(section_path, "_index.md"), "w") as f:
                    f.write(f"""---
title: {section}
---
""")
            
            return True
        except Exception as e:
            print(f"Error creating site: {str(e)}")
            return False
    
    async def update_content(self, site_id: str, content: Dict[str, Any]) -> bool:
        """
        Update content in an existing Hugo site
        """
        try:
            site_path = os.path.join(self.sites_path, site_id)
            
            # Build Hugo site
            result = subprocess.run(
                ["hugo", "--source", site_path, "--destination", "public"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Hugo build failed: {result.stderr}")
            
            return True
        except Exception as e:
            print(f"Error updating site: {str(e)}")
            return False
