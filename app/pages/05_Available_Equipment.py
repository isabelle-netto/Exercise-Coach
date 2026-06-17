import streamlit as st
from pathlib import Path
import base64
from ui import apply_style

st.set_page_config(page_title="Equipment", layout="wide")
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
    <div class="header-title">AVAILABLE EQUIPMENT</div>
    <div class="header-sub">
        Select all equipment you currently have access to.
    </div>
</div>
""", unsafe_allow_html=True)


if "selected_equipment" not in st.session_state:
    st.session_state["selected_equipment"] = []


def toggle_equipment(item):
    if item == "No equipment":
        st.session_state["selected_equipment"] = ["No equipment"]
        return

    if "No equipment" in st.session_state["selected_equipment"]:
        st.session_state["selected_equipment"].remove("No equipment")

    if item in st.session_state["selected_equipment"]:
        st.session_state["selected_equipment"].remove(item)
    else:
        st.session_state["selected_equipment"].append(item)


OPTIONS = [
    (
        "No equipment",
        "no_equipment.png",
        "Bodyweight-based exercises only."
    ),
    (
        "Dumbbell / kettlebell",
        "dumbbell_kettlebell.png",
        "Free-weight exercises using dumbbells or kettlebells."
    ),
    (
        "Gym equipment",
        "gym_equipment.png",
        "Machines or larger gym-based equipment."
    ),
    (
        "Resistance band",
        "resistance_band.png",
        "Band-based resistance training."
    ),
    (
        "Medicine ball",
        "medicine_ball.png",
        "Weighted ball exercises for strength and control."
    ),
]


cols = st.columns(2)

for i, (label, img, desc) in enumerate(OPTIONS):
    with cols[i % 2]:
        img_base64 = get_base64(ICON_DIR / img)
        selected = "selected" if label in st.session_state["selected_equipment"] else ""

        st.markdown(f"""
        <div class="goal-card {selected}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{label}</div>
            <div class="goal-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=f"equipment_{label}", use_container_width=True):
            toggle_equipment(label)
            st.rerun()


if "Gym equipment" in st.session_state["selected_equipment"]:
    st.divider()
    st.subheader("Select Gym Equipment")

    gym_options = [
        "Pull-Up Bar",
        "Smith Machine",
        "Bench Press",
        "Shoulder Press Machine",
        "Lat Pull Down Machine",
        "Row Machine",
        "Leg Press Machine",
        "Leg Extension Machine",
        "Leg Curl Machine",
        "Leg Abduction Machine"
    ]

    selected_gym = st.multiselect(
        "Choose available machines:",
        gym_options,
        key="selected_gym_equipment"
    )

    for item in selected_gym:
        if item not in st.session_state["selected_equipment"]:
            st.session_state["selected_equipment"].append(item)


if st.button("Next: Fitness Goals", use_container_width=True):
    if not st.session_state["selected_equipment"]:
        st.warning("Please select at least one equipment option before continuing.")
    else:
        st.switch_page("pages/06_Fitness_Goals.py")