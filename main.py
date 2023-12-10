
from time import localtime, strftime
import requests
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import pandas as pd

from databases import User, Tasks

# For tests: 5390773324:AAHdwxZ0ktlIME0eU3_9Znc5ewaJHaVo64U
# Working: 5372598363:AAGVj7WRjJo22Bdd5r-U9-SShOntoz9wr-U
bot = Bot(token="5372598363:AAGVj7WRjJo22Bdd5r-U9-SShOntoz9wr-U")

storage = MemoryStorage()
dp = Dispatcher(bot, storage = storage)


API_KEY = "HLnJFYqPEJiDPxRvovIxFpadsVXGGHXt"
ENDPOINT = "https://api.bestupvotes.com/v1/tasks/"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
EMOTICONS = ["🎉", "🥳", "🕺", "🫡", "💃🏻"]
emoticons_number = 0
NUMBERS_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]

start_buttons = ["/Add", "/Balance", "/Tasks", "/Yesterday_tasks"]
start_keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
start_keyboard.add(*start_buttons)

user = User()
tasks_bd = Tasks()

@dp.message_handler(commands = ['start', "help"])
async def start(message: types.Message):
    if user.get_id(message.from_user.id) is None:
        user.add_user(message.from_user.id, message.from_user.first_name)

    await message.answer(
        f"👋 Привет {message.from_user.first_name}! Я платный бот, который будет помогать тебе апвоутить "
        "или даунвоутить посты и комментарии на Reddit!\n\nЧтобы создать новое задание, напиши или нажми "
        "на команду /add\nЧтобы узнать свой баланс, используй команду /balance\nЧтобы посмотреть список "
        "заданий за сегодня, используйте /tasks", reply_markup=start_keyboard)


@dp.message_handler(commands = ["balance"])
async def start(message: types.Message):
    balance_now = user.get_balance(message.from_user.id)
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

        data_need = str(list_of_tasks[i][10])[:4] + "." + str(list_of_tasks[i][10])[4:]
        data_need = data_need[:7] + "." + data_need[7:]
        cash_result = cash_result + f"""{i + 1}) Ссылка: {list_of_tasks[i][3]}\nКол-во голосов: {list_of_tasks[i][4]}\nТип задания: {list_of_tasks[i][5]}\nВремя ожидания: {list_of_tasks[i][6]}\nЦелевая позиция: {list_of_tasks[i][7]}\nВремя закрепления поста: {list_of_tasks[i][8]}\nВремя добавления: {list_of_tasks[i][9]}   {data_need}\n\n"""
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

    for i in tasks_bd.get_tasks(message.chat.id, time_now):
        list_of_tasks.append(i)

    await take_tasks(message, list_of_tasks, "сегодня")


@dp.message_handler(commands = ["yesterday_tasks"])
async def tasks(message: types.Message):
    list_of_tasks = []
    g = localtime()
    time_now = strftime("%Y%m%d", g)

    for i in tasks_bd.get_tasks(message.chat.id, str(int(time_now)-1)):
        list_of_tasks.append(i)

    await take_tasks(message, list_of_tasks, "вчера")


@dp.message_handler(commands = ["SanyaVerniSotkyBojeYyackeKonchene_excel"])
async def excel(message: types.Message):
    g = localtime()
    time_now = strftime("%H:%M %d.%m.%Y", g)

    df = pd.read_sql_query("SELECT * FROM tasks_of_users", tasks_bd.db2)
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
    print(user.get_all_users())
    for value in user.get_all_users():
        print(value)
        result = result + str(value)[1:-1].replace(",", " |") + "\n"
    await message.answer(result)
    await message.answer("Введите ID пользователя:")


@dp.message_handler(state = Balance_up_form.ID)
async def take_id_selected_user(message: types.Message, state: FSMContext):
    if user.get_id(message.text) is None:
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
    balance_now = user.get_balance(id_selected_user)
    try:
        int(message.text)
    except:
        return await message.answer("Вы ввели не число!")

    user.set_balance(id_selected_user, balance_now + int(message.text))
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
    POSITION_TARGET = State()
    HOLD_HOURS = State()
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


@dp.message_handler(state=Task_form.URL)
async def take_url(message: types.Message, state: FSMContext):
    if message.text[0:25] == "https://www.reddit.com/r/" or message.text[0:28] == "https://www.reddit.com/user/":
        async with state.proxy() as data:
            data['URL'] = message.text
        await Task_form.next()

        balance_now = user.get_balance(message.from_user.id)
        await message.answer(f"Введите количество голосов от 7 до 1500 (Ваш баланс {balance_now})")
    else:
        return await message.answer(
            text = """🚫 Вы ввели неправильную ссылку (URL должна начинаться на https://www.reddit.com/r/ или  https://www.reddit.com/user/) """,
            disable_web_page_preview = True)


@dp.message_handler(state=Task_form.NUMBER_OF_VOICES)
async def take_number_of_voices(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if 1500 >= int(message.text) >= 7:
            balance_now = user.get_balance(message.from_user.id)
            if balance_now >= int(message.text):
                async with state.proxy() as data:
                    data['NUMBER_OF_VOICES'] = message.text
                await Task_form.next()
                markup = types.ReplyKeyboardMarkup(resize_keyboard = True, selective = True)
                markup.add("+", "-")
                await message.answer("Выберите функцию: ➕ (для upvote) или ➖ (для downvote)", reply_markup = markup)
            else:
                return await message.answer("""🚫 У вас недостаточно голосов""")
        else:
            return await message.answer("""🚫 Количество голосов должно быть от 7 до 1500!""")
    else:
        return await message.answer("""🚫 Нужно ввести количество голосов от 7 до 1500!""")


@dp.message_handler(state=Task_form.FUNCTION)
async def take_function(message: types.Message, state: FSMContext):
    if message.text in ["+", "-"]:
        async with state.proxy() as data:
            data['FUNCTION'] = message.text
        await Task_form.next()

        await message.answer("""🎯 Введите целевую позицию от 1 до 10. Задание остановится, как только позиция в HOT будет достигнута. Если вы не хотите использовать функцию, введите значение 0""")
    else:
        return await message.answer("🚫 Нужно ввести! ➕ или ➖ !!!")


@dp.message_handler(state=Task_form.POSITION_TARGET)
async def take_position_target(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if 10 >= int(message.text) >= 0:
            async with state.proxy() as data:
                data['POSITION_TARGET'] = int(message.text)
            await Task_form.next()

            await message.answer("""🤼⏳ Укажите время закрепления поста на целевой позиции от 1 до 24 часов.\nТаким образом если пост начнет падать в HOT, накрутка будет возобновлена, а затем остановлена, как только пост вернется на заданную ранее целевую позицию. Этот процесс будет происходить по кругу, пока не истечет заданное время или количество апвоутов выделенное под данную задачу. Если пост не нужно удерживать, то введите значение 0.""")
        else:
            return await message.answer(
                text="""🚫 Введите число от 0 до 10!""",
                disable_web_page_preview=True)
    else:
        return await message.answer("""🚫 Введите число от 0 до 10!""")

@dp.message_handler(state=Task_form.HOLD_HOURS)
async def take_hold_hours(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if 24 >= int(message.text) >= 0:
            async with state.proxy() as data:
                data['HOLD_HOURS'] = int(message.text)
            await Task_form.next()

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("15 secs", "20 secs", "30 secs", "40 secs", "60 secs", "90 secs", "2 mins", "3 mins", "5 mins",
                       "10 mins", "20 mins", "30 mins")
            await message.answer("⏳Выберите минимальное время ожидания между голосами, максимальное не гарантируется",
                                 reply_markup = markup)
        else:
            return await message.answer(
                text="""🚫 Введите число от 0 до 24!""",
                disable_web_page_preview=True)
    else:
        return await message.answer("""🚫 Введите число от 0 до 24!""")

@dp.message_handler(lambda message: message.text not in ["15 secs", "20 secs", "30 secs", "40 secs",
                                    "60 secs", "90 secs", "2 mins", "3 mins", "5 mins",
                       "10 mins", "20 mins", "30 mins"], state = Task_form.MIN_TIME)
async def process_gender_invalid(message: types.Message):
    return await message.answer("Нажмите пожалуйста на одну из кнопок!")


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

        body = {"url": str(data['URL']),
                "votes": int(data['NUMBER_OF_VOICES']),
                "wait": int(data['MIN_TIME']),
                "position_target": int(data["POSITION_TARGET"]),
                "hold_hours": int(data["HOLD_HOURS"]),
                "type": "post"}
        api_request = requests.post(ENDPOINT, data=body, headers=HEADERS).json()

        print(str(api_request))
        if str(api_request["success"]) == "True":
            global emoticons_number
            emoticons_number += 1

            balance_now = user.get_balance(message.from_user.id)

            await bot.send_message(1680516364,
                                   f"""{EMOTICONS[emoticons_number % 5]} Задание принято!\n\nПользователь: {message.from_user.first_name} (@{message.from_user.username})\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}\n\n💰Баланс пользователя: {balance_now - int(data['NUMBER_OF_VOICES'])}
                                                                       """, disable_web_page_preview = True)
            await bot.send_message(2136724237,
                                   f"""Вставай давай""", disable_web_page_preview = True)
            await message.answer(
                f"""{EMOTICONS[emoticons_number % 5]} Задание принято!\n\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}\nЦелевая позиция: {data["POSITION_TARGET"]}\nВремя закрепления поста: {data["HOLD_HOURS"]}\n\n💰Ваш баланс: {balance_now - int(data['NUMBER_OF_VOICES'])}""", reply_markup = start_keyboard)

            user.set_balance(message.from_user.id, balance_now - int(data['NUMBER_OF_VOICES']))

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

            tasks_bd.set_task(str(message.from_user.id),
                              str(message.from_user.first_name),
                              str(message.from_user.username),
                              str(data['URL']), str(data['NUMBER_OF_VOICES']),
                              str(result_func),
                              str(message.text),
                              str(data["POSITION_TARGET"]),
                              str(data["HOLD_HOURS"]),
                              str(time_need[0]),
                              str(time_need[1].replace(":", "")))
        else:
            try:
                if api_request.get("error").get("message") == "Task with this URL exists and already running.":
                    await bot.send_message(1680516364, f"""ЗАДАНИЯ ЗАПУЩЕНО ПОВТОРНО!""")
                elif api_request.get("error").get("message") == "Insufficient points left for this task. You need to wait for the completion of all tasks to see the real points balance.":
                    await bot.send_message(1680516364,f"""НЕДОСТАТОЧНО БАЛАНСА ДЛЯ ЭТОГО ЗАДАНИЯ""")
            except:
                await bot.send_message(986219819, "ПОПАДОС ІДИ ВИППРАВЛЯЙ")

            await bot.send_message(1680516364, f"""{EMOTICONS[emoticons_number % 5]} Задание НЕ принято!\n\nПользователь: {message.from_user.first_name} (@{message.from_user.username})\nСсылка: {data['URL']}\nКол-во голосов: {data['NUMBER_OF_VOICES']}\nТип задания: {result_func}\nВремя ожидания: {message.text}""", disable_web_page_preview = True)
            # await message.answer("""📛 Пост не найден. Пожалуйста, проверьте, правильно ли указана ссылка.""", )

    await state.finish()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp)
