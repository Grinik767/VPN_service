import telebot
import os
from dotenv import load_dotenv
from telebot import types

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bot = telebot.TeleBot(os.environ['BOT_TOKEN'])


@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type == 'private' and message.chat.username in os.environ['HAVE_PERMISSION'].split(','):
        bot.send_message(message.chat.id, "Здравствуйте")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, попробуйте позже.")


bot.polling(none_stop=True, interval=0)
