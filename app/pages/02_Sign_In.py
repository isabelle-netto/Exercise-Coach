import streamlit as st
from db import login_user
from ui import apply_style

st.set_page_config(page_title="Sign In", layout="wide")
apply_style()

st.markdown("""
<style>
.block-container {
    padding-top: 4rem !important;
    max-width: 540px !important;
}

.signin-title {
    font-size: 58px;
    font-weight: 900;
    line-height: 0.9;
    text-transform: uppercase;
    margin-bottom: 35px;
}

.auth-space {
    height: 18px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="signin-title">
WELCOME<br>BACK
</div>
""", unsafe_allow_html=True)

email = st.text_input("Email", key="signin_email")
password = st.text_input("Password", type="password", key="signin_password")

if st.button("SIGN IN", key="signin_button", use_container_width=True):
    email_value = st.session_state.get("signin_email", "").strip().lower()
    password_value = st.session_state.get("signin_password", "").strip()

    if not email_value or not password_value:
        st.warning("Please enter email and password.")
    else:
        try:
            user = login_user(email_value, password_value)

            if user:
                st.session_state["user_id"] = user[0]
                st.session_state["user_name"] = user[1]
                st.success("Login successful.")
                st.switch_page("pages/07_Home.py")
            else:
                st.error("Invalid email or password.")
        except Exception as e:
            st.error(f"Sign in failed: {e}")

st.markdown("<div class='auth-space'></div>", unsafe_allow_html=True)

if st.button("FORGOT PASSWORD?", key="forgot_password_button", use_container_width=True):
    st.switch_page("pages/13_Forgot_Password.py")

if st.button("BACK TO WELCOME", key="back_to_welcome_button", use_container_width=True):
    st.switch_page("main.py")