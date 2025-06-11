import streamlit as st

def render_site_config():
    st.header("Site Configuration")
    
    with st.form("site_config_form"):
        # Basic site information
        st.subheader("Basic Information")
        site_name = st.text_input("Site Name", value=st.session_state.site_config.get("site_name", ""))
        site_description = st.text_area("Site Description", value=st.session_state.site_config.get("site_description", ""))
        
        # Theme selection
        st.subheader("Theme Selection")
        theme_type = st.selectbox(
            "Theme Type",
            ["blog", "portfolio", "business", "documentation"],
            index=["blog", "portfolio", "business", "documentation"].index(
                st.session_state.site_config.get("theme_type", "blog")
            )
        )
        
        # Content structure
        st.subheader("Content Structure")
        main_sections = st.multiselect(
            "Main Sections",
            ["About", "Blog", "Projects", "Contact", "Services", "Documentation"],
            default=st.session_state.site_config.get("main_sections", ["About", "Blog"])
        )
        
        if st.form_submit_button("Save Configuration"):
            st.session_state.site_config = {
                "site_name": site_name,
                "site_description": site_description,
                "theme_type": theme_type,
                "main_sections": main_sections
            }
            st.success("Configuration saved successfully!")
