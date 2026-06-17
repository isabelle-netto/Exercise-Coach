import streamlit as st
from pathlib import Path
import base64
from db import save_profile, save_user_equipment
from ui import apply_style

st.set_page_config(page_title="Fitness Goals", layout="wide")
apply_style()


# ---------- IMAGE LOADER ----------
def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


BASE_DIR = Path(__file__).parent.parent

# ---------- CSS ----------
st.markdown("""
<style>

/* HEADER CARD */
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

/* GOAL GRID */
.goal-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30px;
}

/* GOAL CARD */
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

/* TITLE */
.goal-title {
    font-size: 20px;
    font-weight: 800;
}

/* DESC */
.goal-desc {
    font-size: 13px;
    opacity: 0.7;
}

/* BUTTON */
.complete-btn {
    margin-top: 40px;
    width: 250px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="header-card">
    <div class="header-title">FITNESS GOALS</div>
    <div class="header-sub">
        Choose your goals to personalise your experience
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "selected_goals" not in st.session_state:
    st.session_state["selected_goals"] = []

def toggle_goal(goal):
    if goal in st.session_state["selected_goals"]:
        st.session_state["selected_goals"].remove(goal)
    else:
        st.session_state["selected_goals"].append(goal)


# ---------- GOAL DATA ----------
GOALS = [
    ("Improve mobility", "Increase movement range", "goal_mobility.png"),
    ("Build strength", "Improve muscle control", "goal_strength.png"),
    ("Improve posture/form", "Better body alignment", "goal_posture.png"),
    ("Increase endurance", "Exercise longer", "goal_endurance.png"),
    ("General fitness", "Overall health", "goal_general.png"),
]

# ---------- DISPLAY CARDS ----------
cols = st.columns(2)

for i, (title, desc, img) in enumerate(GOALS):
    with cols[i % 2]:

        img_base64 = get_base64(BASE_DIR / "static" / img)

        selected_class = "selected" if title in st.session_state["selected_goals"] else ""

        st.markdown(f"""
        <div class="goal-card {selected_class}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{title}</div>
            <div class="goal-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=title):
            toggle_goal(title)

# ---------- COMPLETE ----------
st.markdown('<div class="complete-btn">', unsafe_allow_html=True)

if st.button("Complete Profile", use_container_width=True):

    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Please sign in first.")
    else:
        save_profile(
            user_id=user_id,
            limitation_category=st.session_state.get("limitation_category"),
            fitness_goals=", ".join(st.session_state["selected_goals"])
        )

        save_user_equipment(
            user_id=user_id,
            equipment_list=st.session_state.get("selected_equipment", [])
        )

        st.success("Profile completed.")
        st.switch_page("pages/07_Home.py")

st.markdown("</div>", unsafe_allow_html=True)