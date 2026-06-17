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

    .bottom-nav {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 14px 36px;
        border-radius: 40px;
        z-index: 999999;
        display: flex;
        gap: 36px;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.45);
    }

    .bottom-nav a {
        text-decoration: none;
        font-weight: 800;
        font-size: 15px;
    }

    .bottom-nav a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    apply_accessibility_styles()


def bottom_nav():
    st.markdown("""
    <nav class="bottom-nav" aria-label="Main navigation">
        <a href="/Home" target="_self" aria-label="Go to Home page">Home</a>
        <a href="/Exercises" target="_self" aria-label="Go to Exercises page">Exercises</a>
        <a href="/Stats" target="_self" aria-label="Go to Stats page">Stats</a>
        <a href="/Profile" target="_self" aria-label="Go to Profile page">Profile</a>
    </nav>
    """, unsafe_allow_html=True)