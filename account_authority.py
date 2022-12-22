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
    def __init__(self, entry_id, is_complete, email, restaurant, order_date, phone_number, restaurant_pickup_time, pickup_time, price, pickup_location, runner_entry_id):
        self.entry_id = entry_id
        self.email = email
        self.runner_entry_id = runner_entry_id
        self.is_complete = is_complete
        self.restaurant = restaurant
        self.order_date = order_date
        self.phone_number = phone_number
        self.pickup_time = pickup_time
        self.price = price
        self.pickup_location = pickup_location
        self.restaurant_pickup_time = restaurant_pickup_time


class RunnerAvailability:
    def __init__(self, entry_id, runner_entry_id, reserved, date, block):
        self.entry_id = entry_id
        self.runner_entry_id = runner_entry_id
        self.reserved = bool(reserved)
        self.date_string = date
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.block = block
