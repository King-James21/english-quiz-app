import streamlit as st
import random
import time
from questions import questions
from auth import signup, login
from leaderboard import leaderboard

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="CBT Quiz Challenge", layout="centered")

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
# SESSION STATE
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if "user" not in st.session_state:
    st.session_state.user = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = 0


# =========================
# LOGIN PAGE
# =========================
if st.session_state.page == "login":

    st.title("📘 CBT English Quiz Challenge")
    st.subheader("Test yourself & compete with friends 🔥")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        success, msg = login(username, password)

        if success:
            st.session_state.user = username
            st.session_state.page = "home"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()


# =========================
# SIGNUP PAGE
# =========================
elif st.session_state.page == "signup":

    st.title("Create Account")

    username = st.text_input("New Username", key="signup_user")
    password = st.text_input("New Password", type="password", key="signup_pass")

    if st.button("Register"):
        success, msg = signup(username, password)

        if success:
            st.success("Account created!")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error(msg)

    if st.button("Back"):
        st.session_state.page = "login"
        st.rerun()


# =========================
# HOME PAGE (TRAFFIC HUB)
# =========================
elif st.session_state.page == "home":

    st.title("🔥 CBT Challenge Arena")

    st.write(f"Welcome **{st.session_state.user}**")

    st.info("👉 Take the quiz and compete on the leaderboard!")

    st.subheader("Choose Difficulty")

    num_q = st.selectbox("Number of Questions", [5, 10, 15, 20])

    if st.button("Start Challenge 🚀"):

        st.session_state.questions = random.sample(questions, num_q)
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.page = "quiz"

        st.rerun()

    # LEADERBOARD PREVIEW (TRAFFIC DRIVER)
    st.subheader("🏆 Top Players")

    sorted_board = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))

    for i, entry in enumerate(sorted_board[:5]):
        st.write(f"{i+1}. {entry['user']} - {entry['score']}")

    st.caption("🔥 Share your score and challenge friends!")


# =========================
# QUIZ PAGE
# =========================
elif st.session_state.page == "quiz":

    q_index = st.session_state.q_index
    total = len(st.session_state.questions)

    if q_index < total:

        q = st.session_state.questions[q_index]

        st.progress((q_index + 1) / total)

        st.write(f"⏱️ Time: {int(time.time() - st.session_state.start_time)}s")

        st.subheader(q["question"])

        answer = st.radio("Choose answer:", q["options"], key=q_index)

        if st.button("Submit"):

            if answer == q["answer"]:
                st.success("Correct ✅")
                st.session_state.score += 1
            else:
                st.error(f"Wrong ❌ Correct: {q['answer']}")

            st.session_state.q_index += 1
            st.rerun()

    else:
        st.session_state.page = "result"
        st.rerun()


# =========================
# RESULT PAGE (VIRAL ENGINE)
# =========================
elif st.session_state.page == "result":

    st.title("🎉 Challenge Completed!")

    score = st.session_state.score
    total = len(st.session_state.questions)
    time_taken = int(time.time() - st.session_state.start_time)

    st.metric("Score", f"{score}/{total}")
    st.write(f"⏱️ Time: {time_taken}s")

    # Save leaderboard
    leaderboard.append({
        "user": st.session_state.user,
        "score": score,
        "time": time_taken
    })

    # VIRAL SHARE MESSAGE
    share_text = f"I scored {score}/{total} in CBT English Quiz! 🔥 Can you beat me?"

    st.subheader("📲 Share Challenge")
    st.code(share_text)

    st.success("Send this to your friends on WhatsApp!")

    # Leaderboard
    st.subheader("🏆 Leaderboard")

    sorted_board = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))

    for i, entry in enumerate(sorted_board[:5]):
        st.write(f"{i+1}. {entry['user']} - {entry['score']}")

    if st.button("Play Again 🔄"):
        st.session_state.page = "home"
        st.rerun()
