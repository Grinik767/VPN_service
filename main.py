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
    bot.send_message(message.chat.id, "Здравствуйте")


bot.polling(none_stop=True, interval=0)
