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
    clients = vpn.get_list_clients(py_time=True, src_path='/VPN/Clients.xlsx')
    need_to_update_1 = []
    if clients[0]:
        clients = clients[1]
        need_to_update_1 = check_date(clients)
    clients = vpn.get_list_clients(py_time=True, src_path='/VPN/Clients_Russia.xlsx')
    need_to_update_2 = []
    if clients[0]:
        clients = clients[1]
        need_to_update_2 = check_date(clients)
    if len(need_to_update_1) > 0 or len(need_to_update_2) > 0:
        bot.send_message(MESSAGE.chat.id, "Обновите информацию о следующих клиентах:")
        if len(need_to_update_1) > 0:
            bot.send_message(MESSAGE.chat.id, "Европейские сервера:")
            for client in need_to_update_1:
                if client[3].__class__.__name__ == 'datetime':
                    client[3] = client[3].strftime('%d.%m.%Y')
                client[4] = client[4].strftime('%d.%m.%Y')
                if not client[3]:
                    client[3] = 'Пробный период'
                bot.send_message(MESSAGE.chat.id, '-'.join(client))
        if len(need_to_update_2) > 0:
            bot.send_message(MESSAGE.chat.id, "Российский сервер:")
            for client in need_to_update_2:
                if client[3].__class__.__name__ == 'datetime':
                    client[3] = client[3].strftime('%d.%m.%Y')
                client[4] = client[4].strftime('%d.%m.%Y')
                if not client[3]:
                    client[3] = 'Пробный период'
                bot.send_message(MESSAGE.chat.id, '-'.join(client))
