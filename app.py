"""NeuroVision AI — premium multipage Streamlit research application.
Run: streamlit run app.py
"""
from __future__ import annotations
import streamlit as st
from site_theme import footer, header, inject_theme

st.set_page_config(
    page_title="NeuroVision AI | MRI Research Platform",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "NeuroVision AI is an educational MRI research prototype, not a clinical diagnostic system."},
)

inject_theme()
pages = [
    st.Page("site_pages/home.py", title="Home", icon=":material/home:", default=True),
    st.Page("site_pages/analyze.py", title="MRI Analysis", icon=":material/radiology:", url_path="analyze"),
    st.Page("site_pages/about.py", title="About", icon=":material/neurology:", url_path="about"),
    st.Page("site_pages/contact.py", title="Contact", icon=":material/mail:", url_path="contact"),
    st.Page("site_pages/privacy.py", title="Privacy & Ethics", icon=":material/verified_user:", url_path="privacy"),
]
selected = st.navigation(pages, position="top")
header()
selected.run()
footer()
