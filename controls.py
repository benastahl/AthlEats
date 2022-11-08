import sqlite3
import secrets

import bcrypt

from account_authority import User, Staff, Admin


class UserDB:
    def __init__(self):
        self.connection = sqlite3.connect("users.db")
        self.cursor = self.connection.cursor()

    def create_user_table(self) -> bool:
        # Create user table. should only be used once and never again. Only really for resetting.
        self.cursor.execute(
            'CREATE TABLE users (first_name TEXT, last_name TEXT, email TEXT, grade INTEGER, hashed_password TEXT, auth_token TEXT, creation_date INT, staff INT, admin INT)')
        self.connection.commit()
        self.connection.close()
        return True

    def add_user(self, first_name: str, last_name: str, email: str, grade: int, hashed_password: str,
                 auth_token: str, creation_date: int, staff: int, admin: int) -> bool:
        # Creates a row in our database table for a user
        self.cursor.execute(
            f"INSERT INTO users VALUES ('{first_name}', '{last_name}', '{email}', {grade}, '{hashed_password}', '{auth_token}', {creation_date}, {staff}, {admin})")
        self.connection.commit()
        self.connection.close()
        return True

    def get_user(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs if kwarg != "close_conn"])
        # Finds a user based on the keyword arguments. Gives back all the data on the user.
        users = self.cursor.execute(
            f"SELECT first_name, last_name, email, grade, hashed_password, auth_token, creation_date, staff, admin FROM users WHERE {conditions}").fetchall()

        if not users:
            # No user found
            return False
        user = users[0]
        staff = user[7]
        admin = user[8]

        if admin:
            user = Admin(email=user[2], grade=user[3], hashed_password=user[4], auth_token=user[5], creation_date=user[6])
        elif staff:
            user = Staff(email=user[2], grade=user[3], hashed_password=user[4], auth_token=user[5], creation_date=user[6])

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
                UPDATE users
                SET {conditions}
                WHERE email = '{email}'
                ''')
        self.connection.commit()

        # Return new user object with updated args/details.
        user = self.get_user(email=email)
        return user

    def delete_user(self, email: str) -> bool:
        self.cursor.execute(f"DELETE FROM users WHERE email = '{email}'")
        self.connection.commit()
        self.connection.close()
        return True


    def return_all_users(self):

        users = self.cursor.execute(f"SELECT * FROM users").fetchall()

        # all_users = [ for user in users]

        all_users = list()

        for user in users:
            staff = user[7]
            admin = user[8]

            all_users.append(User(user[2], user[3], user[4], user[5], user[6], user[7], user[8]))

        self.connection.close()
        print(all_users)

        return all_users

