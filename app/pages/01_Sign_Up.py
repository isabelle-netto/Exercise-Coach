import streamlit as st
from db import create_user


st.markdown("""
<style>
.block-container {
    padding-top: 4rem;
    max-width: 540px;
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
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-title">
LET’S<br>GET<br>STARTED
</div>
""", unsafe_allow_html=True)

first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("SIGN UP", use_container_width=True):
    full_name = f"{first_name} {last_name}".strip()

    if full_name and email and password:
        user_id = create_user(full_name, email, password)

        if user_id:
            st.session_state["user_id"] = user_id
            st.session_state["user_name"] = full_name
            st.switch_page("pages/03_Profile_Transition.py")
        else:
            st.error("This email already exists.")
    else:
        st.warning("Please fill in all fields.")

st.markdown("<p class='auth-link'>Already have an account?</p>", unsafe_allow_html=True)

if st.button("SIGN IN HERE", use_container_width=True):
    st.switch_page("pages/02_Sign_In.py")