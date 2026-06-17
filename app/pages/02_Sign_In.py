import streamlit as st
from db import login_user
from ui import apply_style

st.set_page_config(page_title="Sign In", layout="wide")
apply_style()

st.title("Sign In")

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Sign In"):
    user = login_user(email, password)

    if user:
        st.session_state["user_id"] = user[0]
        st.success("Login successful")
        st.switch_page("pages/07_Home.py")
    else:
        st.error("Invalid email or password")

st.markdown("---")

if st.button("Forgot Password?"):
    st.switch_page("pages/13_Forgot_Password.py")