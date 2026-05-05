import streamlit as st
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
import random
import time
import os

# ---------------- CONFIG ----------------
APP_NAME = "🛡️ Fraud Shield"

BANKS = {
    "MCB": "mcb@email.com",
    "SBM": "sbm@email.com",
    "ABSA": "absa@email.com"
}

CYBER_CRIME_EMAIL = "cybercrime@gov.mu"

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

RATE_LIMIT_SECONDS = 60

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "otp" not in st.session_state:
    st.session_state.otp = None

if "banks" not in st.session_state:
    st.session_state.banks = BANKS.copy()

if "last_sent" not in st.session_state:
    st.session_state.last_sent = 0

# ---------------- EMAIL FUNCTION ----------------
def send_email(message, bank_email):
    msg = MIMEText(message)
    msg["Subject"] = "Fraud Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = bank_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    server.sendmail(
        SENDER_EMAIL,
        [bank_email, CYBER_CRIME_EMAIL],
        msg.as_string()
    )

    server.quit()

# ---------------- UI ----------------
st.title(APP_NAME)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    st.subheader("Login (+230)")

    phone = st.text_input("Phone number")

    if st.button("Send OTP"):
        otp = random.randint(1000, 9999)
        st.session_state.otp = str(otp)
        st.success(f"OTP (demo only): {otp}")

    user_otp = st.text_input("Enter OTP")

    if st.button("Verify"):
        if user_otp == st.session_state.otp:
            st.session_state.logged_in = True
            st.session_state.phone = phone
            st.success("Logged in successfully")
        else:
            st.error("Invalid OTP")

    st.stop()

# ---------------- AUDIO UPLOAD ----------------
st.subheader("🎤 Upload Voice Message")

audio_file = st.file_uploader("Upload audio file (WAV recommended)", type=["wav"])

if audio_file is not None:

    with open("temp.wav", "wb") as f:
        f.write(audio_file.read())

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        st.session_state.text = text

        st.success("Speech converted successfully")

    except Exception as e:
        st.error("Could not process audio")
        st.write(e)

# ---------------- SHOW TEXT ----------------
if "text" in st.session_state:
    st.subheader("Captured Message")
    st.write(st.session_state.text)

    st.info("No editing allowed. Please confirm below.")

# ---------------- CONFIRMATION ----------------
confirm = st.radio("Confirm message", ["Send", "Record Again"])

if confirm == "Record Again":
    st.session_state.pop("text", None)
    st.stop()

# ---------------- BANK SELECTION ----------------
st.subheader("🏦 Select Bank")

selected_bank = st.selectbox(
    "Choose bank",
    list(st.session_state.banks.keys())
)

# ---------------- SEND ----------------
if st.button("Send Report"):

    if time.time() - st.session_state.last_sent < RATE_LIMIT_SECONDS:
        st.error("Wait before sending another report")
        st.stop()

    if "text" not in st.session_state:
        st.warning("No message found")
        st.stop()

    message = f"""
FRAUD REPORT

Phone: {st.session_state.phone}
Message:
{st.session_state.text}
"""

    send_email(message, st.session_state.banks[selected_bank])

    st.session_state.last_sent = time.time()

    st.success("Report sent to bank + cybercrime unit")

# ---------------- ADMIN ----------------
st.sidebar.title("Admin Panel")

admin = st.sidebar.checkbox("Enable Admin")

if admin:
    password = st.sidebar.text_input("Password", type="password")

    if password == "admin123":

        st.sidebar.success("Admin Access")

        for bank in st.session_state.banks:
            new_email = st.sidebar.text_input(
                bank,
                value=st.session_state.banks[bank]
            )
            st.session_state.banks[bank] = new_email

    else:
        st.sidebar.warning("Wrong password")

# ---------------- LOGOUT ----------------
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()
