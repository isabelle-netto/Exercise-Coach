import streamlit as st
from db import login_user
from ui import apply_style

st.set_page_config(page_title="Sign In", layout="wide")
apply_style()

st.markdown("""
<style>
.block-container {
    padding-top: 40px !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

.signin-title {
    font-size: 64px;
    font-weight: 900;
    line-height: 0.95;
    text-transform: uppercase;
    margin-bottom: 35px;
}

.signin-form div.stButton {
    margin-top: 18px;
    margin-bottom: 20px;
}

.signin-form div.stButton > button {
    width: 100% !important;
    height: 58px !important;
}
</style>
""", unsafe_allow_html=True)

left, middle, right = st.columns([1.5, 1, 1.5])

with middle:
    st.markdown('<div class="signin-title">WELCOME<br>BACK</div>', unsafe_allow_html=True)

    st.markdown('<div class="signin-form">', unsafe_allow_html=True)

    email = st.text_input("Email", key="signin_email")
    password = st.text_input("Password", type="password", key="signin_password")

    if st.button("SIGN IN", key="signin_button", use_container_width=True):
        user = login_user(email, password)

        if user:
            st.session_state["user_id"] = user[0]
            st.success("Login successful")
            st.switch_page("pages/07_Home.py")
        else:
            st.error("Invalid email or password")

    if st.button("FORGOT PASSWORD?", key="forgot_password_button", use_container_width=True):
        st.switch_page("pages/13_Forgot_Password.py")

    if st.button("BACK TO WELCOME", key="back_to_welcome_button", use_container_width=True):
        st.switch_page("main.py")

    st.markdown('</div>', unsafe_allow_html=True)