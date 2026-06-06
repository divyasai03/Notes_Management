from flask import Flask, render_template, redirect, url_for, session, request
import sqlite3
import os  # <-- Added for absolute path handling
from werkzeug.security import generate_password_hash, check_password_hash

n = Flask(__name__)
n.secret_key = "my secrat key"

# --- FIX 1: Enforce Absolute Path so your script and terminal look at the exact same file ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "notes_management.db")

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                profile_name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                title TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (username) REFERENCES user_data(username)
            )
        """)
        conn.commit()

init_db()

@n.route("/")
def welcome():
    return render_template("login.html")

@n.route("/signup", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        p_name = request.form["profile_name"]
        
        with sqlite3.connect(DB_NAME) as conn:
            cursr = conn.cursor()
            cursr.execute("SELECT * FROM user_data WHERE username=?", (username,))
            data1 = cursr.fetchone()
            
            cursr.execute("SELECT * FROM user_data WHERE profile_name=?", (p_name,))
            data2 = cursr.fetchone()
            
            if data1:
                return render_template("register.html", info="username already exists plz try other")
            if data2:
                return render_template("register.html", info="profile name already used plz try other")
            
            hash_password = generate_password_hash(password)
            cursr.execute("INSERT INTO user_data(username, password, profile_name) VALUES(?, ?, ?)", (username, hash_password, p_name))
            conn.commit()
            
        return redirect(url_for("login"))
        
    return render_template("register.html")

@n.route("/signin", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        with sqlite3.connect(DB_NAME) as conn:
            cursr = conn.cursor()
            cursr.execute("SELECT username, password FROM user_data WHERE username=?", (username,))
            data = cursr.fetchone()

        if not data:
            return render_template("register.html", info="user not registered plz register first")
        
        if username == data[0] and check_password_hash(data[1], password):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", info="wrong password")

    return render_template("login.html")

@n.route("/dashboard", methods=["GET", "POST"])
@n.route("/dashboard/<title>/<mode>", methods=["GET", "POST"])
def dashboard(title=None, mode=None):
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session.get("username")
    notes_info = ("",)
    c_mode = ""

    with sqlite3.connect(DB_NAME) as conn:
        cursr = conn.cursor()
        cursr.execute("SELECT profile_name FROM user_data WHERE username=?;", (username,))
        data = cursr.fetchone()

        cursr.execute("SELECT title FROM notes WHERE username=?;", (username,))
        data1 = cursr.fetchall()

        if mode == "read":
            cursr.execute("SELECT notes FROM notes WHERE username=? AND title = ?;", (username, title))
            notes_info = cursr.fetchone() or ("",)
            c_mode = "read"

        elif mode == "update":
            cursr.execute("SELECT notes FROM notes WHERE username=? AND title = ?;", (username, title))
            notes_info = cursr.fetchone() or ("",)
            c_mode = "update"
        
        elif mode == "delete":
            cursr.execute("DELETE FROM notes WHERE username=? AND title = ?;", (username, title))
            conn.commit()
            return redirect(url_for("dashboard"))

    if data:
        return render_template("dashboard.html", profile_name=data[0], notes=data1, s_mode=c_mode, notes_info=notes_info[0], title=title)
    
    return redirect(url_for("welcome"))

@n.route("/notes_form", methods=["GET", "POST"])   
def notes_form():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session.get("username")
    if request.method == "POST":
        title = request.form["title"]
        notes = request.form["notes"]
        
        with sqlite3.connect(DB_NAME) as conn:
            cursr = conn.cursor()
            cursr.execute("SELECT title FROM notes WHERE username=?;", (username,))
            data = cursr.fetchall()

            if (title,) in data:
                return render_template("notes_form.html", re_notes=notes, info="title already exists plz use another", re_title=title)
            
            cursr.execute("INSERT INTO notes (username, title, notes) VALUES(?, ?, ?);", (username, title, notes))
            conn.commit()
            
        return redirect(url_for("dashboard"))

    return render_template("notes_form.html")

@n.route("/update_notes", methods=["GET", "POST"])
def update_notes():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session.get("username")
    if request.method == "POST":
        title = request.form["title"]
        u_notes = request.form["notes_update"]

        with sqlite3.connect(DB_NAME) as conn:
            cursr = conn.cursor()
            cursr.execute("UPDATE notes SET notes=? WHERE username=? AND title=?;", (u_notes, username, title))
            conn.commit()
            
            # 👇 DEBUG PRINT: Confirms exactly what data was written to the file
            print(f"\n[DB UPDATE SUCCESS] Title: '{title}' updated with new text: '{u_notes}'\n")
            
        # --- FIX 2: Redirect back to the READ view of that specific note so changes display immediately ---
        return redirect(url_for("dashboard", title=title, mode="read"))

@n.route("/logout")
def logout():
    if "username" not in session:
        return redirect(url_for("login"))
    
    session.clear()
    return redirect(url_for("welcome"))

if __name__ == "__main__":
    init_db()
    print("\n==================================================")
    print(f"👉 OPEN THIS DATABASE FILE: {DB_NAME}")
    print("==================================================\n")
    n.run(debug=True)