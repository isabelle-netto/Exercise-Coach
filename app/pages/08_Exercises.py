import streamlit as st
from db import get_all_exercises, get_exercise_details
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Exercises", layout="wide")
apply_style()

st.title("Exercises")

search = st.text_input("Search exercises")

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

        st.markdown("### Exercise Profile")
        st.text(instructions)

        if st.button("Start Session"):
            st.session_state["active_exercise_id"] = exercise_id
            st.session_state["active_exercise_name"] = name
            st.switch_page("pages/12_Live_Session.py")


for exercise in exercises:
    exercise_id, name, target_area, difficulty, seated = exercise

    st.markdown(f"""
    <div class="card">
        <h3>{name}</h3>
        <p>{target_area} | {difficulty}</p>
        <p><b>Seated Friendly:</b> {'Yes' if seated == 1 else 'No'}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("View Details", key=f"exercise_{exercise_id}"):
        show_exercise_profile(exercise_id)

bottom_nav()