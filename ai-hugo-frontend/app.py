import streamlit as st
import requests
import json
import zipfile
import io
import os
from pathlib import Path
from utils.llm_client import LLMClient
from utils.hugo_generator import HugoGenerator

# Configure page
st.set_page_config(
    page_title="Hugo AI Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .section-header {
        background: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'site_config' not in st.session_state:
    st.session_state.site_config = {}
if 'generated_site_id' not in st.session_state:
    st.session_state.generated_site_id = None
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = []
if 'site_created' not in st.session_state:
    st.session_state.site_created = False

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Hugo AI Studio</h1>
        <p>Create beautiful websites with AI in minutes - All in one page!</p>
    </div>
    """, unsafe_allow_html=True)

    # Three-column layout
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        render_site_configuration()

    with col2:
        render_content_generation()

    with col3:
        render_preview_and_download()

def render_site_configuration():
    st.markdown('<div class="section-header"><h3>📝 Site Configuration</h3></div>', unsafe_allow_html=True)

    with st.form("site_config_form", clear_on_submit=False):
        site_name = st.text_input(
            "🏷️ Site Name",
            value=st.session_state.site_config.get("site_name", ""),
            placeholder="e.g., Tech Innovation Blog"
        )

        site_description = st.text_area(
            "📝 Site Description",
            value=st.session_state.site_config.get("site_description", ""),
            placeholder="Describe your website in a few sentences...",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            theme_type = st.selectbox(
                "🎨 Theme Type",
                ["blog", "portfolio", "business", "documentation"],
                index=["blog", "portfolio", "business", "documentation"].index(
                    st.session_state.site_config.get("theme_type", "blog")
                )
            )

        with col2:
            main_sections = st.multiselect(
                "📂 Main Sections",
                ["About", "Blog", "Projects", "Contact", "Services", "Documentation"],
                default=st.session_state.site_config.get("main_sections", ["About", "Blog"])
            )

        submitted = st.form_submit_button("🚀 Create Website", use_container_width=True)

        if submitted and site_name and site_description:
            config = {
                "site_name": site_name,
                "site_description": site_description,
                "theme_type": theme_type,
                "main_sections": main_sections
            }

            st.session_state.site_config = config

            with st.spinner("Creating your website..."):
                try:
                    hugo_generator = HugoGenerator()
                    site_id = hugo_generator.create_site(config)
                    st.session_state.generated_site_id = site_id
                    st.session_state.site_created = True

                    st.success("✅ Website created successfully!")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error creating site: {str(e)}")

        elif submitted:
            st.warning("⚠️ Please fill in both site name and description!")

def render_content_generation():
    st.markdown('<div class="section-header"><h3>🤖 Content Generation</h3></div>', unsafe_allow_html=True)

    if not st.session_state.site_created:
        st.info("👈 Create a website first!")
        st.markdown("**Steps:**\n1. Fill site configuration\n2. Click 'Create Website'\n3. Generate content here")
        return

    # Show current site info
    if st.session_state.site_config:
        st.success(f"✅ Working on: **{st.session_state.site_config.get('site_name', 'Your Site')}**")

    with st.form("content_generation_form", clear_on_submit=False):
        content_type = st.selectbox(
            "📝 Content Type",
            ["Blog Post", "About Page", "Contact Page", "Service Page", "Project Page"]
        )

        title = st.text_input(
            "🏷️ Title",
            placeholder="e.g., Welcome to My Blog",
            help="Enter a catchy title for your content"
        )

        requirements = st.text_area(
            "📋 Content Requirements",
            placeholder="Describe what you want the AI to write...\n\nExample: Write a welcome post about technology trends, include sections about AI, machine learning, and future predictions.",
            height=120,
            help="Be specific about what you want - the more details, the better the result!"
        )

        col1, col2 = st.columns(2)
        with col1:
            tone = st.selectbox(
                "🎭 Tone",
                ["Professional", "Casual", "Friendly", "Formal", "Creative"],
                index=0
            )

        with col2:
            length = st.selectbox(
                "📏 Length",
                ["Short (300 words)", "Medium (600 words)", "Long (1000+ words)"],
                index=1
            )

        generate_btn = st.form_submit_button("🚀 Generate Content", use_container_width=True)

        if generate_btn and title and requirements:
            with st.spinner("🤖 AI is writing your content..."):
                try:
                    llm_client = LLMClient()

                    word_count = {"Short (300 words)": "300", "Medium (600 words)": "600", "Long (1000+ words)": "1000+"}[length]

                    prompt = f"""
                    Write a {content_type.lower()} with these specifications:

                    Title: {title}
                    Content Requirements: {requirements}
                    Tone: {tone}
                    Target Length: {word_count} words
                    Website: {st.session_state.site_config.get('site_name', 'My Site')}
                    Website Type: {st.session_state.site_config.get('theme_type', 'blog')}

                    Create engaging, well-structured content in Markdown format.
                    Include:
                    - Compelling introduction
                    - Clear headings and subheadings
                    - Engaging paragraphs
                    - Call-to-action if appropriate
                    - Professional formatting

                    Make it ready to publish and SEO-friendly.
                    """

                    generated_content = llm_client.generate_content(prompt)

                    if generated_content:
                        content_item = {
                            "title": title,
                            "content": generated_content,
                            "type": content_type,
                            "tone": tone,
                            "length": length
                        }
                        st.session_state.generated_content.append(content_item)

                        # Save to backend
                        hugo_generator = HugoGenerator()
                        success = hugo_generator.update_content(
                            st.session_state.generated_site_id,
                            {title.lower().replace(" ", "_"): generated_content}
                        )

                        if success:
                            st.success("✅ Content generated and added to your site!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning("⚠️ Content generated but failed to save to site.")
                    else:
                        st.error("❌ Failed to generate content. Please try again.")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        elif generate_btn:
            st.warning("⚠️ Please fill in both title and requirements!")

def render_preview_and_download():
    st.markdown('<div class="section-header"><h3>🌐 Preview & Download</h3></div>', unsafe_allow_html=True)

    if not st.session_state.site_created:
        st.info("👈 Create a website to see preview!")
        st.markdown("**Your site will appear here once created**")
        return

    # Site information
    if st.session_state.generated_site_id:
        site_name = st.session_state.site_config.get('site_name', 'Your Site')
        preview_url = f"http://43.192.149.110:8080/sites/{st.session_state.generated_site_id}/"

        st.success(f"🎉 **{site_name}** is live!")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("🌐 Open Site", preview_url, use_container_width=True)

        with col2:
            if st.button("📥 Download Site", use_container_width=True):
                download_site()

        # Site stats
        content_count = len(st.session_state.generated_content)
        st.metric("📄 Content Pages", content_count)

        # Generated content list
        if st.session_state.generated_content:
            st.markdown("### 📝 Generated Content")
            for i, content in enumerate(st.session_state.generated_content, 1):
                with st.expander(f"{i}. {content['type']}: {content['title']}"):
                    st.markdown(f"**Tone:** {content.get('tone', 'N/A')}")
                    st.markdown(f"**Length:** {content.get('length', 'N/A')}")
                    st.markdown("**Preview:**")
                    preview_text = content['content'][:200] + "..." if len(content['content']) > 200 else content['content']
                    st.markdown(preview_text)

        # Live preview
        st.markdown("### 🖥️ Live Preview")
        try:
            st.components.v1.iframe(preview_url, height=500, scrolling=True)
        except Exception:
            st.markdown(f"**[Click here to view your site]({preview_url})**")
            st.info("Preview not available in iframe. Click the link above to view your site.")

    else:
        st.info("👈 Generate content to see your site!")

def download_site():
    """Create and offer site download"""
    try:
        if not st.session_state.generated_site_id:
            st.error("No site to download!")
            return

        # Create a zip file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add site files (this is a simplified version)
            site_name = st.session_state.site_config.get('site_name', 'my-site')

            # Add config file
            config_content = f"""
title: {st.session_state.site_config.get('site_name', 'My Site')}
description: {st.session_state.site_config.get('site_description', 'A website created with AI')}
theme: {st.session_state.site_config.get('theme_type', 'blog')}
"""
            zip_file.writestr("config.yaml", config_content)

            # Add generated content
            for i, content in enumerate(st.session_state.generated_content):
                filename = f"content/{content['title'].lower().replace(' ', '-')}.md"
                zip_file.writestr(filename, content['content'])

            # Add README
            readme_content = f"""
# {st.session_state.site_config.get('site_name', 'My Site')}

This website was generated using Hugo AI Studio.

## Generated Content:
{chr(10).join([f"- {content['title']}" for content in st.session_state.generated_content])}

## To use this site:
1. Install Hugo: https://gohugo.io/installation/
2. Extract this zip file
3. Run: hugo server
4. Open: http://localhost:1313

Generated on: {st.session_state.generated_site_id}
"""
            zip_file.writestr("README.md", readme_content)

        zip_buffer.seek(0)

        # Offer download
        site_name = st.session_state.site_config.get('site_name', 'my-site').lower().replace(' ', '-')
        st.download_button(
            label="📥 Download ZIP",
            data=zip_buffer.getvalue(),
            file_name=f"{site_name}-hugo-site.zip",
            mime="application/zip",
            use_container_width=True
        )

        st.success("✅ Site package ready for download!")

    except Exception as e:
        st.error(f"❌ Download failed: {str(e)}")

if __name__ == "__main__":
    main()
