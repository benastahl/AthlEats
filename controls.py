import sqlite3
import secrets

import bcrypt

from account_authority import User, Administrator


class UserDB:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

    def create_user_table(self) -> bool:
        # Create user table. should only be used once and never again. Only really for resetting.
        self.cursor.execute(
            'CREATE TABLE students (first_name TEXT, last_name TEXT, email TEXT, grade INTEGER, hashed_password TEXT, auth_token TEXT, creation_date INT)')
        self.connection.commit()
        self.connection.close()
        return True

    def add_user(self, first_name: str, last_name: str, email: str, grade: int, hashed_password: str,
                 auth_token: str, creation_date: int) -> bool:
        # Creates a row in our database table for a user
        self.cursor.execute(
            f"INSERT INTO students VALUES ('{first_name}', '{last_name}', '{email}', {grade}, '{hashed_password}', '{auth_token}', {creation_date})")
        self.connection.commit()
        self.connection.close()
        return True

    def get_user(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs if kwarg != "close_conn"])
        # Finds a user based on the keyword arguments. Gives back all the data on the user.
        students = self.cursor.execute(
            f"SELECT first_name, last_name, email, grade, hashed_password, auth_token, creation_date FROM students WHERE {conditions}").fetchall()

        if not students:
            # No student found
            return False
        student = students[0]

        user = User(email=student[2], grade=student[3],
                    hashed_password=student[4], auth_token=student[5], creation_date=student[6])

        # Adds option in args to not close the database connection for underlying function using get_user
        if "close_conn" in kwargs and not kwargs.get("close_conn"):
            return user

        self.connection.close()
        # Returns user object
        return user

    def login_user(self, email, password):

        user = self.get_user(email=email)
        if not user or not bcrypt.checkpw(bytes(password.encode("utf-8")), user.hashed_password.encode("utf-8")):
            return False
        return True

    def edit_user(self, email, password, **kwargs):
        # Check the password is correct before it allows to edit a user's details
        if not self.login_user(email=email, password=password):
            return False

        # Update the user's details
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])
        self.cursor.execute(f'''
                UPDATE students
                SET {conditions}
                WHERE email = '{email}'
                ''')

        # Return new user object with updated args/details.
        return self.get_user(email=email)

    def delete_student(self, email: str) -> bool:
        self.cursor.execute(f"DELETE FROM students WHERE email = '{email}'")
        self.connection.commit()
        self.connection.close()
        return True


class AdminDB:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

    def admin_login(self, email, password):
        conditions = f"email = {email} AND password = {password}"

        # Finds a user based on the keyword arguments. Gives back all the data on the user.
        admins = self.cursor.execute(
            f"SELECT first_name, last_name, email, hashed_password, admin_auth_token FROM admins WHERE {conditions}").fetchall()
        self.connection.close()
        if not admins:
            # No administrator found
            return False
        admin = admins[0]

        auth_token = secrets.token_hex()

        # Returns user object
        return Administrator(email=admin[2], hashed_password=admin[4], auth_token=auth_token)

