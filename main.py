import telebot
from telebot import types
from dotenv import load_dotenv
import os
import datetime


# Initialize token from .env file
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))


# Create reply markup for user
userMarkup = types.ReplyKeyboardMarkup(row_width=3)
userBtn_1 = types.KeyboardButton("Розклад на сьогодні")
userBtn_2 = types.KeyboardButton("Розклад на тиждень")
userBtn_3 = types.KeyboardButton("Адмін")
userMarkup.add(userBtn_1, userBtn_2, userBtn_3)

adminMarkupMain = types.ReplyKeyboardMarkup(row_width=3)
adminMainBtn_1 = types.KeyboardButton("Редагувати розклад")
adminMainBtn_2 = types.KeyboardButton("Зробити оповістку")
adminMainBtn_3 = types.KeyboardButton("Список відміченних")
adminMainBtn_4 = types.KeyboardButton("Вийти")
adminMarkupMain.add(adminMainBtn_1, adminMainBtn_2, adminMainBtn_3, adminMainBtn_4)


class ScheduleDay:
    def __init__(self, name, type_of_lesson, instructor, time, date, link):
        self.dayName = name
        self.type = type_of_lesson
        self.instructor = instructor
        self.time = time
        self.date = date
        self.link = link

schedule = {
    "Monday": [
        ScheduleDay("Дискретна математика", "Лабораторна", "Аршава Олена Олександрівна", "10:10 - 11:30", "09.09", "www.zoom.com")
    ],
    "Tuesday": [
        ScheduleDay("Алгоритмізація та структури данних", "Лекція", "Струков Михайло Володимирович", "10:10 - 11:30", "10.09", "https://www.youtube.com"),
        ScheduleDay("Вища математика", "Практика", "Ніколенко Ірина Генадіївна", "12:00 - 13:20", "10.09", "www.zoom.com")
    ],
}


def send_schedule_today(message):
    today = datetime.datetime.now().strftime('%A')

    if today in schedule:
        today_lessons = schedule[today]

        formatted_message = "Сьогодні у вас:\n"

        for i, lesson in enumerate(today_lessons, start=1):
            formatted_message += (
                f"\nПара {i}:\n"
                f"*Дисципліна:* {lesson.dayName}\n"
                f"*Тип заняття:* {lesson.type}\n"
                f"*Викладач:* {lesson.instructor}\n"
                f"*Час:* {lesson.time}\n"
                f"*Дата:* {lesson.date}\n"
                f"*Посилання:* {lesson.link}\n"
            )
    else:
        formatted_message = "На сьогодні немає занять."

    bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown", disable_web_page_preview=True)


def send_schedule_weekly(message):
    formatted_message = "Розклад на тиждень:\n"

    for day, lessons in schedule.items():
        formatted_message += f"\n*{day}:*\n"

        if lessons:
            for i, lesson in enumerate(lessons, start=1):
                formatted_message += (
                    f"\n*Пара:* {i}:\n"
                    f"*Дисципліна:* {lesson.dayName}\n"
                    f"*Тип заняття:* {lesson.type}\n"
                    f"*Викладач:* {lesson.instructor}\n"
                    f"*Час:* {lesson.time}\n"
                    f"*Дата:* {lesson.date}\n"
                    f"*Посилання:* {lesson.link}\n"
                )
        else:
            formatted_message += "На цей день немає занять.\n"

    bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown", disable_web_page_preview=True)


def log(tag, message, user_id=None, user_name=None):
    if user_id and user_name:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}] - [USER_NAME: {user_name}]: {message}")
    elif user_id:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}]: {message}")
    else:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}]: {message}")


@bot.message_handler(commands=['start', 'help', 'schedule', 'scheduleAll', 'admin'])
def commands_handler(message):
    log("info", f"{message.text}", user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "/start":
        with open("subscribed.txt", "r+", encoding="utf-8") as file:
            read_file = file.readlines()
            if str(f"{message.from_user.id}, ") not in read_file:
                file.write(f"{str(message.from_user.id)}, ")
        bot.send_message(message.chat.id, f"Привіт, {message.from_user.first_name}!\nМене було створено спеціально для групи *КС-11*.\nАдміністраторам - /login", parse_mode="Markdown", reply_markup=userMarkup)
    elif message.text == "/help":
        bot.send_message(message.chat.id, "*Для студентів*\n\n/schedule - Розклад пар на сьогодні\n/scheduleAll - Розклад пар на тиждень\n\n*Для адміністраторів*\n\n/login", parse_mode="Markdown")
    elif message.text == "/schedule":
        send_schedule_today(message)
    elif message.text == "/scheduleAll":
        send_schedule_weekly(message)
    elif message.text == "/admin":
        bot.send_message(message.chat.id, f"Вітаю в адмін панелі, {message.from_user.first_name}!", reply_markup=adminMarkupMain)


@bot.message_handler(content_types=["text"])
def message_handler(message):
    log("info", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "Розклад на сьогодні":
        send_schedule_today(message)
    elif message.text == "Розклад на тиждень":
        send_schedule_weekly(message)
    elif message.text == "Адмін":
        bot.send_message(message.chat.id, f"Вітаю в адмін панелі, *{message.from_user.first_name}*!", reply_markup=adminMarkupMain, parse_mode="Markdown")
    elif message.text == "Редагувати розклад":
        pass
    elif message.text == "Зробити оповістку":
        pass
    elif message.text == "Список відміченних":
        pass
    elif message.text == "Вийти":
        bot.send_message(message.chat.id, "Дякую :)", reply_markup=userMarkup)



bot.polling(non_stop=True)
