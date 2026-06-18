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
    except:
        return ""


BASE_DIR = Path(__file__).parent.parent
bg = get_base64(BASE_DIR / "static" / "profiletransition.png")

st.markdown(
    f"""
    <style>

    .stApp {{
        background-image: url("data:image/png;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .main {{
        background: rgba(0,0,0,0);
    }}

    .profile-card {{
        background: rgba(0,0,0,0.55);
        padding: 40px;
        border-radius: 20px;
        margin-top: 80px;
    }}

    .profile-title {{
        color: white;
        font-size: 60px;
        font-weight: 900;
        line-height: 1.0;
        margin-bottom: 20px;
    }}

    .profile-text {{
        color: white;
        font-size: 18px;
        line-height: 1.6;
        margin-bottom: 25px;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1])

with right:

    st.markdown(
        """
        <div class="profile-card">

        <div class="profile-title">
        LET'S BUILD<br>
        YOUR PROFILE
        </div>

        <div class="profile-text">
        Before we recommend exercises, let's learn a little about you.

        We'll personalise your exercise programme based on:

        • Movement capability<br>
        • Available equipment<br>
        • Fitness goals
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(25)

    st.write("Profile Setup Progress: 25%")

    if st.button("START PROFILE SETUP", use_container_width=True):

        if not st.session_state.get("user_id"):
            st.error("Please sign in first.")
            st.switch_page("pages/02_Sign_In.py")

        else:
            st.switch_page("pages/04_Mobility_Capability.py")