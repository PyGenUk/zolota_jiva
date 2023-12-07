

import sqlite3

class User:
    def __init__(self):
        self.db = sqlite3.connect('mydatabase5.db', check_same_thread = False)
        self.sql = self.db.cursor()
        self.sql.execute("""CREATE TABLE IF NOT EXISTS users(
                    ID INT,
                    balance INT,
                    name STR
                )""")
        self.db.commit()

    def add_user(self, id, first_name):
        self.sql.execute(f"INSERT INTO users VALUES(?, ?, ?)", (id, 0, first_name))
        self.db.commit()

    def get_id(self, id):
        return self.sql.execute(f"SELECT ID FROM users WHERE ID = '{id}'").fetchone()

    def get_balance(self, id):
        return self.sql.execute(f"SELECT * FROM users WHERE ID = '{id}'").fetchone()[1]

    def get_all_users(self):
        return self.sql.execute("SELECT * FROM users")

    def set_balance(self, id, balance):
        self.sql.execute(f"UPDATE users SET balance = {balance} WHERE ID = '{id}'")
        self.db.commit()


class Tasks:
    def __init__(self):
        self.db2 = sqlite3.connect('tasks.db', check_same_thread = False)
        self.sql2 = self.db2.cursor()
        self.sql2.execute("""CREATE TABLE IF NOT EXISTS tasks_of_users(
                ID STR,
                FIRST_NAME STR,
                USERNAME STR,
                URL STR,
                NUMBER_OF_VOICES STR,
                FUNCTION STR,
                MIN_TIME STR,
                POSITION_TARGET STR,
                HOLD_HOURS STR,
                TIME_CREATED STR,
                DATE_CREATED STR
            )""")
        self.db2.commit()

    def get_tasks(self, id, time):
        return self.sql2.execute(f"SELECT * FROM tasks_of_users WHERE ID = '{id}' AND DATE_CREATED = '{time}'")

    def set_task(self, id, first_name, username, url, voices, result_func, min_time, position_target, hold_hours, time, date):
        self.sql2.execute(f"INSERT INTO tasks_of_users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (id, first_name, username, url, voices,
                      result_func, min_time, position_target, hold_hours, time, date))
        self.db2.commit()