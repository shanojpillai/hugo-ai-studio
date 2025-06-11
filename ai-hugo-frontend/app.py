import streamlit as st
import requests
import json
import time
from pathlib import Path
from components.site_config import render_site_config
from components.content_generator import render_content_generator
from components.preview import render_preview
from utils.llm_client import LLMClient
from utils.hugo_generator import HugoGenerator

# Health check route
def handle_health_check():
    if st.experimental_get_query_params().get("_health") == ["check"]:
        st.write({"status": "healthy"})
        st.stop()

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Hugo Site Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'generation_status' not in st.session_state:
    st.session_state.generation_status = None
if 'site_config' not in st.session_state:
    st.session_state.site_config = {}
if 'generated_site_id' not in st.session_state:
    st.session_state.generated_site_id = None

def main():
    st.title("AI-Powered Hugo Site Generator")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Site Configuration", "Content Generation", "Preview"]
    )
    
    if page == "Site Configuration":
        render_site_config()
    elif page == "Content Generation":
        render_content_generator()
    else:
        render_preview()

if __name__ == "__main__":
    handle_health_check()
    main()
