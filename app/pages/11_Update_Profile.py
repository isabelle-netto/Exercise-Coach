import streamlit as st

from ui import apply_style, bottom_nav
from accessibility import (
    accessibility_settings_panel,
    speak,
    screen_reader_status,
)

st.set_page_config(page_title="Update Profile", layout="wide")
apply_style()

st.title("Profile Settings")

screen_reader_status("Profile settings page loaded.")

st.markdown("""
<div class="card">
    <h3>Accessibility Preferences</h3>
    <p>
    You can update your accessibility preferences at any time.
    These settings will be applied across the Exercise Coach app.
    </p>
</div>
""", unsafe_allow_html=True)

accessibility_settings_panel()

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h3>Accessibility Preview</h3>
    <p>
    Use the controls above to test Light Mode, Dark Mode, Large Text,
    Audio Feedback, and Voice Control.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Read Accessibility Settings",
        use_container_width=True
    ):
        speak(
            f"""
            Current theme is {st.session_state.get('theme')}.
            Current text size is {st.session_state.get('text_size')}.
            Audio feedback is {'enabled' if st.session_state.get('audio_feedback') else 'disabled'}.
            Voice control is {'enabled' if st.session_state.get('voice_control') else 'disabled'}.
            """
        )

with col2:
    if st.button(
        "Save Accessibility Preferences",
        use_container_width=True
    ):
        st.success("Accessibility preferences saved.")
        speak("Accessibility preferences saved.")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h3>Physical Accessibility Profile</h3>
    <p>
    If your physical capabilities change over time,
    you can update your profile and mobility information.
    This helps the system provide safer exercise recommendations.
    </p>
</div>
""", unsafe_allow_html=True)

mobility_assistance = st.selectbox(
    "Mobility Status",
    [
        "No mobility impairment",
        "Wheelchair user",
        "Limited lower limb mobility",
        "Limited upper limb mobility",
        "Uses walking aid",
        "Other"
    ]
)

limb_status = st.multiselect(
    "Available Limbs",
    [
        "Right Arm",
        "Left Arm",
        "Right Leg",
        "Left Leg"
    ],
    default=[
        "Right Arm",
        "Left Arm",
        "Right Leg",
        "Left Leg"
    ]
)

if st.button(
    "Save Physical Accessibility Profile",
    use_container_width=True
):
    st.session_state["mobility_status"] = mobility_assistance
    st.session_state["available_limbs"] = limb_status

    st.success("Physical accessibility profile updated.")

    speak(
        "Physical accessibility profile updated successfully."
    )

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h3>Mobility Assessment</h3>
    <p>
    If your physical condition has changed,
    you should repeat the mobility assessment.
    This ensures exercise recommendations and coaching
    remain accurate.
    </p>
</div>
""", unsafe_allow_html=True)

if st.button(
    "Go To Mobility Assessment",
    use_container_width=True
):
    st.switch_page("pages/14_Mobility_Test.py")

bottom_nav()