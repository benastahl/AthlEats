
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
    def __init__(self, email, password, grade, payment_type):
        self.email = email
        self.password = password
        self.grade = grade
        self. payment_type = payment_type
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]

    def update_email(self, email):
        self.email = email
        self.first_name = email.split('@')[0].split('_')[0]
        self.last_name = email.split('@')[0].split('_')[1]

