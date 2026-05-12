import json
import os

USER_FILE = "users.json"


# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)


# Save users
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


# Sign up
def signup(username, password):
    users = load_users()

    if username in users:
        return False, "User already exists"

    users[username] = password
    save_users(users)
    return True, "Account created successfully"


# Login
def login(username, password):
    users = load_users()

    if username not in users:
        return False, "User not found"

    if users[username] != password:
        return False, "Wrong password"

    return True, "Login successful"