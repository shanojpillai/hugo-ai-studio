from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import os
import uuid
import json
import sqlite3
import zipfile
import io
import httpx
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Hugo AI Studio Backend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/sites.db")
SITES_PATH = "/app/sites"

# Ensure directories exist
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(SITES_PATH, exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class WebsiteRequest(BaseModel):
    description: str

class WebsiteResponse(BaseModel):
    siteId: str
    siteName: str
    previewUrl: str

# LLM Service
async def generate_with_ollama(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Ollama error: {e}")
            return "Error generating content"

# Hugo Site Generator
def create_hugo_site(site_id: str, site_name: str, content: str):
    site_dir = Path(SITES_PATH) / site_id
    site_dir.mkdir(exist_ok=True)
    
    # Create Hugo config
    config_content = f'''
title = "{site_name}"
baseURL = "/"
languageCode = "en-us"

[params]
  description = "Generated by Hugo AI Studio"
'''
    
    with open(site_dir / "config.toml", "w") as f:
        f.write(config_content)
    
    # Create content directory
    content_dir = site_dir / "content"
    content_dir.mkdir(exist_ok=True)
    
    # Create index page
    index_content = f'''---
title: "Welcome to {site_name}"
date: {datetime.now().isoformat()}
---

{content}
'''
    
    with open(content_dir / "_index.md", "w") as f:
        f.write(index_content)
    
    # Create simple HTML template
    layouts_dir = site_dir / "layouts"
    layouts_dir.mkdir(exist_ok=True)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .header {{ background: linear-gradient(135deg, #007acc, #0056b3); color: white; padding: 20px; margin: -20px -20px 20px -20px; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{site_name}</h1>
        <p>Generated by Hugo AI Studio</p>
    </div>
    <div class="content">
        {content.replace(chr(10), '<br>')}
    </div>
    <div class="footer">
        <p>Created on {datetime.now().strftime('%B %d, %Y')}</p>
    </div>
</body>
</html>'''
    
    with open(site_dir / "index.html", "w") as f:
        f.write(html_template)
    
    return True

# API Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/create-website", response_model=WebsiteResponse)
async def create_website(request: WebsiteRequest):
    try:
        # Generate site details using LLM
        analysis_prompt = f'''
        Based on this description: "{request.description}"
        
        Create a website with:
        1. A catchy site name (2-4 words)
        2. Detailed content (3-5 paragraphs)
        
        Format your response as:
        SITE_NAME: [name here]
        CONTENT: [detailed content here]
        
        Make it professional and engaging.
        '''
        
        llm_response = await generate_with_ollama(analysis_prompt)
        
        # Parse LLM response
        lines = llm_response.split('\n')
        site_name = "My AI Website"
        content = "Welcome to your AI-generated website!"
        
        for line in lines:
            if line.startswith("SITE_NAME:"):
                site_name = line.replace("SITE_NAME:", "").strip()
            elif line.startswith("CONTENT:"):
                content = line.replace("CONTENT:", "").strip()
        
        # Generate additional content if needed
        if len(content) < 100:
            content_prompt = f"Write detailed, engaging content for a website about: {request.description}. Make it 3-5 paragraphs."
            content = await generate_with_ollama(content_prompt)
        
        # Create unique site ID
        site_id = str(uuid.uuid4())
        
        # Store in database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sites (id, name, description, content)
            VALUES (?, ?, ?, ?)
        ''', (site_id, site_name, request.description, content))
        
        conn.commit()
        conn.close()
        
        # Create Hugo site
        create_hugo_site(site_id, site_name, content)
        
        return WebsiteResponse(
            siteId=site_id,
            siteName=site_name,
            previewUrl=f"http://43.192.149.110:8080/sites/{site_id}/"
        )
        
    except Exception as e:
        print(f"Error creating website: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{site_id}")
async def download_site(site_id: str):
    try:
        # Get site from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
        site = cursor.fetchone()
        conn.close()
        
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            site_dir = Path(SITES_PATH) / site_id
            
            # Add all files from site directory
            if site_dir.exists():
                for file_path in site_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(site_dir)
                        zip_file.write(file_path, arcname)
            
            # Add README
            readme_content = f'''# {site[1]}

This website was generated using Hugo AI Studio.

## Description
{site[2]}

## Generated Content
{site[3][:200]}...

## To use this site:
1. Extract this ZIP file
2. Open index.html in your browser
3. Or use with Hugo static site generator

Generated on: {site[4]}
'''
            zip_file.writestr("README.md", readme_content)
        
        zip_buffer.seek(0)
        
        # Return ZIP file
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={site[1].replace(' ', '-')}-website.zip"}
        )
        
    except Exception as e:
        print(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
