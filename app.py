import uuid
from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from controls import UsersCloud, OrdersCloud

from account_authority import Order
import calendar
from datetime import datetime, date
import os

import bcrypt
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'./receipts'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER",
          "DECEMBER"]
error_handles = {
    500: {
        "name": "Internal Server Error (500)",
        "message": "Something wrong happened on our end. The error has been logged and will be reviewed."
    },
    404: {
        "name": "Page not Found (404)",
        "message": "This page was not found."
    }
}

# for handle in error_handles.items():
#     # Sets redirect for custom error pages.
#     status_code = handle[0]
#     app.register_error_handler(
#         status_code,
#         lambda x: render_template(
#             "error-page.html",
#             error_name=handle[1]["name"],
#             error_msg=handle[1]["message"]
#         )
#     )


# @app.before_request
# def before_request():
#     if "127" not in str(request.url) or "localhost" not in str(request.url):
#         if not request.is_secure:
#             url = request.url.replace('http://', 'https://', 1)
#             code = 301
#             return redirect(url, code=code)


@app.route("/", methods=["GET"])
def home():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UsersCloud().get_entry(auth_token=auth_token)
        return render_template("home.html", user=user)

    # Redirects back to log in if no auth token found
    return render_template("home.html", user=False)


def process_login(_request):
    email = _request.form["email"]
    password = _request.form["pass"]  # plain text password

    # login_user returns auth_token of user if email and password correct
    auth_token = UsersCloud().login_user(email, password)
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
    if UsersCloud().get_entry(email=email):
        return render_template("home.html", message_type="signup", message="Email is already in use.")

    # Check if email is valid student email
    if "waylandps.org" not in email:
        return render_template("home.html", message_type="signup", message="Not a valid WHS email.")

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

    # Create timestamp of the creation date of the account
    creation_date = int(datetime.timestamp(datetime.now()))

    # Add user to database
    UsersCloud().create_entry(
        entry_id=uuid.uuid4(),
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
    month_name = request.args.get("month")

    if not auth_token:
        return redirect("/", 302)

    # Checks to see if there's a corresponding user with auth token.
    user = UsersCloud().get_entry(auth_token=auth_token)

    now = datetime.now()
    if not month_name:
        month_name = months[now.month - 1].upper()

    month = months.index(month_name.upper()) + 1
    year = now.year

    day = now.day

    first_weekday, past_month_days = calendar.monthrange(year, month - 1)
    first_weekday, num_days_in_month = calendar.monthrange(year, month)
    next_month_weekday, next_month_days = calendar.monthrange(year, 1)
    if month + 1 != 13:
        next_month_weekday, next_month_days = calendar.monthrange(year, month + 1)

    weekends = [day_num + 1 for day_num in range(num_days_in_month) if
                datetime(year, month, day_num + 1).isoweekday() in [6, 7]]
    print(weekends)
    month_names = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

    available_days = {
        10: {
            "runner_entry_id": "",
        },
        15: {

        },
        20: {

        }
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

                           available_days=available_days
                           )


@app.route("/reserve-form", methods=["GET"])
def display_reserve_form():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    reserve_date = request.args.get("reserve_date")
    if not date:
        return redirect("/reserve-calendar", 302)

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UsersCloud().get_entry(auth_token=auth_token)
        if user:
            return render_template("reserve_form.html", user=user)

    return redirect("/", 302)


@app.route("/reserve-form", methods=["POST"])
def process_reserve_form():
    email = str(request.form['user_email'])
    price = str(request.form['input-dollar'])
    receipt = request.files['receipt-upload']
    restaurant = request.form['restaurant']
    phone_number = request.form['phone-number']
    restaurant_pickup_time = str(request.form['restaurant-pickup-time'])
    pickup_time = str(request.form['pickup'])
    pickup_location = request.form['pickup-location']
    order_date = datetime.now().strftime("%D %H:%M:%S")
    fee = round(float(price) * 0.3, 2)

    OrdersCloud().create_entry(
        entry_id=str(uuid.uuid4()),
        is_complete=0,
        email=email,
        restaurant=restaurant,
        order_date=order_date,
        phone_number=phone_number,
        restaurant_pickup_time=restaurant_pickup_time,
        pickup_time=pickup_time,
        price=price,
        pickup_location=pickup_location

    )

    auth_token = request.cookies.get("auth_token")

    if auth_token:
        user = UsersCloud().get_entry(auth_token=auth_token)
        if user:
            return render_template("order-complete.html", user=user, pickup_time=pickup_time,
                                   pickup_location=pickup_location, fee=fee)

    return redirect("/", 302)


@app.route("/order-reserved", methods=["GET"])
def display_complete_form():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UsersCloud().get_entry(auth_token=auth_token)
        if user:
            return render_template("order-complete.html", user=user)

    return redirect("/", 302)


@app.route("/staff-dashboard", methods=["GET"])
def display_staff_dashboard():
    auth_token = request.cookies.get("auth_token")
    user = UsersCloud().get_entry(auth_token=auth_token)

    if not user.staff or not user.admin:
        return redirect("/", 302)

    return render_template("staff-dashboard.html", user=user)


@app.route("/admin-dashboard", methods=["GET"])
def display_admin_dashboard():
    auth_token = request.cookies.get("auth_token")
    user = UsersCloud().get_entry(auth_token=auth_token)
    orders_list = OrdersCloud().get_all_entries()
    user_list = UsersCloud().get_all_entries()
    incomplete_orders = []
    completed_orders = []
    staff_list = []
    for order in orders_list:
        if order.is_complete == 0:
            incomplete_orders.append(order)
        else:
            completed_orders.append(order)

    for user1 in user_list:
        if user1.staff == 1:
            staff_list.append(user1)

    if not user or not user.admin:
        return redirect("/", 302)

    return render_template("admin-dashboard.html", user=user, incomplete_orders=incomplete_orders,
                           completed_orders=completed_orders, user_list=user_list, staff_list=staff_list)


@app.route("/admin-dashboard", methods=["POST"])
def process_complete_order():
    if request.form.get('complete-order') == 'complete-order-value':
        entry_id = request.form.get("index")
        order_db = OrdersCloud()
        order_db.edit_entry(entry_id=entry_id, is_complete=1)

    return redirect("/admin-dashboard", 302)


@app.route("/profile", methods=["GET"])
def display_profile():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    if auth_token:
        # Checks to see if there's a corresponding user with auth token.
        user = UsersCloud().get_entry(auth_token=auth_token)
        if user:
            orders_list = OrdersCloud().get_all_entries()
            user_orders_list = []
            for order in orders_list:
                if order.email == user.email:
                    user_orders_list.append(order)

            return render_template("profile.html", user=user, user_order_list=user_orders_list)

    return redirect("/", 302)


@app.route("/logout", methods=["GET"])
def logout():
    # Remove auth token cookie
    response = redirect("/", 302)
    response.set_cookie("auth_token", "", expires=0)

    return response


if __name__ == '__main__':
    app.run(debug=True, port=4949)
