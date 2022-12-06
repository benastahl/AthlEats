import secrets
import sqlalchemy
import bcrypt

from datetime import datetime
from termcolor import colored
from account_authority import User, Order

sql_username = "b74577def82ecb"
sql_password = "75ca9aed"
sql_host = "us-cdbr-east-06.cleardb.net"
# dialect+driver://username:password@host:port/database


class AthlEatsCloud:
    def __init__(self, table_name: str, table_attributes: list, Instance: type):
        self.Instance = Instance
        self.table_attributes = table_attributes
        self.table_name = table_name
        self.database_name = "heroku_455007dcaac34a6"

        self.log("Connecting to database...", "p")
        self.connection = sqlalchemy.create_engine(
            f"mysql+pymysql://{sql_username}:{sql_password}@{sql_host}/{self.database_name}").connect()
        self.log(f"Successfully connected to database '{self.database_name}'.", "s")

    def log(self, text: str, status: str) -> None:
        """
        Prints informative log message with details of process occurring.
        :param text: Message printed.
        :param status: Color of message. Signals status of process.
        :return:
        """
        color_schemes = {
            "s": "green",
            "f": "red",
            "p": "cyan",
            "d": "yellow"
        }
        print(
            colored(
                f"[{datetime.now().strftime('%m-%d-%Y %H:%M:%S')}] - "
                f"[ATHLEATS DATABASE CLOUD: {sql_username}] - "
                f"[TABLE: {self.table_name.upper()}] - "
                f"{text}",
                color_schemes.get(status)
            )
        )

    @staticmethod
    def sql_conv(value):
        if type(value) == int:
            return f"{value}"
        else:
            return f"'{value}'"

    def create_table(self, reset=False) -> bool:
        """
        Creates a new table based on table_attributes. Should only be used once.
        :param reset: Deletes table in entirety before creating new one (if set to 'True').
        :return: True bool if successful.
        """
        if reset:
            self.log(f"Resetting table (dropping) '{self.table_name}'.", "d")
            self.connection.execute(f"DROP TABLE {self.table_name}")
        attributes = ", ".join([f"{attr.split(':')[0]} {attr.split(':')[1]}" for attr in self.table_attributes])
        self.connection.execute(f'CREATE TABLE {self.table_name} ({attributes})')
        self.connection.close()
        self.log(f"Successfully created table '{self.table_name}'", "s")
        return True

    def create_entry(self, **kwargs):
        # Creates a row in our database table for a user

        # Create SQL query strings
        attributes = ", ".join([self.sql_conv(kwarg) for kwarg in kwargs.values()])
        conditions = " AND ".join([f"{kwarg} = {self.sql_conv(kwargs[kwarg])}" for kwarg in kwargs])

        self.connection.execute(
            f"INSERT INTO {self.table_name} "
            f"VALUES ({attributes})"
        )
        entries = self.connection.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}").fetchall()
        self.connection.close()

        assert entries, f"Failed to find a user with kwargs given ({kwargs})."
        entry = entries[0]
        self.log(f"Successfully created entry '{kwargs.get('entry_id')}'.", "s")
        return self.Instance(**entry)

    def edit_entry(self, entry_id, **kwargs):
        conditions = " AND ".join([f"{kwarg} = {self.sql_conv(kwargs[kwarg])}" for kwarg in kwargs])
        self.connection.execute(
                f"UPDATE {self.table_name} "
                f"SET {conditions} "
                f"WHERE entry_id = '{entry_id}'"
                )

        entries = self.connection.execute(f"SELECT * FROM {self.table_name} WHERE entry_id = '{entry_id}'").fetchall()
        self.connection.close()
        assert entries, f"Failed to find a user with kwargs given ({kwargs})."
        entry = entries[0]
        return self.Instance(**entry)

    def delete_entry(self, entry_id):
        self.connection.execute(
            f"DELETE FROM {self.table_name} "
            f"WHERE entry_id = '{entry_id}'"
        )
        self.connection.close()
        self.log(f"Deleted account: {entry_id}.", "p")

    def get_entry(self, close_conn=True, **filters):
        conditions = " AND ".join([f"{param} = {self.sql_conv(filters[param])}" for param in filters])
        entries = self.connection.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}").fetchall()
        if close_conn:
            self.connection.close()
        if not entries:
            return False
        entry = entries[0]
        self.log(f"Successfully collected entry '{entry[0]}'", "s")
        return self.Instance(**entry)

    def get_all_entries(self, **filters):
        conditions = " AND ".join([f"{param} = {self.sql_conv(filters[param])}" for param in filters])
        entries = self.connection.execute(
            f"SELECT * "
            f"FROM {self.table_name} "
        ).fetchall()
        if not entries:
            return []
        # assert entries, f"Failed to find a user with kwargs given ({kwargs})."
        self.log(f"Successfully collected entries from table '{self.table_name}'", "s")

        return [self.Instance(**entry) for entry in entries]

    def get_entries(self, close_conn=True, **filters):
        sql_string = f"SELECT * FROM {self.table_name}"
        if filters:
            conditions = " AND ".join([f"{param} = {self.sql_conv(filters[param])}" for param in filters])
            sql_string += f" WHERE {conditions}"
        entries = self.connection.execute(sql_string).fetchall()
        if close_conn:
            self.connection.close()
        if not entries:
            return False
        entry = entries[0]
        self.log(f"Successfully collected entry '{entry[0]}'", "s")
        return self.Instance(**entry)


# EACH CHILD CLASS REPRESENTS A TABLE
class UsersCloud(AthlEatsCloud):
    def __init__(self):
        self.table_name = "users"
        # FORMAT: "attribute name":"sql datatype name"
        self.table_attributes = [
            "entry_id:TEXT",
            "email:TEXT",
            "grade:INT",
            "hashed_password:TEXT",
            "auth_token:TEXT",
            "creation_date:INT",
            "staff:INT",
            "admin:INT"
        ]

        super().__init__(self.table_name, self.table_attributes, Instance=User)

    def login_user(self, email, password, new_auth=True):

        # Authenticates user email and password
        user = self.get_entry(close_conn=False, email=email)
        if not user or not bcrypt.checkpw(bytes(password.encode("utf-8")), user.hashed_password.encode("utf-8")):
            return False
        if new_auth:
            # Creates new random auth token string
            auth_token = secrets.token_hex()
            # Sets new auth token to user database row
            authenticated_user = self.edit_entry(entry_id=user.entry_id, auth_token=auth_token)

            # Returns new auth token of authenticated user
            return authenticated_user.auth_token

        # Returns current auth token of user
        return user.auth_token


class OrdersCloud(AthlEatsCloud):
    def __init__(self):
        self.table_name = "orders"
        # FORMAT: "attribute name":"sql datatype name"
        self.table_attributes = [
            "entry_id:TEXT",
            "is_complete:INT",
            "email:TEXT",
            "restaurant:TEXT",
            "order_date:TEXT",
            "phone_number:TEXT",
            "restaurant_pickup_time:TEXT",
            "pickup_time:TEXT",
            "price:TEXT",
            "pickup_location:TEXT"

        ]
        super().__init__(self.table_name, self.table_attributes, Instance=Order)
