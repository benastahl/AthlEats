import secrets
import sqlalchemy
import bcrypt

from datetime import datetime
from termcolor import colored
from account_authority import User


# athleats
# zoccoceo4ever
# dialect+driver://username:password@host:port/database


class AthlEatsCloud:
    def __init__(self, table_name: str, table_attributes: list, Instance: type):
        self.Instance = Instance
        self.table_attributes = table_attributes
        self.table_name = table_name
        self.database_name = "heroku_455007dcaac34a6"
        self.sql_datatypes = {int: "INT", str: "TEXT"}

        self.__sql_username = "b74577def82ecb"
        self.__sql_password = "75ca9aed"
        self.__sql_host = "us-cdbr-east-06.cleardb.net/heroku_455007dcaac34a6"
        self.log("Connecting to database...", "p")
        self.connection = sqlalchemy.create_engine(
            f"mysql+pymysql://{self.__sql_username}:{self.__sql_password}@{self.__sql_host}").connect()
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
                f"[ATHLEATS DATABASE CLOUD: {self.__sql_username}] - "
                f"[TABLE: {self.table_name.upper()}] - "
                f"{text}",
                color_schemes.get(status)
            )
        )

    def create_table(self, name: str, reset=False) -> str:
        """
        Creates a new table based on table_attributes. Should only be used once.
        :param name: Name for table. (ex: users, admins, foods, etc.).
        :param reset: Deletes table in entirety before creating new one (if set to 'True').
        :return: Message if table is created successfully.
        """
        if reset:
            self.connection.execute(f"DROP TABLE {self.table_name}")
        attributes = ", ".join([f"{attr.split(':')[0]} {attr.split(':')[1]}" for attr in self.table_attributes])
        self.connection.execute(f'CREATE TABLE {name} ({attributes})')
        self.connection.close()
        return f"Successfully created table: '{name}'"

    def create_entry(self, **kwargs):
        # Create SQL query string
        attributes = []
        for kwarg in kwargs.values():
            if type(kwarg) == str:
                attributes.append(f"'{kwarg}'")
                continue
            attributes.append(f"{kwarg}")
        attributes = ", ".join(attributes)

        # Creates a row in our database table for a user
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])

        self.connection.execute(
            f"INSERT INTO {self.table_name} "
            f"VALUES ({attributes})"
        )
        entries = self.connection.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}").fetchall()
        self.connection.close()

        if not entries:
            return False
        entry = entries[0]
        return self.Instance(**entry)

    def edit_entry(self, identifier, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs if kwarg != identifier])
        self.connection.execute(
                f"UPDATE {self.table_name}"
                f"SET {conditions}"
                f"WHERE {identifier} = '{kwargs[identifier]}'"
                )

        entries = self.connection.execute(f"SELECT * FROM {self.table_name} WHERE {identifier} = '{kwargs[identifier]}'").fetchall()
        self.connection.close()
        if not entries:
            return False
        entry = entries[0]
        return self.Instance(**entry)

    def get_entry(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs])
        entries = self.connection.execute(f"SELECT * FROM users WHERE {conditions}").fetchall()
        self.connection.close()
        if not entries:
            return False
        entry = entries[0]
        return self.Instance(**entry)


class UsersCloud(AthlEatsCloud):
    def __init__(self):
        self.table_name = "users"
        # FORMAT: "attribute name":"sql datatype name"
        self.table_attributes = [
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
        user = self.get_entry(email=email)
        if not user or not bcrypt.checkpw(bytes(password.encode("utf-8")), user.hashed_password.encode("utf-8")):
            return False
        if new_auth:
            # Creates new random auth token string
            auth_token = secrets.token_hex()
            # Sets new auth token to user database row
            authenticated_user = self.edit_entry(identifier="email", email=user.email, auth_token=auth_token)
            if not authenticated_user:
                return False
            # Returns new auth token of authenticated user
            return authenticated_user.auth_token

        # Returns current auth token of user
        return user.auth_token
