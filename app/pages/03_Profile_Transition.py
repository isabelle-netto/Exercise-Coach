import streamlit as st
from pathlib import Path
import base64
from ui import apply_style

st.set_page_config(page_title="Set Up Profile", layout="wide")
apply_style()


def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


BASE_DIR = Path(__file__).parent.parent
bg = get_base64(BASE_DIR / "static" / "profiletransition.png")

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/png;base64,{bg}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

.title-text {{
    position: fixed;
    top: 11%;
    right: 10%;
    width: 360px;
    color: white !important;
    font-size: 56px;
    font-weight: 900;
    line-height: 0.95;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.button-box {{
    position: fixed;
    right: 12%;
    bottom: 17%;
    width: 260px;
}}

.button-box div.stButton > button {{
    background-color: #9fb9d4 !important;
    color: black !important;
    border: none !important;
    height: 58px !important;
    font-weight: 900 !important;
    font-size: 18px !important;
}}

.button-box div.stButton > button * {{
    color: black !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-text">
    TIME TO<br>
    SET UP YOUR<br>
    PROFILE!
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="button-box">', unsafe_allow_html=True)

if st.button("LET'S GO!", use_container_width=True):
    if not st.session_state.get("user_id"):
        st.error("Please sign in first.")
        st.switch_page("pages/02_Sign_In.py")
    else:
        st.switch_page("pages/04_Mobility_Capability.py")

st.markdown('</div>', unsafe_allow_html=True)