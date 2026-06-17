import streamlit as st
from pathlib import Path
import base64
from ui import apply_style

st.set_page_config(page_title="Movement Capability", layout="wide")
apply_style()


def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


BASE_DIR = Path(__file__).parent.parent
ICON_DIR = BASE_DIR / "assets" / "icons"

theme = st.session_state.get("theme", "Dark")
icon_filter = "invert(1)" if theme == "Dark" else "invert(0)"

st.markdown(f"""
<style>
.header-card {{
    background-color: #1f2421;
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 40px;
}}

.header-title {{
    font-size: 48px;
    font-weight: 900;
}}

.header-sub {{
    font-size: 18px;
    opacity: 0.7;
}}

.goal-card {{
    background-color: #1f2421;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    cursor: pointer;
    transition: 0.2s;
    min-height: 210px;
}}

.goal-card:hover {{
    transform: scale(1.03);
}}

.goal-card.selected {{
    border: 3px solid #9fb9d4;
}}

.goal-img {{
    width: 95px;
    height: 95px;
    object-fit: contain;
    margin-bottom: 18px;
    filter: {icon_filter};
}}

.goal-title {{
    font-size: 20px;
    font-weight: 800;
}}

.goal-desc {{
    font-size: 13px;
    opacity: 0.7;
}}

div.stButton > button {{
    margin-bottom: 25px;
}}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="header-card">
    <div class="header-title">MOVEMENT CAPABILITY</div>
    <div class="header-sub">
        Select your movement capability. You may also run a camera mobility test.
    </div>
</div>
""", unsafe_allow_html=True)


if "selected_mobility" not in st.session_state:
    st.session_state["selected_mobility"] = None


OPTIONS = [
    (
        "Upper-body limitation",
        "upper_body_limitation.png",
        "Limited shoulder, arm, or upper-body movement."
    ),
    (
        "Upper + lower limitation",
        "upper_lower_limitation.png",
        "Limitations affecting both upper and lower body movement."
    ),
    (
        "Lower-body limitation",
        "lower_body_limitation.png",
        "Limited hip, knee, ankle, or leg movement."
    ),
    (
        "Balance / stability limitation",
        "balance_stability_limitation.png",
        "Difficulty with balance, standing, or stability."
    ),
]


cols = st.columns(2)

for i, (label, img, desc) in enumerate(OPTIONS):
    with cols[i % 2]:
        img_base64 = get_base64(ICON_DIR / img)
        selected = "selected" if st.session_state["selected_mobility"] == label else ""

        st.markdown(f"""
        <div class="goal-card {selected}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{label}</div>
            <div class="goal-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=f"mobility_{label}", use_container_width=True):
            st.session_state["selected_mobility"] = label
            st.rerun()


st.divider()

camera_img = get_base64(ICON_DIR / "camera_mobility_test.png")

st.markdown(f"""
<div class="goal-card">
    <img class="goal-img" src="data:image/png;base64,{camera_img}">
    <div class="goal-title">Camera Mobility Test</div>
    <div class="goal-desc">
        Run a camera-based mobility assessment to measure your current movement range.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Start Camera Mobility Test", use_container_width=True):
    st.switch_page("pages/14_Mobility_Test.py")


if st.button("Next: Equipment", use_container_width=True):
    if not st.session_state["selected_mobility"]:
        st.warning("Please select your movement capability before continuing.")
    else:
        st.session_state["limitation_category"] = st.session_state["selected_mobility"]
        st.switch_page("pages/05_Available_Equipment.py")