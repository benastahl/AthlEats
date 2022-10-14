import secrets


class Administrator:
    def __init__(self, email, hashed_password, auth_token):
        self.email = email
        self.hashed_password = hashed_password
        self.auth_token = auth_token
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]


class User:
    def __init__(self, email, grade, hashed_password, auth_token, creation_date):
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
        self.auth_token = auth_token
        self.creation_date = creation_date

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
