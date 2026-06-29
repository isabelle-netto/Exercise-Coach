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
    background-image:
        linear-gradient(90deg, rgba(0,0,0,0.05), rgba(0,0,0,0.65)),
        url("data:image/png;base64,{bg}");
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
    top: 18%;
    right: 8%;
    width: 520px;
    color: white !important;
    font-size: 68px;
    font-weight: 900;
    line-height: 0.95;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-align: left;
}}

.subtitle-text {{
    position: fixed;
    top: 49%;
    right: 8%;
    width: 520px;
    color: white !important;
    font-size: 20px;
    line-height: 1.55;
    font-weight: 500;
    text-align: left;
}}

.profile-points {{
    position: fixed;
    top: 62%;
    right: 8%;
    width: 520px;
    color: white !important;
    font-size: 18px;
    line-height: 1.8;
    font-weight: 700;
    text-align: left;
}}

.button-box {{
    position: fixed;
    right: 8%;
    bottom: 15%;
    width: 360px;
}}

.button-box div.stButton > button {{
    background-color: #9fb9d4 !important;
    color: black !important;
    border: none !important;
    height: 62px !important;
    font-weight: 900 !important;
    font-size: 18px !important;
    border-radius: 14px !important;
    letter-spacing: 1px;
}}

.button-box div.stButton > button * {{
    color: black !important;
}}

.button-box div.stButton > button:hover {{
    opacity: 0.95;
    transform: scale(1.02);
}}

@media (max-width: 900px) {{
    .title-text {{
        top: 12%;
        left: 8%;
        right: auto;
        width: 84%;
        font-size: 46px;
    }}

    .subtitle-text {{
        top: 39%;
        left: 8%;
        right: auto;
        width: 84%;
        font-size: 17px;
    }}

    .profile-points {{
        top: 56%;
        left: 8%;
        right: auto;
        width: 84%;
        font-size: 16px;
    }}

    .button-box {{
        left: 8%;
        right: auto;
        bottom: 12%;
        width: 84%;
    }}
}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-text">
LET'S BUILD<br>
YOUR PROFILE
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="subtitle-text">
Before we recommend exercises, let's learn a little about you.
Your profile helps Exercise Coach personalise safer movement,
suitable equipment, and realistic fitness goals.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="profile-points">
✓ Movement capability<br>
✓ Available equipment<br>
✓ Fitness goals<br>
✓ Personalised exercise guidance
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="button-box">', unsafe_allow_html=True)

if st.button("START PROFILE SETUP", use_container_width=True):
    if not st.session_state.get("user_id"):
        st.error("Please sign in first.")
        st.switch_page("pages/02_Sign_In.py")
    else:
        st.switch_page("pages/04_Mobility_Capability.py")

st.markdown('</div>', unsafe_allow_html=True)