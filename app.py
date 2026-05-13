import streamlit as st
import random, time, json, bcrypt
from auth import signup, login

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CBT Quiz System", layout="centered")

# ---------------- EMAIL ----------------
import smtplib
from email.mime.text import MIMEText

EMAIL_ADDRESS = "yourgmail@gmail.com"
EMAIL_PASSWORD = "yourapppassword"

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# ---------------- HELPERS ----------------
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def gen_code(name):
    return name[:3].upper() + str(random.randint(100,999))

# ---------------- LOAD DATA ----------------
users = load_json("users.json", {})
logs = load_json("users_log.json", [])
analytics = load_json("analytics.json", [])
leaderboard = load_json("leaderboard.json", [])
referrals = load_json("referrals.json", {})

# ---------------- SESSION ----------------
for key, val in {
    "page":"login","user":"","score":0,"q_index":0,
    "questions":[],"start_time":0,"points":0,"ref_code":""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- LOGIN ----------------
if st.session_state.page == "login":

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        ok, msg = login(u,p)
        if ok:
            st.session_state.user = u
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Sign Up"):
        st.session_state.page = "signup"; st.rerun()

    if st.button("Forgot Password"):
        st.session_state.page = "forgot"; st.rerun()

# ---------------- SIGNUP ----------------
elif st.session_state.page == "signup":

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    email = st.text_input("Email")
    ref = st.text_input("Referral Code (optional)")

    if st.button("Register"):
        ok, msg = signup(u,p)
        if ok:
            users[u]["email"] = email
            code = gen_code(u)

            referrals[u] = {"code":code,"points":0,"invited_by":ref}

            if ref:
                for k,v in referrals.items():
                    if v["code"] == ref:
                        v["points"] += 10

            save_json("users.json", users)
            save_json("referrals.json", referrals)

            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()

# ---------------- FORGOT PASSWORD ----------------
elif st.session_state.page == "forgot":

    u = st.text_input("Username")

    if st.button("Send OTP"):
        if u in users:
            code = str(random.randint(100000,999999))
            st.session_state.reset = code
            st.session_state.reset_user = u
            st.session_state.reset_time = time.time()

            send_email(users[u]["email"],"OTP Code",f"Code: {code}")
            st.success("OTP sent")
        else:
            st.error("User not found")

    otp = st.text_input("OTP")
    newp = st.text_input("New Password", type="password")

    if st.button("Reset"):
        if time.time() - st.session_state.get("reset_time",0) > 300:
            st.error("Expired"); st.stop()

        if otp == st.session_state.get("reset"):
            hashed = bcrypt.hashpw(newp.encode(), bcrypt.gensalt()).decode()
            users[u]["password"] = hashed
            save_json("users.json", users)

            st.success("Password updated")
            st.session_state.page = "login"
            st.rerun()

# ---------------- HOME ----------------
elif st.session_state.page == "home":

    st.write(f"Welcome {st.session_state.user}")

    st.code(referrals.get(st.session_state.user,{}).get("code",""))

    n = st.selectbox("Questions",[5,10,15])

    if st.button("Start"):
        from questions import questions
        st.session_state.questions = random.sample(questions,n)
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.page = "quiz"
        st.rerun()

# ---------------- QUIZ ----------------
elif st.session_state.page == "quiz":

    i = st.session_state.q_index
    total = len(st.session_state.questions)

    if i < total:
        q = st.session_state.questions[i]
        ans = st.radio(q["question"], q["options"], key=i)

        if st.button("Submit"):
            if ans == q["answer"]:
                st.session_state.score += 1
            st.session_state.q_index += 1
            st.rerun()
    else:
        st.session_state.page = "result"
        st.rerun()

# ---------------- RESULT ----------------
elif st.session_state.page == "result":

    score = st.session_state.score
    total = len(st.session_state.questions)

    st.metric("Score", f"{score}/{total}")

    analytics.append({"user":st.session_state.user,"score":score})
    save_json("analytics.json", analytics)

    share = f"I scored {score}/{total}! Join me!"
    st.code(share)

    if st.button("Home"):
        st.session_state.page = "home"
        st.rerun()
