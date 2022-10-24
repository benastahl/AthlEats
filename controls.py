import sqlite3
import secrets

import bcrypt

from account_authority import User, PickupRequest


class UserDB:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

    def create_user_table(self) -> bool:
        # Create user table. should only be used once and never again. Only really for resetting.
        self.cursor.execute(
            'CREATE TABLE students (first_name TEXT, last_name TEXT, email TEXT, grade INTEGER, hashed_password TEXT, auth_token TEXT, creation_date INT, admin BOOLEAN)')
        self.connection.commit()
        self.connection.close()
        return True

    def add_user(self, first_name: str, last_name: str, email: str, grade: int, hashed_password: str,
                 auth_token: str, creation_date: int, admin: bool) -> bool:
        # Creates a row in our database table for a user
        self.cursor.execute(
            f"INSERT INTO students VALUES ('{first_name}', '{last_name}', '{email}', {grade}, '{hashed_password}', '{auth_token}', {creation_date}, {admin})")
        self.connection.commit()
        self.connection.close()
        return True

    def get_user(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs if kwarg != "close_conn"])
        # Finds a user based on the keyword arguments. Gives back all the data on the user.
        students = self.cursor.execute(
            f"SELECT first_name, last_name, email, grade, hashed_password, auth_token, creation_date, admin FROM students WHERE {conditions}").fetchall()

        if not students:
            # No student found
            return False
        student = students[0]

        user = User(email=student[2], grade=student[3],
                    hashed_password=student[4], auth_token=student[5], creation_date=student[6], admin=student[7])

        # Adds option in args to not close the database connection for underlying function using get_user
        if "close_conn" in kwargs and not kwargs.get("close_conn"):
            return user

        self.connection.close()
        # Returns user object
        return user

    def login_user(self, email, password, new_auth=True):

        # Authenticates user email and password
        user = self.get_user(email=email, close_conn=False)
        if not user or not bcrypt.checkpw(bytes(password.encode("utf-8")), user.hashed_password.encode("utf-8")):
            return False
        if new_auth:
            # Creates new random auth token string
            auth_token = secrets.token_hex()
            # Sets new auth token to user database row
            authenticated_user = self.edit_user(email=email, password=password, auth_token=auth_token)
            if not authenticated_user:
                return False
            # Returns new auth token of authenticated user
            return authenticated_user.auth_token

        # Returns current auth token of user
        return user.auth_token

    def edit_user(self, email, password, **kwargs):
        # Check the password is correct before it allows to edit a user's details
        if not self.login_user(email=email, password=password, new_auth=False):
            return False

        # Update the user's details
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])
        self.cursor.execute(f'''
                UPDATE students
                SET {conditions}
                WHERE email = '{email}'
                ''')
        self.connection.commit()

        # Return new user object with updated args/details.
        user = self.get_user(email=email)
        return user

    def delete_student(self, email: str) -> bool:
        self.cursor.execute(f"DELETE FROM students WHERE email = '{email}'")
        self.connection.commit()
        self.connection.close()
        return True
