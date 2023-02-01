import base64
import copy
import json
import random
import uuid
import bcrypt
import secrets
import traceback
import smtplib

from werkzeug.exceptions import HTTPException
from email.message import EmailMessage
from email.utils import formataddr
from flask import Flask, render_template, request, redirect, session, abort
from controls import AthlEatsDatabase, google_app_password, flask_secret_password
from datetime import datetime
import image_processing

app = Flask(__name__)
app.secret_key = flask_secret_password
error_handles = {
    404: {
        "name": "Page not found (404)",
        "message": "This page was not found."
    },
    403: {
        "name": "Access Denied (403)",
        "message": "You do not have permissions to access this resource."
    },
    429: {
        "name": "Too many connections (429)",
        "message": "We are experiencing a lot of traffic right now. Please try again in a bit.",
    },
    500: {
        "name": "Internal Server Error (500)",
        "message": "Something wrong happened on our end. The error has been logged and will be reviewed."
    },

}
sport_teams = {
    "fall": [
        # Fall Sports
        "Cross Country",
        "Field Hockey",
        "Football",
        "Golf",
        "Boys Soccer",
        "Girls Soccer",
        "Girls Volleyball",
    ],
    "winter": [
        # Winter Sports
        "Boys Basketball",
        "Girls Basketball",
        "Girls Hockey",
        "Boys Hockey",
        "Indoor Track",
        "Ski",
        "Swimming/Dive",
        "Wrestling",
    ],
    "spring": [
        # Spring Sports
        "Baseball",
        "Boys Lacrosse",
        "Girls Lacrosse",
        "Outdoor Track",
        "Boys Tennis",
        "Girls Tennis",
        "Boys Volleyball",
        "Softball",
    ]
}
sport_season = "winter"  # Change to season (fall, winter, spring). Case sensitive.

# locations
LOCATIONS = {
    "Panera": 1,
    "Chipotle": 1,
    "Five-Guys": 1,
    "McDonalds": 2,
    "Chick-Fil-A": 2,
    "Wayland-Pizza-House": 3,
    "Dunkin Donuts": 4
}


# Fee calculator
def calculate_fees(price) -> float:
    return round(float(price) * 0.35, 2)


def send_email(sender_name, recipient, subject, body):
    em = EmailMessage()
    em["From"] = formataddr((sender_name, "athleats.wayland@gmail.com"))
    em["To"] = recipient
    em["Subject"] = subject
    em.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("athleats.wayland@gmail.com", google_app_password)
        smtp.sendmail("athleats.wayland@gmail.com", recipient, em.as_string())


# Do not touch thanks <3
# @app.before_request
# def coconut_malld():
#     return render_template("coconut.html")


@app.errorhandler(Exception)
def handle_outlier_exceptions(e):
    exception = traceback.TracebackException.from_exception(e)
    ending_cause = exception.stack[len(exception.stack) - 1]

    exception_data = {
        "exception_type": exception.exc_type,
        "exception_desc": exception.__dict__['_str'],
        "lineno": ending_cause.lineno,
        "filename": ending_cause.filename
    }

    # return error data
    for name, details in exception_data.items():
        print(f"{name} -> {details}")
    data = {
        "code": 500,
        "name": "Internal Server Error",
        "description": exception_data,
    }
    return render_template(
        "error-page.html",
        error_data=data
    )


@app.errorhandler(HTTPException)
def handle_exceptions(e):
    data = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    return render_template(
        "error-page.html",
        error_data=data
    )


@app.route("/", methods=["GET"])
def home():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    signup_error = request.args.get("signup_error")
    login_error = request.args.get("login_error")
    confirmation_mode = request.args.get("confirmation_mode")
    reset_password_mode = request.args.get("reset_password_mode")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

    # Returns user whether it can find auth token or not. Displays signup and login buttons if user=False.
    return render_template("home.html",
                           user=user,
                           login_error=login_error,
                           signup_error=signup_error,
                           confirmation_mode=confirmation_mode,
                           reset_password_mode=reset_password_mode,
                           sport_season=sport_season,
                           sport_teams=sport_teams.get(sport_season)
                           )


@app.route("/login", methods=["POST"])
def process_login():
    email = request.form["email"]
    password = request.form["pass"]  # plain text password

    database = AthlEatsDatabase()
    with database:
        # login_user returns auth_token of user if email and password correct
        auth_token = database.login_user(email, password)

    if not auth_token:
        return redirect("/?login_error=Email or password not found", 302)

    response = redirect("/", 302)
    # Create an auth browser cookie (random letters and numbers) as our authentication
    # token so the user doesn't have to log in every single time.
    response.set_cookie('auth_token', auth_token, max_age=60 * 60 * 24 * 365)  # One year expiration (in seconds)
    return response


@app.route("/signup", methods=["POST"])
def process_signup():
    # Collect POST request params from signup
    tos_agree = request.form.get("tos")
    email = request.form["email"]
    grade = int(request.form["grade"])
    sport_team = request.form['sport_team']
    confirmation_mode = request.args.get("confirmation_mode")

    # Hash password (hashing means that it is encrypted and impossible to decrypt)
    # We can now only check to see if a plain text input matches the hashed password (bcrypt.checkpw).
    hashed_password = bcrypt.hashpw(bytes(str(request.form["pass"]).encode("utf-8")), bcrypt.gensalt()).decode("utf-8")

    # Check if email is valid student email
    if "waylandps.org" not in email or "_" not in email:
        return redirect("/?signup_error=Not a valid WHS email.")

    # Checks if email is a real valid email address
    # if not validate_email(email, verify=True):
    #     return render_template("signup.html", message="Not a real email address.")

    # Check to see if Terms of Service is agreed to
    if tos_agree != "agree":
        return redirect("/?signup_error=Please agree to TOS to access the website.")

    auth_token = secrets.token_hex()

    # Create timestamp of the creation date of the account
    creation_date = int(datetime.timestamp(datetime.now()))

    # Check if email is already in use (get_student returns list of users with that email).
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", email=email)

        if user:
            return redirect("/?signup_error=Email is already in use.")

        # Add user to database
        user = database.create_entry(
            table_name="users",
            entry_id=uuid.uuid4(),
            email=email,
            grade=grade,
            hashed_password=hashed_password,
            auth_token=auth_token,
            creation_date=creation_date,
            staff=0,
            admin=0,
            sport_team=sport_team
        )

    # Set auth cookie token
    response = redirect("/?confirmation_mode=true", 302)

    # Create an auth browser cookie (random letters and numbers) as our authentication
    # token so the user doesn't have to log in every single time.
    response.set_cookie('auth_token', auth_token, max_age=31540000)  # One year expiration (in seconds)

    # user_data = {
    #     "email": email,
    #     "grade": grade,
    #     "hashed_password": hashed_password,
    #     "auth_token": auth_token,
    #     "sport_team": sport_team
    # }
    # data_as_string = json.dumps(user_data)
    # session["user_data"] = data_as_string

    # Hash verification code and set it as a session value. When the user inputs a verification code,
    # it will be checked it against the hashed session value.
    # verification_code = str(random.randint(100000, 999999))
    # session['verifCode'] = bcrypt.hashpw(bytes(str(verification_code).encode("utf8")), bcrypt.gensalt()).decode("utf8")

    send_email(
        sender_name="WHS AthlEats",
        recipient="athleats.wayland@gmail.com",
        subject=f"SIGNUP ALERT: {user.first_name.capitalize()} {user.last_name.capitalize()}",
        body=f"""

        A new user has just signed up:
        {user.email}
        {user.year_name}
        {user.sport_team}

        """
    )

    # send_email(sender_name="WHS AthlEats",
    #            recipient=email,
    #            subject=f"ATHLEATS SIGNUP VERIFICATION",
    #            body=f"""
    #
    #             Verification Code: {verification_code}
    #
    #             """)

    return response


@app.route("/confirm-signup", methods=["POST"])
def confirm_signup():
    auth_token = request.cookies.get("auth_token")
    code = request.form["confirm"]

    stored_code = session['verifCode']

    if bcrypt.checkpw(bytes(code.encode("utf8")), bytes(stored_code.encode("utf8"))):
        return redirect("/?confirm_error=Verification code is incorrect.")

    user_data = json.loads(session["user_data"])

    # Create timestamp of the creation date of the account
    creation_date = int(datetime.timestamp(datetime.now()))

    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", email=user_data["email"])

        if user:
            return redirect("/?signup_error=Email is already in use.")

        # Add user to database
        user = database.create_entry(
            table_name=user_data["users"],
            entry_id=uuid.uuid4(),
            email=user_data["email"],
            grade=user_data["grade"],
            hashed_password=user_data["hashed_password"],
            auth_token=user_data["auth_token"],
            creation_date=creation_date,
            staff=0,
            admin=0,
            sport_team=user_data["sport_team"]
        )
    return redirect("/")


@app.route("/password-recovery", methods=["POST"])
def password_recovery():
    auth_token = request.cookies.get("auth_token")
    email = request.form["email"]

    database = AthlEatsDatabase()
    with database:
        # login_user returns auth_token of user if email and password correct
        user = database.get_entry(table_name="users", email=email, auth_token=auth_token)

    if not user:
        return redirect("/?signup_error=Email not found")

    # make OTP for password reset
    one_time_password = str(random.randint(1000000000, 9999999999))

    # store all necessary information for reset_password() in session variables
    session["password_creation_time"] = int(datetime.timestamp(datetime.now()))
    session["reset_password_for_email"] = email
    session["hashed_OTP"] = bcrypt.hashpw(bytes(str(one_time_password).encode("utf8")), bcrypt.gensalt()).decode("utf8")

    # sends email to recipient with OTP
    send_email(sender_name="WHS AthlEats",
               recipient=email,
               subject=f"Password Reset",
               body=f"""
                    
                    One time passord: {one_time_password}
                    This temporary password expires in 10 minutes.
                    If you did not make this request or this was a mistake please ignore this email.
                """)

    return redirect("/?reset_password_mode=true")


@app.route("/reset-password", methods=["POST"])
def reset_password():
    email = request.form["email"]
    one_time_password = request.form["one time password"]  # one time password
    password = request.form["new password"]  # new password
    auth_token = request.cookies.get("auth_token")

    # confirm emails are the same
    if email != session["reset_password_for_email"]:
        return redirect("/?reset_password_error=emails do not match for password reset", 302)

    # confirm OTP has not expired
    current_time = int(datetime.timestamp(datetime.now()))
    if current_time - session["password_creation_time"] >= 600:
        return redirect("/?reset_password_error=OTP expired", 302)

    # confirm OTP is correct
    if not bcrypt.checkpw(bytes(one_time_password.encode("utf8")), bytes(session["hashed_OTP"].encode("utf8"))):
        return redirect("/?reset_password_error=Incorrect OTP", 302)

    # hashes new password and saves it to user in the database
    new_password = str(bcrypt.hashpw(bytes(str(password).encode("utf-8")), bcrypt.gensalt()).decode("utf-8"))
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", email=email, auth_token=auth_token)
        # change user password
        database.edit_entry(table_name="users", entry_id=user.entry_id, hashed_password=new_password)

    return redirect("/")


@app.route("/reserve-calendar", methods=["GET"])
def display_reserve_calendar():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

        if not user:
            return redirect("/", 302)

        # Clear all outdated availabilities.
        database.clear_old_availabilities()

        availabilities = database.get_all_entries(table_name="runner_availabilities")

        # make a subset of the list with non completed availabilities
        true_availability = []
        # Format time in table
        for avail in availabilities:
            avail.date_string = avail.date.strftime("%A, %m/%d/%y")
            if not avail.is_complete:
                true_availability.append(avail)

    return render_template("new_reserve_calendar.html",
                           user=user,
                           availabilities=true_availability,

                           )


@app.route("/reserve-form", methods=["GET"])
def display_reserve_form():
    auth_token = request.cookies.get("auth_token")
    entry_id = request.args.get("availability")

    database = AthlEatsDatabase()
    with database:
        availability = database.get_entry(table_name="runner_availabilities", entry_id=entry_id)
        user = database.get_entry(table_name="users", auth_token=auth_token)



    if not availability:
        return redirect("/reserve-calendar", 302)
    if not user:
        return redirect("/", 302)
    if availability.location is not None and availability.location != 0:
        return render_template("reserve_form.html",
                               user=user,
                               location=availability.location,
                               block=availability.block
                               )
    else:
        return render_template("reserve_form.html",
                               user=user,
                               location=0,
                               block=availability.block
                               )


@app.route("/reserve-form", methods=["POST"])
def process_reserve_form():
    receipt = request.files['receipt-upload']
    availability_entry_id = request.args.get("availability")
    auth_token = request.cookies.get("auth_token")

    compressed_image = image_processing.compress_file(receipt)
    order_entry_id = str(uuid.uuid4())

    # file byte stream of compressed image to be uploaded and name
    receipt_id = image_processing.upload(compressed_image, order_entry_id)
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)
        if not user:
            return redirect("/", 302)

        # Checks if availability is valid/real and still available (not reserved)
        availability = database.get_entry(table_name="runner_availabilities", entry_id=availability_entry_id)

        if availability.location is not None and availability.location != 0:
            if availability.location != LOCATIONS[request.form['restaurant']]:
                return redirect("/reserve-calendar", 302)
        # Set reserved status of availability to true.
        if availability.order_entry_id == '':
            full_order_entry_id = order_entry_id
        else:
            full_order_entry_id = f"{availability.order_entry_id},{order_entry_id}"
        database.edit_entry(table_name="runner_availabilities", entry_id=availability_entry_id, reserved=1,
                            order_entry_id=full_order_entry_id, location=LOCATIONS[request.form['restaurant']])

        # Collect runner user instance
        runner = database.get_entry(table_name="users", entry_id=availability.runner_entry_id)

        sport_team = str(request.form.get("sports-team"))  # TODO: Sports team leaderboard
        price = str(request.form['input-dollar'])
        fee = calculate_fees(price)
        print("--------{}-----".format(type(str(request.form['pickup-location']))))
        order = database.create_entry(
            table_name="orders",
            entry_id=order_entry_id,
            availability_entry_id=availability_entry_id,
            runner_entry_id=availability.runner_entry_id,
            is_complete=0,
            email=str(request.form['user_email']),
            restaurant=request.form['restaurant'],
            order_date=datetime.now().strftime("%D %H:%M:%S"),
            phone_number=request.form['phone-number'],
            restaurant_pickup_time=str(request.form['restaurant-pickup-time']),
            price=price,
            pickup_name=request.form['pickup-name'],
            pickup_location= str(request.form['pickup-location']),
            receipt_id=receipt_id,
            location=LOCATIONS[request.form['restaurant']],
            pickup_time=str(request.form['pickup-time'])
        )


    send_email(
        sender_name="WHS AthlEats Deliveries",
        recipient=runner.email,
        subject="ALERT: Delivery Scheduled",
        body=f"""
        
        An availability you have created has been scheduled for a reservation!
        Set a reminder or alert for yourself so you do not forget.
        
        Click this link or go to your staff dashboard for more details about the order:
        https://www.athleats.app/order/{order_entry_id}
        
        """
    )
    send_email(
        sender_name="WHS AthlEats Deliveries",
        recipient=user.email,
        subject="Pickup Confirmation - AthlEats Deliveries",
        body=f"""

        Hello {user.first_name.capitalize()},
        
        Your delivery is scheduled for:
        {availability.date_string} after school at {order.pickup_location}.
        
        To view full details about your order, follow this link:
        https://www.athleats.app/order/{order_entry_id}
        
        Thanks for ordering with WHS AthlEats,
        
        Sincerely,
        The AthlEats Team
        athleats.wayland@gmail.com

        """
    )

    # TODO: Wesley: in the order-complete.html, add more details
    #       about the order/availability using the instances provided
    #       in jinja below. Check account_authority.py classes to see what info you can show :).

    # NOTE: url does not change (reserve-form), only renders new html template
    return render_template("order-complete.html",
                           user=user,
                           order=order,
                           availability=availability,
                           runner=runner,
                           fee=fee
                           )


@app.route("/order/<order_entry_id>", methods=["GET"])
def display_order_details(order_entry_id):
    auth_token = request.cookies.get("auth_token")
    failed_response = redirect("/", 302)

    database = AthlEatsDatabase()
    with database:
        # Confirm order is real. Does not need a user logged in to see order details. Anyone can see it with link.
        order = database.get_entry(table_name="orders", entry_id=order_entry_id)
        if not order:
            return redirect("/", 302)
        availability = database.get_entry(table_name="runner_availabilities", entry_id=order.availability_entry_id)
        if not availability:
            return redirect("/", 302)
        runner = database.get_entry(table_name="users", entry_id=availability.runner_entry_id)
        if not runner:
            return redirect("/", 302)
        user = database.get_entry(table_name="users", auth_token=auth_token)

    return render_template("order-complete.html",
                           user=user,
                           order=order,
                           availability=availability,
                           runner=runner,
                           fee=calculate_fees(order.price),
                           )


@app.route("/availability/<availability_entry_id>", methods=["GET"])
def display_availability_details(availability_entry_id):
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        # Confirm order is real. Does not need a user logged in to see order details. Anyone can see it with link.
        availability = database.get_entry(table_name="runner_availabilities", entry_id=availability_entry_id)
        runner = database.get_entry(table_name="users", entry_id=availability.runner_entry_id)
        user = database.get_entry(table_name="users", auth_token=auth_token)

    if not availability or not runner:
        return redirect("/", 302)

    locations = None
    if availability.location > 0:
        locations = []
        for place, code in LOCATIONS.items():
            if code == availability.location:
                locations.append(place)

    return render_template("availability_details.html",
                           user=user,
                           availability=availability,
                           runner=runner,
                           locations=locations,
                           )


@app.route("/staff-dashboard", methods=["GET"])
def display_staff_dashboard():
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)
        if not user or not user.staff:
            return redirect("/", 302)
        orders_list = database.get_all_entries(table_name="orders", entry_id=user.entry_id)
        availabilities = database.get_all_entries(table_name="runner_availabilities",
                                                  runner_entry_id=user.entry_id)  # TODO: delete connection closes
        database.clear_old_availabilities()

    incomplete_orders = [order for order in orders_list if order.is_complete == 0]
    completed_orders = [order for order in orders_list if order.is_complete == 1]

    your_availabilities = [avail for avail in availabilities if
                           avail.date >= datetime.now() and avail.runner_entry_id == user.entry_id]
    reserved_availabilities = [avail for avail in availabilities if
                               avail.reserved and avail.runner_entry_id == user.entry_id]

    completed_reserved_orders = [avail for avail in availabilities if
                                 avail.reserved and avail.runner_entry_id == user.entry_id and avail.is_complete == 1]
    incomplete_reserved_orders = [avail for avail in availabilities if
                                  avail.reserved and avail.runner_entry_id == user.entry_id and avail.is_complete == 0]

    reserved_orders = []
    for avail in incomplete_reserved_orders:
        if ',' in str(avail.order_entry_id):
            orders = avail.order_entry_id.split(',')
            for order in orders:
                duplicate = copy.deepcopy(avail)
                duplicate.order_entry_id = order
                reserved_orders.append(duplicate)
        else:
            reserved_orders.append(avail)

    for avail in reserved_orders:
        print(avail.order_entry_id)

    return render_template("staff-dashboard.html",
                           user=user,
                           availabilities=availabilities,
                           reserved_availabilities=reserved_availabilities,
                           incomplete_orders=incomplete_orders,
                           completed_orders=completed_orders,
                           completed_reserved_orders=completed_reserved_orders,
                           incomplete_reserved_orders=reserved_orders
                           )


@app.route("/order-complete", methods=["POST"])
def process_complete_order():
    entry_id = request.form.get("entry_id")
    database = AthlEatsDatabase()
    with database:
        order = database.edit_entry(table_name="orders", entry_id=entry_id, is_complete=1)
        database.edit_entry(table_name="runner_availabilities", entry_id=order.availability_entry_id, is_complete=1)

    return redirect("/staff-dashboard", 302)


@app.route("/new-availability", methods=["POST"])
def process_new_availability():
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        runner = database.get_entry(table_name="users", auth_token=auth_token)

        if not runner or not runner.staff:
            return "Access Denied", 403

        # Create new runner availability
        database.create_entry(
            table_name="runner_availabilities",

            entry_id=uuid.uuid4(),
            runner_entry_id=runner.entry_id,
            order_entry_id="",  # TBD
            reserved=0,
            date=request.form.get("date"),
            block=request.form.get("block"),
            is_complete=0,
            location=request.form.get("location")
        )

    return redirect("/staff-dashboard", 302)


@app.route("/edit-availability", methods=["POST"])
def process_edit_availability():
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        runner = database.get_entry(table_name="users", auth_token=auth_token)

        if not runner or not runner.staff:
            return "Access Denied", 403

        availability_entry_id = request.form.get("availability_entry_id")

        # Edit runner availability
        avail = database.get_entry(table_name="runner_availabilities", entry_id=availability_entry_id)
        if not avail:
            return "Availability not found", 500

        database.edit_entry(
            table_name="runner_availabilities",

            entry_id=availability_entry_id,
            date=request.form.get("date"),
            block=request.form.get("block"),
        )

    return redirect("/staff-dashboard", 302)


@app.route("/delete-availability", methods=["POST"])
def process_delete_availability():
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        runner = database.get_entry(table_name="users", auth_token=auth_token)

        if not runner or not runner.staff:
            return "Access Denied", 403

        availability_entry_id = request.form.get("availability_entry_id")

        # Edit runner availability
        avail = database.get_entry(table_name="runner_availabilities", entry_id=availability_entry_id)
        if not avail:
            return "Availability not found", 500

        database.delete_entry(table_name="runner_availabilities", entry_id=availability_entry_id)

    return redirect("/staff-dashboard", 302)


@app.route("/admin-dashboard", methods=["GET"])
def display_admin_dashboard():
    auth_token = request.cookies.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

        if not user or not user.admin:
            return redirect("/", 302)

        orders = database.get_all_entries(table_name="orders")
        users = database.get_all_entries(table_name="users")

    completed_orders = [order for order in orders if order.is_complete]
    incomplete_orders = [order for order in orders if not order.is_complete]
    staff_list = [user for user in users if user.staff]

    total_profits = sum([calculate_fees(order.price) for order in completed_orders])
    total_orders = len(completed_orders)
    average_order_value = round(sum([float(order.price) for order in completed_orders]) / total_orders,
                                2) if total_orders else 0
    restaurants = {}
    # new_users
    # for order in completed_orders:
    # most_popular_restaurant


    return render_template("admin-dashboard.html",
                           user=user,
                           incomplete_orders=incomplete_orders,
                           completed_orders=completed_orders,
                           user_list=users,
                           staff_list=staff_list,
                           total_profits=total_profits,
                           total_orders=total_orders,
                           average_order_value=average_order_value,
                           calculate_fees=calculate_fees
                           )


def calc_total_profits(days):
    # today = datetime.date.today()
    # datetime.date.today().strftime("%D %H:%M:%S")
    # week_ago = today - datetime.timedelta(days=7)
    # print(week_ago)

    return 2


@app.route("/process-admin-order-update/<table>", methods=["POST"])
def process_admin_order_update(table):
    auth_token = request.args.get("auth_token")

    database = AthlEatsDatabase()
    with database:
        user = database.get_entry("users", auth_token=auth_token)
        if not user:
            return redirect("/", 302)

        # kwargs to pass to edit_entry()
        form_as_dict = request.form.to_dict()
        # get table type/name from HTML
        table_name = str(table)
        # get entry_id (this only works for orders right now)
        entry_id = request.form.get("index")

        database.edit_entry(table_name=table_name, entry_id=entry_id, **form_as_dict)

    return redirect("/admin-dashboard", 302)


@app.route("/profile", methods=["GET"])
def display_profile():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

        if not user:
            return redirect("/", 302)

        orders = database.get_all_entries(table_name="orders", email=user.email)

    user_current_orders = [order for order in orders if not order.is_complete]
    user_orders = [order for order in orders]
    return render_template("profile.html",
                           user=user,
                           user_current_orders=user_current_orders,
                           user_order_list=user_orders
                           )


@app.route("/settings", methods=["GET"])
def display_settings():
    auth_token = request.cookies.get("auth_token")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

    if not user:
        return redirect("/", 302)

    return render_template("settings.html", user=user)


@app.route("/settings", methods=["POST"])
def process_settings():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

        if not user:
            return redirect("/", 302)

        if "delete-account" in request.form.keys():
            database.delete_entry(table_name="users", entry_id=user.entry_id)
            return redirect("/", 302)

    return render_template("settings.html", user=user)


@app.route("/logout", methods=["GET"])
def logout():
    # Remove auth token cookie
    response = redirect("/", 302)
    response.set_cookie("auth_token", "", expires=0)

    return response


@app.route("/coconut", methods=["GET"])
def display_coconut():
    return redirect("https://youjustgotcoconutmalld.com/", 302)


@app.route("/about-us", methods=["GET"])
def display_about():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

    return render_template("about.html", user=user)

@app.route("/support-faq", methods=["GET"])
def display_support():
    # Redirects to dashboard if user has auth_token cookie (otherwise redirects to signup)
    auth_token = request.cookies.get("auth_token")
    database = AthlEatsDatabase()
    with database:
        user = database.get_entry(table_name="users", auth_token=auth_token)

    return render_template("support_FAQ.html", user=user)


if __name__ == '__main__':
    app.run(debug=True, port=4949)
