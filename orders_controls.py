import sqlite3
import secrets

import bcrypt

from account_authority import Order, PickupRequest


class OrdersDB:
    def __init__(self):
        self.connection = sqlite3.connect("orders.db")
        self.cursor = self.connection.cursor()

    def create_orders_table(self) -> bool:
        # Create user table. should only be used once and never again. Only really for resetting.
        self.cursor.execute(
            '''CREATE TABLE orders(student_first_name TEXT, student_last_name TEXT, food_order TEXT, order_time INT, restaurant TEXT, order_id INT)''')
        self.connection.commit()
        self.connection.close()
        return True

    def add_orders(self, student_first_name: str, student_last_name: str, food_order: str, order_time: int, restaurant:
                    str, order_id: int) -> bool:
        # Creates a row in our database table for a user
        self.cursor.execute(
            f"INSERT INTO orders VALUES ('{student_first_name}', '{student_last_name}', '{food_order}', {order_time}, '{restaurant}', '{order_id}')")
        self.connection.commit()
        self.connection.close()
        return True

    def get_order(self, **kwargs):
        conditions = " AND ".join([f"{kwarg} = '{kwargs[kwarg]}'" for kwarg in kwargs if kwarg != "close_conn"])
        # Finds a user based on the keyword arguments. Gives back all the data on the user.
        orders = self.cursor.execute(
            f"SELECT student_first_name, student_last_name, food_order, order_time, restaurant, order_id, FROM orders WHERE {conditions}").fetchall()

        if not orders:
            # No order found
            return False
        order = orders[0]

        order = Order(fname=orders[2], lname=orders[3], food_order=orders[4], restaurant=orders[5], id=orders[6])

        # Adds option in args to not close the database connection for underlying function using get_user
        if "close_conn" in kwargs and not kwargs.get("close_conn"):
            return order

        self.connection.close()
        # Returns user object
        return order

    def return_all_orders(self):

        orders = self.cursor.execute(
            f"SELECT * FROM orders").fetchall()

        all_orders = list()

        for order in orders:
            all_orders.append(Order(order[0], order[1], order[2], order[3], order[4], order[5]))
        self.connection.close()
        return all_orders
