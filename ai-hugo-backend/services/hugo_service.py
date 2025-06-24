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
    
    async def create_site(self, site_id: str, config: Dict[str, Any]) -> bool:
        """
        Create a new Hugo site with the specified configuration
        """
        try:
            site_path = os.path.join(self.sites_path, site_id)

            # Create basic Hugo site structure
            os.makedirs(site_path, exist_ok=True)
            os.makedirs(os.path.join(site_path, "content"), exist_ok=True)
            os.makedirs(os.path.join(site_path, "static"), exist_ok=True)
            os.makedirs(os.path.join(site_path, "layouts"), exist_ok=True)

            # Create Hugo config file
            config_data = {
                "baseURL": f"http://43.192.149.110:8080/sites/{site_id}/",
                "languageCode": "en-us",
                "title": config.get("site_name", "My Site"),
                "params": {
                    "description": config.get("site_description", "A website created with AI")
                }
            }

            with open(os.path.join(site_path, "config.yaml"), "w") as f:
                yaml.dump(config_data, f)

            # Create basic index page
            with open(os.path.join(site_path, "content", "_index.md"), "w") as f:
                f.write(f"""---
title: {config.get("site_name", "My Site")}
---

# Welcome to {config.get("site_name", "My Site")}

{config.get("site_description", "A website created with AI")}
""")

            # Initialize content directories
            for section in config.get("main_sections", ["About"]):
                section_path = os.path.join(site_path, "content", section.lower())
                os.makedirs(section_path, exist_ok=True)

                # Create section index
                with open(os.path.join(section_path, "_index.md"), "w") as f:
                    f.write(f"""---
title: {section}
---

# {section}

Content for {section} section.
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
            content_path = os.path.join(site_path, "content")

            # Save content files
            for filename, content_text in content.items():
                file_path = os.path.join(content_path, f"{filename}.md")

                # Create frontmatter
                frontmatter = f"""---
title: {filename.replace('_', ' ').title()}
date: {subprocess.run(['date', '+%Y-%m-%dT%H:%M:%S'], capture_output=True, text=True).stdout.strip()}
---

"""

                with open(file_path, "w") as f:
                    f.write(frontmatter + content_text)

            return True
        except Exception as e:
            print(f"Error updating content: {str(e)}")
            return False

    async def build_site(self, site_id: str) -> bool:
        """
        Build the Hugo site and copy to nginx directory
        """
        try:
            site_path = os.path.join(self.sites_path, site_id)
            output_path = f"/usr/share/nginx/html/sites/{site_id}"

            # Ensure output directory exists
            os.makedirs(output_path, exist_ok=True)

            # Build Hugo site
            result = subprocess.run(
                ["hugo", "--source", site_path, "--destination", output_path],
                capture_output=True,
                text=True,
                cwd=site_path
            )

            if result.returncode != 0:
                print(f"Hugo build failed: {result.stderr}")
                return False

            print(f"Site {site_id} built successfully to {output_path}")
            return True

        except Exception as e:
            print(f"Error building site: {str(e)}")
            return False
