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
    margin-bottom: 35px;
}}

.header-title {{
    font-size: 48px;
    font-weight: 900;
}}

.header-sub {{
    font-size: 18px;
    opacity: 0.75;
}}

.option-card {{
    background-color: #1f2421;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    min-height: 225px;
    margin-bottom: 12px;
}}

.option-card.selected {{
    border: 3px solid #9fb9d4;
}}

.option-img {{
    width: 95px;
    height: 95px;
    object-fit: contain;
    margin-bottom: 18px;
    filter: {icon_filter};
}}

.option-title {{
    font-size: 20px;
    font-weight: 900;
}}

.option-desc {{
    font-size: 13px;
    opacity: 0.75;
}}

div.stButton > button {{
    margin-bottom: 25px;
    font-weight: 900 !important;
}}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="header-card">
    <div class="header-title">MOVEMENT CAPABILITY</div>
    <div class="header-sub">
        Select your movement capability. If you are unsure, choose Camera Mobility Test so the system can use your actual range of motion instead of a broad limitation category.
    </div>
</div>
""", unsafe_allow_html=True)


if "selected_mobility" not in st.session_state:
    st.session_state["selected_mobility"] = None


OPTIONS = [
    (
        "Upper-body limitation",
        "upper_body_limitation.png",
        "Choose this only if upper-body movement is generally limited."
    ),
    (
        "Upper + lower limitation",
        "upper_lower_limitation.png",
        "Choose this if both upper and lower body movement are broadly limited."
    ),
    (
        "Lower-body limitation",
        "lower_body_limitation.png",
        "Choose this only if lower-body movement is generally limited."
    ),
    (
        "Balance / stability limitation",
        "balance_stability_limitation.png",
        "Choose this if balance, standing, or stability is the main concern."
    ),
    (
        "Camera Mobility Test",
        "camera_mobility_test.png",
        "Best option for personalised guidance. The system measures your actual ROM instead of assuming a broad limitation."
    ),
]


cols = st.columns(2)

for i, (label, img, desc) in enumerate(OPTIONS):
    with cols[i % 2]:
        img_base64 = get_base64(ICON_DIR / img)
        selected = "selected" if st.session_state["selected_mobility"] == label else ""

        st.markdown(f"""
        <div class="option-card {selected}">
            <img class="option-img" src="data:image/png;base64,{img_base64}">
            <div class="option-title">{label}</div>
            <div class="option-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=f"mobility_{label}", use_container_width=True):
            st.session_state["selected_mobility"] = label
            st.session_state["limitation_category"] = label

            if label == "Camera Mobility Test":
                st.switch_page("pages/14_Mobility_Test.py")
            else:
                st.rerun()


st.divider()

if st.button("Next: Equipment", use_container_width=True):
    if not st.session_state["selected_mobility"]:
        st.warning("Please select your movement capability before continuing.")
    else:
        st.session_state["limitation_category"] = st.session_state["selected_mobility"]
        st.switch_page("pages/05_Available_Equipment.py")