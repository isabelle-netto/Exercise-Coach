import streamlit as st
from db import get_user_session_results
from ui import apply_style, bottom_nav

st.set_page_config(page_title="Stats", layout="wide")
apply_style()

st.title("Your Stats")

user_id = st.session_state.get("user_id")

if not user_id:
    st.warning("Please sign in to view your stats.")
    bottom_nav()
    st.stop()

# ---------------- FETCH DATA ----------------

results = get_user_session_results(user_id)

# ---------------- SUMMARY ----------------

st.subheader("Summary")

if not results:
    st.info("No session data yet. Complete a workout to see your stats.")
else:
    total_sessions = len(results)
    total_duration = sum([row[2] for row in results])
    avg_accuracy = sum([row[4] for row in results]) / total_sessions

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Sessions", total_sessions)

    with col2:
        st.metric("Total Duration (sec)", total_duration)

    with col3:
        st.metric("Avg Accuracy (%)", f"{avg_accuracy:.1f}")

# ---------------- HISTORY ----------------

st.divider()
st.subheader("Session History")

if not results:
    st.info("No sessions recorded yet.")
else:
    for row in results:
        date, exercise_name, duration, reps, accuracy = row

        st.markdown(f"""
        <div class="card">
            <h4>{exercise_name}</h4>
            <p><b>Date:</b> {date}</p>
            <p><b>Reps:</b> {reps}</p>
            <p><b>Duration:</b> {duration} seconds</p>
            <p><b>Accuracy:</b> {accuracy}%</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- NAV ----------------

bottom_nav()