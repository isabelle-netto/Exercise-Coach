import os
import smtplib
from email.mime.text import MIMEText
import streamlit as st


def get_secret_value(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key)


EMAIL_ADDRESS = get_secret_value("EMAIL_ADDRESS")
EMAIL_PASSWORD = get_secret_value("EMAIL_PASSWORD")


def send_reset_email(to_email, code):
    subject = "Password Reset Code"
    body = f"Your password reset code is: {code}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)