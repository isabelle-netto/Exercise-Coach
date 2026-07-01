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
        padding-bottom: 95px !important;
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
        border-radius: 10px;
        border: none;
        padding: 0.7rem 1.4rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .nav-gap {
        height: 110px;
    }

    .floating-nav {
        position: fixed;
        bottom: 22px;
        left: 50%;
        transform: translateX(-50%);
        width: min(430px, 92vw);
        background: rgba(18, 16, 15, 0.82);
        border: 1px solid rgba(159, 185, 212, 0.45);
        border-radius: 999px;
        padding: 10px 12px;
        z-index: 999999;
        box-shadow: 0 12px 35px rgba(0,0,0,0.45);
        backdrop-filter: blur(16px);
    }

    .floating-nav div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: white !important;
        box-shadow: none !important;
        height: 48px !important;
        min-height: 48px !important;
        font-size: 24px !important;
        padding: 0 !important;
        border-radius: 999px !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }

    .floating-nav div.stButton > button:hover {
        background: rgba(159, 185, 212, 0.28) !important;
        transform: scale(1.06);
    }

    .floating-nav div.stButton > button * {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    apply_accessibility_styles()


def bottom_nav():
    st.markdown("<div class='nav-gap'></div>", unsafe_allow_html=True)

    st.markdown("<div class='floating-nav'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🏠", use_container_width=True, key="nav_home", help="Home"):
            st.switch_page("pages/07_Home.py")

    with col2:
        if st.button("🏋️", use_container_width=True, key="nav_exercises", help="Exercises"):
            st.switch_page("pages/08_Exercises.py")

    with col3:
        if st.button("📊", use_container_width=True, key="nav_stats", help="Stats"):
            st.switch_page("pages/09_Stats.py")

    with col4:
        if st.button("👤", use_container_width=True, key="nav_profile", help="Profile"):
            st.switch_page("pages/11_Update_Profile.py")

    st.markdown("</div>", unsafe_allow_html=True)