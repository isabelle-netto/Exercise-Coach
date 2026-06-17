import streamlit as st
from pathlib import Path
import base64
from db import save_profile, save_user_equipment
from ui import apply_style

st.set_page_config(page_title="Fitness Goals", layout="wide")
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

.complete-btn {{
    margin-top: 30px;
}}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="header-card">
    <div class="header-title">FITNESS GOALS</div>
    <div class="header-sub">
        Choose one or more goals to personalise your experience.
    </div>
</div>
""", unsafe_allow_html=True)


if "selected_goals" not in st.session_state:
    st.session_state["selected_goals"] = []


def toggle_goal(goal):
    if goal in st.session_state["selected_goals"]:
        st.session_state["selected_goals"].remove(goal)
    else:
        st.session_state["selected_goals"].append(goal)


GOALS = [
    (
        "Improve mobility",
        "Improve movement range and ease of motion.",
        "improve_mobility.png"
    ),
    (
        "Improve posture/form",
        "Support safer alignment and better exercise control.",
        "improve_posture_form.png"
    ),
    (
        "General fitness",
        "Improve overall health, consistency, and activity level.",
        "general_fitness.png"
    ),
    (
        "Build strength",
        "Develop muscle control and functional strength.",
        "build_strength.png"
    ),
    (
        "Increase endurance",
        "Improve stamina and ability to exercise for longer.",
        "increase_endurance.png"
    ),
]


cols = st.columns(2)

for i, (title, desc, img) in enumerate(GOALS):
    with cols[i % 2]:
        img_base64 = get_base64(ICON_DIR / img)
        selected = "selected" if title in st.session_state["selected_goals"] else ""

        st.markdown(f"""
        <div class="goal-card {selected}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{title}</div>
            <div class="goal-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=f"goal_{title}", use_container_width=True):
            toggle_goal(title)
            st.rerun()


st.markdown('<div class="complete-btn">', unsafe_allow_html=True)

if st.button("Complete Profile", use_container_width=True):
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Please sign in first.")

    elif not st.session_state.get("limitation_category"):
        st.warning("Please complete the movement capability step first.")

    elif not st.session_state.get("selected_equipment"):
        st.warning("Please complete the equipment step first.")

    elif not st.session_state.get("selected_goals"):
        st.warning("Please select at least one fitness goal.")

    else:
        equipment_list = list(dict.fromkeys(st.session_state.get("selected_equipment", [])))

        save_profile(
            user_id=user_id,
            limitation_category=st.session_state.get("limitation_category"),
            fitness_goals=", ".join(st.session_state["selected_goals"])
        )

        save_user_equipment(
            user_id=user_id,
            equipment_list=equipment_list
        )

        st.success("Profile completed.")
        st.switch_page("pages/07_Home.py")

st.markdown("</div>", unsafe_allow_html=True)