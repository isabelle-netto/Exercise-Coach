import streamlit as st
from pathlib import Path
import base64
from ui import apply_style

apply_style()

st.set_page_config(page_title="Set Up Profile", layout="wide")

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BASE_DIR = Path(__file__).parent.parent
bg = get_base64(BASE_DIR / "static" / "profiletransition.png")

st.markdown(f"""
<style>
#MainMenu, header, footer {{visibility: hidden;}}

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
    color: white;
    font-size: 56px;
    font-weight: 900;
    line-height: 0.95;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.mockup-button {{
    position: fixed;
    right: 12%;
    bottom: 17%;
    background-color: #9fb9d4;
    color: black !important;
    padding: 18px 46px;
    border-radius: 4px;
    text-decoration: none !important;
    font-weight: 900;
    font-size: 18px;
}}
</style>

<div class="title-text">
    TIME TO<br>
    SET UP YOUR<br>
    PROFILE!
</div>

<a class="mockup-button" href="/Mobility_Capability" target="_self">LET’S GO!</a>
""", unsafe_allow_html=True)