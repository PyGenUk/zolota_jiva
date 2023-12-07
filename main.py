import sqlite3
from time import localtime, strftime
import requests
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import pandas as pd

bot = Bot(token = "5372598363:AAGVj7WRjJo22Bdd5r-U9-SShOntoz9wr-U")

storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)

db = sqlite3.connect('mydatabase5.db', check_same_thread = False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users(
    ID INT,
    balance INT,
    name STR
)""")
db.commit()

db2 = sqlite3.connect('tasks.db', check_same_thread = False)
sql2 = db2.cursor()
sql2.execute("""CREATE TABLE IF NOT EXISTS tasks_of_users(
    ID STR,
    FIRST_NAME STR,
    USERNAME STR,
    URL STR,
    NUMBER_OF_VOICES STR, 
    FUNCTION STR, 
    MIN_TIME STR,
    TIME_CREATED STR,
    DATA_CREATED STR
)""")
db2.commit()

API_KEY = "HLnJFYqPEJiDPxRvovIxFpadsVXGGHXt"
ENDPOINT = "https://api.bestupvotes.com/v1/tasks/"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
EMOTICONS = ["🎉", "🥳", "🕺", "🫡", "💃🏻"]
emoticons_number = 0
NUMBERS_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]

start_buttons = ["/Add", "/Balance", "/Tasks", "/Yesterday_tasks"]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
start_keyboard.add(*start_buttons)


@dp.message_handler(commands = ['start', "help"])
async def start(message: types.Message):
    if sql.execute(f"SELECT ID FROM users WHERE ID = '{message.from_user.id}'").fetchone() is None:
        sql.execute(f"INSERT INTO users VALUES(?, ?, ?)", (message.from_user.id, 0, message.from_user.first_name))
        db.commit()

    await message.answer(
        f"👋 Привет {message.from_user.first_name}! Я платный бот, который будет помогать тебе апвоутить "
        "или даунвоутить посты и комментарии на Reddit!\n\nЧтобы создать новое задание, напиши или нажми "
        "на команду /add\nЧтобы узнать свой баланс, используй команду /balance\nЧтобы посмотреть список "
        "заданий за сегодня, используйте /tasks", reply_markup = start_keyboard)


@dp.message_handler(commands = ["balance"])
async def start(message: types.Message):
    balance_now = sql.execute(f"SELECT * FROM users WHERE ID = '{message.from_user.id}'").fetchone()[1]
    await message.answer(f"💰 Ваш баланс: {balance_now}")


async def take_tasks(message, list_of_tasks, today_or_yesterday):
    cash_result = ""
    cash_check = 0

    for i in range(len(list_of_tasks)):
        if int(i) / 10 in NUMBERS_LIST:
            if cash_check == 0:
                await message.answer(f"📝 Список заданий за {today_or_yesterday}:\n\n" + cash_result,
                                     disable_web_page_preview = True)
            else:
                await message.answer(cash_result, disable_web_page_preview = True)
            cash_result = ""
            cash_check = 1

        data_need = str(list_of_tasks[i][8])[:4] + "." + str(list_of_tasks[i][8])[4:]
        data_need = data_need[:7] + "." + data_need[7:]
        cash_result = cash_result + f"""{i + 1}) Ссылка: {list_of_tasks[i][3]}\nКол-во голосов: {list_of_tasks[i][4]}\nТип задания: {list_of_tasks[i][5]}\nВремя ожидания: {list_of_tasks[i][6]}\nВремя добавления: {list_of_tasks[i][7]} {data_need}\n\n"""
    if cash_result != "":
        if cash_check == 0:
            if today_or_yesterday == "сегодня":
                await message.answer(
                    f"📝 Список заданий за {today_or_yesterday}:\n\n" + cash_result + "Все задания за вчера: /yesterday_tasks",
                    disable_web_page_preview = True)
            else:
                await message.answer(f"📝 Список заданий за {today_or_yesterday}:\n\n" + cash_result,
                    disable_web_page_preview = True)
        else:
            if today_or_yesterday == "сегодня":
                await message.answer(cash_result + "Все задания за вчера: /Yesterday_tasks",
                    disable_web_page_preview = True)
            else:
                await message.answer(cash_result, disable_web_page_preview = True)
    else:
        await message.answer(f"Вы ещё не запускали задания {today_or_yesterday} 🥲")


@dp.message_handler(commands = ["tasks"])
async def tasks(message: types.Message):
    list_of_tasks = []
    g = localtime()
    time_now = strftime("%Y%m%d", g)

    for i in sql2.execute(f"SELECT * FROM tasks_of_users WHERE ID = '{message.chat.id}' AND DATA_CREATED = '{time_now}'"):
        list_of_tasks.append(i)

    await take_tasks(message, list_of_tasks, "сегодня")


@dp.message_handler(commands = ["yesterday_tasks"])
async def tasks(message: types.Message):
    list_of_tasks = []
    g = localtime()
    time_now = strftime("%Y%m%d", g)

    for i in sql2.execute(f"SELECT * FROM tasks_of_users WHERE ID = '{message.chat.id}' AND DATA_CREATED = '{str(int(time_now)-1)}'"):
        list_of_tasks.append(i)

    await take_tasks(message, list_of_tasks, "вчера")


@dp.message_handler(commands = ["SanyaVerniSotkyBojeYyackeKonchene_excel"])
async def excel(message: types.Message):
    g = localtime()
    time_now = strftime("%d.%m.%Y", g)

    df = pd.read_sql_query("SELECT * FROM tasks_of_users", db2)
    df.to_excel(f'All tasks {time_now} .xlsx', index = False)
    await message.reply_document(open(f'All tasks {time_now} .xlsx', 'rb'))


"""********************************** Начало опроса для поповнення рахунків ****************************************"""


class Balance_up_form(StatesGroup):
    ID = State()
    NUMBER_OF_VOICES = State()


@dp.message_handler(state = '*', commands = 'stop')
@dp.message_handler(Text(equals = 'stop', ignore_case = True), state = '*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Stoped')


@dp.message_handler(commands = 'SanyaVerniSotkyBojeYyackeKonchene', state = None)
async def balance_up_form_start(message: types.Message):
    await Balance_up_form.ID.set()

    await message.answer("Список пользователей:")
    result = ""
    for value in sql.execute("SELECT * FROM users"):
        result = result + str(value)[1:-1].replace(",", " |") + "\n"
    await message.answer(result)
    await message.answer("Введите ID пользователя:")


@dp.message_handler(state = Balance_up_form.ID)
async def take_id_selected_user(message: types.Message, state: FSMContext):
    if sql.execute(f"SELECT ID FROM users WHERE ID = '{message.text}'").fetchone() is None:
        await message.answer("Такого пользователя нет:")
    else:
        async with state.proxy() as data:
            data['ID'] = message.text
        await Balance_up_form.next()
        await message.answer("💵 Введите кол-во голосов, которое нужно добавить или убрать:")


@dp.message_handler(state = Balance_up_form.NUMBER_OF_VOICES)
async def take_number_of_voices(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id_selected_user = data['ID']
    balance_now = sql.execute(f"SELECT * FROM users WHERE ID = '{id_selected_user}'").fetchone()[1]
    try:
        int(message.text)
    except:
        return await message.answer("Вы ввели не число!")

    sql.execute(f"UPDATE users SET balance = {balance_now + int(message.text)} WHERE ID = '{id_selected_user}'")
    db.commit()
    if int(message.text) > 0:
        await message.answer("Добавлено")
        await bot.send_message(id_selected_user, f"✅ Ваш баланс пополнен на {message.text} голосов!")
    elif int(message.text) == 0:
        await message.answer("Зачем 0?")
    else:
        await message.answer("Убрано")
    await state.finish()


"""********************************** Начало опроса для завдання ***************************************************"""


class Task_form(StatesGroup):
    URL = State()
    NUMBER_OF_VOICES = State()
    FUNCTION = State()
    MIN_TIME = State()


@dp.message_handler(state = '*', commands = 'stop')
@dp.message_handler(Text(equals = 'stop', ignore_case = True), state = '*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Stoped')


@dp.message_handler(commands = 'add', state = None)
async def form_start(message: types.Message):
    await Task_form.URL.set()
    await message.answer(
        "🌎 Введите ссылку на пост или комментарий: \n\n(Вы в любой момент можете остановить создания задания с помощью команды /stop)", )


@dp.message_handler(state = Task_form.URL)
async def take_url(message: types.Message, state: FSMContext):
    if message.text[0:25] == "https://www.reddit.com/r/" or message.text[0:28] == "https://www.reddit.com/user/":
        async with state.proxy() as data:
            data['URL'] = message.text
        await Task_form.next()

        balance_now = sql.execute(f"SELECT * FROM users WHERE ID = '{message.from_user.id}'").fetchone()[1]
        await message.answer(f"Введите количество голосов от 7 до 1500 (Ваш баланс {balance_now})")
    else:
        return await message.answer(
            text = """🚫 Вы ввели неправильную ссылку (URL должна начинаться на https://www.reddit.com/r/ или  https://www.reddit.com/user/) """,
            disable_web_page_preview = True)


@dp.message_handler(state = Task_form.NUMBER_OF_VOICES)
async def take_number_of_voices(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if 1500 >= int(message.text) >= 7:
            balance_now = sql.execute(f"SELECT * FROM users WHERE ID = '{message.from_user.id}'").fetchone()[1]
            if balance_now >= int(message.text):
                async with state.proxy() as data:
                    data['NUMBER_OF_VOICES'] = message.text
                await Task_form.next()
                markup = types.ReplyKeyboardMarkup(resize_keyboard = True, selective = True)
                markup.add("+", "-")
                await message.answer("Выберите функцию: ➕ (для upvote) или ➖ (для downvote)", reply_markup = markup)
            else:
                return await message.reply("""🚫 У вас недостаточно голосов""")
        else:
            return await message.reply("""🚫 Количество голосов должно быть от 7 до 1500!""")
    else:
        return await message.reply("""🚫 Нужно ввести количество голосов от 7 до 1500!""")


@dp.message_handler(state = Task_form.FUNCTION)
async def take_function(message: types.Message, state: FSMContext):
    if message.text in ["+", "-"]:
        async with state.proxy() as data:
            data['FUNCTION'] = message.text
        await Task_form.next()

        markup = types.ReplyKeyboardMarkup(resize_keyboard = True, selective = True)
        markup.add("15 secs", "30 secs", "60 secs", "90 secs", "3 mins", "5 mins",
                   "10 mins", "20 mins", "30 mins")

        await message.answer("⏳Выберите минимальное время ожидания между голосами, максимальное не гарантируется",
                             reply_markup = markup)
    else:
        return await message.answer("🚫 Нужно ввести! ➕ или ➖ !!!")


@dp.message_handler(lambda message: message.text not in ["15 secs", "30 secs", "60 secs", "90 secs", "3 mins", "5 mins",
                                                         "10 mins", "20 mins", "30 mins"], state = Task_form.MIN_TIME)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Нажмите пожалуйста на одну из кнопок!")


@dp.message_handler(state = Task_form.MIN_TIME)
async def take_min_time(message: types.Message, state: FSMContext):
    split = message.text.split()
    async with state.proxy() as data:

        if split[1] == "mins":
            data['MIN_TIME'] = int(split[0]) * 60
        else:
            data['MIN_TIME'] = int(split[0])
        if data["FUNCTION"] == "+":
            result_func = "upvote"
        else:
            result_func = "downvote"

        body = {"url": str(data['URL']), "votes": int(data['NUMBER_OF_VOICES']), "wait": int(data['MIN_TIME']), "type": "post"}
        api_request = requests.post(ENDPOINT, data = body, headers = HEADERS).json()

        print(str(api_request))
        if str(api_request["success"]) == "True":
            global emoticons_number
            emoticons_number += 1

            balance_now = sql.execute(f"SELECT * FROM users WHERE ID = '{message.from_user.id}'").fetchone()[1]

            await bot.send_message(1680516364,
                                   f"""{EMOTICONS[emoticons_number % 5]} Задание принято!\n\nПользователь: {message.from_user.first_name} (@{message.from_user.username})\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}\n\n💰Баланс пользователя: {balance_now - int(data['NUMBER_OF_VOICES'])}
                                                                       """, disable_web_page_preview = True)
            await bot.send_message(2136724237,
                                   f"""Вставай давай""", disable_web_page_preview = True)
            await message.answer(
                f"""{EMOTICONS[emoticons_number % 5]} Задание принято!\n\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}\n\n💰Ваш баланс: {balance_now - int(data['NUMBER_OF_VOICES'])}""", reply_markup = start_keyboard)

            sql.execute(
                f"UPDATE users SET balance = {balance_now - int(data['NUMBER_OF_VOICES'])} WHERE ID = '{message.from_user.id}'")
            db.commit()

            g = localtime()
            time_now = strftime("%H:%M:%Y:%m:%d", g)
            time_split = time_now.split(":")
            if 21 > int(time_split[0]) > 6:
                time_split[0] = str((int(time_split[0]) + 3))
                cash = ":".join(time_split)
                cash = cash[:5] + " " + cash[5 + 1:]
                time_need = cash.split(" ")
            else:
                time_split[0] = "0" + str((int(time_split[0]) + 3) % 24)
                cash = ":".join(time_split)
                cash = cash[:5] + " " + cash[5 + 1:]
                time_need = cash.split(" ")

            sql2.execute(f"INSERT INTO tasks_of_users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (str(message.from_user.id), str(message.from_user.first_name), str(message.from_user.username),
                              str(data['URL']), str(data['NUMBER_OF_VOICES']),
                              str(result_func), str(message.text), str(time_need[0]), str(time_need[1].replace(":", ""))))
            db2.commit()

        else:
            try:
                if api_request.get("error").get("message") == "Task with this URL exists and already running.":
                    await bot.send_message(1680516364, f"""ЗАДАНИЯ ЗАПУЩЕНО ПОВТОРНО!""")
                elif api_request.get("error").get("message") == "Insufficient points left for this task. You need to wait for the completion of all tasks to see the real points balance.":
                    await bot.send_message(1680516364,f"""НЕДОСТАТОЧНО БАЛАНСА ДЛЯ ЭТОГО ЗАДАНИЯ""")
            except:
                bot.send_message(986219819, "ПОПАДОС ІДИ ВИППРАВЛЯЙ")

            await bot.send_message(1680516364, f"""{EMOTICONS[emoticons_number % 5]} Задание НЕ принято!\n\nПользователь: {message.from_user.first_name} (@{message.from_user.username})\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}""", disable_web_page_preview = True)
            # await message.answer("""📛 Пост не найден. Пожалуйста, проверьте, правильно ли указана ссылка.""", )

    await state.finish()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp)
