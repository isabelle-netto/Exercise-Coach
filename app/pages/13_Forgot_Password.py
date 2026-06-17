import streamlit as st
from db import generate_reset_code, save_reset_code, verify_reset_code, update_password
from email_utils import send_reset_email
from ui import apply_style

st.set_page_config(page_title="Reset Password", layout="wide")
apply_style()

st.title("Reset Password")

# STEP 1: EMAIL
email = st.text_input("Enter your email")

if st.button("Send Reset Code"):
    code = generate_reset_code()
    save_reset_code(email, code)
    send_reset_email(email, code)
    st.success("Reset code sent to your email")

st.markdown("---")

# STEP 2: RESET
code_input = st.text_input("Enter Code")
new_password = st.text_input("New Password", type="password")

if st.button("Reset Password"):
    if verify_reset_code(email, code_input):
        update_password(email, new_password)
        st.success("Password updated successfully")
    else:
        st.error("Invalid or expired code")

st.markdown("---")

if st.button("Back to Sign In"):
    st.switch_page("pages/02_Sign_In.py")