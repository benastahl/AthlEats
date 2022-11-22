from controls import UsersCloud, OrdersCloud
import time
import uuid

if __name__ == '__main__':
    order_db = OrdersCloud()
    order_db.create_table(reset=True)
    [print(order.email) for order in order_db.get_all_entries()]
    OrdersCloud().create_entry(
        entry_id=str(uuid.uuid4()),
        email="benastahl@gmail.com",
        restaurant="TOPANGA",
        order_date="11/22/22 10:46:59",
        phone_number="5021241352",
        restaurant_pickup_time="13:46",
        pickup_time="15:46",
        price="52.33",
        pickup_location="matthew daddy"
    )
