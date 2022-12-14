from datetime import datetime


class User:
    def __init__(self, entry_id, email, grade, hashed_password, auth_token, creation_date, staff, admin):
        self.entry_id = entry_id

        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
        self.year_name = {9: "Freshman", 10: "Sophomore", 11: "Junior", 12: "Senior"}.get(self.grade)
        self.auth_token = auth_token
        self.creation_date = datetime.fromtimestamp(creation_date)

        # Special Roles
        self.staff = bool(staff)
        self.admin = bool(admin)


class Order:
    def __init__(self, entry_id, is_complete, email, restaurant, order_date, phone_number, restaurant_pickup_time, pickup_time, price, pickup_location, runner):
        self.email = email
        self.is_complete = is_complete
        self.restaurant = restaurant
        self.entry_id = entry_id
        self.order_date = order_date
        self.phone_number = phone_number
        self.pickup_time = pickup_time
        self.price = price
        self.pickup_location = pickup_location
        self.restaurant_pickup_time = restaurant_pickup_time
        self.runner = runner


class RunnerAvailability:
    def __init__(self, entry_id, runner_entry_id, status, date, start_time, end_time):
        self.entry_id = entry_id,
        self.runner_entry_id = runner_entry_id
        self.status = status
        self.date_string = datetime.fromtimestamp(date)
        self.date = datetime.fromtimestamp(date)
        self.start_time = start_time
        self.end_time = end_time
