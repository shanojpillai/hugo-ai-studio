from pydantic import BaseModel
from typing import Dict, Any, Optional

class GenerationRequest(BaseModel):
    prompt: str
    params: Optional[Dict[str, Any]] = None
    content_type: str
    section: Optional[str] = None
    tone: Optional[str] = "Professional"
