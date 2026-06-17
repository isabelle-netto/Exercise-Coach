import streamlit as st
from db import login_user
from ui import apply_style

st.set_page_config(page_title="Sign In", layout="wide")
apply_style()

st.markdown("""
<style>
.signin-wrapper {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.signin-box {
    width: 480px;
    max-width: 90vw;
}

.signin-title {
    font-size: 64px;
    font-weight: 900;
    line-height: 0.95;
    margin-bottom: 40px;
    text-transform: uppercase;
}

.signin-button-space {
    height: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="signin-wrapper"><div class="signin-box">', unsafe_allow_html=True)

st.markdown("""
<div class="signin-title">
    WELCOME<br>
    BACK
</div>
""", unsafe_allow_html=True)

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("SIGN IN", use_container_width=True):
    user = login_user(email, password)

    if user:
        st.session_state["user_id"] = user[0]
        st.success("Login successful")
        st.switch_page("pages/07_Home.py")
    else:
        st.error("Invalid email or password")

st.markdown('<div class="signin-button-space"></div>', unsafe_allow_html=True)

if st.button("FORGOT PASSWORD?", use_container_width=True):
    st.switch_page("pages/13_Forgot_Password.py")

st.markdown('<div class="signin-button-space"></div>', unsafe_allow_html=True)

if st.button("BACK TO WELCOME", use_container_width=True):
    st.switch_page("main.py")

st.markdown('</div></div>', unsafe_allow_html=True)