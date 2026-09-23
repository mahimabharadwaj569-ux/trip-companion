from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================================
# CREATE FLASK APPLICATION
# ==========================================================

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "trip_companion_secret_key_2026"

# SQLite database file
DATABASE = "trip_companion.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================================
# CREATE DATABASE TABLE
# ==========================================================

def create_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            phone TEXT NOT NULL,

            password TEXT NOT NULL,

            travel_preference TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================================
# REGISTER / CREATE ACCOUNT
# ==========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        phone = request.form["phone"]

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        travel_preference = request.form["travel_preference"]


        # Check password confirmation
        if password != confirm_password:

            flash(
                "Passwords do not match!",
                "error"
            )

            return redirect(
                url_for("register")
            )


        # Connect to database
        connection = get_db()


        # Check whether email already exists
        existing_user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()


        if existing_user:

            connection.close()

            flash(
                "This email is already registered!",
                "error"
            )

            return redirect(
                url_for("register")
            )


        # Securely hash password
        hashed_password = generate_password_hash(
            password
        )


        # Insert new user
        connection.execute("""
            INSERT INTO users
            (
                name,
                email,
                phone,
                password,
                travel_preference
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            hashed_password,
            travel_preference
        ))


        connection.commit()

        connection.close()


        flash(
            "Account created successfully!",
            "success"
        )


        # Go to LOGIN
        return redirect(
            url_for("login")
        )


    return render_template(
        "register.html"
    )


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        connection = get_db()


        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()


        connection.close()


        # Check login details
        if user and check_password_hash(
            user["password"],
            password
        ):

            # Store user ID in session
            session["user_id"] = user["id"]


            # Go to Dashboard
            return redirect(
                url_for("dashboard")
            )


        flash(
            "Invalid email or password!",
            "error"
        )


    return render_template(
        "login.html"
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    # Check whether user is logged in
    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()


    connection.close()


    return render_template(
        "dashboard.html",
        user=user
    )


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]


        connection = get_db()


        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()


        connection.close()


        if user:

            # Store user temporarily
            # for college-project reset process
            session["reset_user"] = user["id"]


            return redirect(
                url_for("reset_password")
            )


        flash(
            "Email address not found!",
            "error"
        )


    return render_template(
        "forgot_password.html"
    )


# ==========================================================
# RESET PASSWORD
# ==========================================================

@app.route(
    "/reset-password",
    methods=["GET", "POST"]
)
def reset_password():

    # User must come through Forgot Password
    if "reset_user" not in session:

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]


        # Check passwords
        if password != confirm_password:

            flash(
                "Passwords do not match!",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )


        # Hash new password
        hashed_password = generate_password_hash(
            password
        )


        connection = get_db()


        connection.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (
            hashed_password,
            session["reset_user"]
        ))


        connection.commit()

        connection.close()


        # Remove reset session
        session.pop(
            "reset_user"
        )


        flash(
            "Password reset successfully!",
            "success"
        )


        # Go back to Login
        return redirect(
            url_for("login")
        )


    return render_template(
        "reset_password.html"
    )


# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()


    connection.close()


    return render_template(
        "profile.html",
        user=user
    )


# ==========================================================
# EDIT PROFILE
# ==========================================================

@app.route(
    "/edit-profile",
    methods=["GET", "POST"]
)
def edit_profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db()


    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()


    if request.method == "POST":

        name = request.form["name"]

        phone = request.form["phone"]

        travel_preference = request.form[
            "travel_preference"
        ]


        connection.execute("""
            UPDATE users

            SET
                name = ?,
                phone = ?,
                travel_preference = ?

            WHERE id = ?
        """, (
            name,
            phone,
            travel_preference,
            session["user_id"]
        ))


        connection.commit()

        connection.close()


        flash(
            "Profile updated successfully!",
            "success"
        )


        return redirect(
            url_for("profile")
        )


    connection.close()


    return render_template(
        "edit_profile.html",
        user=user
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
def logout():

    # Remove login session
    session.clear()


    flash(
        "You have been logged out successfully!",
        "success"
    )


    return redirect(
        url_for("login")
    )


# ==========================================================
# START APPLICATION
# ==========================================================

if __name__ == "__main__":

    # Create database and table
    create_database()

    # Start Flask server
    app.run(
        debug=True
    )