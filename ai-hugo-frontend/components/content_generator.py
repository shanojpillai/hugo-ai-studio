import streamlit as st
from utils.llm_client import LLMClient
from utils.hugo_generator import HugoGenerator

def render_content_generator():
    st.header("Content Generation")
    
    if not st.session_state.site_config:
        st.warning("Please complete the site configuration first!")
        return
    
    with st.form("content_generation_form"):
        st.subheader("Content Requirements")
        
        # Content type selection
        content_type = st.selectbox(
            "Content Type",
            ["Page Content", "Blog Post", "Project Description"]
        )
        
        # Content details
        title = st.text_input("Title")
        requirements = st.text_area(
            "Content Requirements",
            help="Describe what you want the AI to generate"
        )
        
        tone = st.select_slider(
            "Content Tone",
            options=["Formal", "Professional", "Neutral", "Casual", "Friendly"],
            value="Professional"
        )
        
        if st.form_submit_button("Generate Content"):
            with st.spinner("Generating content..."):
                try:
                    # Initialize LLM client
                    llm_client = LLMClient()
                    hugo_generator = HugoGenerator()

                    # Create site first if not exists
                    if not st.session_state.generated_site_id:
                        site_id = hugo_generator.create_site(st.session_state.site_config)
                        st.session_state.generated_site_id = site_id
                        st.info(f"Created new site with ID: {site_id}")

                    # Generate content using LLM
                    prompt = f"""
                    Create {content_type.lower()} content with the following details:

                    Title: {title}
                    Requirements: {requirements}
                    Tone: {tone}
                    Site Type: {st.session_state.site_config.get('theme_type', 'blog')}

                    Generate well-structured, engaging content in Markdown format.
                    Include appropriate headings, paragraphs, and formatting.
                    """

                    generated_content = llm_client.generate_content(prompt)

                    if generated_content:
                        # Update site content
                        success = hugo_generator.update_content(
                            st.session_state.generated_site_id,
                            {title.lower().replace(" ", "_"): generated_content}
                        )

                        if success:
                            st.success("✅ Content generated and saved successfully!")
                            st.markdown("### Generated Content Preview:")
                            st.markdown(generated_content[:500] + "..." if len(generated_content) > 500 else generated_content)

                            # Show preview link
                            preview_url = f"http://43.192.149.110:8080/sites/{st.session_state.generated_site_id}/"
                            st.markdown(f"🌐 **Preview your site**: [View Site]({preview_url})")
                        else:
                            st.error("Failed to save content to site")
                    else:
                        st.error("Failed to generate content. Please try again.")

                except Exception as e:
                    st.error(f"Error generating content: {str(e)}")
                    st.error("Please check that all services are running and try again.")
