from datetime import datetime


class User:
    def __init__(self, entry_id, email, grade, hashed_password, auth_token, creation_date, staff, admin, sport_team):
        self.entry_id = entry_id

        self.first_name = email.split('@')[0].split('_')[0].capitalize()
        self.last_name = email.split('@')[0].split('_')[1].capitalize()
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
        self.year_name = {9: "Freshman", 10: "Sophomore", 11: "Junior", 12: "Senior"}.get(self.grade)
        self.auth_token = auth_token
        self.creation_date = datetime.fromtimestamp(creation_date)
        self.sport_team = sport_team

        # Special Roles
        self.staff = bool(staff)
        self.admin = bool(admin)


class Order:
    def __init__(self, entry_id, availability_entry_id,  is_complete, email, restaurant, order_date, phone_number, restaurant_pickup_time, price, pickup_location, pickup_name, runner_entry_id):
        self.entry_id = entry_id
        self.email = email
        self.availability_entry_id = availability_entry_id
        self.runner_entry_id = runner_entry_id
        self.is_complete = is_complete
        self.restaurant = restaurant
        self.order_date = order_date
        self.phone_number = phone_number
        self.price = price
        self.pickup_name = pickup_name
        self.pickup_location = pickup_location
        self.restaurant_pickup_time = restaurant_pickup_time


class RunnerAvailability:
    def __init__(self, entry_id, runner_entry_id, order_entry_id, reserved, date, block, is_complete):
        self.entry_id = entry_id
        self.runner_entry_id = runner_entry_id
        self.order_entry_id = order_entry_id
        self.reserved = bool(reserved)
        self.date_string = date
        self.date = datetime.strptime(date, "%Y-%m-%d")
        self.block = block
        self.is_complete = int(is_complete)


# Experimental
class Statistics:
    def __init__(self,
                 current_user_count,
                 all_time_user_count,
                 staff_count,

                 deliveries_scheduled,
                 deliveries_successful,
                 availabilities_scheduled,

                 gross_fees_income,
                 gross_spent_by_users,

                 ):
        # Users
        self.current_user_count = current_user_count
        self.all_time_user_count = all_time_user_count
        self.staff_count = staff_count

        # Deliveries
        self.deliveries_scheduled_count = deliveries_scheduled
        self.deliveries_successful_count = deliveries_successful
        self.availabilities_scheduled_count = availabilities_scheduled

        # Finances
        self.gross_fees_income = gross_fees_income
        self.gross_spent_by_users = gross_spent_by_users