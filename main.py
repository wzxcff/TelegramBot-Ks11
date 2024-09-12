import csv

import telebot
from telebot import types
from dotenv import load_dotenv
import os
import datetime
from random import randint as rnd

def build_buttons(admin_markup, labels):
    buttons = []
    for label in labels:
        button = types.KeyboardButton(label)
        buttons.append(button)
    admin_markup.add(*buttons)


# Initialize token from .env file
load_dotenv()
bot = telebot.TeleBot(os.getenv("TOKEN"))
admins = os.getenv("ADMINS")
scheduleFiles = ["Monday.csv", "Tuesday.csv", "Wednesday.csv", "Thursday.csv", "Friday.csv", "Saturday.csv"]
today = datetime.datetime.now().strftime('%A')

pingedUsers = {}
links = {
    "Алгоритмізація та структури данних": "https://meet.google.com/dbf-jyxe-wco",
    "Вища математика": "https://us02web.zoom.us/j/85968110027\nКод: Nikolenko1",
    "Дискретна математика": "https://us02web.zoom.us/j/87437049146?",
    "Університетські студії та вступ до комп'ютерних наук": "https://meet.google.com/jnn-nrgu-xpt",
    "Іноземна мова": "https://us05web.zoom.us/j/3749499044?pwd=DAta1gOcsU3yUStFEn7gbSuTJVxcbR.1",
    "Історія України: Цивілізаційний вимір": "https://us05web.zoom.us/j/4833912715?pwd=aD1SU2RTMVpKaUJ4Q3Z6Ry80ak5IZz09",
    "Кураторська година": "https://us02web.zoom.us/j/82682991107\nКод: Nikolenko1"
}

# Create reply markup for user
userMarkup = types.ReplyKeyboardMarkup(row_width=3)
userBtn_labels = ["Розклад на сьогодні", "Розклад на тиждень", "Адмін", "Конфідеційність", "Відмітитись на парах", "Підтримати"]
build_buttons(userMarkup, userBtn_labels)

userPingMarkup = types.ReplyKeyboardMarkup(row_width=3)
userPingBtn_labels = ["Першій парі", "Другій парі", "Третій парі", "Четвертій парі", "П'ятій парі", "Шостій парі", "Скасувати відмітку", "Повернутись", "На всіх"]
build_buttons(userPingMarkup, userPingBtn_labels)

adminMarkupMain = types.ReplyKeyboardMarkup(row_width=3)
adminMarkupMain_labels = ["Редагувати розклад", "Зробити оповістку", "Список відміченних", "Повернутись"]
build_buttons(adminMarkupMain, adminMarkupMain_labels)

adminAlert = types.ReplyKeyboardMarkup()
adminAlertBtn_1 = types.KeyboardButton("Скасувати оповістку")
adminAlert.add(adminAlertBtn_1)

adminEditSchedule = types.ReplyKeyboardMarkup(row_width=3)
adminEditSchedule_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Скасувати"]
build_buttons(adminEditSchedule, adminEditSchedule_labels)

adminModeSchedule = types.ReplyKeyboardMarkup(row_width=1)
adminModeScheduleBtn_1 = types.KeyboardButton("Очистити розклад на день")
adminModeScheduleBtn_2 = types.KeyboardButton("Додати пару")
adminModeScheduleBtn_3 = types.KeyboardButton("Скасувати")
adminModeSchedule.add(adminModeScheduleBtn_2, adminModeScheduleBtn_1, adminModeScheduleBtn_3)

adminTypeLesson = types.ReplyKeyboardMarkup(row_width=3)
lesson_types = ["Лекція", "Практика", "Лабораторна", "Контроль", "Скасувати", "Екзамен"]
build_buttons(adminTypeLesson, lesson_types)

adminTimeSchedule = types.ReplyKeyboardMarkup(row_width=3)
timeSchedule = ["10:10 - 11:30", "12:00 - 13:20", "13:40 - 15:00", "15:20 - 16:40", "17:00 - 18:20", "18:40 - 20:00", "Скасувати"]
build_buttons(adminTimeSchedule, timeSchedule)

adminLesson = types.ReplyKeyboardMarkup(row_width=3)
lessons = ["Алгоритмізація та структури данних", "Вища математика", "Дискретна математика", "Університетські студії та вступ до комп'ютерних наук", "Іноземна мова", "Історія України: Цивілізаційний вимір", "Кураторська година", "Скасувати", " "]
build_buttons(adminLesson, lessons)

adminInstructors = types.ReplyKeyboardMarkup(row_width=3)
instructors = ["Струков Михайло Володимирович", "Ніколенко Ірина Генадіївна", "Аршава Олена Олександрівна", "Шкабура Ярослав Іванович", "Нестеренко Вікторія Олександрівна", "Єршова Ілона Шонівна", "Зінов'єв Дмитро Васильович та Ткачук Микола Вячеславович", "Зінов'єв Дмитро Васильович", "Ткачук Микола Вячеславович", "Скасувати"]
build_buttons(adminInstructors, instructors)

adminLinks = types.ReplyKeyboardMarkup(row_width=3)
build_buttons(adminLinks, lessons[:-1])

adminIsItCorrect = types.ReplyKeyboardMarkup(row_width=1)
adminIsItCorrectBtn_1 = types.KeyboardButton("Так, вірно")
adminIsItCorrectBtn_2 = types.KeyboardButton("Ні, скинути")
adminIsItCorrect.add(adminIsItCorrectBtn_1, adminIsItCorrectBtn_2)

adminPingedUsers = types.ReplyKeyboardMarkup(row_width=1)
adminPingedUsers_labels = ["Подивитись", "Очистити", "Повернутись"]
build_buttons(adminPingedUsers, adminPingedUsers_labels)



class ScheduleDay:
    def __init__(self, name, type_of_lesson, instructor, time, link):
        self.name = name
        self.type = type_of_lesson
        self.instructor = instructor
        self.time = time
        self.link = link


def load_csv():
    for file in scheduleFiles:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8", newline="") as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                writer.writerow(["day", "name", "type", "instructor", "time", "link"])
            log("CSV - created", f"successfully created {file}")
        else:
            log("CSV - found", f"found already created {file} file")

def read_csv_today(message):
    try:
        if today == "Sunday":
            bot.send_message(message.chat.id, "У неділю пар немає, відпочивайте :)")
        else:
            with open(f"{today}.csv", "r", encoding="utf-8", newline="") as csv_file:
                reader = csv.reader(csv_file)
                formatted_message = f"Розклад на *{today}*\n\n"
                next(reader)
                for i, item in enumerate(reader, start=1):
                    if item:
                        lesson_created = ScheduleDay(item[1], item[2], item[3], item[4], item[5])
                        formatted_message += (
                            f"\n*Пара {i}:*\n"
                            f"*Дисципліна:* {lesson_created.name}\n"
                            f"*Тип:* {lesson_created.type}\n"
                            f"*Викладач:* {lesson_created.instructor}\n"
                            f"*Час:* {lesson_created.time}\n"
                            f"*Посилання:* {lesson_created.link}\n\n"
                        )
                if formatted_message == f"Розклад на *{today}*\n\n":
                    formatted_message += "Пар немає."
                    bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown", disable_web_page_preview=True)
                else:
                    bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown", disable_web_page_preview=True)
    except FileNotFoundError:
        log("error - read_csv_today", f"Cannot read '{today}.csv'! File exists?")

def read_csv_all(message):
    formatted_to_send = ""
    try:
        for file in scheduleFiles:
            formatted_to_send += "——————————————————\n"
            with open(f"{file}", "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                formatted_message = f"\nРозклад на *{"".join(file.split(".")[0])}*\n\n"
                next(reader)
                for i, item in enumerate(reader, start=1):
                    if item:
                        lesson_created = ScheduleDay(item[1], item[2], item[3], item[4], item[5])
                        formatted_message += (
                            f"\n*Пара {i}:*\n"
                            f"*Дисципліна:* {lesson_created.name}\n"
                            f"*Тип:* {lesson_created.type}\n"
                            f"*Викладач:* {lesson_created.instructor}\n"
                            f"*Час:* {lesson_created.time}\n"
                            f"*Посилання:* {lesson_created.link}\n\n"
                        )
                if formatted_message == f"\nРозклад на *{"".join(file.split(".")[0])}*\n\n":
                    formatted_message += "\nПар немає.\n\n"
                    formatted_to_send += formatted_message
                else:
                    formatted_to_send += formatted_message
        bot.send_message(message.chat.id, formatted_to_send, parse_mode="Markdown", disable_web_page_preview=True)
    except FileNotFoundError:
        log("error - read_csv_all", f"Cannot read schedule.csv! File exists?")

def write_csv(day, mode, info=None):
    try:
        if info:
            if str(mode).lower() == "додати пару":
                with open(f"{day}.csv", "a", encoding="utf-8", newline="") as csv_file:
                    csv.writer(csv_file, delimiter=",").writerow(info)
        elif str(mode).lower() == "очистити розклад на день":
            with open(f"{day}.csv", "w", encoding="utf-8", newline="") as csv_file:
                csv.writer(csv_file, delimiter=",").writerow(["day", "name", "type", "instructor", "time", "date", "link"])
    except FileNotFoundError:
        log("error - write_csv", f"Cannot write to '{day}'.csv! File exists?")


def log(tag, message, user_id=None, user_name=None):
    if user_id and user_name:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}] - [USER_NAME: {user_name}]: {message}")
    elif user_id:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}]: {message}")
    else:
        print(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}]: {message}")



def handle_day_selection(message):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] and str(message.from_user.id) in admins:
        day = message.text
        bot.send_message(message.chat.id, "Що Ви хочете зробити?", reply_markup=adminModeSchedule)
        bot.register_next_step_handler(message, handle_admin_action, day)

def handle_admin_action(message, day):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text == "Додати пару" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Оберіть час.", reply_markup=adminTimeSchedule)
        bot.register_next_step_handler(message, handle_time_selection, day)
    elif message.text == "Очистити розклад на день" and str(message.from_user.id) in admins:
        write_csv(day, "очистити розклад на день")
        bot.send_message(message.chat.id, "Розклад на день видалено.", reply_markup=adminMarkupMain)

def handle_time_selection(message, day):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in timeSchedule and str(message.from_user.id) in admins:
        time = message.text
        bot.send_message(message.chat.id, "Оберіть дисципліну.", reply_markup=adminLesson)
        bot.register_next_step_handler(message, handle_lesson_selection, day, time)

def handle_lesson_selection(message, day, time):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in lessons and str(message.from_user.id) in admins:
        lesson = message.text
        bot.send_message(message.chat.id, "Оберіть тип.", reply_markup=adminTypeLesson)
        bot.register_next_step_handler(message, handle_lesson_type_selection, day, time, lesson)

def handle_lesson_type_selection(message, day, time, lesson):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in lesson_types:
        lessonType = message.text
        bot.send_message(message.chat.id, "Оберіть викладача.", reply_markup=adminInstructors)
        bot.register_next_step_handler(message, handle_instructor_selection, day, time, lesson, lessonType)

def handle_instructor_selection(message, day, time, lesson, lessonType):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in instructors and str(message.from_user.id) in admins:
        instructor = message.text
        bot.send_message(message.chat.id, "Оберіть посилання із збережених постійних посилань.", reply_markup=adminLinks)
        bot.register_next_step_handler(message, handle_link_selection, day, time, lesson, lessonType, instructor)

def handle_link_selection(message, day, time, lesson, lessonType, instructor):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    else:
        link = links[message.text]
        bot.send_message(message.chat.id, f"*Перевірте інформацію*\n\n*День тижня:* {day}\n*Дисципліна:* {lesson}\n*Тип:* {lessonType}\n*Викладач:* {instructor}\n*Час:* {time}\n*Посилання:* {link}\n\n*Це вірно?*", parse_mode="Markdown", reply_markup=adminIsItCorrect, disable_web_page_preview=True)
        bot.register_next_step_handler(message, handle_confirm_selection, day, time, lesson, lessonType, instructor, link)

def handle_confirm_selection(message, day, time, lesson, lessonType, instructor, link):
    if message.text == "Так, вірно" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Дякую, розклад змінено!", reply_markup=adminMarkupMain)
        write_csv(day, "додати пару", [day, lesson, lessonType, instructor, time, link])
    elif message.text == "Ні, скинути" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Розклад скинено.", reply_markup=adminMarkupMain)


@bot.message_handler(commands=['start', 'help', 'admin_help'])
def commands_handler(message):
    log("info", f"{message.text}", user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "/start":
        with open("subscribed.txt", "r+", encoding="utf-8") as file:
            read_file = file.readline()
            if str(f"{message.from_user.id}") not in read_file:
                file.write(f"{str(message.from_user.id)}, ")
        bot.send_message(
            message.chat.id,
            f"👋 Привіт, *{message.from_user.first_name}*!\n"
            "Мене було створено спеціально для групи *КС-11*, щоб допомагати вам зі всіма організаційними питаннями.\n\n"
            "💼 Я можу показати розклад пар, допомогти вам відмітитися на парах і навіть нагадати про важливі події.\n\n"
            "❓ Якщо вам потрібна допомога або ви хочете дізнатися про мої можливості, просто натисніть -> */help*.\n\n"
            "Залишайтеся продуктивними та успіхів у навчанні! 🎓",
            parse_mode="Markdown", reply_markup=userMarkup
        )
    elif message.text == "/help":
        bot.send_message(
            message.chat.id,
            "Доступні функції:\n\n"
            "📅 *Розклад на сьогодні* — перегляньте розклад на поточний день.\n\n"
            "🗓 *Розклад на тиждень* — ознайомтеся з розкладом на цілий тиждень.\n\n"
            "✅ *Відмітитись на парах* — відмічайтеся на яких парах Ви будете (інформація для старости).\n\n"
            "⚙️ Допомога адміністраторам — */admin_help*",
            parse_mode="Markdown"
        )
    elif message.text == "/admin_help" and str(message.from_user.id) in admins:
        bot.send_message(
            message.chat.id,
            "На що здатна адмін панель:\n\n"
            "📝 *Редагувати розклад* — редагуйте розклад по днях.\n\n"
            "📢 *Зробити оповістку* — надіслати повідомлення для всіх користувачів, які взаємодіяли з ботом.\n\n"
            "📋 *Список відмічених* — переглянути список тих, хто сьогодні відмітився на парах.\n\n"
            "🔙 *Повернутись* — повернутися до панелі звичайного користувача.",
            parse_mode="Markdown"
        )


def send_alert(message):
    if message.text == "Скасувати оповістку" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Оповістку скасовано.", reply_markup=adminMarkupMain)
        return
    else:
        with open("subscribed.txt", "r", encoding="utf-8") as file:
            readed = file.readline().replace(" ", "").split(",")
            for el in readed:
                if el.isdigit():
                    bot.send_message(int(el), f"*Оповістка:* {str(message.text)}", parse_mode="Markdown")
                    log("alert", f"Alert to {int(el)} sent successfully!")
        bot.send_message(message.chat.id, "Оповістку успішно надіслано.", reply_markup=userMarkup)


@bot.message_handler(content_types=["text"])
def message_handler(message):
    global pingedUsers
    log("info", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"] and str(message.from_user.id) in admins:
        handle_day_selection(message)
    elif message.text == "Розклад на сьогодні":
        read_csv_today(message)
    elif message.text == "Розклад на тиждень":
        read_csv_all(message)
    elif message.text == "Адмін" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, f"Вітаю в адмін панелі, *{message.from_user.first_name}*!", reply_markup=adminMarkupMain, parse_mode="Markdown")
    elif message.text == "Адмін" and str(message.from_user.id) not in admins:
        bot.send_message(message.chat.id, "Нажаль, Ви не маєте доступу до адмін панелі.")
        log("access denied", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    elif message.text == "Редагувати розклад" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Ви в режимі редагування розкладу!\n\n*Важливо!* не обов'язково користуватись готовими кнопками, Ви також можете відправити мені текст. Це стосується: часу, дисципліни, типу, викладача, *посилання*.", reply_markup=adminEditSchedule, parse_mode="Markdown")
    elif message.text == "Зробити оповістку" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Введіть текст повідомлення.", reply_markup=adminAlert)
        bot.register_next_step_handler(message, send_alert)
    elif message.text == "Зробити оповістку" and str(message.from_user.id) not in admins:
        bot.send_message(message.chat.id, "Нажаль, Ви не маєте доступу до адмін панелі.")
        log("access denied", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    elif message.text == "Список відміченних" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Оберіть дію.", reply_markup=adminPingedUsers)
    elif message.text == "Подивитись" and str(message.from_user.id) in admins:
        formatted_message = ""
        if pingedUsers.items():
            for key, value in pingedUsers.items():
                unpacked_value = value.split(";")[:-1]
                formatted_message += f"*@{key}* \nпланує бути на:\n\n"
                for para in unpacked_value:
                    formatted_message += f"- {para}\n"
                formatted_message += "\n\n"
            bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "Нажаль, ще немає відміченних.")
    elif message.text == "Очистити" and str(message.from_user.id) in admins:
        pingedUsers = {}
        bot.send_message(message.chat.id, "Успішно очищено.")
    elif message.text == "Повернутись":
        bot.send_message(message.chat.id, "Повертаю Вас.", reply_markup=userMarkup)
    elif message.text == "Відмітитись на парах":
        read_csv_today(message)
        bot.send_message(message.chat.id, f"*{message.from_user.first_name}*, оберіть пари на яких Ви плануєте бути сьогодні.\nВи будете на: ", parse_mode="Markdown", reply_markup=userPingMarkup)
    elif message.text in userPingBtn_labels:
        username = message.from_user.username
        firstname = message.from_user.first_name
        lastname = message.from_user.last_name
        if message.text == "На всіх":
            pingedUsers[f"{username} ({firstname} {lastname})"] = f"{message.text};"
            bot.send_message(message.chat.id, "Ви відмітились на всіх парах!")
        elif message.text == "Скасувати відмітку":
            pingedUsers[f"{username} ({firstname} {lastname})"] = ""
            bot.send_message(message.chat.id, "Відмітки скасовані!")
        elif message.text in userPingBtn_labels[:-3]:
            if username:
                read_dict = pingedUsers.get(f"{username} ({firstname} {lastname})", "").replace("На всіх;", "")
                if message.text in read_dict:
                    bot.send_message(message.chat.id, "Ви вже тут відмітились.")
                else:
                    pingedUsers[f"{username} ({firstname} {lastname})"] = read_dict + f"{message.text};"
                    bot.send_message(message.chat.id, f"Вас успішно відмічено!")
            else:
                read_dict = pingedUsers.get(f"{firstname} {lastname}", "").replace("На всіх;", "")
                if message.text in read_dict:
                    bot.send_message(message.chat.id, "Ви вже тут відмітились.")
                else:
                    pingedUsers[f"{firstname} {lastname}"] = read_dict + f"{message.text};"
                    bot.send_message(message.chat.id, f"Вас успішно відмічено!")
    elif message.text == "Підтримати":
        bot.send_message(message.chat.id, "Привіт!\n\nДякую за вашу фінансову підтримку цього бота! Ваша допомога надзвичайно важлива для мене і дозволяє продовжувати покращувати сервіс.\n\nЯкщо є питання або пропозиції, не вагайтеся звертатися — *@wzxcff*.\n\nhttps://send.monobank.ua/jar/7yZdwvmNRf", disable_web_page_preview=True, parse_mode="Markdown")
    elif message.text == "Конфідеційність":
        bot.send_message(message.chat.id, "*Щодо використання ваших даних*\n\nРозробник ніяк не може отримати доступ до вашого акаунту, паролів або особистих повідомлень. Бот зберігає лише ваш *ID, юзернейм, ім’я та прізвище* для забезпечення коректної роботи сервісу в межах університетської групи.\n\nВаші дані залишаються конфіденційними та використовуються виключно для покращення взаємодії з ботом. Жодна інформація не передається третім сторонам або використовується для інших цілей.\n\nЯкщо у вас є питання стосовно збереження даних або ви хочете видалити вашу інформацію, будь ласка, звертайтеся до мене напряму — *@wzxcff*. Я завжди на зв'язку і готовий допомогти.", parse_mode="Markdown")
    else:
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEtpzhm4tpt122kZPVMthLwqisN4yYkQwACfRUAAkS00UsbeN9xiHDUUTYE", message.id)
load_csv()
log("boot", "bot live")
bot.polling(non_stop=True)