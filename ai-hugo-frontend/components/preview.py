import streamlit as st

def render_preview():
    st.header("Site Preview")
    
    if not st.session_state.generated_site_id:
        st.warning("No site has been generated yet!")
        return
    
    # Display preview options
    preview_type = st.radio(
        "Preview Type",
        ["Live Preview", "Code View"]
    )
    
    if preview_type == "Live Preview":
        st.components.v1.iframe(
            f"http://localhost:8080/sites/{st.session_state.generated_site_id}",
            height=600
        )
    else:
        st.code("""
        # Example Hugo configuration
        baseURL = 'http://example.org/'
        languageCode = 'en-us'
        title = 'My New Hugo Site'
        """, language="toml")
