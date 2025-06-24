from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uuid
import json
from pathlib import Path
from models.site_config import SiteConfig
from models.generation_request import GenerationRequest
from services.content_service import ContentService
from services.hugo_service import HugoService
from services.llm_service import LLMService

app = FastAPI(title="AI Hugo Generator Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
content_service = ContentService()
hugo_service = HugoService()
llm_service = LLMService()

# Simple in-memory storage for sites (in production, use a database)
sites_storage = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/sites")
async def create_site(config: Dict[str, Any]) -> Dict[str, str]:
    """Create a new Hugo site"""
    try:
        site_id = str(uuid.uuid4())

        # Store site config
        sites_storage[site_id] = {
            "config": config,
            "content": [],
            "created_at": str(uuid.uuid4()),
            "status": "created"
        }

        # Create actual Hugo site
        success = await hugo_service.create_site(site_id, config)
        if success:
            sites_storage[site_id]["status"] = "ready"
            return {"site_id": site_id, "status": "created"}
        else:
            raise Exception("Failed to create Hugo site")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sites/{site_id}")
async def get_site(site_id: str) -> Dict[str, Any]:
    """Get site information"""
    if site_id not in sites_storage:
        raise HTTPException(status_code=404, detail="Site not found")

    site_data = sites_storage[site_id]
    preview_url = f"http://43.192.149.110:8080/sites/{site_id}/"

    return {
        "site_id": site_id,
        "config": site_data["config"],
        "content": site_data["content"],
        "status": site_data["status"],
        "preview_url": preview_url
    }

@app.get("/sites")
async def list_sites() -> Dict[str, Any]:
    """List all sites"""
    return {"sites": list(sites_storage.keys()), "count": len(sites_storage)}

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
        if site_id not in sites_storage:
            raise HTTPException(status_code=404, detail="Site not found")

        # Store content in memory
        sites_storage[site_id]["content"].append(content)

        # Update actual Hugo site
        success = await hugo_service.update_content(site_id, content)

        if success:
            # Build the site
            build_success = await hugo_service.build_site(site_id)
            return {"success": build_success}
        else:
            return {"success": False}

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
