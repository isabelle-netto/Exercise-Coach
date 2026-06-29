import streamlit as st
from db import (
    get_recommended_exercises,
    get_exercise_details,
    save_diary_entry,
    get_diary_entries,
    get_user_goals
)
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Home", layout="wide")
apply_style()

st.title("Home")
st.write("Welcome to your Exercise Coach dashboard.")

st.divider()
st.subheader("Today’s Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric("Sessions", "3")

with col2:
    st.metric("Duration", "190 mins")

st.divider()
st.subheader("Recommended for You")

user_id = st.session_state.get("user_id")
recommended = get_recommended_exercises(user_id)


@st.dialog("Exercise Profile")
def show_exercise_profile(exercise_id):
    details = get_exercise_details(exercise_id)

    if details:
        name, target_area, instructions, difficulty, seated = details

        st.subheader(name)
        st.write(f"**Target Area:** {target_area}")
        st.write(f"**Difficulty:** {difficulty}")
        st.write(f"**Seated Friendly:** {'Yes' if seated else 'No'}")

        st.markdown("### Instructions")
        st.write(instructions)

        if st.button("Start Session"):
            st.session_state["active_exercise_id"] = exercise_id
            st.session_state["active_exercise_name"] = name
            st.switch_page("pages/12_Live_Session.py")


if not user_id:
    st.warning("Please sign in to view personalised recommendations.")

elif not recommended:
    st.info("No recommendations yet. Please complete your profile setup.")

else:
    cols = st.columns(2)

    for i, item in enumerate(recommended):
        score, ex_id, name, target_area, difficulty, seated = item

        with cols[i % 2]:
            st.markdown(f"""
            <div class="card">
                <h3>{name}</h3>
                <p>{target_area} | {difficulty}</p>
                <p><b>Recommendation Score:</b> {score}</p>
                <p><b>Seated Friendly:</b> {'Yes' if seated else 'No'}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Details", key=f"rec_{ex_id}"):
                show_exercise_profile(ex_id)

st.divider()
st.subheader("Progress Diary")

if not user_id:
    st.warning("Please sign in to use the diary.")

else:
    goals = get_user_goals(user_id)

    st.write("Your diary questions are personalised based on your selected goals.")

    QUESTION_BANK = {
        "Improve mobility": {
            "Do your joints feel easier to move today?": [
                "Much worse",
                "Slightly worse",
                "About the same",
                "Slightly better",
                "Much better"
            ],
            "Did you notice improvement in your range of motion?": [
                "No improvement",
                "Slight improvement",
                "Moderate improvement",
                "Significant improvement"
            ],
            "Were you able to move with less stiffness?": [
                "Much more stiff",
                "Slightly more stiff",
                "No change",
                "Less stiff",
                "Much less stiff"
            ],
        },
        "Build strength": {
            "Did exercises feel easier than before?": [
                "Much harder",
                "Slightly harder",
                "About the same",
                "Slightly easier",
                "Much easier"
            ],
            "Did you feel stronger during movements?": [
                "Not at all",
                "A little",
                "Moderately",
                "Very much"
            ],
            "Were you able to complete more repetitions?": [
                "Fewer reps",
                "Same reps",
                "A few more reps",
                "Many more reps"
            ],
        },
        "Improve posture/form": {
            "Did you feel more aware of your posture?": [
                "Not at all",
                "Slightly",
                "Mostly",
                "Completely"
            ],
            "Were you able to maintain proper form?": [
                "Rarely",
                "Sometimes",
                "Most of the time",
                "Throughout the exercise"
            ],
        },
        "Increase endurance": {
            "Did you feel less tired during exercise?": [
                "More tired",
                "About the same",
                "Slightly less tired",
                "Much less tired"
            ],
            "Were you able to exercise longer?": [
                "Shorter than usual",
                "Same duration",
                "Slightly longer",
                "Much longer"
            ],
        },
        "General fitness": {
            "How was your overall energy after exercising?": [
                "Very low",
                "Low",
                "Moderate",
                "High",
                "Excellent"
            ],
            "Do you feel more confident being active?": [
                "Not yet",
                "A little more confident",
                "Moderately confident",
                "Very confident"
            ],
        }
    }

    selected_questions = {}

    for goal in goals:
        if goal in QUESTION_BANK:
            selected_questions.update(QUESTION_BANK[goal])

    if not selected_questions:
        st.info("No goals found. Please update your profile.")

    else:
        with st.expander("Add Diary Entry"):
            answers = []

            for question, options in selected_questions.items():
                ans = st.radio(
                    question,
                    options,
                    horizontal=True,
                    key=f"diary_{question}"
                )
                answers.append(f"{question} → {ans}")

            note = st.text_area("Personal reflection")

            if st.button("Save Diary Entry"):
                entry_text = "\n".join(answers)

                if note:
                    entry_text += f"\n\nNote: {note}"

                save_diary_entry(user_id, entry_text)
                st.success("Diary entry saved.")

        with st.expander("View Previous Entries"):
            entries = get_diary_entries(user_id)

            if not entries:
                st.info("No entries yet.")
            else:
                for date, note in entries:
                    formatted_note = note.replace("\n", "<br>")

                    st.markdown(f"""
                    <div class="card">
                        <b>{date}</b><br><br>
                        {formatted_note}
                    </div>
                    """, unsafe_allow_html=True)

bottom_nav()