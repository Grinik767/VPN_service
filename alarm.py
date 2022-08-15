import telebot
import os
import datetime
import yadisk
from dotenv import load_dotenv
from bash import Bash
from pivpn import Pivpn
from pickle import load

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
    clients = vpn.get_list_clients(py_time=True)
    if clients[0]:
        clients = clients[1]
        need_to_update = []
        for client in clients:
            if client[-1].date() == datetime.datetime.now().date():
                need_to_update.append(client)
        if need_to_update:
            bot.send_message(MESSAGE.chat.id, "Обновите информацию о следующих клиентах:")
            for client in need_to_update:
                if client[-2].__class__.__name__ == 'datetime':
                    client[-2] = client[-2].strftime('%d.%m.%Y')
                client[-1] = client[-1].strftime('%d.%m.%Y')
                if not client[-2]:
                    client[-2] = 'Пробный период'
                bot.send_message(MESSAGE.chat.id, '-'.join(client))
