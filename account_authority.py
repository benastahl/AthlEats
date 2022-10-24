class User:
    def __init__(self, email, grade, hashed_password, auth_token, creation_date, admin):
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
        self.admin = admin
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
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

