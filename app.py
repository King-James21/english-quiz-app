import streamlit as st
import random
import time
from questions import questions
from auth import signup, login
from leaderboard import leaderboard
import json
import os

if "username" not in st.session_state:
    st.session_state.username = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "q_index" not in st.session_state:
    st.session_state.q_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0
# Initialize all session state variables at the start
if 'num_q' not in st.session_state:
    st.session_state.num_q = 10  # Default to 10 questions
if 'q_index' not in st.session_state:
    st.session_state.q_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'start_time' not in st.session_state:
    import time
    st.session_state.start_time = time.time() 
st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="Medical Quiz Pro", layout="centered")

st.title("Login System")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# SIGN UP
if choice == "Sign Up":
    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        success, msg = signup(username, password)
        if success:
            st.success(msg)
        else:
            st.error(msg)
    

    st.title("Create Account")

    username = st.text_input("New Username", key="signup_user")
    password = st.text_input("New Password", type="password", key="signup_pass")

    if st.button("Register"):
        success, msg = signup(username, password)
        st.success(msg)
        st.session_state.page = "login"
        st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


            # Check if the user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- SHOW LOGIN FORM ---
    
    if st.button("Login"):
        success, msg = login(username, password)
        if success:
            st.session_state.logged_in = True
            st.success(msg)
            st.rerun() # This refreshes the app to show the quiz
        else:
            st.error(msg)

if st.session_state.page == "login":

    st.title("Login System")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        success, msg = login(username, password)

        if success:
            st.session_state.page = "home"
            st.session_state.user = username
            st.rerun()
        else:
            st.error(msg)

    if st.button("Create Account"):
        st.session_state.page = "signup"
        st.rerun()
else:
    # --- SHOW QUIZ CONTENT HERE ---
    st.title("Welcome to the English Language Quiz!")
    st.write("You are now logged in.")
    # Your quiz code goes here...
# ---------------------------
# MAIN APP
# ---------------------------
    

    # START SCREEN
    if "started" not in st.session_state:
        st.session_state.started = False

    if not st.session_state.started:
        st.subheader("Choose quiz length")

        num_q = st.selectbox("Select:", [10, 15, 20])

    if st.button("Start Quiz"):
            st.session_state.started = True
            st.session_state.num_q = num_q
            st.session_state.score = 0
            st.session_state.q_index = 0
            st.session_state.start_time = time.time()

            st.session_state.questions = random.sample(questions, num_q)

            for q in st.session_state.questions:
                random.shuffle(q["options"])

            st.rerun()

    elif st.session_state.page == "home":

        st.title("Welcome to English Quiz")
        st.write(f"You are logged in as {st.session_state.user}")

    if st.button("Start Quiz"):
        st.session_state.page = "quiz"
        st.rerun()

    # QUIZ
    else:
        total_q = st.session_state.num_q
        current_q = st.session_state.q_index

        st.progress(current_q / total_q)

        elapsed = int(time.time() - st.session_state.start_time)
        st.write(f"⏱️ Time: {elapsed}s")
current_q = st.session_state.q_index
if current_q < len(st.session_state.questions):

    q = st.session_state.questions[current_q]

    st.subheader(f"Question {current_q + 1}/{total_q}")
    st.write(q["question"])

    selected = st.radio("Choose answer:", q["options"], key=current_q)

    if st.button("Submit"):
        if selected == q["answer"]:
            st.success("✅ Correct")
            st.session_state.score += 1
        else:
            st.error(f"❌ Correct: {q['answer']}")

        st.session_state.q_index += 1
        st.rerun()
    else:
        st.session_state.page == "quiz"

    st.subheader("Quiz Running...")

    # your quiz logic here

    if st.button("Finish Quiz"):
        st.session_state.page = "result"
        st.rerun()

        # RESULT
else:
            st.success("🎉 Completed!")
            total_q = len(st.session_state.questions)
            score = st.session_state.score
            st.metric("Score", f"{score}/{total_q}")

            if score >= total_q * 0.8:
                st.write("🔥 Excellent")
            elif score >= total_q * 0.5:
                st.write("👍 Good effort")
            else:
                st.write("📚 Revise more")
 else:
     st.session_state.page == "result"

    st.success("Completed!")

    st.write("Score here...")

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.rerun()
            elapsed = int(time.time() - st.session_state.start_time)
            st.write(f"⏱️ Time: {elapsed}s")

            # SAVE TO LEADERBOARD
            leaderboard.append({
                "user": st.session_state.username,
                "score": score,
                "time": elapsed
            })

            # SHOW LEADERBOARD
            st.subheader("🏆 Leaderboard")

            sorted_board = sorted(leaderboard, key=lambda x: (-x["score"], x["time"]))

            for i, entry in enumerate(sorted_board[:5]):
                st.write(f"{i+1}. {entry['user']} - {entry['score']} ({entry['time']}s)")

            # Restart
            if st.button("🔄 Play Again"):
                st.session_state.started = False
                st.rerun()
