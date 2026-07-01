import streamlit as st
from ui import apply_style, bottom_nav
from accessibility import (
    accessibility_settings_panel,
    speak,
    save_accessibility_settings,
)
from db import (
    get_user_profile,
    get_user_equipment,
    get_user_goals,
    get_user_mobility_results,
)

st.set_page_config(page_title="Profile Settings", layout="wide")
apply_style()

user_id = st.session_state.get("user_id")

if not user_id:
    st.warning("Please sign in first.")
    if st.button("Go to Sign In"):
        st.switch_page("pages/02_Sign_In.py")
    st.stop()

name = st.session_state.get("user_name", "User")

movement_capability = get_user_profile(user_id) or st.session_state.get(
    "limitation_category", "Not set"
)

equipment = get_user_equipment(user_id) or st.session_state.get(
    "selected_equipment", []
)

goals = get_user_goals(user_id) or st.session_state.get(
    "fitness_goals", []
)

mobility_results = get_user_mobility_results(user_id)

st.markdown(
    """
<style>
.profile-wrapper {
    padding: 35px;
}

.profile-hero {
    background: linear-gradient(135deg, #1f2421, #2d3530);
    border-radius: 24px;
    padding: 32px;
    margin-bottom: 26px;
}

.profile-title {
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 8px;
}

.profile-sub {
    font-size: 17px;
    opacity: 0.8;
}

.profile-card {
    background: rgba(31,36,33,0.92);
    border-radius: 22px;
    padding: 26px;
    margin-bottom: 20px;
}

.profile-card h3 {
    margin-top: 0;
    font-size: 22px;
}

.profile-value {
    font-size: 20px;
    font-weight: 800;
    margin-top: 12px;
}

.profile-muted {
    opacity: 0.75;
    font-size: 15px;
}

.result-pill {
    display: inline-block;
    background: rgba(159,185,212,0.18);
    border: 1px solid #9fb9d4;
    padding: 8px 14px;
    border-radius: 999px;
    margin: 5px;
    font-weight: 700;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="profile-wrapper">

<div class="profile-hero">
    <div class="profile-title">Profile Settings</div>
    <div class="profile-sub">
        Hello {name}. View your current exercise profile, accessibility settings,
        mobility data, and account options.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
<div class="profile-card">
    <h3>Movement Capability</h3>
    <div class="profile-muted">Based on your profile setup selection.</div>
    <div class="profile-value">{movement_capability}</div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    goals_text = ", ".join(goals) if goals else "Not set"

    st.markdown(
        f"""
<div class="profile-card">
    <h3>Fitness Goals</h3>
    <div class="profile-muted">
        Used to personalise diary questions and exercise recommendations.
    </div>
    <div class="profile-value">{goals_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )

equipment_text = ", ".join(equipment) if equipment else "Not set"

st.markdown(
    f"""
<div class="profile-card">
    <h3>Available Equipment</h3>
    <div class="profile-muted">Used to filter suitable exercises.</div>
    <div class="profile-value">{equipment_text}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="profile-card">
    <h3>Accessibility Settings</h3>
    <div class="profile-muted">
        Adjust theme, text size, and audio feedback.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

accessibility_settings_panel()

col_a, col_b = st.columns(2)

with col_a:
    if st.button("Read Accessibility Settings", use_container_width=True):
        speak(
            "Accessibility settings. You can change theme, text size, "
            "and audio feedback."
        )

with col_b:
    if st.button("Save Accessibility Preferences", use_container_width=True):
        save_accessibility_settings()
        st.success("Accessibility preferences saved.")
        st.rerun()

st.markdown(
    """
<div class="profile-card">
    <h3>Mobility Assessment</h3>
    <div class="profile-muted">
        Your mobility test results help the system understand your range of motion.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if mobility_results:
    for key, result in mobility_results.items():
        st.markdown(
            f"""
<span class="result-pill">
    {key}: ROM {result.get("rom", 0)}°, 
    Safe Limit {result.get("safe_limit_angle", 0)}°
</span>
""",
            unsafe_allow_html=True,
        )
else:
    st.info("No saved mobility test results yet.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Update Profile Setup", use_container_width=True):
        st.switch_page("pages/04_Mobility_Capability.py")

with col2:
    if st.button("Go to Mobility Assessment", use_container_width=True):
        st.switch_page("pages/14_Mobility_Test.py")

st.divider()

if st.button("Sign Out", use_container_width=True):
    st.session_state.clear()
    st.switch_page("main.py")

st.markdown("</div>", unsafe_allow_html=True)

bottom_nav()