import streamlit as st
from db import get_all_exercises, get_exercise_details
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Exercises", layout="wide")
apply_style()

st.markdown("""
<style>
.exercise-page {
    padding: 34px;
}

.exercise-hero {
    background: linear-gradient(135deg, #1f2421, #2d3530);
    border-radius: 24px;
    padding: 32px;
    margin-bottom: 24px;
}

.exercise-hero h1 {
    margin: 0;
    font-size: 46px;
    font-weight: 900;
}

.exercise-hero p {
    margin-top: 10px;
    opacity: 0.8;
    font-size: 17px;
}

.exercise-card {
    background: rgba(31,36,33,0.92);
    border-radius: 22px;
    padding: 26px;
    margin-bottom: 16px;
    min-height: 210px;
    border-left: 6px solid #9fb9d4;
}

.exercise-card h3 {
    font-size: 24px;
    margin-bottom: 14px;
}

.exercise-pill {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(159,185,212,0.18);
    border: 1px solid #9fb9d4;
    margin-right: 8px;
    font-weight: 800;
    font-size: 14px;
}

.search-box {
    margin-bottom: 22px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="exercise-page">
<div class="exercise-hero">
    <h1>Exercises</h1>
    <p>Browse exercises, view instructions, and start a guided live session.</p>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='exercise-page search-box'>", unsafe_allow_html=True)
search = st.text_input("Search exercises", placeholder="Search by exercise name...")
st.markdown("</div>", unsafe_allow_html=True)

exercises = get_all_exercises()

if search:
    exercises = [ex for ex in exercises if search.lower() in ex[1].lower()]


@st.dialog("Exercise Profile")
def show_exercise_profile(exercise_id):
    details = get_exercise_details(exercise_id)

    if details:
        name, target_area, instructions, difficulty, seated = details

        st.subheader(name)
        st.write(f"**Target Area:** {target_area}")
        st.write(f"**Difficulty:** {difficulty}")
        st.write(f"**Seated Friendly:** {'Yes' if seated == 1 else 'No'}")

        st.markdown("### Instructions")
        st.write(instructions)

        if st.button("Start Session", use_container_width=True):
            st.session_state["active_exercise_id"] = exercise_id
            st.session_state["active_exercise_name"] = name
            st.switch_page("pages/12_Live_Session.py")


st.markdown("<div class='exercise-page'>", unsafe_allow_html=True)

if not exercises:
    st.info("No exercises found.")

else:
    cols = st.columns(2)

    for i, exercise in enumerate(exercises):
        exercise_id, name, target_area, difficulty, seated = exercise

        with cols[i % 2]:
            st.markdown(f"""
<div class="exercise-card">
    <h3>{name}</h3>
    <span class="exercise-pill">{target_area}</span>
    <span class="exercise-pill">{difficulty}</span>
    <span class="exercise-pill">{"Seated Friendly" if seated == 1 else "Standing"}</span>
    <br><br>
    <p>Select this exercise to view instructions and begin a live coached session.</p>
</div>
""", unsafe_allow_html=True)

            if st.button("View Details", key=f"exercise_{exercise_id}", use_container_width=True):
                show_exercise_profile(exercise_id)

st.markdown("</div>", unsafe_allow_html=True)

bottom_nav()