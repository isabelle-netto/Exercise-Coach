import streamlit as st
from db import get_all_exercises, get_exercise_details
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Exercises", layout="wide")
apply_style()

st.markdown("""
<style>

.exercise-page{
    padding:35px;
}

.exercise-hero{
    background:linear-gradient(135deg,#1f2421,#2d3530);
    border-radius:28px;
    padding:60px;
    margin-bottom:35px;
}

.exercise-title{
    font-size:64px;
    font-weight:900;
    line-height:1;
    margin-bottom:18px;
}

.exercise-subtitle{
    font-size:22px;
    opacity:.85;
    max-width:760px;
}

.exercise-search{
    margin-bottom:30px;
}

.exercise-card{
    background:#1f2421;
    border-radius:22px;
    padding:26px;
    margin-bottom:22px;
    border-left:6px solid #9fb9d4;
    min-height:240px;
}

.exercise-name{
    font-size:28px;
    font-weight:900;
    margin-bottom:18px;
}

.exercise-pill{
    display:inline-block;
    padding:8px 15px;
    margin-right:10px;
    margin-bottom:12px;
    border-radius:999px;
    background:rgba(159,185,212,.18);
    border:1px solid #9fb9d4;
    font-size:15px;
    font-weight:700;
}

.exercise-desc{
    margin-top:18px;
    opacity:.8;
    line-height:1.6;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="exercise-page">

<div class="exercise-hero">

<div class="exercise-title">
Exercise Library
</div>

<div class="exercise-subtitle">
Browse personalised exercises, learn the correct technique,
and begin a live AI-guided coaching session whenever you're ready.
</div>

</div>

</div>
""", unsafe_allow_html=True)

search = st.text_input(
    "Search exercises",
    placeholder="Search by exercise name..."
)

exercises = get_all_exercises()

if search:
    exercises = [
        ex for ex in exercises
        if search.lower() in ex[1].lower()
    ]


@st.dialog("Exercise Profile")
def show_exercise_profile(exercise_id):

    details = get_exercise_details(exercise_id)

    if details:

        name, target_area, instructions, difficulty, seated = details

        st.subheader(name)

        st.write(f"**Target Area:** {target_area}")
        st.write(f"**Difficulty:** {difficulty}")
        st.write(f"**Seated Friendly:** {'Yes' if seated else 'No'}")

        st.divider()

        st.markdown("### Instructions")

        st.write(instructions)

        if st.button(
            "Start Live Session",
            use_container_width=True
        ):
            st.session_state["active_exercise_id"] = exercise_id
            st.session_state["active_exercise_name"] = name
            st.switch_page("pages/12_Live_Session.py")


if not exercises:

    st.info("No exercises found.")

else:

    cols = st.columns(2)

    for i, exercise in enumerate(exercises):

        exercise_id, name, target_area, difficulty, seated = exercise

        with cols[i % 2]:

            st.markdown(f"""
            <div class="exercise-card">

            <div class="exercise-name">
            {name}
            </div>

            <span class="exercise-pill">
            {target_area}
            </span>

            <span class="exercise-pill">
            {difficulty}
            </span>

            <span class="exercise-pill">
            {'Seated Friendly' if seated else 'Standing Exercise'}
            </span>

            <div class="exercise-desc">
            View detailed instructions and launch a real-time
            AI coaching session with posture analysis.
            </div>

            </div>
            """, unsafe_allow_html=True)

            if st.button(
                "View Details",
                key=f"exercise_{exercise_id}",
                use_container_width=True
            ):
                show_exercise_profile(exercise_id)

bottom_nav()