import json
import bcrypt

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# -----------------------
# SIGNUP
# -----------------------
def signup(username, password):
    users = load_users()

    if username in users:
        return False, "User already exists"

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    users[username] = {
        "password": hashed
    }

    save_users(users)

    return True, "Account created"

# -----------------------
# LOGIN
# -----------------------
def login(username, password):
    users = load_users()

    if username not in users:
        return False, "User not found"

    stored_hash = users[username]["password"].encode()

    if bcrypt.checkpw(password.encode(), stored_hash):
        return True, "Login successful"
    else:
        return False, "Wrong password"
