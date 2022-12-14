from controls import UsersCloud, OrdersCloud, RunnerAvailabilitiesCloud
from controls import UsersCloud
import time
import uuid

if __name__ == '__main__':
    RunnerAvailabilitiesCloud().create_table()
    avails = RunnerAvailabilitiesCloud().get_all_entries()
    print(avails)
