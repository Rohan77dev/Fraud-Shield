import streamlit as st
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
import random
import time
import pyttsx3

# ---------------- CONFIG ----------------
APP_NAME = "🛡️ Fraud Shield"

DEFAULT_BANKS = {
    "MCB": "mcb@email.com",
    "SBM": "sbm@email.com",
    "ABSA": "absa@email.com"
}

CYBER_CRIME_EMAIL = "cybercrime@gov.mu"

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"

RATE_LIMIT_SECONDS = 60  # prevent spam

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "otp" not in st.session_state:
    st.session_state.otp = None

if "banks" not in st.session_state:
    st.session_state.banks = DEFAULT_BANKS.copy()

if "last_sent" not in st.session_state:
    st.session_state.last_sent = 0

# ---------------- TTS ENGINE ----------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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

    st.subheader("Login")

    phone = st.text_input("Phone Number (+230)")

    if st.button("Send OTP"):
        otp = random.randint(1000, 9999)
        st.session_state.otp = str(otp)
        st.success(f"OTP (demo): {otp}")

    user_otp = st.text_input("Enter OTP")

    if st.button("Verify"):
        if user_otp == st.session_state.otp:
            st.session_state.logged_in = True
            st.session_state.phone = phone
            st.success("Logged in")
        else:
            st.error("Invalid OTP")

    st.stop()

# ---------------- MAIN APP ----------------
st.subheader("🎤 Record Complaint")

if st.button("Start Recording"):
    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("Speak now...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            st.session_state.text = text
            st.success("Recording complete")

            speak("Your message has been recorded")

        except:
            st.error("Could not understand audio")

# ---------------- SHOW TEXT ----------------
if "text" in st.session_state:
    st.subheader("Captured Message")
    st.write(st.session_state.text)

    if st.button("🔊 Play Message"):
        speak(st.session_state.text)

# ---------------- CONFIRMATION ----------------
confirm = st.radio(
    "Confirm message?",
    ["Yes - Send", "No - Record Again"]
)

if confirm == "No - Record Again":
    st.session_state.pop("text", None)
    st.warning("Please record again")
    st.stop()

# ---------------- BANK SELECTION ----------------
st.subheader("🏦 Select Bank")

selected_bank = st.selectbox(
    "Choose bank",
    list(st.session_state.banks.keys())
)

# ---------------- SEND ----------------
if st.button("Send Report"):

    # Rate limiting
    if time.time() - st.session_state.last_sent < RATE_LIMIT_SECONDS:
        st.error("Please wait before sending another report")
        st.stop()

    if "text" not in st.session_state:
        st.warning("Record first")
        st.stop()

    message = f"""
    FRAUD REPORT

    Phone: {st.session_state.phone}
    Bank: {selected_bank}

    Message:
    {st.session_state.text}
    """

    send_email(message, st.session_state.banks[selected_bank])

    st.session_state.last_sent = time.time()

    st.success("Report sent successfully")

# ---------------- ADMIN PANEL ----------------
st.sidebar.title("Admin Panel")

admin_mode = st.sidebar.checkbox("Enable Admin")

if admin_mode:

    password = st.sidebar.text_input("Admin Password", type="password")

    if password == "admin123":  # change later!

        st.sidebar.success("Admin Access")

        st.sidebar.subheader("Edit Bank Emails")

        for bank in st.session_state.banks:
            new_email = st.sidebar.text_input(
                f"{bank} Email",
                value=st.session_state.banks[bank]
            )
            st.session_state.banks[bank] = new_email

    else:
        st.sidebar.error("Wrong password")

# ---------------- LOGOUT ----------------
if st.button("Logout"):
    st.session_state.clear()
    st.session_state.logged_in = False
