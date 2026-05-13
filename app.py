import streamlit as st
import random
import time
import json

from questions import questions
from auth import signup, login

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="CBT Quiz System", layout="centered")

st.title("📘 CBT English Quiz System")

# ---------------------------
# LOAD FILES
# ---------------------------
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

def generate_code(name):
    return name[:3].upper() + str(random.randint(100,999))

referrals = load_json("referrals.json", {})
leaderboard = load_json("leaderboard.json", [])

# ---------------------------
# SESSION STATE
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = ""

if "score" not in st.session_state:
    st.session_state.score = 0

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "questions" not in st.session_state:
    st.session_state.questions = []

if "start_time" not in st.session_state:
    st.session_state.start_time = 0

if "ref_code" not in st.session_state:
    st.session_state.ref_code = ""

if "points" not in st.session_state:
    st.session_state.points = 0


# ---------------------------
# LOGIN PAGE
# ---------------------------
if st.session_state.page == "login":

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        success, msg = login(username, password)

        if success:
            st.session_state.user = username
            st.session_state.ref_code = referrals.get(username, {}).get("code", "")
            st.session_state.points = referrals.get(username, {}).get("points", 0)
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()


# ---------------------------
# SIGNUP PAGE
# ---------------------------
elif st.session_state.page == "signup":

    username = st.text_input("New Username", key="signup_user")
    password = st.text_input("New Password", type="password", key="signup_pass")
    referral = st.text_input("Referral Code (optional)", key="ref_input")

    if st.button("Register"):
        success, msg = signup(username, password)

        if success:

            code = generate_code(username)

            referrals[username] = {
                "code": code,
                "invited_by": referral if referral else None,
                "points": 0
            }

            # reward inviter
            if referral:
                for user, data in referrals.items():
                    if data.get("code") == referral:
                        data["points"] += 10

            save_json("referrals.json", referrals)

            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()


# ---------------------------
# HOME PAGE (VIRAL HUB)
# ---------------------------
elif st.session_state.page == "home":

    st.write(f"Welcome **{st.session_state.user}**")

    st.subheader("🎯 Referral System")
    st.code(st.session_state.ref_code)
    st.write(f"⭐ Points: {st.session_state.points}")

    st.subheader("Choose Quiz Length")
    num_q = st.selectbox("Questions", [5, 10, 15, 20])

    if st.button("Start Quiz 🚀"):

        st.session_state.questions = random.sample(questions, num_q)
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.page = "quiz"

        st.rerun()

    st.subheader("🏆 Top Players")

    sorted_board = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))

    for i, entry in enumerate(sorted_board[:5]):
        st.write(f"{i+1}. {entry['user']} - {entry['score']}")


# ---------------------------
# QUIZ PAGE
# ---------------------------
elif st.session_state.page == "quiz":

    i = st.session_state.q_index
    total = len(st.session_state.questions)

    if i < total:

        q = st.session_state.questions[i]

        st.progress((i+1)/total)
        st.write(q["question"])

        answer = st.radio("Choose answer:", q["options"], key=i)

        if st.button("Submit"):

            if answer == q["answer"]:
                st.success("Correct")
                st.session_state.score += 1
            else:
                st.error(f"Correct: {q['answer']}")

            st.session_state.q_index += 1
            st.rerun()

    else:
        st.session_state.page = "result"
        st.rerun()


# ---------------------------
# RESULT PAGE (VIRAL ENGINE)
# ---------------------------
elif st.session_state.page == "result":

    score = st.session_state.score
    total = len(st.session_state.questions)
    time_taken = int(time.time() - st.session_state.start_time)

    st.title("🎉 Completed!")

    st.metric("Score", f"{score}/{total}")
    st.write(f"⏱️ Time: {time_taken}s")

    leaderboard.append({
        "user": st.session_state.user,
        "score": score,
        "time": time_taken
    })

    save_json("leaderboard.json", leaderboard)

    share_text = f"I scored {score}/{total} in CBT Quiz 🔥 Join using code {st.session_state.ref_code}"

    st.subheader("📲 Share")
    st.code(share_text)

    if st.button("Play Again"):
        st.session_state.page = "home"
        st.rerun()
