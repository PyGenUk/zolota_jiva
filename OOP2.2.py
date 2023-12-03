import telebot
from telebot import types
import sqlite3
from time import localtime, strftime

bot = telebot.TeleBot("5432392957:AAE9er1GSbbT7PAY8sEEEzSj50wUj2QTd0Q")

db = sqlite3.connect('mydatabase5.db', check_same_thread = False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users5(
    ID INT,
    balance INT,
    name STR
)""")
db.commit()

db2 = sqlite3.connect('tasks.db', check_same_thread = False)
sql2 = db2.cursor()
sql2.execute("""CREATE TABLE IF NOT EXISTS tasks_of_users2(
    ID STR,
    URL STR,
    NUMBER_OF_VOICES STR, 
    FUNCTION2 STR, 
    MIN_TIME STR,
    WHEN_TIME
)""")
db2.commit()

db3 = sqlite3.connect('yesterday_tasks.db', check_same_thread = False)
sql3 = db3.cursor()
sql3.execute("""CREATE TABLE IF NOT EXISTS yesterday_tasks_of_users(
    ID STR,
    URL STR,
    NUMBER_OF_VOICES STR, 
    FUNCTION2 STR, 
    MIN_TIME STR,
    WHEN_TIME
)""")
db3.commit()

comand_markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
comand_button1 = types.KeyboardButton(text = "/add")
comand_button3 = types.KeyboardButton(text = "/help")
comand_button2 = types.KeyboardButton(text = "/balance")
comand_button4 = types.KeyboardButton(text = "/tasks")
comand_markup.add(comand_button1, comand_button2, comand_button3, comand_button4)

numbers_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
g = localtime()
CASH_DATA = strftime("%d", g)
list_today = ["📝 Список заданий за вчера:", ["Вчера не было заданий 😐"]]
list_yesterday = ["📝 Список заданий за сегодня:", ["Вы ещё не запускали задания сегодня 🥲"]]


@bot.message_handler(commands = ["start"])
def start_message(message):
    list = []
    for value in sql.execute("SELECT * FROM users5"):
        list.append(str(value[0]))
    if str(message.chat.id) not in list:
        sql.execute(f"INSERT INTO users5 VALUES(?, ?, ?)",
                    (message.chat.id, 0, message.from_user.first_name))
        db.commit()
    bot.send_message(message.chat.id,
                     text = f"""👋 Привет {message.from_user.first_name}! Я платный бот, который будет помогать тебе апвоутить или даунвоутить посты и комментарии на Reddit!\n\nЧтобы создать новое задание, напиши или нажми на команду /add\nЧтобы узнать свой баланс, используй команду /balance\nЧтобы посмотреть список заданий за сегодня, используйте /tasks""",
                     reply_markup = comand_markup)


@bot.message_handler(commands = ["help"])
def start_message(message):
    bot.send_message(message.chat.id,
                     text = f"""👋 Привет {message.from_user.first_name}! Я платный бот, который будет помогать тебе апвоутить или даунвоутить посты и комментарии на Reddit!\n\nЧтобы создать новое задание, напиши или нажми на команду /add\nЧтобы узнать свой баланс, используй команду /balance\nЧтобы посмотреть список заданий за сегодня, используйте /tasks""",
                     reply_markup = comand_markup)


@bot.message_handler(commands = ["SanyaVerniSotkyBojeYyackeKonchene"])
def get_id_vubranogo_usera(message):
    bot.send_message(message.chat.id, "Список пользователей:")
    result = ""
    for value in sql.execute("SELECT * FROM users5"):
        result = result + str(value) + "\n"
    bot.send_message(message.chat.id, result)
    bot.send_message(message.chat.id, "Введите ID пользователя:")
    bot.register_next_step_handler(message, get_id_vubranogo_usera_check)


def get_id_vubranogo_usera_check(message):
    global id_vubranogo_usera
    id_vubranogo_usera = message.text
    list2 = []
    for value in sql.execute("SELECT * FROM users5"):
        list2.append(str(value[0]))
    if str(message.text) not in list2:
        bot.send_message(message.chat.id, "Такого пользователя нет в базе даных. Попробуйте еще раз")
        get_id_vubranogo_usera(message)
    else:
        get_num_vubranogo_usera(message)


def get_num_vubranogo_usera(message):
    bot.send_message(message.chat.id, "💵 Введите кол-во голосов, которое нужно добавить или убрать:")
    bot.register_next_step_handler(message, choice_balance)


def choice_balance(message):
    global num_vubranogo_usera
    num_vubranogo_usera = message.text

    global balance
    for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{id_vubranogo_usera}'"):
        balance = i[0]

    try:
        if type(int(num_vubranogo_usera)) == int:
            sql.execute(
                f"UPDATE users5 SET balance = {balance + int(num_vubranogo_usera)} WHERE ID = '{id_vubranogo_usera}'")
            db.commit()
            if int(num_vubranogo_usera) > 0:
                bot.send_message(message.chat.id, "Добавлено")
                bot.send_message(id_vubranogo_usera, f"✅ Ваш баланс пополнен на {num_vubranogo_usera} голосов!")
            else:
                bot.send_message(message.chat.id, "Убрано")
    except:
        bot.send_message(message.chat.id, "Вы ввели не число!")
        get_num_vubranogo_usera(message)


@bot.message_handler(commands = ['balance'])
def balance(message):
    global ID
    global FIRST_OR_NO
    FIRST_OR_NO = 0
    for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{message.chat.id}'"):
        bot.send_message(message.chat.id, f"💰 Ваш баланс: {i[0]} ")


@bot.message_handler(commands = ["yesterday_tasks"])
def yesterday_tasks(message):
    TABLE = "yesterday_tasks_of_users"
    Update_Tasks(message.chat.id)
    Send_Tasks(message.chat.id, TABLE)


@bot.message_handler(commands = ["tasks"])
def tasks(message):
    TABLE = "tasks_of_users2"
    Update_Tasks(message.chat.id)
    Send_Tasks(message.chat.id, TABLE)


def Update_Tasks(id):
    global CASH_DATA

    g = localtime()
    DATA = strftime("%m:%d:%Y", g)
    SPLIT_DATA = DATA.split(":")

    if int(SPLIT_DATA[1]) - int(CASH_DATA) == 1:
        CASH_DATA = SPLIT_DATA[1]
        sql3.execute(f"DELETE FROM yesterday_tasks_of_users")
        db3.commit()

        for i in sql2.execute(f"SELECT * FROM tasks_of_users2 WHERE ID = '{id}'"):
            sql3.execute(f"INSERT INTO yesterday_tasks_of_users VALUES(?, ?, ?, ?, ?, ?)",
                         (str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]),
                          str(i[5])))
            db3.commit()

        sql2.execute(f"DELETE FROM tasks_of_users2")
        db2.commit()

    if int(SPLIT_DATA[1]) != int(CASH_DATA):
        CASH_DATA = SPLIT_DATA[1]
        sql3.execute(f"DELETE FROM yesterday_tasks_of_users")
        db3.commit()
        sql2.execute(f"DELETE FROM tasks_of_users2")
        db2.commit()


def Send_Tasks(id, TABLE):
    cash_result = ""
    cash_number = 0
    cash_list = []
    if TABLE == "yesterday_tasks_of_users":
        use_now_list = list_yesterday
    else:
        use_now_list = list_today
    for i in sql3.execute(f"SELECT * FROM {TABLE} WHERE ID = '{id}'"):
        cash_list.append(i)

    cash_check = 0
    for i in range(len(cash_list)):
        if int(i) / 10 in numbers_list:
            if cash_check == 0:
                bot.send_message(id, f"{use_now_list[0]}\n\n" + cash_result,
                                 disable_web_page_preview = True)
            else:
                bot.send_message(id, cash_result, disable_web_page_preview = True)
            cash_result = ""
            cash_check = 1
        cash_result = cash_result + f"""{i + 1}) Ссылка: {cash_list[i][1]}\nКол-во голосов: {cash_list[i][2]}\nТип задания: {cash_list[i][3]}\nВремя ожидания: {cash_list[i][4]}\nВремя добавления: {cash_list[i][5]}\n\n"""
        cash_number += cash_list[i][2]
    if cash_result != "":
        if cash_check == 0:
            bot.send_message(id,
                             f"{use_now_list[0]}\n\n" + cash_result + f"Все голоса: {cash_number}\n" + "Все задания за вчера: /yesterday_tasks",
                             disable_web_page_preview = True)
        else:
            bot.send_message(id,
                             cash_result + f"Все голоса: {cash_number}\n" + "Все задания за вчера: /yesterday_tasks",
                             disable_web_page_preview = True)
    else:
        bot.send_message(id, use_now_list[1])


@bot.message_handler(commands = ['add'])
def add(message):
    global balance
    global new_task

    g = localtime()
    WHEN_TIME3 = strftime("%H.%M", g)
    WHEN_TIME2 = float(WHEN_TIME3) + 3
    WHEN_TIME = str(WHEN_TIME2).replace(".", ":")
    DATA = strftime("%m:%d:%Y", g)
    SPLIT_DATA = DATA.split(":")

    for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{message.chat.id}'"):
        balance = i[0]
    new_task = Add(message.from_user.first_name, message.from_user.username, message.chat.id, message.chat.id,
                   balance, WHEN_TIME, SPLIT_DATA)
    new_task.stage_1()


class Add():
    def __init__(self, NAME, NAME2, ID, CHAT_ID, BALANCE, WHEN_TIME, SPLIT_DATA):
        self.NAME = NAME
        self.NAME2 = NAME2
        self.ID = ID
        self.CHAT_ID = CHAT_ID
        self.FIRST_OR_NO = 0
        self.BALANCE = BALANCE
        self.WHEN_TIME = WHEN_TIME
        self.SPLIT_DATA = SPLIT_DATA

    def stage_1(self):
        global msg
        for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{self.CHAT_ID}'"):
            if int(i[0]) < 7:
                bomj_balance = i[0]
                bot.send_message(self.CHAT_ID, f"""У вас недостаточно голосов (Ваш баланс: {bomj_balance})""")
                return

        if self.FIRST_OR_NO == 0:
            msg = bot.send_message(self.CHAT_ID, "🌎 Введите ссылку на пост или комментарий:")
        bot.register_next_step_handler(msg, self.check_stage_1)

    def check_stage_1(self, msg):
        if msg.text[0:25] == "https://www.reddit.com/r/" or msg.text[0:28] == "https://www.reddit.com/user/":
            self.FIRST_OR_NO = 0
            self.URL = msg.text
            self.stage_2()
        else:
            if msg.text == "/balance":
                for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{msg.chat.id}'"):
                    bot.send_message(msg.chat.id, f"💰 Ваш баланс: {i[0]} ")
                return
            if msg.text == "/add":
                self.FIRST_OR_NO = 0
                self.stage_1()
            else:
                bot.send_message(msg.chat.id,
                                 text = """🚫 Вы ввели неправильную ссылку (URL должна начинаться на https://www.reddit.com/r/ или  https://www.reddit.com/user/) """,
                                 disable_web_page_preview = True)
                self.FIRST_OR_NO = 1
                self.stage_1()

    def stage_2(self):
        global msg

        if self.FIRST_OR_NO == 0:
            msg = bot.send_message(self.CHAT_ID,
                                   f"""🔝 Введите количество голосов от 7 до 1500 (Ваш баланс: {self.BALANCE})""")
        bot.register_next_step_handler(msg, self.check_stage_2)

    def check_stage_2(self, msg):
        try:
            if 1500 >= int(msg.text) >= 7:
                if self.BALANCE >= int(msg.text):
                    self.NUMBER_OF_VOICES = int(msg.text)
                    self.FIRST_OR_NO = 0
                    self.stage_3()
                else:
                    bot.send_message(self.CHAT_ID, """🚫 У вас недостаточно голосов""")
                    self.FIRST_OR_NO = 1
                    self.stage_2()
            else:
                bot.send_message(msg.chat.id, text = """🚫 Количество голосов должно быть от 7 до 1500!""")
                self.FIRST_OR_NO = 1
                self.stage_2()
        except:
            if msg.text == "/add":
                self.FIRST_OR_NO = 0
                self.stage_1()
            else:
                bot.send_message(msg.chat.id, text = """🚫 Нужно ввести количество голосов от 7 до 1500!""")
                self.FIRST_OR_NO = 1
                self.stage_2()

    def stage_3(self):
        global msg
        markup_inline2 = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text = "+", callback_data = "plus")
        button2 = types.InlineKeyboardButton(text = "-", callback_data = "minus")
        markup_inline2.add(button1, button2)

        if self.FIRST_OR_NO == 0:
            msg = bot.send_message(self.CHAT_ID, """Выберите функцию: ➕ (для upvote) или ➖ (для downvote)""",
                                   reply_markup = markup_inline2)

    def check_stage_3(self):
        global FIRST_OR_NO
        global FUNCTION

        self.FIRST_OR_NO = 0
        self.FUNCTION = FUNCTION
        self.stage_4()

    def stage_4(self):
        global msg
        markup_inline = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text = "15 сек", callback_data = "min_time_15sec")
        button2 = types.InlineKeyboardButton(text = "30 сек", callback_data = "min_time_30sec")
        button3 = types.InlineKeyboardButton(text = "1 мин", callback_data = "min_time_1min")
        button4 = types.InlineKeyboardButton(text = "1.5 мин", callback_data = "min_time_1.5min")
        button5 = types.InlineKeyboardButton(text = "2 мин", callback_data = "min_time_2min")
        button6 = types.InlineKeyboardButton(text = "3 мин", callback_data = "min_time_3min")
        button7 = types.InlineKeyboardButton(text = "5 мин", callback_data = "min_time_5min")
        button8 = types.InlineKeyboardButton(text = "10 мин", callback_data = "min_time_10min")
        button9 = types.InlineKeyboardButton(text = "20 мин", callback_data = "min_time_20min")
        button10 = types.InlineKeyboardButton(text = "30 мин", callback_data = "min_time_30min")

        markup_inline.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10)
        bot.send_message(self.CHAT_ID,
                         """⏳Выберите минимальное время ожидания между голосами, максимальное не гарантируется""",
                         reply_markup = markup_inline)

    def result(self):
        global CASH_DATA

        if FUNCTION == "+":
            for i in sql.execute(f"SELECT balance FROM users5 WHERE ID = '{self.CHAT_ID}'"):
                self.BALANCE = i[0]
                sql.execute(
                    f"UPDATE users5 SET balance = {self.BALANCE - int(self.NUMBER_OF_VOICES)} WHERE ID = '{self.CHAT_ID}'")
            db.commit()
            FUNCTION2 = "upvote"
        else:
            FUNCTION2 = "downvote"

        Update_Tasks(self.CHAT_ID)

        sql2.execute(f"INSERT INTO tasks_of_users2 VALUES(?, ?, ?, ?, ?, ?)",
                     (str(self.CHAT_ID), str(self.URL), str(self.NUMBER_OF_VOICES), str(FUNCTION2), str(MIN_TIME),
                      str(self.WHEN_TIME)))
        db2.commit()

        bot.send_message(self.CHAT_ID,
                         f"""🥳 Задание принято!\n\nСсылка: {self.URL}\nКол-во голосов: {self.NUMBER_OF_VOICES}\nТип задания: {FUNCTION2}\nВремя ожидания: {MIN_TIME}\n\n💰Ваш баланс: {self.BALANCE - int(self.NUMBER_OF_VOICES)}""", )
        bot.send_message(1680516364,
                         f"""🥳 Задание принято!\n\nПользователь: {self.NAME} (@{self.NAME2})\nСсылка: {self.URL}\nКол-во голосов: {self.NUMBER_OF_VOICES}\nТип задания: {FUNCTION2}\nВремя ожидания: {MIN_TIME}\n\n💰Баланс пользователя: {self.BALANCE - int(self.NUMBER_OF_VOICES)}""",
                         disable_web_page_preview = True)
        bot.send_message(2136724237, f"""Вставай давай""", disable_web_page_preview = True)


@bot.callback_query_handler(func = lambda call: True)
def save_min_time(call):
    global MIN_TIME
    global FUNCTION

    bot.delete_message(chat_id = call.from_user.id, message_id = call.message.message_id)
    if call.data == "min_time_15sec":
        MIN_TIME = "15 сек"
        new_task.result()
    elif call.data == "min_time_30sec":
        MIN_TIME = "30 сек"
        new_task.result()
    elif call.data == "plus":
        FUNCTION = "+"
        new_task.check_stage_3()
    elif call.data == "minus":
        FUNCTION = "-"
        new_task.check_stage_3()
    elif call.data == "min_time_1min":
        MIN_TIME = "1 мин"
        new_task.result()
    elif call.data == "min_time_1.5min":
        MIN_TIME = "1.5 мин"
        new_task.result()
    elif call.data == "min_time_2min":
        MIN_TIME = "2 мин"
        new_task.result()
    elif call.data == "min_time_3min":
        MIN_TIME = "3 мин"
        new_task.result()
    elif call.data == "min_time_5min":
        MIN_TIME = "5 мин"
        new_task.result()
    elif call.data == "min_time_10min":
        MIN_TIME = "10 мин"
        new_task.result()
    elif call.data == "min_time_20min":
        MIN_TIME = "20 мин"
        new_task.result()
    elif call.data == "min_time_30min":
        MIN_TIME = "30 мин"
        new_task.result()


if __name__ == '__main__':
    bot.polling(none_stop = True)
