import telebot
import os
import datetime
from dotenv import load_dotenv
from telebot import types

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bot = telebot.TeleBot(os.environ['BOT_TOKEN'])

global MESSAGE, qr, name, place, phone, date_start, date_finish, price, amount_devices, block


@bot.message_handler(commands=["start"])
def start(message):
    global MESSAGE
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/add_user"), types.KeyboardButton("/delete_user"),
                   types.KeyboardButton("/get_info_clients"), types.KeyboardButton("/get_info_server"))
        bot.send_message(message.chat.id, "Доступ разрешен", reply_markup=markup)
        MESSAGE = message
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


@bot.message_handler(commands=["add_user"])
def add_user(message):
    global MESSAGE
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        bot.send_message(message.chat.id, "Введите имя клиента:")
        bot.register_next_step_handler(message, get_name)
        MESSAGE = message
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global qr, MESSAGE, block
    if 'QR' in call.data:
        if call.data == 'QR':
            qr = True
        else:
            qr = False
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Да', callback_data='block'))
        markup.add(types.InlineKeyboardButton(text='Нет', callback_data='no_block'))
        bot.send_message(MESSAGE.chat.id, 'Нужна ли блокировка рекламы:', reply_markup=markup)
    elif 'block' in call.data:
        if call.data == 'block':
            block = True
        else:
            block = False
        bot.send_message(MESSAGE.chat.id, 'Кол-во устройств:')
        bot.register_next_step_handler(MESSAGE, get_amount_devices)


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Площадка ("1" если площадка Авито):')
    bot.register_next_step_handler(message, get_place)


def get_place(message):
    global place
    place = message.text
    bot.send_message(message.chat.id, 'Номер телефона без "+" ("1" если не нужен):')
    bot.register_next_step_handler(message, get_phone)


def get_phone(message):
    global phone
    phone = message.text
    bot.send_message(message.chat.id, 'Дата крайней оплаты ("1" если пробный период"):')
    bot.register_next_step_handler(message, get_date_start)


def get_date_start(message):
    global date_start
    try:
        date_start = message.text
        date_start_check = datetime.datetime.strptime(date_start, "%d.%m.%Y")
    except Exception:
        date_start_check = datetime.datetime.now() + datetime.timedelta(days=365 * 1000)
    if date_start == '1' or date_start_check <= datetime.datetime.now():
        bot.send_message(message.chat.id, 'Оплачен до:')
        bot.register_next_step_handler(message, get_date_finish)
    else:
        bot.send_message(message.from_user.id, 'Неправильный формат даты')
        bot.register_next_step_handler(message, get_date_start)


def get_date_finish(message):
    global date_finish
    try:
        date_finish = message.text
        date_finish_check = datetime.datetime.strptime(date_finish, "%d.%m.%Y")
    except Exception:
        date_finish_check = datetime.datetime.now() - datetime.timedelta(days=365 * 1000)
    if date_finish_check > datetime.datetime.now():
        bot.send_message(message.chat.id, 'Стоимость:')
        bot.register_next_step_handler(message, get_price)
    else:
        bot.send_message(message.from_user.id, 'Неправильный формат даты')
        bot.register_next_step_handler(message, get_date_finish)


def get_price(message):
    global price
    price = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Смартфоны', callback_data='QR'))
    markup.add(types.InlineKeyboardButton(text='ПК', callback_data='no_QR'))
    bot.send_message(message.chat.id, 'Тип устройств (смартфон или ПК):', reply_markup=markup)


def get_amount_devices(message):
    global amount_devices, place, phone, date_start
    amount_devices = message.text
    if phone == "1":
        phone = ""
    if place == "1":
        place = "Авито"
    if date_start == "1":
        date_start = ""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='Да'), types.KeyboardButton(text='Нет'))
    bot.send_message(message.chat.id, f"{name}-{place}-{phone}-{date_start}-{date_finish}-{price}-QR:{qr}-блок:{block}")


bot.polling(none_stop=True, interval=0)
