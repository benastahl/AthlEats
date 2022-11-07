class User:
    def __init__(self, email, grade, hashed_password, auth_token, creation_date, staff, admin):
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
        self.staff = staff
        self.admin = admin
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
        self.year_name = {9: "Freshman", 10: "Sophomore", 11: "Junior", 12: "Senior"}.get(self.grade)
        self.auth_token = auth_token
        self.creation_date = creation_date

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]


class PickupRequest:
    def __init__(self, user, contact_phone, order_description, creation_date):
        self.user = user
        self.contact_phone = contact_phone
        self.order_description = order_description
        self.creation_date = creation_date

class Order:
    def __init__(self, fname, lname, food_order, restaurant, date, id):
        self.first_name = fname
        self.last_name = lname
        self.food_order=food_order
        self.restaurant=restaurant
        self.id = id
        self.date = date
