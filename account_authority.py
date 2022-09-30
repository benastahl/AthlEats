
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

    def update_password(self, password):
        self.password = password

    def update_grade(self, grade):
        self.grade = grade

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_grade(self):
        return self.password


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

    def update_password(self, password):
        self.password = password

    def update_grade(self, grade):
        self.grade = grade

    def update_payment_type(self, payment_type):
        self.payment_type = payment_type

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def get_grade(self):
        return self.password

    def get_payment_type(self):
        return self.payment_type

