from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uuid
from models.site_config import SiteConfig
from models.generation_request import GenerationRequest
from services.content_service import ContentService
from services.hugo_service import HugoService
from services.llm_service import LLMService

app = FastAPI(title="AI Hugo Generator Backend")

# Initialize services
content_service = ContentService()
hugo_service = HugoService()
llm_service = LLMService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/sites")
async def create_site(config: SiteConfig) -> Dict[str, str]:
    """Create a new Hugo site"""
    try:
        site_id = str(uuid.uuid4())
        await hugo_service.create_site(site_id, config)
        return {"site_id": site_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_content(request: GenerationRequest) -> Dict[str, str]:
    """Generate content using LLM"""
    try:
        content = await llm_service.generate_content(request.prompt, request.params)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sites/{site_id}/content")
async def update_site_content(site_id: str, content: Dict[str, Any]) -> Dict[str, bool]:
    """Update content in an existing Hugo site"""
    try:
        success = await hugo_service.update_content(site_id, content)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv

    load_dotenv()

    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, log_level="info")
