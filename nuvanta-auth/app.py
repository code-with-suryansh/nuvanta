from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt
import uuid
import csv
import os
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "nuvanta_secret_key"

# ---------------- EMAIL CONFIG ---------------- #

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'namonuvanta@gmail.com'
app.config['MAIL_PASSWORD'] = 'wygu npml oenb zowj'

mail = Mail(app)

# ---------------- DATABASE ---------------- #

def create_db():

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    password BLOB,
    token TEXT,
    verified INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

create_db()

# ---------------- LOGIN LOGGING ---------------- #

def log_login(email, status):

    file_exists = os.path.isfile("login_logs.csv")

    with open("login_logs.csv", "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Email","Time","Status","IP"])

        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip = request.remote_addr

        writer.writerow([email,time,status,ip])

# ---------------- EMAIL SENDER ---------------- #

def send_verification_email(email, token):

    verify_link = f"http://127.0.0.1:5000/verify/{token}"

    msg = Message(
        "Verify your Nuvanta account",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.body = f"""
Click the link to verify your account:

{verify_link}
"""

    mail.send(msg)

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect("/login")

# -------- SIGNUP -------- #

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        token = str(uuid.uuid4())

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
        "INSERT INTO users(username,email,password,token) VALUES(?,?,?,?)",
        (username,email,hashed,token))

        conn.commit()
        conn.close()

        send_verification_email(email,token)

        return "Signup successful. Please check your email."

    return render_template("signup.html")

# -------- VERIFY EMAIL -------- #

@app.route("/verify/<token>")
def verify(token):

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE token=?", (token,))
    user = c.fetchone()

    if user is None:
        conn.close()
        return "Invalid verification link"

    c.execute("UPDATE users SET verified=1, token=NULL WHERE token=?", (token,))
    conn.commit()

    conn.close()

    return render_template("verified.html")

# -------- LOGIN -------- #

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT password, verified FROM users WHERE email=?", (email,))
        user = c.fetchone()

        conn.close()

        if user is None:
            log_login(email,"User not found")
            return "User not found"

        hashed_password = user[0]
        verified = user[1]

        if verified == 0:
            log_login(email,"Email not verified")
            return "Please verify your email first"

        if bcrypt.checkpw(password.encode(), hashed_password):

            session["user"] = email

            log_login(email,"Login success")

            return redirect("/dashboard")

        else:

            log_login(email,"Wrong password")

            return "Wrong password"

    return render_template("login.html")

# -------- DASHBOARD -------- #

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

# -------- LOGOUT -------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    app.run(debug=True)