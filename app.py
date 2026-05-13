import streamlit as st
import random
import time
from questions import questions
from auth import signup, login
from leaderboard import leaderboard

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="English Quiz App", layout="centered")

st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "started" not in st.session_state:
    st.session_state.started = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "questions" not in st.session_state:
    st.session_state.questions = []

if "start_time" not in st.session_state:
    st.session_state.start_time = 0


# ---------------------------
# LOGIN PAGE
# ---------------------------
if st.session_state.page == "login":

    st.title("Login System")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        success, msg = login(username, password)

        if success:
            st.session_state.logged_in = True
            st.session_state.user = username
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

    st.title("Create Account")

    username = st.text_input("New Username", key="signup_user")
    password = st.text_input("New Password", type="password", key="signup_pass")

    if st.button("Register"):
        success, msg = signup(username, password)

        if success:
            st.success(msg)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()


# ---------------------------
# HOME PAGE
# ---------------------------
elif st.session_state.page == "home":

    st.title("Welcome to English Quiz")
    st.write(f"Logged in as: **{st.session_state.user}**")

    num_q = st.selectbox("Choose quiz length", [10, 15, 20])

    if st.button("Start Quiz"):
        st.session_state.questions = random.sample(questions, num_q)

        for q in st.session_state.questions:
            random.shuffle(q["options"])

        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.page = "quiz"

        st.rerun()


# ---------------------------
# QUIZ PAGE
# ---------------------------
elif st.session_state.page == "quiz":

    q_index = st.session_state.q_index
    total = len(st.session_state.questions)

    if q_index < total:

        q = st.session_state.questions[q_index]

        st.progress((q_index + 1) / total)

        elapsed = int(time.time() - st.session_state.start_time)
        st.write(f"⏱️ Time: {elapsed}s")

        st.subheader(f"Question {q_index + 1}/{total}")
        st.write(q["question"])

        selected = st.radio("Choose answer:", q["options"], key=q_index)

        if st.button("Submit"):

            if selected == q["answer"]:
                st.success("Correct")
                st.session_state.score += 1
            else:
                st.error(f"Correct answer: {q['answer']}")

            st.session_state.q_index += 1
            st.rerun()

    else:
        st.session_state.page = "result"
        st.rerun()


# ---------------------------
# RESULT PAGE
# ---------------------------
elif st.session_state.page == "result":

    st.title("🎉 Quiz Completed!")

    score = st.session_state.score
    total = len(st.session_state.questions)
    time_taken = int(time.time() - st.session_state.start_time)

    st.metric("Score", f"{score}/{total}")
    st.write(f"⏱️ Time: {time_taken}s")

    if score >= total * 0.8:
        st.success("🔥 Excellent")
    elif score >= total * 0.5:
        st.warning("👍 Good effort")
    else:
        st.info("📚 Keep practicing")

    leaderboard.append({
        "user": st.session_state.user,
        "score": score,
        "time": time_taken
    })

    st.subheader("🏆 Leaderboard")

    sorted_board = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))

    for i, entry in enumerate(sorted_board[:5]):
        st.write(f"{i+1}. {entry['user']} - {entry['score']} ({entry['time']}s)")

    if st.button("Play Again"):
        st.session_state.page = "home"
        st.rerun()
