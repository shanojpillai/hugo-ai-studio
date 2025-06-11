from pydantic import BaseModel
from typing import List, Optional

class SiteConfig(BaseModel):
    site_name: str
    site_description: str
    theme_type: str
    main_sections: List[str]
    language_code: str = "en-us"
    base_url: Optional[str] = None
