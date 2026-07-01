import streamlit as st
from textwrap import dedent
from db import (
    get_recommended_exercises,
    get_exercise_details,
    save_diary_entry,
    get_diary_entries,
    get_user_goals,
    get_user_session_results
)
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Home", layout="wide")
apply_style()


def html(content):
    st.markdown(dedent(content), unsafe_allow_html=True)


user_id = st.session_state.get("user_id")
user_name = st.session_state.get("user_name", "User")

sessions = get_user_session_results(user_id) if user_id else []
total_sessions = len(sessions)
total_minutes = sum([row[2] or 0 for row in sessions]) if sessions else 0

html("""
<style>
.home-wrap {
    padding: 35px;
}

.hero-card {
    background: linear-gradient(135deg, #1f2421, #2d3530);
    border-radius: 24px;
    padding: 38px;
    margin-bottom: 28px;
}

.hero-title {
    font-size: 44px;
    font-weight: 900;
    margin-bottom: 8px;
}

.hero-sub {
    font-size: 18px;
    opacity: 0.82;
}

.stat-card {
    background: rgba(31,36,33,0.92);
    border-radius: 22px;
    padding: 28px;
    text-align: center;
    min-height: 150px;
}

.stat-number {
    font-size: 46px;
    font-weight: 900;
}

.stat-label {
    font-size: 16px;
    opacity: 0.78;
}

.exercise-card {
    background: rgba(31,36,33,0.92);
    border-radius: 22px;
    padding: 26px;
    margin-bottom: 18px;
    min-height: 245px;
    border-left: 6px solid #9fb9d4;
}

.exercise-card h3 {
    font-size: 24px;
    margin-bottom: 18px;
}

.section-title {
    font-size: 28px;
    font-weight: 900;
    margin-top: 35px;
    margin-bottom: 18px;
}
</style>

<div class="home-wrap">
""")

html(f"""
<div class="hero-card">
    <div class="hero-title">Welcome Back, {user_name}</div>
    <div class="hero-sub">Your personalised Exercise Coach dashboard is ready.</div>
</div>
""")

html("<div class='section-title'>Today’s Summary</div>")

col1, col2 = st.columns(2)

with col1:
    html(f"""
    <div class="stat-card">
        <div class="stat-number">{total_sessions}</div>
        <div class="stat-label">Sessions Completed</div>
    </div>
    """)

with col2:
    html(f"""
    <div class="stat-card">
        <div class="stat-number">{total_minutes}</div>
        <div class="stat-label">Minutes Exercised</div>
    </div>
    """)

html("<div class='section-title'>Recommended for You</div>")

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
            html(f"""
            <div class="exercise-card">
                <h3>{name}</h3>
                <p><b>Target Area:</b> {target_area}</p>
                <p><b>Difficulty:</b> {difficulty}</p>
                <p><b>Recommendation Score:</b> {score}</p>
                <p><b>Seated Friendly:</b> {'Yes' if seated else 'No'}</p>
            </div>
            """)

            if st.button("View Details", key=f"rec_{ex_id}", use_container_width=True):
                show_exercise_profile(ex_id)

html("<div class='section-title'>Progress Diary</div>")

if not user_id:
    st.warning("Please sign in to use the diary.")

else:
    goals = get_user_goals(user_id)
    st.write("Your diary questions are personalised based on your selected goals.")

    QUESTION_BANK = {
        "Improve mobility": {
            "Do your joints feel easier to move today?": [
                "Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"
            ],
            "Did you notice improvement in your range of motion?": [
                "No improvement", "Slight improvement", "Moderate improvement", "Significant improvement"
            ],
            "Were you able to move with less stiffness?": [
                "Much more stiff", "Slightly more stiff", "No change", "Less stiff", "Much less stiff"
            ],
        },
        "Build strength": {
            "Did exercises feel easier than before?": [
                "Much harder", "Slightly harder", "About the same", "Slightly easier", "Much easier"
            ],
            "Did you feel stronger during movements?": [
                "Not at all", "A little", "Moderately", "Very much"
            ],
            "Were you able to complete more repetitions?": [
                "Fewer reps", "Same reps", "A few more reps", "Many more reps"
            ],
        },
        "Improve posture/form": {
            "Did you feel more aware of your posture?": [
                "Not at all", "Slightly", "Mostly", "Completely"
            ],
            "Were you able to maintain proper form?": [
                "Rarely", "Sometimes", "Most of the time", "Throughout the exercise"
            ],
        },
        "Increase endurance": {
            "Did you feel less tired during exercise?": [
                "More tired", "About the same", "Slightly less tired", "Much less tired"
            ],
            "Were you able to exercise longer?": [
                "Shorter than usual", "Same duration", "Slightly longer", "Much longer"
            ],
        },
        "General fitness": {
            "How was your overall energy after exercising?": [
                "Very low", "Low", "Moderate", "High", "Excellent"
            ],
            "Do you feel more confident being active?": [
                "Not yet", "A little more confident", "Moderately confident", "Very confident"
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

                    html(f"""
                    <div class="exercise-card">
                        <b>{date}</b><br><br>
                        {formatted_note}
                    </div>
                    """)

html("</div>")

bottom_nav()