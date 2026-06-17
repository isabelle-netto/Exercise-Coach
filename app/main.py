import streamlit as st
from pathlib import Path
import base64

from ui import apply_style
from accessibility import accessibility_settings_panel

st.set_page_config(page_title="Exercise Coach", layout="wide")
apply_style()


def get_base64(paths):
    for path in paths:
        try:
            if path.exists():
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
        except Exception:
            pass
    return ""


BASE_DIR = Path(__file__).parent

bg_data = get_base64([
    BASE_DIR / "static" / "welcome_bg.jpg",
    BASE_DIR / "assets" / "welcome_bg.jpg",
])

logo_data = get_base64([
    BASE_DIR / "static" / "logo_transparentbackground.png",
    BASE_DIR / "assets" / "logo_transparentbackground.png",
])

theme = st.session_state.get("theme", "Dark")

if theme == "Light":
    app_bg = "#f7f4ef"
    bg_image = "none"
    text_color = "#111111"
    button_bg = "#111111"
    button_text = "#ffffff"
    logo_filter = "invert(0)"
else:
    app_bg = "#12100f"
    bg_image = f'linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), url("data:image/jpeg;base64,{bg_data}")'
    text_color = "#ffffff"
    button_bg = "#9fb9d4"
    button_text = "#ffffff"
    logo_filter = "invert(1)"

st.markdown(f"""
<style>
.stApp {{
    background-color: {app_bg} !important;
    background-image: {bg_image} !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}}

.block-container {{
    padding: 24px 48px 24px 48px !important;
    max-width: 100% !important;
    overflow: hidden !important;
}}

.logo-img {{
    width: 88px;
    filter: {logo_filter};
}}

.hero-wrapper {{
    height: calc(100vh - 170px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-top: -20px;
    text-align: center;
}}

.hero-title {{
    color: {text_color} !important;
    font-size: 68px !important;
    font-weight: 900 !important;
    line-height: 0.92 !important;
    text-transform: uppercase !important;
    margin-bottom: 24px !important;
}}

.hero-subtitle {{
    color: {text_color} !important;
    font-size: 21px !important;
    font-weight: 500 !important;
    max-width: 760px;
    margin: 0 auto 34px auto !important;
    line-height: 1.4 !important;
}}

.main-buttons {{
    margin-top: -120px !important;
}}

.main-buttons div.stButton {{
    margin-bottom: 0px !important;
}}

.main-buttons div.stButton > button {{
    width: 360px !important;
    height: 60px !important;
    background-color: {button_bg} !important;
    color: {button_text} !important;
    border: none !important;
    font-weight: 900 !important;
}}

.main-buttons div.stButton > button * {{
    color: {button_text} !important;
}}

.main-buttons div.stButton > button:hover {{
    opacity: 0.92;
}}

@media (max-width: 900px) {{
    .block-container {{
        padding: 18px 24px !important;
    }}

    .hero-wrapper {{
        height: auto;
        margin-top: 40px;
    }}

    .hero-title {{
        font-size: 46px !important;
    }}

    .hero-subtitle {{
        font-size: 18px !important;
    }}

    .main-buttons {{
        margin-top: 20px !important;
    }}

    .main-buttons div.stButton > button {{
        width: 100% !important;
    }}

    .logo-img {{
        width: 68px;
    }}
}}
</style>
""", unsafe_allow_html=True)

top_left, top_mid, top_right = st.columns([5, 2, 1])

with top_mid:
    accessibility_settings_panel()

with top_right:
    if logo_data:
        st.markdown(
            f'<img class="logo-img" src="data:image/png;base64,{logo_data}" alt="Exercise Coach logo">',
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="hero-wrapper">'
    '<div class="hero-title">START<br>YOUR FITNESS<br>JOURNEY<br>TODAY</div>'
    '<p class="hero-subtitle">An accessible AI-based exercise guidance system designed to support safer and more personalised movement.</p>'
    '</div>',
    unsafe_allow_html=True
)

btn_left, btn_mid, btn_right = st.columns([2, 1, 2])

with btn_mid:
    st.markdown('<div class="main-buttons">', unsafe_allow_html=True)

    if st.button("SIGN IN", key="main_sign_in", use_container_width=True):
        st.switch_page("pages/02_Sign_In.py")

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    if st.button("SIGN UP HERE", key="main_sign_up", use_container_width=True):
        st.switch_page("pages/01_Sign_Up.py")

    st.markdown('</div>', unsafe_allow_html=True)