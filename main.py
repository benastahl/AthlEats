from flask import Flask, render_template, request, redirect
from controls import UserDB, AdminDB
# from validate_email_address import validate_email
from datetime import datetime

import bcrypt
import secrets

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        if UserDB().get_user(auth_token=auth_token):
            return redirect("/dashboard", 302)

    # Redirects back to log in if no auth token found
    return redirect("/login", 302)


@app.route("/dashboard", methods=["GET"])
def display_dashboard():

    # # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    # auth_token = request.cookies.get("auth_token")
    #
    # if not auth_token:
    #     # Redirects back to log in if no auth token found
    #     return redirect("/login", 302)
    #
    # # Checks to see if there's a corresponding user with auth token.
    # user = UserDB().get_user(auth_token=auth_token)
    # if not user:
    #     # Redirects back to log in if user not found
    #     return redirect("/login", 302)

    return render_template("dashboard.html", user=user)


@app.route("/login", methods=["GET"])
def display_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    email = request.form["email"]
    password = request.form["pass"]  # plain text password

    # login_user returns auth_token of user if email and password correct
    auth_token = UserDB().login_user(email, password)
    if not auth_token:
        return render_template("login.html", message="Password or email incorrect not found")

    response = redirect("/dashboard", 302)
    # Create an auth browser cookie (random letters and numbers) as our authentication
    # token so the user doesn't have to log in every single time.
    response.set_cookie('auth_token', auth_token, max_age=31540000)  # One year expiration (in seconds)

    return response


@app.route("/signup", methods=["GET"])
def display_signup():
    return render_template("signup.html")


@app.route("/admin-login", methods=["GET"])
def display_admin_login():
    return render_template("admin-login.html")


@app.route("/admin-login", methods=["POST"])
def process_admin_login():
    email = request.form["email"]
    password = request.form["pass"]

    admin = AdminDB().admin_login(email=email, password=password)
    if not admin:
        return redirect("/login", 302)

    response = redirect("/admin-dashboard", 302)
    response.set_cookie('admin_auth_token', admin.auth_token, max_age=60 * 60 * 24)  # 24 hour expiration (in seconds)

    return response


@app.route("/admin-dashboard", methods=["GET"])
def display_admin_dashboard():
    return render_template("admin-dashboard.html")


@app.route("/signup", methods=["POST"])
def process_signup():
    # Collect POST request params from signup
    tos_agree = request.form.get("tos-agree")
    email = request.form["email"]
    grade = int(request.form["grade"])
    # Hash password (hashing means that it is encrypted and impossible to decrypt)
    # We can now only check to see if a plain text input matches the hashed password (bcrypt.checkpw).
    hashed_password = bcrypt.hashpw(bytes(str(request.form["pass"]).encode("utf-8")), bcrypt.gensalt()).decode("utf-8")

    # Check if email is already in use (get_student returns list of users with that email).
    if UserDB().get_user(email=email):
        return render_template("signup.html", message="Email is already in use.")

    # Check if email is valid student email
    if "@student.waylandps.org" not in email:
        return render_template("signup.html", message="Not a valid WHS student email.")

    # Checks if email is a real valid email address
    # if not validate_email(email, verify=True):
    #     return render_template("signup.html", message="Not a real email address.")

    # Check to see if Terms of Service is agreed to
    if tos_agree != "on":
        return render_template("signup.html", message="Please agree to TOS to access the website.")

    # Set auth cookie token
    response = redirect("/dashboard", 302)

    # Create an auth browser cookie (random letters and numbers) as our authentication
    # token so the user doesn't have to log in every single time.
    auth_token = secrets.token_hex()
    response.set_cookie('auth_token', auth_token, max_age=31540000)  # One year expiration (in seconds)

    # Parse first and last name from email address.
    first_name = email.split("_")[0].capitalize()
    last_name = email.split("_")[1].split("@")[0].capitalize()

    # Create timestamp of the creation date of the account
    creation_date = int(datetime.timestamp(datetime.now()))

    # Add user to database
    UserDB().add_user(first_name=first_name, last_name=last_name, email=email, grade=grade,
                      hashed_password=hashed_password, auth_token=auth_token, creation_date=creation_date)

    return response


if __name__ == '__main__':
    app.run(debug=True)
