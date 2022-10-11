import sqlite3

import bcrypt

from account_authority import User, Administrator


class UserDB:
    def __init__(self):
        self.connection = sqlite3.connect("students.db")
        self.cursor = self.connection.cursor()

    def create_user_table(self) -> bool:
        self.cursor.execute(
            'CREATE TABLE students (first_name TEXT, last_name TEXT, email TEXT, grade INTEGER, hashed_password TEXT, auth_token TEXT)')
        self.connection.commit()
        self.connection.close()
        return True

    def add_user(self, first_name: str, last_name: str, email: str, grade: int, hashed_password: str,
                 auth_token: str) -> bool:
        self.cursor.execute(
            f"INSERT INTO students VALUES ('{first_name}', '{last_name}', '{email}', {grade}, '{hashed_password}', '{auth_token}',)")
        self.connection.commit()
        self.connection.close()
        return True

    def get_user(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])
        students = self.cursor.execute(
            f"SELECT first_name, last_name, email, grade, hashed_password, auth_token FROM students WHERE {conditions}").fetchall()
        self.connection.close()
        if not students:
            # No student found
            return False
        student = students[0]
        return User(first_name=student[0], last_name=student[1], email=student[2], grade=student[3],
                    hashed_password=student[4], auth_token=student[5])

    def edit_user(self, email, password, **kwargs):
        user = self.get_user(email=email)
        if not bcrypt.checkpw(bytes(password.encode("utf-8")), user.hashed_password.encode("utf-8")):
            return False

        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])
        self.cursor.execute(f'''
                UPDATE students
                SET {conditions}
                WHERE email = {email}
                ''')

    def delete_student(self, email: str) -> bool:
        self.cursor.execute(f"DELETE FROM students WHERE email = '{email}'")
        self.connection.commit()
        self.connection.close()
        return True

