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
                    # Here we would integrate with the LLM service
                    st.success("Content generated successfully!")
                except Exception as e:
                    st.error(f"Error generating content: {str(e)}")
