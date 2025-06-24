import streamlit as st
import requests
import json
import time
import uuid
from pathlib import Path
from utils.llm_client import LLMClient
from utils.hugo_generator import HugoGenerator

# Configure page
st.set_page_config(
    page_title="AI Hugo Site Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    st.title("🚀 AI-Powered Hugo Site Generator")
    st.markdown("Create beautiful websites with AI in minutes!")

    # Single page layout with columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Site Configuration")
        render_site_config()

        st.header("🤖 Content Generation")
        render_content_generator()

    with col2:
        st.header("🌐 Live Preview")
        render_preview()

def render_site_config():
    with st.form("site_config_form"):
        site_name = st.text_input("Site Name", value=st.session_state.site_config.get("site_name", "My Awesome Site"))
        site_description = st.text_area("Site Description", value=st.session_state.site_config.get("site_description", "A beautiful website created with AI"))

        theme_type = st.selectbox(
            "Theme Type",
            ["blog", "portfolio", "business", "documentation"],
            index=["blog", "portfolio", "business", "documentation"].index(
                st.session_state.site_config.get("theme_type", "blog")
            )
        )

        main_sections = st.multiselect(
            "Main Sections",
            ["About", "Blog", "Projects", "Contact", "Services", "Documentation"],
            default=st.session_state.site_config.get("main_sections", ["About", "Blog"])
        )

        if st.form_submit_button("💾 Save & Create Site"):
            config = {
                "site_name": site_name,
                "site_description": site_description,
                "theme_type": theme_type,
                "main_sections": main_sections
            }

            st.session_state.site_config = config

            # Create site immediately
            try:
                hugo_generator = HugoGenerator()
                site_id = hugo_generator.create_site(config)
                st.session_state.generated_site_id = site_id
                st.session_state.site_created = True
                st.success(f"✅ Site created successfully! Site ID: {site_id}")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating site: {str(e)}")

def render_content_generator():
    if not st.session_state.site_created:
        st.info("👆 Please create a site first using the configuration above.")
        return

    with st.form("content_generation_form"):
        content_type = st.selectbox(
            "Content Type",
            ["Blog Post", "Page Content", "About Page", "Contact Page"]
        )

        title = st.text_input("Title", placeholder="e.g., Welcome to My Site")
        requirements = st.text_area(
            "Content Requirements",
            placeholder="Describe what you want the AI to generate...",
            help="Be specific about what you want"
        )

        tone = st.select_slider(
            "Content Tone",
            options=["Formal", "Professional", "Neutral", "Casual", "Friendly"],
            value="Professional"
        )

        if st.form_submit_button("🚀 Generate Content"):
            if not title or not requirements:
                st.error("Please fill in both title and requirements.")
                return

            with st.spinner("Generating content with AI..."):
                try:
                    llm_client = LLMClient()

                    prompt = f"""
                    Create {content_type.lower()} content with the following details:

                    Title: {title}
                    Requirements: {requirements}
                    Tone: {tone}
                    Site Type: {st.session_state.site_config.get('theme_type', 'blog')}
                    Site Name: {st.session_state.site_config.get('site_name', 'My Site')}

                    Generate well-structured, engaging content in Markdown format.
                    Include appropriate headings, paragraphs, and formatting.
                    Make it professional and ready to publish.
                    """

                    generated_content = llm_client.generate_content(prompt)

                    if generated_content:
                        # Store content in session state
                        content_item = {
                            "title": title,
                            "content": generated_content,
                            "type": content_type,
                            "tone": tone
                        }
                        st.session_state.generated_content.append(content_item)

                        # Save to backend
                        hugo_generator = HugoGenerator()
                        success = hugo_generator.update_content(
                            st.session_state.generated_site_id,
                            {title.lower().replace(" ", "_"): generated_content}
                        )

                        if success:
                            st.success("✅ Content generated and saved!")
                            st.rerun()
                        else:
                            st.warning("Content generated but failed to save to site.")
                    else:
                        st.error("Failed to generate content. Please try again.")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

def render_preview():
    if not st.session_state.site_created:
        st.info("No site created yet. Create a site to see the preview.")
        return

    if st.session_state.generated_site_id:
        preview_url = f"http://43.192.149.110:8080/sites/{st.session_state.generated_site_id}/"

        st.markdown(f"**🌐 Your Site URL:** [{preview_url}]({preview_url})")

        # Show generated content
        if st.session_state.generated_content:
            st.subheader("📄 Generated Content")
            for i, content in enumerate(st.session_state.generated_content):
                with st.expander(f"{content['type']}: {content['title']}"):
                    st.markdown(content['content'][:300] + "..." if len(content['content']) > 300 else content['content'])

        # Embed preview
        st.subheader("🖥️ Live Preview")
        try:
            st.components.v1.iframe(preview_url, height=600, scrolling=True)
        except:
            st.markdown(f"**Preview not available in iframe. [Open in new tab]({preview_url})**")
    else:
        st.info("Generate some content to see your site preview.")

if __name__ == "__main__":
    main()
