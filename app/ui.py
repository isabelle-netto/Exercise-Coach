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
    import streamlit as st

    st.markdown("""
<style>
.floating-nav-html {
    position: fixed;
    left: 50%;
    bottom: 24px;
    transform: translateX(-50%);
    width: 330px;
    height: 64px;
    background: rgba(18, 16, 15, 0.88);
    border: 1px solid rgba(159,185,212,0.5);
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: space-around;
    z-index: 999999;
    box-shadow: 0 12px 35px rgba(0,0,0,0.45);
    backdrop-filter: blur(16px);
}

.floating-nav-html a {
    text-decoration: none;
    font-size: 25px;
    width: 52px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
}

.floating-nav-html a:hover {
    background: rgba(159,185,212,0.28);
}
</style>

<div class="floating-nav-html">
    <a href="/Home" target="_self" title="Home">🏠</a>
    <a href="/Exercises" target="_self" title="Exercises">🏋️</a>
    <a href="/Stats" target="_self" title="Stats">📊</a>
    <a href="/Update_Profile" target="_self" title="Profile">👤</a>
</div>
""", unsafe_allow_html=True)