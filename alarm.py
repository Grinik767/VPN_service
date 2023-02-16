import telebot
import os
import datetime
import yadisk
from dotenv import load_dotenv
from bash import Bash
from pivpn import Pivpn
from pickle import load


def check_date(clients):
    need_to_update = []
    for client in clients:
        if client[4].date() <= datetime.datetime.now().date():
            need_to_update.append(client)
    return need_to_update


def make_array_to_update(path_to_table):
    clients = vpn.get_list_clients(py_time=True, src_path=path_to_table)
    res = []
    if clients[0]:
        clients = clients[1]
        res = check_date(clients)
    return res


def send_info_update(phrase, array):
    bot.send_message(MESSAGE.chat.id, f"{phrase}:")
    for client in array:
        if client[3].__class__.__name__ == 'datetime':
            client[3] = client[3].strftime('%d.%m.%Y')
        client[4] = client[4].strftime('%d.%m.%Y')
        if not client[3]:
            client[3] = 'Пробный период'
        bot.send_message(MESSAGE.chat.id, '-'.join(client))


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bash = Bash(host=os.environ['HOST'], user=os.environ['USER'], password=os.environ['PASSWORD'])
disk = yadisk.YaDisk(id=os.environ['DISK_ID'], secret=os.environ['DISK_SECRET'],
                     token=os.environ['DISK_TOKEN'])
vpn = Pivpn(bash, disk)
bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
with open('default_message.pkl', mode='rb') as f:
    MESSAGE = load(f)

if MESSAGE.chat.type == 'private' and MESSAGE.chat.username in os.environ['HAVE_PERMISSION'].split(','):
    need_to_update_1 = make_array_to_update('/VPN/Clients.xlsx')
    need_to_update_2 = make_array_to_update('/VPN/Clients_Russia.xlsx')
    need_to_update_3 = make_array_to_update('/VPN/Clients_Routers.xlsx')
    if len(need_to_update_1) > 0 or len(need_to_update_2) > 0 or len(need_to_update_3) > 0:
        bot.send_message(MESSAGE.chat.id, "Обновите информацию о следующих клиентах:")
        if len(need_to_update_1) > 0:
            send_info_update('Немецкий сервер (Wireguard)', need_to_update_1)
        if len(need_to_update_2) > 0:
            send_info_update('Российский сервер (Wireguard)', need_to_update_2)
        if len(need_to_update_3) > 0:
            send_info_update('Польский сервер (OpenVPN)', need_to_update_3)
