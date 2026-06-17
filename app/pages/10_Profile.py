import streamlit as st
from ui import apply_style, bottom_nav

apply_style()

st.title("Profile")

st.write(f"**Name:** {st.session_state.get('user_name', 'Demo User')}")
st.write("**Email:** Saved in database")

st.divider()

st.subheader("Preferences")

st.write("**Movement Capability:**", st.session_state.get("limitation_category", "Not set"))
st.write("**Equipment:**", ", ".join(st.session_state.get("selected_equipment", [])) or "Not set")
st.write("**Fitness Goals:**", ", ".join(st.session_state.get("fitness_goals", [])) or "Not set")

if st.button("Update Profile"):
    st.switch_page("pages/04_Mobility_Capability.py")

if st.button("Sign Out"):
    st.session_state.clear()
    st.switch_page("main.py")

bottom_nav()