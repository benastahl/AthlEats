import secrets


class Administrator:
    def __init__(self, email, password, grade):
        self.email = email
        self.password = password
        self.grade = grade
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]


class User:
    def __init__(self, first_name, last_name, email, grade, hashed_password, auth_token):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = hashed_password
        self.grade = grade
        self.auth_token = auth_token

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]
