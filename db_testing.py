from controls import UsersCloud
import time

if __name__ == '__main__':
    user_db = UsersCloud()
    user_db.create_table(name="users")