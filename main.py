from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from controls import UserDB
from orders_controls import OrdersDB
import calendar
from datetime import datetime
import os

import bcrypt
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'./receipts'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]


@app.route("/", methods=["GET"])
def home():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UserDB().get_user(auth_token=auth_token)
        return render_template("home.html", user=user)

    # Redirects back to log in if no auth token found
    return render_template("home.html", user=False)


def process_login(_request):
    email = _request.form["email"]
    password = _request.form["pass"]  # plain text password

    # login_user returns auth_token of user if email and password correct
    auth_token = UserDB().login_user(email, password)
    if not auth_token:
        return render_template("home.html", message_type="login", message="Password or email incorrect not found")

    response = redirect("/", 302)
    # Create an auth browser cookie (random letters and numbers) as our authentication
    # token so the user doesn't have to log in every single time.
    response.set_cookie('auth_token', auth_token, max_age=31540000)  # One year expiration (in seconds)
    return response


def process_signup(_request):
    # Collect POST request params from signup
    tos_agree = _request.form.get("tos")
    email = _request.form["email"]
    grade = int(_request.form["grade"])
    # Hash password (hashing means that it is encrypted and impossible to decrypt)
    # We can now only check to see if a plain text input matches the hashed password (bcrypt.checkpw).
    hashed_password = bcrypt.hashpw(bytes(str(_request.form["pass"]).encode("utf-8")), bcrypt.gensalt()).decode("utf-8")

    # Check if email is already in use (get_student returns list of users with that email).
    if UserDB().get_user(email=email):
        return render_template("home.html", message_type="signup", message="Email is already in use.")

    # Check if email is valid student email
    if "@student.waylandps.org" not in email:
        return render_template("home.html", message_type="signup", message="Not a valid WHS student email.")

    # Checks if email is a real valid email address
    # if not validate_email(email, verify=True):
    #     return render_template("signup.html", message="Not a real email address.")

    # Check to see if Terms of Service is agreed to
    if tos_agree != "agree":
        return render_template("home.html", message_type="signup", message="Please agree to TOS to access the website.")

    # Set auth cookie token
    response = redirect("/", 302)

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
    UserDB().add_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        grade=grade,
        hashed_password=hashed_password,
        auth_token=auth_token,
        creation_date=creation_date,
        staff=0,
        admin=0
    )

    return response


@app.route("/", methods=["POST"])
def process_homepage():
    if "tos" in request.form:
        return process_signup(_request=request)
    else:
        return process_login(_request=request)


@app.route("/reserve-calendar", methods=["GET"])
def display_reserve_calendar():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if not auth_token:
        return redirect("/", 302)
    # Checks to see if there's a corresponding user with auth token.
    user = UserDB().get_user(auth_token=auth_token)

    now = datetime.now()

    month_name = months[now.month - 1].upper()
    month = months.index(month_name.lower()) + 1
    year = now.year

    day = now.day

    first_weekday, past_month_days = calendar.monthrange(year, month - 1)
    first_weekday, num_days_in_month = calendar.monthrange(year, month)
    next_month_weekday, next_month_days = calendar.monthrange(year, month + 1)

    weekends = [day_num + 1 for day_num in range(num_days_in_month) if
                datetime(year, month, day_num + 1).isoweekday() in [6, 7]]
    print(weekends)

    available_time_format = {

    }

    return render_template("reserve_calendar.html",
                           user=user,

                           # Calendar data
                           month_name=month_name,
                           month=month,
                           year=year,
                           day=day,

                           weekends=weekends,
                           past_month_days=past_month_days,
                           num_days_in_month=num_days_in_month,
                           next_month_weekday=next_month_weekday,
                           first_weekday=first_weekday,

                           available_days=["1", "9", "20"]
                           )


@app.route("/reserve-form", methods=["GET"])
def display_reserve_form():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UserDB().get_user(auth_token=auth_token)
        if user:
            return render_template("reserve_form.html", user=user)

    return redirect("/", 302)


@app.route("/reserve-form", methods=["POST"])
def process_reserve_form():
    first_name = request.form['reserve-first-name']
    last_name = request.form['reserve-last-name']
    price = request.form['input-dollar']
    receipt = request.files['receipt']
    pickup_time = request.form['pickup']
    fee = int(price) * .3

    filename = secure_filename(receipt.filename)
    receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('download_file', name=filename))


@app.route("/staff-dashboard", methods=["GET"])
def display_staff_dashboard():
    auth_token = request.cookies.get("auth_token")
    user = UserDB().get_user(auth_token=auth_token)

    if not user or not user.__repr__() in ["Staff", "Admin"]:
        return redirect("/", 302)

    return render_template("staff-dashboard.html", user=user)


@app.route("/admin-dashboard", methods=["GET"])
def display_admin_dashboard():
    auth_token = request.cookies.get("auth_token")
    user = UserDB().get_user(auth_token=auth_token)

    if not user or not user.__repr__() in ["Admin"]:
        return redirect("/", 302)

    return render_template("admin-dashboard.html", user=user)


@app.route("/profile", methods=["GET"])
def display_profile():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UserDB().get_user(auth_token=auth_token)
        if user:
            return render_template("profile.html", user=user)

    return redirect("/", 302)


@app.route("/logout", methods=["GET"])
def logout():
    # Remove auth token cookie
    response = redirect("/", 302)
    response.set_cookie("auth_token", "", expires=0)

    return response


if __name__ == '__main__':
    app.run(debug=True, port=4949)

# ADMIN USER: UserDB().edit_user(email="wesley_tse@student.waylandps.org", password="wps200423", admin=1)
# STAFF USER: UserDB().edit_user(email="wesley_tse@student.waylandps.org", password="wps200423", staff=1)
