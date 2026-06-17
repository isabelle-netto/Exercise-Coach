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

.auth-space {
    height: 18px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-title">
LET’S<br>GET<br>STARTED
</div>
""", unsafe_allow_html=True)

first_name = st.text_input("First Name", key="signup_first_name")
last_name = st.text_input("Last Name", key="signup_last_name")
email = st.text_input("Email", key="signup_email")
password = st.text_input("Password", type="password", key="signup_password")

if st.button("SIGN UP", key="signup_button", use_container_width=True):
    first_name_value = st.session_state.get("signup_first_name", "").strip()
    last_name_value = st.session_state.get("signup_last_name", "").strip()
    email_value = st.session_state.get("signup_email", "").strip().lower()
    password_value = st.session_state.get("signup_password", "").strip()

    full_name = f"{first_name_value} {last_name_value}".strip()

    if not first_name_value or not last_name_value or not email_value or not password_value:
        st.warning("Please fill in all fields.")
    else:
        try:
            user_id = create_user(full_name, email_value, password_value)

            if user_id:
                st.session_state["user_id"] = user_id
                st.session_state["user_name"] = full_name
                st.success("Account created successfully.")
                st.switch_page("pages/03_Profile_Transition.py")
            else:
                st.error("This email already exists. Please sign in instead.")

        except Exception as e:
            st.error(f"Sign up failed: {e}")

st.markdown("<div class='auth-space'></div>", unsafe_allow_html=True)
st.write("Already have an account?")

if st.button("SIGN IN HERE", key="signup_to_signin", use_container_width=True):
    st.switch_page("pages/02_Sign_In.py")