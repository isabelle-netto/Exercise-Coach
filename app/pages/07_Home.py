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

st.markdown("""
<style>

.hero-banner{
    background: linear-gradient(135deg,#1f2421,#2d3530);
    border-radius:20px;
    padding:30px;
    margin-bottom:25px;
}

.hero-title{
    font-size:52px;
    font-weight:900;
    line-height:1;
}

.hero-sub{
    font-size:18px;
    opacity:0.8;
    margin-top:10px;
}

.metric-card{
    background:#1f2421;
    border-radius:18px;
    padding:25px;
    text-align:center;
}

.metric-number{
    font-size:42px;
    font-weight:900;
}

.metric-label{
    opacity:0.7;
}

.exercise-card{
    background:#1f2421;
    border-radius:18px;
    padding:22px;
    margin-bottom:15px;
    border-left:5px solid #9fb9d4;
}

.exercise-title{
    font-size:24px;
    font-weight:900;
}

.exercise-tag{
    color:#9fb9d4;
    font-weight:700;
    margin-bottom:10px;
}

.diary-header{
    font-size:32px;
    font-weight:900;
}

</style>
""", unsafe_allow_html=True)

user_name = st.session_state.get("user_name", "Athlete")

st.markdown(f"""
<div class="hero-banner">

<div class="hero-title">
Welcome Back 💪
</div>

<div class="hero-sub">
Hello {user_name}.

Your Exercise Coach is ready to guide your next session.
</div>

</div>
""", unsafe_allow_html=True)

st.markdown("<h2>Today's Summary</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">3</div>
        <div class="metric-label">
            Sessions Completed
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">190</div>
        <div class="metric-label">
            Minutes Exercised
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown("<h2>Recommended For You</h2>", unsafe_allow_html=True)

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
            <div class="exercise-card">

                <div class="exercise-tag">
                    PERSONALISED RECOMMENDATION
                </div>

                <div class="exercise-title">
                    {name}
                </div>

                <br>

                <p><b>Target Area:</b> {target_area}</p>

                <p><b>Difficulty:</b> {difficulty}</p>

                <p><b>Match Score:</b> {score}</p>

                <p><b>Seated Friendly:</b> {'Yes' if seated else 'No'}</p>

            </div>
            """, unsafe_allow_html=True)

            if st.button("View Details", key=f"rec_{ex_id}"):

                show_exercise_profile(ex_id)

st.divider()

st.markdown("""
<div class="diary-header">
Progress Diary 📖
</div>
""", unsafe_allow_html=True)

if not user_id:

    st.warning("Please sign in to use the diary.")

else:

    goals = get_user_goals(user_id)

    st.write(
        "Your diary questions are personalised based on your selected goals."
    )

    QUESTION_BANK = {

        "Improve mobility": [
            "Do your joints feel easier to move today?",
            "Did you notice improvement in your range of motion?",
            "Were you able to move with less stiffness?"
        ],

        "Build strength": [
            "Did exercises feel easier than before?",
            "Did you feel stronger during movements?",
            "Were you able to complete more repetitions?"
        ],

        "Improve posture/form": [
            "Did you feel more aware of your posture?",
            "Were you able to maintain proper form?"
        ],

        "Increase endurance": [
            "Did you feel less tired during exercise?",
            "Were you able to exercise longer?"
        ],

        "General fitness": [
            "How was your overall energy after exercising?",
            "Do you feel more confident being active?"
        ]
    }

    selected_questions = []

    for goal in goals:

        if goal in QUESTION_BANK:

            selected_questions.extend(
                QUESTION_BANK[goal]
            )

    if not selected_questions:

        st.info(
            "No goals found. Please update your profile."
        )

    else:

        with st.expander("Add Diary Entry"):

            answers = []

            for q in selected_questions:

                ans = st.selectbox(
                    q,
                    [
                        "Not yet",
                        "Slightly",
                        "Moderately",
                        "A lot"
                    ],
                    key=q
                )

                answers.append(
                    f"{q} → {ans}"
                )

            note = st.text_area(
                "Personal reflection"
            )

            if st.button(
                "Save Diary Entry"
            ):

                entry_text = "\n".join(
                    answers
                )

                if note:

                    entry_text += (
                        f"\n\nNote: {note}"
                    )

                save_diary_entry(
                    user_id,
                    entry_text
                )

                st.success(
                    "Diary entry saved."
                )

        with st.expander(
            "View Previous Entries"
        ):

            entries = get_diary_entries(
                user_id
            )

            if not entries:

                st.info(
                    "No entries yet."
                )

            else:

                for date, note in entries:

                    formatted_note = (
                        note.replace(
                            "\n",
                            "<br>"
                        )
                    )

                    st.markdown(
                        f"""
                        <div class="exercise-card">
                            <b>{date}</b>
                            <br><br>
                            {formatted_note}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

bottom_nav()