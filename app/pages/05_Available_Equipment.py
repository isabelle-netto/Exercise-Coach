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
    except:
        return ""


BASE_DIR = Path(__file__).parent.parent


# ---------- CSS ----------
st.markdown("""
<style>

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

.goal-img {
    width: 120px;
    margin-bottom: 10px;
}

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
    <div class="header-title">AVAILABLE EQUIPMENT</div>
    <div class="header-sub">
        Select the equipment you have access to.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- STATE ----------
if "selected_equipment" not in st.session_state:
    st.session_state["selected_equipment"] = []

def toggle(item):
    if item in st.session_state["selected_equipment"]:
        st.session_state["selected_equipment"].remove(item)
    else:
        st.session_state["selected_equipment"].append(item)


# ---------- OPTIONS ----------
OPTIONS = [
    ("No equipment", "equipment_none.png"),
    ("Resistance band", "equipment_band.png"),
    ("Dumbbell / kettlebell", "equipment_dumbbell.png"),
    ("Medicine ball", "equipment_medicine.png"),
    ("Gym equipment", "equipment_gym.png"),
]


cols = st.columns(2)

for i, (label, img) in enumerate(OPTIONS):
    with cols[i % 2]:
        img_base64 = get_base64(BASE_DIR / "static" / img)

        selected = "selected" if label in st.session_state["selected_equipment"] else ""

        st.markdown(f"""
        <div class="goal-card {selected}">
            <img class="goal-img" src="data:image/png;base64,{img_base64}">
            <div class="goal-title">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Select", key=label):
            toggle(label)


# ---------- GYM OPTIONS ----------
if "Gym equipment" in st.session_state["selected_equipment"]:
    st.divider()
    st.subheader("Select Gym Equipment")

    gym = st.multiselect(
        "Choose available machines:",
        [
            "Pull-Up Bar", "Smith Machine", "Bench Press",
            "Shoulder Press Machine", "Lat Pull Down Machine",
            "Row Machine", "Leg Press Machine",
            "Leg Extension Machine", "Leg Curl Machine",
            "Leg Abduction Machine"
        ]
    )

    st.session_state["selected_equipment"].extend(gym)


# ---------- NEXT ----------
if st.button("Next: Fitness Goals"):
    st.switch_page("pages/06_Fitness_Goals.py")