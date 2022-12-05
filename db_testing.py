from controls import UsersCloud
import time

if __name__ == '__main__':
    user_db = UsersCloud()
    user_db.set_permission(email="benjamin_stahl@student.waylandps.org", admin_key="WATKINS", admin=True, staff=True)
