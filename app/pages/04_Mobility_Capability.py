import streamlit as st
from pathlib import Path
import base64
from ui import apply_style

st.set_page_config(page_title="Movement Capability", layout="wide")
apply_style()


# ---------- IMAGE LOADER ----------
def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


BASE_DIR = Path(__file__).parent.parent


# ---------- CSS (MATCH FITNESS GOALS) ----------
st.markdown("""
<style>

/* HEADER */
.header-card {
    background-color: #1f2421;
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 40px;
}

.header-title {
    font-size: 48px;
    font-weight: 900;
}

.header-sub {
    font-size: 18px;
    opacity: 0.7;
}

/* GRID */
.goal-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
}

/* CARD */
.goal-card {
    background-color: #1f2421;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: 0.2s;
}

.goal-card:hover {
    transform: scale(1.03);
}

.goal-card.selected {
    border: 3px solid #9fb9d4;
}

/* IMAGE */
.goal-img {
    width: 120px;
    margin-bottom: 10px;
}

/* TEXT */
.goal-title {
    font-size: 20px;
    font-weight: 800;
}

.goal-desc {
    font-size: 13px;
    opacity: 0.7;
}

</style>
""", unsafe_allow_html=True)


# ---------- HEADER ----------
st.markdown("""
<div class="header-card">
    <div class="header-title">MOVEMENT CAPABILITY</div>
    <div class="header-sub">
        Select your movement ability. You may also run a camera test.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- STATE ----------
if "selected_mobility" not in st.session_state:
    st.session_state["selected_mobility"] = None

def select_option(option):
    st.session_state["selected_mobility"] = option


# ---------- OPTIONS ----------
OPTIONS = [
    ("Upper-body limitation", "mobility_upper.png"),
    ("Lower-body limitation", "mobility_lower.png"),
    ("Upper + lower limitation", "mobility_full.png"),
    ("Balance / stability limitation", "mobility_balance.png"),
]


# ---------- CARDS ----------
cols = st.columns(2)

for i, (label, img) in enumerate(OPTIONS):
    with cols[i % 2]:
        img_base64 = get_base64(BASE_DIR / "static" / img)

        selected = "selected" if st.session_state["selected_mobility"] == label else ""

        st.markdown(f"""
        <div class="goal-card {selected}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=label):
            select_option(label)


# ---------- CAMERA TEST ----------
st.divider()
st.subheader("Camera Mobility Test")

camera_img = get_base64(BASE_DIR / "static" / "camera_placeholder.png")

st.markdown(f"""
<div class="goal-card">
    <img class="goal-img" src="data:image/png;base64,{camera_img}">
    <div class="goal-title">Run Mobility Assessment</div>
    <div class="goal-desc">
        The system will analyse your movement range using your camera.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Start Camera Test"):
    st.info("Camera feature coming next.")


# ---------- NEXT ----------
if st.button("Next: Equipment"):
    st.session_state["limitation_category"] = st.session_state["selected_mobility"]
    st.switch_page("pages/05_Available_Equipment.py")