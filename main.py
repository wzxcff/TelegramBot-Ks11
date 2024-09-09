import telebot
from dotenv import load_dotenv
import os

from telebot import TeleBot

# Initialize token from .env file
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))


@bot.message_handler(content_types=["text"])
def message_handler(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, "Hello world!")


bot.polling(non_stop=True)
