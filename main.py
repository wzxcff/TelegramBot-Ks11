import telebot

bot = telebot.TeleBot("7117881292:AAGeVFk-YL1YKuOyoMEkRWv5JaNbcnQWpSo")

@bot.message_handler(content_types=["text"])
def message_handler(message):
    if message.text == "/start":
        bot.send_message(message.chat.id, "Hello world!")


bot.polling(non_stop=True)