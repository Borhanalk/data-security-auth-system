import os
import sqlite3
import hashlib
from flask import (Flask,
                   render_template, request, redirect, url_for, session, flash)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

app = Flask(__name__)
app.secret_key = "secret-key"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def clear_users():
    conn = get_db_connection()
    conn.execute("DELETE FROM users")
    conn.commit()
    conn.close()


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
        """
    )
    conn.commit()
    conn.close()

    clear_users()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter username and password")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and user["password_hash"] == hash_password(password):
            session["username"] = user["username"]
            session["role"] = user["role"]
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("user"))

        flash("Wrong username or password")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            flash("All fields are required")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        conn = get_db_connection()
        user_count = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()[0]

        if user_count == 0:
            role = "admin"
            flash("You are the first user. Role set to admin.")
        else:
            role = "user"

        existing = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if existing:
            conn.close()
            flash("Username already exists")
            return redirect(url_for("register"))

        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        conn.close()

        flash("Account created!")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html", username=session.get("username"))

@app.route("/user")
def user():
    if session.get("role") != "user":
        return redirect(url_for("login"))
    return render_template("user.html", username=session.get("username"))

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            flash("Username is required")
            return redirect(url_for("forgot"))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if not user:
            flash("User not found")
            return redirect(url_for("forgot"))

        return redirect(url_for("reset", username=username))

    return render_template("forgot.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    username = request.args.get("username")
    if not username:
        flash("Missing username")
        return redirect(url_for("forgot"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not password or not confirm_password:
            flash("All fields are required")
            return redirect(url_for("reset", username=username))

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect(url_for("reset", username=username))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            conn.close()
            flash("User not found")
            return redirect(url_for("forgot"))

        conn.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_password(password), username))
        conn.commit()
        conn.close()

        flash("Password updated")
        return redirect(url_for("login"))

    return render_template("reset.html", username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
