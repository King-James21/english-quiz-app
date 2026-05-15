import streamlit as st
import random, time, json

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CBT Quiz System", layout="centered")

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

# ---------------- LOAD DATA ----------------
analytics = load_json("analytics.json", [])
leaderboard = load_json("leaderboard.json", [])

# ---------------- SESSION ----------------
for key, val in {
    "page": "home",
    "score": 0,
    "q_index": 0,
    "questions": [],
    "start_time": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- HOME ----------------
if st.session_state.page == "home":

    st.title("CBT Quiz System")

    name = st.text_input("Enter Your Name")

    n = st.selectbox("Number of Questions", [5, 10, 15])

    if st.button("Start Quiz"):

        if not name:
            st.error("Please enter your name")
        else:
            from questions import questions

            st.session_state.user = name
            st.session_state.questions = random.sample(questions, n)
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.start_time = time.time()
            st.session_state.page = "quiz"

            st.rerun()

# ---------------- QUIZ ----------------
elif st.session_state.page == "quiz":

    i = st.session_state.q_index
    total = len(st.session_state.questions)

    st.write(f"Player: {st.session_state.user}")

    if i < total:

        q = st.session_state.questions[i]

        st.subheader(f"Question {i+1} of {total}")

        ans = st.radio(
            q["question"],
            q["options"],
            key=i
        )

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

    st.title("Quiz Result")

    st.metric("Score", f"{score}/{total}")

    analytics.append({
        "user": st.session_state.user,
        "score": score
    })

    save_json("analytics.json", analytics)

    share = f"{st.session_state.user} scored {score}/{total} in the CBT Quiz!"
    st.code(share)

    if st.button("Play Again"):
        st.session_state.page = "home"
        st.rerun()
