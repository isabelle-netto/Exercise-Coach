import streamlit as st
from accessibility import init_accessibility_settings, apply_accessibility_styles


def apply_style():
    init_accessibility_settings()

    st.markdown("""
    <style>
    #MainMenu, footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
        height: 0px;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

    .card {
        padding: 24px;
        border-radius: 18px;
        margin-bottom: 18px;
    }

    div.stButton > button {
        border-radius: 6px;
        border: none;
        padding: 0.7rem 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .nav-gap {
        height: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

    apply_accessibility_styles()


def bottom_nav():
    st.markdown("<div class='nav-gap'></div>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Home", use_container_width=True, key="nav_home"):
            st.switch_page("pages/07_Home.py")

    with col2:
        if st.button("Exercises", use_container_width=True, key="nav_exercises"):
            st.switch_page("pages/08_Exercises.py")

    with col3:
        if st.button("Stats", use_container_width=True, key="nav_stats"):
            st.switch_page("pages/11_Stats.py")

    with col4:
        if st.button("Profile", use_container_width=True, key="nav_profile"):
            st.switch_page("pages/04_Mobility_Capability.py")