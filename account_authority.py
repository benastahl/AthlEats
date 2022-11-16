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
        self.creation_date = creation_date

        # Special Roles
        self.staff = staff
        self.admin = admin


class Order:
    def __init__(self, email, location, entry_id, order_date, phone_number, pickup_time, payed):
        self.email = email
        self.location = location
        self.entry_id = entry_id
        self.order_date = order_date
        self.phone_number = phone_number
        self.pickup_time = pickup_time
        self.payed = payed
