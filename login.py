
from flask import (
    Flask, request, redirect, url_for,
    render_template_string, session, flash
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

DATABASE = "users.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()


# ---------------- HTML + CSS ----------------

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title }} | Auth Portal</title>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #fff;
    background:
        radial-gradient(circle at 10% 15%, #273d76, transparent 36%),
        radial-gradient(circle at 90% 85%, #42245f, transparent 36%),
        #0b1020;
}

.card {
    width: 100%;
    max-width: 440px;
    padding: 38px;
    background: rgba(20, 28, 49, .96);
    border: 1px solid #303b56;
    border-radius: 22px;
    box-shadow: 0 25px 80px #0006;
}

.logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    margin-bottom: 25px;
    border-radius: 16px;
    background: linear-gradient(135deg, #7958ff, #438ef5);
    font-size: 28px;
    font-weight: 800;
}

.eyebrow {
    color: #a995ff;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 3px;
    margin-bottom: 10px;
}

h1 { font-size: 32px; margin-bottom: 10px; }

.subtitle {
    color: #a3aec5;
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 25px;
}

.group { margin-bottom: 19px; }

label {
    display: block;
    margin-bottom: 8px;
    color: #e0e6f3;
    font-size: 14px;
    font-weight: 600;
}

input {
    width: 100%;
    padding: 14px;
    border: 1px solid #34415f;
    border-radius: 10px;
    outline: none;
    color: white;
    background: #111a30;
    font-size: 14px;
}

input:focus {
    border-color: #927bff;
    box-shadow: 0 0 0 3px #927bff22;
}

button, .button {
    width: 100%;
    display: block;
    padding: 15px;
    margin-top: 7px;
    border: none;
    border-radius: 10px;
    text-align: center;
    text-decoration: none;
    color: white;
    background: linear-gradient(100deg, #7558f5, #478df5);
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    transition: .2s;
}

button:hover, .button:hover {
    transform: translateY(-2px);
    filter: brightness(1.1);
}

.message {
    padding: 12px;
    margin-bottom: 20px;
    border-radius: 9px;
    font-size: 13px;
    line-height: 1.5;
}

.success { color: #8af0bd; background: #22c55e1c; }
.error { color: #ff9b9b; background: #ef44441c; }

.bottom {
    margin-top: 23px;
    text-align: center;
    color: #a3aec5;
    font-size: 13px;
}

a { color: #a995ff; text-decoration: none; font-weight: 600; }
a:hover { text-decoration: underline; }

.footer {
    margin-top: 24px;
    text-align: center;
    color: #7886a2;
    font-size: 12px;
}

@media(max-width: 480px) {
    .card { padding: 27px 22px; }
    h1 { font-size: 28px; }
}
</style>
</head>

<body>
<div class="card">

    <div class="logo">B</div>

    {% if mode == 'login' %}
        <p class="eyebrow">WELCOME BACK</p>
        <h1>Sign in</h1>
        <p class="subtitle">Login with your registered account.</p>

    {% elif mode == 'register' %}
        <p class="eyebrow">GET STARTED</p>
        <h1>Create account</h1>
        <p class="subtitle">Join us by creating your account below.</p>

    {% else %}
        <p class="eyebrow">ACCOUNT</p>
        <h1>Welcome, {{ username }}!</h1>
        <p class="subtitle">You have successfully logged in.</p>
    {% endif %}

    {% for category, message in get_flashed_messages(with_categories=true) %}
        <div class="message {{ category }}" role="status">
            {{ message }}
        </div>
    {% endfor %}

    {% if mode == 'login' %}
        <form method="POST" action="{{ url_for('login') }}">
            <div class="group">
                <label for="username">Username</label>
                <input id="username" name="username"
                       placeholder="Enter username"
                       autocomplete="username" required>
            </div>

            <div class="group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password"
                       placeholder="Enter password"
                       autocomplete="current-password" required>
            </div>

            <button type="submit">Sign In →</button>
        </form>

        <p class="bottom">
            Don't have an account?
            <a href="{{ url_for('register') }}">Create an account</a>
        </p>

    {% elif mode == 'register' %}
        <form method="POST" action="{{ url_for('register') }}">
            <div class="group">
                <label for="username">Username</label>
                <input id="username" name="username"
                       placeholder="Choose a username"
                       minlength="3" maxlength="30"
                       autocomplete="username" required>
            </div>

            <div class="group">
                <label for="email">Email address</label>
                <input type="email" id="email" name="email"
                       placeholder="Enter your email"
                       maxlength="254" autocomplete="email" required>
            </div>

            <div class="group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password"
                       placeholder="At least 8 characters"
                       minlength="8" autocomplete="new-password" required>
            </div>

            <div class="group">
                <label for="confirm_password">Confirm password</label>
                <input type="password" id="confirm_password"
                       name="confirm_password"
                       placeholder="Enter password again"
                       minlength="8" autocomplete="new-password" required>
            </div>

            <button type="submit">Create Account →</button>
        </form>

        <p class="bottom">
            Already have an account?
            <a href="{{ url_for('login') }}">Sign in</a>
        </p>

    {% else %}
        <a class="button" href="{{ url_for('logout') }}">Logout</a>
    {% endif %}

    <p class="footer">Secure Access · Auth Portal</p>
</div>
</body>
</html>
"""


# ---------------- LOGIN PAGE ----------------

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template_string(
        PAGE, mode="login", title="Sign In"
    )


# ---------------- REGISTRATION PAGE ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not 3 <= len(username) <= 30:
            flash("Username must be 3 to 30 characters.", "error")

        elif any(char.isspace() for char in username):
            flash("Username cannot contain spaces.", "error")

        elif len(email) > 254 or not email or "@" not in email:
            flash("Please enter a valid email address.", "error")

        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        else:
            hashed_password = generate_password_hash(password)

            try:
                with get_db() as conn:
                    conn.execute(
                        """
                        INSERT INTO users (username, email, password)
                        VALUES (?, ?, ?)
                        """,
                        (username, email, hashed_password)
                    )

                flash(
                    "Account created successfully! Please sign in.",
                    "success"
                )
                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                flash(
                    "Username or email already exists. Please try another.",
                    "error"
                )

    return render_template_string(
        PAGE, mode="register", title="Create Account"
    )


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        flash("Please sign in to continue.", "error")
        return redirect(url_for("login"))

    return render_template_string(
        PAGE,
        mode="dashboard",
        title="Dashboard",
        username=session.get("username")
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
