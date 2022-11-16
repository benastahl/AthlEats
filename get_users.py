import sqlalchemy

sql_username = "b74577def82ecb"
sql_password = "75ca9aed"
sql_host = "us-cdbr-east-06.cleardb.net"


def get_users():
    print("Connecting to database...")
    connection = sqlalchemy.create_engine(f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}/heroku_455007dcaac34a6").connect()
    print("Connected to database.")

    users = connection.execute("SELECT * FROM users").fetchall()
    if not users:
        print("no users found.")

    for user in users:
        print(user)


if __name__ == '__main__':
    get_users()
