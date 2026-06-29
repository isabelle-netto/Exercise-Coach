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

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(90deg, rgba(0,0,0,0.15), rgba(0,0,0,0.75)),
            url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    .profile-wrapper {{
        height: 100vh;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-right: 7%;
        box-sizing: border-box;
    }}

    .profile-panel {{
        width: 560px;
        background: rgba(0,0,0,0.72);
        border-radius: 28px;
        padding: 50px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.35);
    }}

    .profile-kicker {{
        color: #9fb9d4;
        font-size: 15px;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 16px;
        text-transform: uppercase;
    }}

    .profile-title {{
        color: white;
        font-size: 62px;
        font-weight: 900;
        line-height: 0.95;
        margin-bottom: 24px;
        text-transform: uppercase;
    }}

    .profile-text {{
        color: white;
        font-size: 18px;
        line-height: 1.6;
        opacity: 0.92;
        margin-bottom: 28px;
    }}

    .step-list {{
        color: white;
        font-size: 16px;
        line-height: 1.9;
        margin-bottom: 32px;
    }}

    .progress-label {{
        color: white;
        font-weight: 800;
        margin-bottom: 8px;
    }}

    div.stProgress > div > div > div {{
        background-color: #9fb9d4 !important;
    }}

    .button-area {{
        margin-top: -170px;
        width: 460px;
        margin-left: auto;
        margin-right: 7%;
    }}

    div.stButton > button {{
        background-color: #9fb9d4 !important;
        color: black !important;
        border: none !important;
        height: 64px !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        letter-spacing: 1px;
    }}

    div.stButton > button * {{
        color: black !important;
    }}

    div.stButton > button:hover {{
        transform: scale(1.01);
        opacity: 0.95;
    }}

    @media (max-width: 900px) {{
        .profile-wrapper {{
            justify-content: center;
            padding: 24px;
        }}

        .profile-panel {{
            width: 100%;
            padding: 34px;
        }}

        .profile-title {{
            font-size: 46px;
        }}

        .button-area {{
            width: calc(100% - 48px);
            margin: -150px auto 0 auto;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="profile-wrapper">
        <div class="profile-panel">
            <div class="profile-kicker">Step 1 of 4</div>

            <div class="profile-title">
                Let’s Build<br>
                Your Profile
            </div>

            <div class="profile-text">
                Before we recommend exercises, let’s learn a little about you.
                Your profile helps Exercise Coach personalise safer movement,
                suitable equipment, and realistic fitness goals.
            </div>

            <div class="step-list">
                ✓ Movement capability<br>
                ✓ Available equipment<br>
                ✓ Fitness goals<br>
                ✓ Personalised exercise guidance
            </div>

            <div class="progress-label">Profile Setup Progress: 25%</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="button-area">', unsafe_allow_html=True)
st.progress(25)

if st.button("START PROFILE SETUP", use_container_width=True):
    if not st.session_state.get("user_id"):
        st.error("Please sign in first.")
        st.switch_page("pages/02_Sign_In.py")
    else:
        st.switch_page("pages/04_Mobility_Capability.py")

st.markdown("</div>", unsafe_allow_html=True)