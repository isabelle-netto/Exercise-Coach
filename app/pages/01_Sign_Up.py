import streamlit as st
from db import create_user
from ui import apply_style

st.set_page_config(page_title="Sign Up", layout="wide")
apply_style()

st.markdown("""
<style>
.block-container {
    padding-top: 4rem !important;
    max-width: 540px !important;
}

.auth-title {
    font-size: 58px;
    font-weight: 900;
    line-height: 0.9;
    text-transform: uppercase;
    margin-bottom: 35px;
}

.auth-link {
    margin-top: 18px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-title">
LET’S<br>GET<br>STARTED
</div>
""", unsafe_allow_html=True)

with st.form("signup_form", clear_on_submit=False):
    first_name = st.text_input("First Name", key="signup_first_name")
    last_name = st.text_input("Last Name", key="signup_last_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")

    submitted = st.form_submit_button("SIGN UP", use_container_width=True)

if submitted:
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()
    password = password.strip()

    full_name = f"{first_name} {last_name}".strip()

    if not first_name or not last_name or not email or not password:
        st.warning("Please fill in all fields.")

    else:
        user_id = create_user(full_name, email, password)

        if user_id:
            st.session_state["user_id"] = user_id
            st.session_state["user_name"] = full_name
            st.success("Account created successfully.")
            st.switch_page("pages/03_Profile_Transition.py")
        else:
            st.error("This email already exists. Please sign in instead.")

st.markdown("<p class='auth-link'>Already have an account?</p>", unsafe_allow_html=True)

if st.button("SIGN IN HERE", use_container_width=True):
    st.switch_page("pages/02_Sign_In.py")