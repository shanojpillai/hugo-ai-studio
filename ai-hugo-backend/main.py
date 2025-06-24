from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uuid
import json
import sqlite3
import zipfile
import io
from pathlib import Path
from datetime import datetime
from services.hugo_service import HugoService
from services.llm_service import LLMService

app = FastAPI(title="Hugo AI Studio Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
hugo_service = HugoService()
llm_service = LLMService()

# Database setup
def init_db():
    conn = sqlite3.connect('/app/data/sites.db')
    cursor = conn.cursor()

    # Sites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            id TEXT PRIMARY KEY,
            site_name TEXT NOT NULL,
            site_description TEXT,
            theme_type TEXT,
            main_sections TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'created'
        )
    ''')

    # Content table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id TEXT,
            content_type TEXT,
            title TEXT,
            content TEXT,
            tone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES sites (id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database
os.makedirs('/app/data', exist_ok=True)
init_db()

# Pydantic models
class SiteConfigRequest(BaseModel):
    siteName: str
    siteDescription: str
    themeType: str
    mainSections: List[str]

class ContentGenerationRequest(BaseModel):
    siteId: str
    contentType: str
    title: str
    requirements: str
    tone: str
    siteConfig: Dict[str, Any]

class ChatCreateRequest(BaseModel):
    description: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/sites")
async def create_site(config: SiteConfigRequest) -> Dict[str, str]:
    """Create a new Hugo site with database storage"""
    try:
        site_id = str(uuid.uuid4())

        # Store in database
        conn = sqlite3.connect('/app/data/sites.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sites (id, site_name, site_description, theme_type, main_sections, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            site_id,
            config.siteName,
            config.siteDescription,
            config.themeType,
            json.dumps(config.mainSections),
            'creating'
        ))

        conn.commit()
        conn.close()

        # Create actual Hugo site
        site_config = {
            "site_name": config.siteName,
            "site_description": config.siteDescription,
            "theme_type": config.themeType,
            "main_sections": config.mainSections
        }

        success = await hugo_service.create_site(site_id, site_config)

        if success:
            # Update status in database
            conn = sqlite3.connect('/app/data/sites.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE sites SET status = ? WHERE id = ?', ('ready', site_id))
            conn.commit()
            conn.close()

            return {"site_id": site_id, "status": "created"}
        else:
            raise Exception("Failed to create Hugo site")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-content")
async def generate_content(request: ContentGenerationRequest) -> Dict[str, Any]:
    """Generate content using LLM and save to database"""
    try:
        # Create prompt for LLM
        prompt = f"""
        Create {request.contentType.lower()} content with the following details:

        Title: {request.title}
        Requirements: {request.requirements}
        Tone: {request.tone}
        Site Type: {request.siteConfig.get('themeType', 'blog')}
        Site Name: {request.siteConfig.get('siteName', 'My Site')}

        Generate well-structured, engaging content in Markdown format.
        Include appropriate headings, paragraphs, and formatting.
        Make it professional and ready to publish.
        """

        # Generate content using LLM
        generated_content = await llm_service.generate_content(prompt, {"model": "llama3.2"})

        if not generated_content:
            raise Exception("Failed to generate content")

        # Save to database
        conn = sqlite3.connect('/app/data/sites.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO content (site_id, content_type, title, content, tone)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.siteId,
            request.contentType,
            request.title,
            generated_content,
            request.tone
        ))

        conn.commit()
        conn.close()

        # Update Hugo site
        success = await hugo_service.update_content(
            request.siteId,
            {request.title.lower().replace(" ", "_"): generated_content}
        )

        if success:
            # Build the site
            await hugo_service.build_site(request.siteId)

        return {
            "id": cursor.lastrowid,
            "title": request.title,
            "contentType": request.contentType,
            "content": generated_content[:200] + "..." if len(generated_content) > 200 else generated_content,
            "tone": request.tone,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sites/{site_id}/download")
async def download_site(site_id: str):
    """Download site as ZIP file"""
    try:
        # Get site info from database
        conn = sqlite3.connect('/app/data/sites.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM sites WHERE id = ?', (site_id,))
        site_row = cursor.fetchone()

        if not site_row:
            raise HTTPException(status_code=404, detail="Site not found")

        # Get content
        cursor.execute('SELECT * FROM content WHERE site_id = ?', (site_id,))
        content_rows = cursor.fetchall()
        conn.close()

        # Create ZIP file
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add config file
            config_content = f"""
title: {site_row[1]}
description: {site_row[2]}
theme: {site_row[3]}
baseURL: "/"
"""
            zip_file.writestr("config.yaml", config_content)

            # Add content files
            for content_row in content_rows:
                filename = f"content/{content_row[3].lower().replace(' ', '-')}.md"
                frontmatter = f"""---
title: {content_row[3]}
type: {content_row[2]}
---

"""
                zip_file.writestr(filename, frontmatter + content_row[4])

            # Add README
            readme_content = f"""
# {site_row[1]}

This website was generated using Hugo AI Studio.

## Generated Content:
{chr(10).join([f"- {row[3]}" for row in content_rows])}

## To use this site:
1. Install Hugo: https://gohugo.io/installation/
2. Extract this zip file
3. Run: hugo server
4. Open: http://localhost:1313

Generated on: {site_row[5]}
"""
            zip_file.writestr("README.md", readme_content)

        zip_buffer.seek(0)

        # Return ZIP file
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={site_row[1].replace(' ', '-')}-hugo-site.zip"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-from-description")
async def create_from_description(request: ChatCreateRequest) -> Dict[str, Any]:
    """Create a complete website from natural language description"""
    try:
        # Use LLM to analyze the description and extract site details
        analysis_prompt = f"""
        Analyze this website description and extract the key information:
        "{request.description}"

        Return a JSON object with:
        - siteName: A catchy name for the website
        - siteDescription: A professional description
        - themeType: one of "blog", "portfolio", "business", "documentation"
        - mainSections: array of relevant sections like ["About", "Blog", "Contact", "Services", "Portfolio"]
        - contentIdeas: array of 3-5 content pieces to create with titles and descriptions

        Make it professional and relevant to the user's request.
        Return only valid JSON.
        """

        analysis_result = await llm_service.generate_content(analysis_prompt, {"model": "llama3.2"})

        # Parse the LLM response
        import json
        try:
            site_config = json.loads(analysis_result)
        except:
            # Fallback if JSON parsing fails
            site_config = {
                "siteName": "My AI Website",
                "siteDescription": request.description,
                "themeType": "blog",
                "mainSections": ["About", "Blog", "Contact"],
                "contentIdeas": [
                    {"title": "Welcome", "description": "Welcome page content"}
                ]
            }

        # Create the site
        site_id = str(uuid.uuid4())

        # Store in database
        conn = sqlite3.connect('/app/data/sites.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sites (id, site_name, site_description, theme_type, main_sections, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            site_id,
            site_config.get("siteName", "My AI Website"),
            site_config.get("siteDescription", request.description),
            site_config.get("themeType", "blog"),
            json.dumps(site_config.get("mainSections", ["About", "Blog"])),
            'creating'
        ))

        conn.commit()
        conn.close()

        # Create Hugo site
        hugo_config = {
            "site_name": site_config.get("siteName", "My AI Website"),
            "site_description": site_config.get("siteDescription", request.description),
            "theme_type": site_config.get("themeType", "blog"),
            "main_sections": site_config.get("mainSections", ["About", "Blog"])
        }

        success = await hugo_service.create_site(site_id, hugo_config)

        if not success:
            raise Exception("Failed to create Hugo site")

        # Generate content for each idea
        content_ideas = site_config.get("contentIdeas", [])
        for idea in content_ideas[:3]:  # Limit to 3 pieces of content
            content_prompt = f"""
            Create {idea.get('description', 'content')} for a website about: {request.description}

            Title: {idea.get('title', 'Welcome')}

            Write engaging, professional content in Markdown format.
            Include appropriate headings, paragraphs, and formatting.
            Make it relevant to the website theme and description.
            """

            generated_content = await llm_service.generate_content(content_prompt, {"model": "llama3.2"})

            if generated_content:
                # Save content to database
                conn = sqlite3.connect('/app/data/sites.db')
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO content (site_id, content_type, title, content, tone)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    site_id,
                    "Page",
                    idea.get('title', 'Welcome'),
                    generated_content,
                    "Professional"
                ))

                conn.commit()
                conn.close()

                # Update Hugo site
                await hugo_service.update_content(
                    site_id,
                    {idea.get('title', 'welcome').lower().replace(" ", "_"): generated_content}
                )

        # Build the site
        await hugo_service.build_site(site_id)

        # Update status
        conn = sqlite3.connect('/app/data/sites.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE sites SET status = ? WHERE id = ?', ('ready', site_id))
        conn.commit()
        conn.close()

        return {
            "siteId": site_id,
            "siteName": site_config.get("siteName", "My AI Website"),
            "siteDescription": site_config.get("siteDescription", request.description),
            "previewUrl": f"http://43.192.149.110:8080/sites/{site_id}/",
            "status": "ready"
        }

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
