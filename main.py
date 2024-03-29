import telebot
import os
import datetime
import yadisk
from dotenv import load_dotenv
from telebot import types
from bash import Bash
from pivpn import Pivpn
from text_func import *

global MESSAGE, qr, name, place, phone, date_start, date_finish, price, amount_devices, block, number_to_delete, \
    act_button
MESSAGE = None
act_button = False

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bash = Bash(host=os.environ['HOST'], user=os.environ['USER'], password=os.environ['PASSWORD'])
disk = yadisk.YaDisk(id=os.environ['DISK_ID'], secret=os.environ['DISK_SECRET'],
                     token=os.environ['DISK_TOKEN'])
vpn = Pivpn(bash, disk)

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])


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


@bot.message_handler(commands=['delete_user'])
def delete_user(message):
    global MESSAGE
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        MESSAGE = message
        clients = vpn.get_list_clients()
        if clients[0]:
            clients = '\n'.join(
                ['-'.join(['данные отсутствуют' if not par else par for par in client]) + '\n' for client in
                 clients[1]])
            send_split_message(bot, message.chat.id,
                               split_message(f"Выберите клиента для удаления (номер):\n\n{clients}"))
            bot.register_next_step_handler(message, get_number_to_delete)
        else:
            bot.send_message(message.chat.id, "Произошла ошибка")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


@bot.message_handler(commands=['get_info_clients'])
def get_info_clients(message):
    global MESSAGE
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        clients = vpn.get_list_clients()
        MESSAGE = message
        if clients[0]:
            clients = '\n'.join(
                ['-'.join(['данные отсутствуют' if not par else par for par in client]) + '\n' for client in
                 clients[1]])
            send_split_message(bot, message.chat.id, split_message(clients))
        else:
            bot.send_message(message.chat.id, "Произошла ошибка")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


@bot.message_handler(commands=['get_info_server'])
def get_info_server(message):
    global MESSAGE
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        users = vpn.get_list_users(numbers=True)
        MESSAGE = message
        if users[0]:
            users = '\n'.join(users[1])
            send_split_message(bot, message.chat.id, split_message(users))
        else:
            bot.send_message(message.chat.id, "Произошла ошибка")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global qr, MESSAGE, block, act_button
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
    elif 'add' in call.data:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/add_user"), types.KeyboardButton("/delete_user"),
                   types.KeyboardButton("/get_info_clients"), types.KeyboardButton("/get_info_server"))
        if call.data == 'yes_add' and act_button:
            result = vpn.add_new_client(name=name, date_s=date_start, date_f=date_finish, cost=price,
                                        count=int(amount_devices), platform=place, phone=phone, qr=qr, no_ads=block)
            if result[0]:
                if qr:
                    nickname = result[1]
                    for i in range(1, int(amount_devices) + 1):
                        bot.send_photo(MESSAGE.chat.id, open(f'{nickname}_{i}.jpg', 'rb'))
                        os.remove(f'{nickname}_{i}.jpg')
                else:
                    links = result[1]
                    for link in links:
                        bot.send_message(MESSAGE.chat.id, link)
                bot.send_message(MESSAGE.chat.id, "Пользователь добавлен", reply_markup=markup)
            else:
                bot.send_message(MESSAGE.chat.id, "Произошла ошибка", reply_markup=markup)
        elif act_button:
            bot.send_message(MESSAGE.chat.id, "Возвращаюсь в меню", reply_markup=markup)
        act_button = False
    elif 'delete' in call.data:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/add_user"), types.KeyboardButton("/delete_user"),
                   types.KeyboardButton("/get_info_clients"), types.KeyboardButton("/get_info_server"))
        if call.data == 'yes_delete' and act_button:
            try:
                if vpn.delete_client(int(number_to_delete))[0]:
                    bot.send_message(MESSAGE.chat.id, "Пользователь удален", reply_markup=markup)
                else:
                    bot.send_message(MESSAGE.chat.id, "Произошла ошибка", reply_markup=markup)
            except ValueError:
                bot.send_message(MESSAGE.chat.id, "Произошла ошибка", reply_markup=markup)
        elif act_button:
            bot.send_message(MESSAGE.chat.id, "Возвращаюсь в меню", reply_markup=markup)
        act_button = False


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
    global price, act_button
    price = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Смартфоны', callback_data='QR'))
    markup.add(types.InlineKeyboardButton(text='ПК', callback_data='no_QR'))
    bot.send_message(message.chat.id, 'Тип устройств (смартфон или ПК):', reply_markup=markup)
    act_button = True


def get_amount_devices(message):
    global amount_devices, place, phone, date_start
    amount_devices = message.text
    phone_to_check = phone
    date_start_to_check = date_start
    if qr:
        qr_to_check = 'QR коды'
    else:
        qr_to_check = 'Файлы'
    if block:
        block_to_check = 'С блокировкой рекламы'
    else:
        block_to_check = 'Без блокировки рекламы'
    if phone == "1":
        phone = ""
        phone_to_check = 'Телефон не нужен'
    if place == "1":
        place = "Авито"
    if date_start == "1":
        date_start = ""
        date_start_to_check = 'Пробный период'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Да', callback_data='yes_add'))
    markup.add(types.InlineKeyboardButton(text='Нет', callback_data='no_add'))
    data_to_check = f"Данные верны?\n\n{name}-{place}-{phone_to_check}-{date_start_to_check}-{date_finish}-{qr_to_check}-{block_to_check}-{price}р-{amount_devices} устройство/а"
    bot.send_message(message.chat.id, data_to_check, reply_markup=markup)


def get_number_to_delete(message):
    global number_to_delete, act_button
    number_to_delete = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Да', callback_data='yes_delete'))
    markup.add(types.InlineKeyboardButton(text='Нет', callback_data='no_delete'))
    try:
        clients = vpn.get_list_clients()
        client_name = clients[1][int(number_to_delete) - 1][1]
        client_nickname = clients[1][int(number_to_delete) - 1][5]
        bot.send_message(message.chat.id,
                         f"Вы уверены, что хотите удалить пользователя под номером {number_to_delete} ({client_name}-{client_nickname})?",
                         reply_markup=markup)
    except Exception as err:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("/add_user"), types.KeyboardButton("/delete_user"),
                   types.KeyboardButton("/get_info_clients"), types.KeyboardButton("/get_info_server"))
        bot.send_message(MESSAGE.chat.id, "Произошла ошибка")
        bot.send_message(MESSAGE.chat.id, "Возвращаюсь в меню", reply_markup=markup)
    act_button = True


bot.polling(none_stop=True, interval=0)
