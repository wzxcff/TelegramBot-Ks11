import threading
from pathlib import Path
import uuid
import json, time
import psutil, platform, subprocess

import telebot, os, datetime, csv
from fontTools.mtiLib import build
from telebot import types
from dotenv import load_dotenv
from borb.io.read.types import Decimal
from borb.pdf import Document, FlexibleColumnWidthTable, PDF, Page, PageLayout, Paragraph, SingleColumnLayout, \
    TableCell, TrueTypeFont, FixedColumnWidthTable
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.font.font import Font


def log(tag, message, user_id=None, user_name=None):
    if os.path.exists("log.txt"):
        with open("log.txt", "a", encoding="utf-8") as file:
            if user_id and user_name:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}] - [USER_NAME: {user_name}]: {message}\n")
            elif user_id:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}]: {message}\n")
            else:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}]: {message}\n")
    else:
        with open("log.txt", "w", encoding="utf-8") as file:
            if user_id and user_name:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}] - [USER_NAME: {user_name}]: {message}\n")
            elif user_id:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}] - [USER_ID: {user_id}]: {message}\n")
            else:
                file.write(f"[{datetime.datetime.now().strftime("%H:%M:%S")}] - [{str(tag).upper()}]: {message}\n")



log("boot", "initializing bot")


def save_pinged():
    with open("pinged.json", "w") as file:
        json.dump(pingedUsers, file)
        log("json/pinged", "dumped pingedUsers to json file!")

def load_pinged():
    try:
        with open("pinged.json", "r") as file:
            log("json/pinged", "loaded pinged.json for access!")
            return json.load(file)
    except FileNotFoundError:
        log("json/pinged", "Couldn't find a file. Does it exists?")
        return {}

def save_reacted():
    converted_alerts_responses = {key: list(value) for key, value in alerts_responses.items()}
    with open("reactedR.json", "w") as file:
        json.dump(converted_alerts_responses, file)
    with open("reactedS.json", "w") as file:
        json.dump(alert_storage, file)





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
links = {
    "Алгоритмізація та програмування": os.getenv("PROGRAMMING"),
    "Вища математика": os.getenv("HIGHER_MATH"),
    "Дискретна математика": os.getenv("DISCRETE_MATH"),
    "Історія України: Цивілізаційний вимір": os.getenv("HISTORY"),
}
scheduleFiles = ["Monday.csv", "Tuesday.csv", "Wednesday.csv", "Thursday.csv", "Friday.csv", "Saturday.csv"]

pingedUsers = load_pinged()

mainChoiceMarkup = types.ReplyKeyboardMarkup(row_width=2)
mainChoice_labels = ["Користувач", "Адмін"]
build_buttons(mainChoiceMarkup, mainChoice_labels)

scheduleMarkup = types.ReplyKeyboardMarkup(row_width=2)
scheduleMarkup_labels = ["Розклад на сьогодні", "Розклад на тиждень", "Поверни"]
build_buttons(scheduleMarkup, scheduleMarkup_labels)

# Create reply markup for user
userMarkup = types.ReplyKeyboardMarkup(row_width=3)
userBtn_labels = ["Розклад", "Відмітитись на парах", "Домашні завдання", "Конфідеційність та підтримка", "Головне меню", "Грати :)"]
build_buttons(userMarkup, userBtn_labels)

userPingMarkup = types.ReplyKeyboardMarkup(row_width=3)
userPingBtn_labels = ["Першій парі", "Другій парі", "Третій парі", "Четвертій парі", "П'ятій парі", "Шостій парі", "Скасувати відмітку", "Поверни", "На всіх"]
build_buttons(userPingMarkup, userPingBtn_labels)

adminMarkupMain = types.ReplyKeyboardMarkup(row_width=3)
adminMarkupMain_labels = ["Редагувати розклад", "Оповістки", "Список відміченних", "Головне меню"]
build_buttons(adminMarkupMain, adminMarkupMain_labels)

adminAlert = types.ReplyKeyboardMarkup()
adminAlertBtn_1 = types.KeyboardButton("Скасувати оповістку")
adminAlert.add(adminAlertBtn_1)

adminAlertMainMenu = types.ReplyKeyboardMarkup(row_width=3)
adminAlertMain_labels = ["Зробити оповістку", "Подивитись хто ознайомився", "Очистити список ознайомлених", "Повернутись"]
build_buttons(adminAlertMainMenu, adminAlertMain_labels)

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
lessons = ["Алгоритмізація та програмування", "Вища математика", "Дискретна математика", "Університетські студії та вступ до комп'ютерних наук", "Іноземна мова", "Історія України: Цивілізаційний вимір", "Кураторська година", "Скасувати", " "]
build_buttons(adminLesson, lessons)

adminInstructors = types.ReplyKeyboardMarkup(row_width=3)
instructors = ["Струков Володимир Михайлович", "Ніколенко Ірина Генадіївна", "Аршава Олена Олександрівна", "Шкабура Ярослав Іванович", "Нестеренко Вікторія Олександрівна", "Єршова Ілона Шонівна", "Зінов'єв Дмитро Васильович та Ткачук Микола Вячеславович", "Зінов'єв Дмитро Васильович", "Ткачук Микола Вячеславович", "Скасувати"]
build_buttons(adminInstructors, instructors)

adminLinks = types.ReplyKeyboardMarkup(row_width=3)
build_buttons(adminLinks, links.keys())

adminIsItCorrect = types.ReplyKeyboardMarkup(row_width=1)
adminIsItCorrectBtn_1 = types.KeyboardButton("Так, вірно")
adminIsItCorrectBtn_2 = types.KeyboardButton("Ні, скинути")
adminIsItCorrect.add(adminIsItCorrectBtn_1, adminIsItCorrectBtn_2)

adminPingedUsers = types.ReplyKeyboardMarkup(row_width=1)
adminPingedUsers_labels = ["Подивитись", "Очистити", "Повернутись"]
build_buttons(adminPingedUsers, adminPingedUsers_labels)

alerts_responses = {}
alert_storage = {}

class ScheduleDay:
    def __init__(self, name, type_of_lesson, instructor, time, link):
        self.name = name
        self.type = type_of_lesson
        self.instructor = instructor
        self.time = time
        self.link = link


def load_reacted():
    global alerts_responses
    global alert_storage

    try:
        with open("reactedR.json", "r") as file:
            loaded_alerts_responses = json.load(file)
            alerts_responses = {key: set(value) for key, value in loaded_alerts_responses.items()}

        with open("reactedS.json", "r") as file:
            alert_storage = json.load(file)
    except FileNotFoundError:
        alerts_responses = {}
        alert_storage = {}



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
    today = datetime.datetime.now().strftime('%A')
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
    try:
        max_message_length = 4096
        formatted_to_send = ""
        separate_messages = []

        for file in scheduleFiles:
            day_schedule = "——————————————————\n"
            with open(f"{file}", "r", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)
                day_name = "".join(file.split(".")[0])
                formatted_message = f"\nРозклад на *{day_name}*\n\n"
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

                if formatted_message == f"\nРозклад на *{day_name}*\n\n":
                    formatted_message += "\nПар немає.\n\n"

                day_schedule += formatted_message
                separate_messages.append(day_schedule)
                formatted_to_send += day_schedule

        if len(formatted_to_send) > max_message_length:
            for day_message in separate_messages:
                day_message += "——————————————————\n"
                bot.send_message(message.chat.id, day_message, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            formatted_to_send += "——————————————————\n"
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
    elif str(message.from_user.id) in admins:
        time = message.text
        bot.send_message(message.chat.id, "Оберіть дисципліну.", reply_markup=adminLesson)
        bot.register_next_step_handler(message, handle_lesson_selection, day, time)


def handle_lesson_selection(message, day, time):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif str(message.from_user.id) in admins:
        lesson = message.text
        bot.send_message(message.chat.id, "Оберіть тип.", reply_markup=adminTypeLesson)
        bot.register_next_step_handler(message, handle_lesson_type_selection, day, time, lesson)


def handle_lesson_type_selection(message, day, time, lesson):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif str(message.from_user.id) in admins:
        lessonType = message.text
        bot.send_message(message.chat.id, "Оберіть викладача.", reply_markup=adminInstructors)
        bot.register_next_step_handler(message, handle_instructor_selection, day, time, lesson, lessonType)


def handle_instructor_selection(message, day, time, lesson, lessonType):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif str(message.from_user.id) in admins:
        instructor = message.text
        bot.send_message(message.chat.id, "Оберіть посилання із збережених постійних посилань.", reply_markup=adminLinks)
        bot.register_next_step_handler(message, handle_link_selection, day, time, lesson, lessonType, instructor)


def handle_link_selection(message, day, time, lesson, lessonType, instructor):
    if message.text == "Скасувати":
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    else:
        try:
            link = links[message.text]
            bot.send_message(message.chat.id, f"*Перевірте інформацію*\n\n*День тижня:* {day}\n*Дисципліна:* {lesson}\n*Тип:* {lessonType}\n*Викладач:* {instructor}\n*Час:* {time}\n*Посилання:* {link}\n\n*Це вірно?*", parse_mode="Markdown", reply_markup=adminIsItCorrect, disable_web_page_preview=True)
            bot.register_next_step_handler(message, handle_confirm_selection, day, time, lesson, lessonType, instructor, link)
        except:
            link = str(message.text)
            bot.send_message(message.chat.id,f"*Перевірте інформацію*\n\n*День тижня:* {day}\n*Дисципліна:* {lesson}\n*Тип:* {lessonType}\n*Викладач:* {instructor}\n*Час:* {time}\n*Посилання:* {link}\n\n*Це вірно?*",parse_mode="Markdown", reply_markup=adminIsItCorrect, disable_web_page_preview=True)
            bot.register_next_step_handler(message, handle_confirm_selection, day, time, lesson, lessonType, instructor, link)


def handle_confirm_selection(message, day, time, lesson, lessonType, instructor, link):
    if message.text == "Так, вірно" and str(message.from_user.id) in admins:
        write_csv(day, "додати пару", [day, lesson, lessonType, instructor, time, link])
        read_csv_all(message)
        bot.send_message(message.chat.id, "Дякую, розклад змінено!", reply_markup=adminMarkupMain)
    elif message.text == "Ні, скинути" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Розклад скинено.", reply_markup=adminMarkupMain)


def sort_based_on_reference(test_array, reference_array):
    index_mapping = {value: idx for idx, value in enumerate(reference_array)}

    def sorting_key(element):
        return index_mapping.get(element, float('inf'))

    sorted_array = sorted(test_array, key=sorting_key)
    return sorted_array


def generate_pdf(message):
    today = datetime.datetime.now().strftime('%A')
    para = []
    username = message.from_user.username
    firstname = message.from_user.first_name
    lastname = message.from_user.last_name
    doc: Document = Document()
    page: Page = Page()
    doc.add_page(page)
    layout: PageLayout = SingleColumnLayout(page)
    font: Font = TrueTypeFont.true_type_font_from_file(Path("Montserrat-Light.ttf"))
    bold: Font = TrueTypeFont.true_type_font_from_file(Path("Montserrat-Bold.ttf"))
    todayDayMonth = datetime.datetime.now().strftime("%d.%m")
    layout.add(Paragraph(f"{todayDayMonth}", font=bold, font_size=Decimal(12)))
    with open(f"{today}.csv", "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader)

        for el in reader:
            para.append(f"{el[1]} - {el[2]}")
        print(f"number of columns: {len(para) + 1}, number of rows: {len(pingedUsers.keys())}")
        if not len(pingedUsers.keys()):
            to_add = FixedColumnWidthTable(number_of_columns=len(para) + 1, number_of_rows=1)
        else:
            to_add = FixedColumnWidthTable(number_of_columns=len(para) + 1, number_of_rows=len(pingedUsers.keys()))
        to_add.add(Paragraph("Ім'я та прізвище студента", font=bold, font_size=Decimal(8)))
        if not para:
            bot.send_message(message.chat.id, "Сьогодні пар немає.")
        else:
            for el in para:
                to_add.add(Paragraph(el, font=bold, font_size=Decimal(8)))
            layout.add(to_add.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(0.5), Decimal(10)))

            for user in pingedUsers.keys():
                to_add.add(Paragraph(user, font=font, font_size=Decimal(8)))


            with open(f"Відмічені.pdf", "wb") as out_file_handle:
                PDF.dumps(out_file_handle, doc)
                print("Generated document!")

            bot.send_document(message.chat.id, open("Відмічені.pdf", "rb"))
            os.remove(f"Відмічені.pdf")

def write_welcome_user(message):
    row = [message.from_user.id, message.from_user.username]
    row_str = f"{row[0]},{row[1]}\r\n"
    if os.path.exists("users.csv"):
        with open("users.csv", "r+", encoding="utf-8", newline="") as csv_file:
            read_file = csv_file.readlines()
            if row_str not in read_file:
                log("new user", f"new user added to users.csv")
                writer = csv.writer(csv_file, delimiter=",")
                writer.writerow(row)
            else:
                log("new user", "new user wasn't added to users.csv, already exists")
    else:
        with open("users.csv", "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerow(["id", "username"])
            writer.writerow(row)
            log("new user", "created users.csv, added user to it")

@bot.message_handler(commands=['start', 'help', 'admin_help', 'date', 'keyboard', 'status'])
def commands_handler(message):
    log("info", f"{message.text}", user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "/start":
        write_welcome_user(message)
        bot.send_message(
            message.chat.id,
            f"👋 Привіт, *{message.from_user.first_name}*!\n"
            "Мене було створено спеціально для групи *КС-11*, щоб допомагати вам зі всіма організаційними питаннями.\n\n"
            "💼 Я можу показати розклад пар, допомогти вам відмітитися на парах і навіть нагадати про важливі події.\n\n"
            "❓ Якщо вам потрібна допомога або ви хочете дізнатися про мої можливості, просто натисніть -> */help*.\n\n"
            "📢 Для останніх оновлень, статусу бота та багфіксів підписуйтесь на наш канал: [оновлення бота](https://t.me/+oh-WlmlOuyI4ODEy).\n\n"
            "Залишайтеся продуктивними та успіхів у навчанні! 🎓",
            parse_mode="Markdown", reply_markup=mainChoiceMarkup, disable_web_page_preview=True
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
            "📢 *Оповістки* — надіслати повідомлення для всіх користувачів, які взаємодіяли з ботом, подивитись хто відмітився.\n\n"
            "📋 *Список відмічених* — переглянути список тих, хто сьогодні відмітився на парах.\n\n"
            "🔙 *Повернутись* — повернутися до панелі звичайного користувача.",
            parse_mode="Markdown"
        )
    elif message.text == "/date" and str(message.from_user.id) in admins:
        today = datetime.datetime.now().strftime('%A')
        bot.send_message(message.chat.id, f"Date and time on server:\n\n{today}, {datetime.datetime.now().strftime("%H:%M:%S")}")
    elif message.text == "/keyboard":
        bot.send_message(message.chat.id, "Надав *Вам* клавіатуру :)", reply_markup=mainChoiceMarkup, parse_mode="Markdown")
    elif message.text == "/status" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, get_server_status())

def send_alert(message):
    if message.text == "Скасувати оповістку" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Оповістку скасовано.", reply_markup=adminMarkupMain)
        return
    else:
        if len(alerts_responses) > 5:
            bot.send_message(message.chat.id, "*Реакцій на оповістки вже більше 5, рекомендую очистити список ознайомлених!*", parse_mode="Markdown")
        unique_id = str(uuid.uuid4())
        alert_storage[unique_id] = message.text
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="Ознайомлен(а) ✅", callback_data=f"okay:{unique_id}")
        markup.add(button)

        with open("users.csv", "r") as file:
            csv_reader = csv.DictReader(file)
            user_dict = {row['id']: row['username'] for row in csv_reader}
            log("alert", f"Users to send: {user_dict.keys()}")
            for user in user_dict.keys():
                try:
                    bot.send_message(user, f"*Оповістка:* {message.text}", reply_markup=markup, parse_mode="Markdown")
                except Exception as e:
                    bot.send_message(message.chat.id, f"Неможливо знайти чат з @{user_dict[user]}. Скоріш за все користувач заблокував бота.")
                    log("error", f"Cannot find {user} chat. Maybe user blocked bot?")
                    log("exception - error", f"{e}")
            bot.send_message(message.chat.id, "Оповістка надіслана!", reply_markup=adminMarkupMain)
            log("alert", "alerts were sent successfully!")

def get_responses(message):
    if str(message.from_user.id) in admins:
        for alert_text, users in alerts_responses.items():
            users_list = "\n".join(f"- @{user}" for user in users)
            response_text = f'"{alert_text}" \n\nкористувачі відреагували:\n{users_list}'
            bot.send_message(message.chat.id, response_text)

def clear_json():
    with open("pinged.json", "w") as file:
        json.dump({}, file)
    log("json/pinged", "json cleared!")

def clear_reacted():
    global alerts_responses, alert_storage
    with open("reactedR.json", "w") as file:
        json.dump({}, file)
    with open("reactedS.json", "w") as file:
        json.dump({}, file)
    alerts_responses = {}
    alert_storage = {}
    log("json/reacted", "json cleared!")

def send_user_data_dump():
    global pingedUsers, alerts_responses
    while True:
        try:
            now = datetime.datetime.now()
            if 10 <= now.hour <= 18:
                pingedUsers = load_pinged()
                formatted_message = ""
                if pingedUsers.items():
                    for key, value in pingedUsers.items():
                        unpacked_value = value.split(";")[:-1]
                        formatted_message += f"*@{key}* \nпланує бути на:\n\n"
                        for para in unpacked_value:
                            formatted_message += f"- {para}\n"
                        formatted_message += "\n\n"
                    bot.send_message(774380830, formatted_message, parse_mode="Markdown")
                load_reacted()
                if alerts_responses:
                    for alert_text, users in alerts_responses.items():
                        users_list = "\n".join(f"- @{user}" for user in users)
                        response_text = f'"{alert_text}" \n\nкористувачі відреагували:\n{users_list}'
                        bot.send_message(774380830, response_text)
                    log("dump", "Data dump was sent successfully to main admin!")
            time.sleep(18000)
        except Exception as e:
            log("error", "Error in send_user_data_dump!")

def start_timer():
    timer_thread = threading.Thread(target=send_user_data_dump, daemon=True)
    timer_thread.start()

def get_server_status():
    uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()

    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    disk = psutil.disk_usage('/')
    disk_usage = disk.percent

    os_info = platform.system() + " " + platform.release()
    status_message = (
        f"Server Status:\n"
        f"OS: {os_info}\n"
        f"Uptime: {uptime}\n"
        f"CPU Usage: {cpu_usage}%\n"
        f"Memory Usage: {memory_usage}%\n"
        f"Disk Usage: {disk_usage}%\n"
    )
    return status_message

@bot.message_handler(content_types=["text"])
def message_handler(message):
    global pingedUsers, alerts_responses, alert_storage
    log("info", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    if message.text == "Скасувати" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Дякую за вашу працю :)", reply_markup=adminMarkupMain)
    elif message.text == "Оповістки" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Надаю меню оповісток.", reply_markup=adminAlertMainMenu)
    elif message.text == "Поверни":
        bot.send_message(message.chat.id, "Повернув!", reply_markup=userMarkup)
    elif message.text == "Домашні завдання":
        bot.send_message(message.chat.id, "Розділ в розробці.")
    elif message.text == "Подивитись хто ознайомився" and str(message.from_user.id) in admins:
        load_reacted()
        if alerts_responses:
            get_responses(message)
        else:
            bot.send_message(message.chat.id, "Нажаль, відміток ще немає :(")
    elif message.text == "Очистити список ознайомлених" and str(message.from_user.id) in admins:
        clear_reacted()
        bot.send_message(message.chat.id, "Список очищено!")
    elif message.text == "Користувач":
        bot.send_message(message.chat.id, "Надаю меню користувача!", reply_markup=userMarkup)
    elif message.text == "Розклад":
        bot.send_message(message.chat.id, "Оберіть режим відображення.", reply_markup=scheduleMarkup)
    elif message.text == "Сгенерувати PDF" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "На цьому моменті розробник втомився, тому, нажаль, функція в розробці.")
        # generate_pdf(message)
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
        bot.send_message(message.chat.id, "Ви в режимі редагування розкладу!\n\n*Важливо!* не обов'язково користуватись готовими кнопками, Ви також можете відправити мені текст. Це стосується: часу, дисципліни, типу, викладача, *посилання*.\nТакож, важливий порядок пар, додавайте в порядку зранку до вечора.", reply_markup=adminEditSchedule, parse_mode="Markdown")
    elif message.text == "Зробити оповістку" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Введіть текст повідомлення.", reply_markup=adminAlert)
        bot.register_next_step_handler(message, send_alert)
    elif message.text == "Зробити оповістку" and str(message.from_user.id) not in admins:
        bot.send_message(message.chat.id, "Нажаль, Ви не маєте доступу до адмін панелі.")
        log("access denied", message.text, user_id=message.from_user.id, user_name=message.from_user.first_name)
    elif message.text == "Список відміченних" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Оберіть дію.", reply_markup=adminPingedUsers)
    elif message.text == "Подивитись" and str(message.from_user.id) in admins:
        pingedUsers = load_pinged()
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
        clear_json()
        bot.send_message(message.chat.id, "Успішно очищено.")
    elif message.text == "Повернутись" and str(message.from_user.id) in admins:
        bot.send_message(message.chat.id, "Повертаю Вас.", reply_markup=adminMarkupMain)
    elif message.text == "Відмітитись на парах":
        pingedUsers = load_pinged()
        read_csv_today(message)
        bot.send_message(message.chat.id, f"*{message.from_user.first_name}*, оберіть пари на яких Ви плануєте бути сьогодні.\nВи будете на: ", parse_mode="Markdown", reply_markup=userPingMarkup)
    elif message.text in userPingBtn_labels:
        pingedUsers = load_pinged()
        username = message.from_user.username
        firstname = message.from_user.first_name
        lastname = message.from_user.last_name
        if message.text == "На всіх":
            if lastname:
                pingedUsers[f"{username} ({firstname} {lastname})"] = f"{message.text};"
                bot.send_message(message.chat.id, "Ви відмітились на всіх парах!")
            else:
                pingedUsers[f"{username} ({firstname})"] = f"{message.text};"
                bot.send_message(message.chat.id, "Ви відмітились на всіх парах!")
        elif message.text == "Скасувати відмітку":
            if lastname:
                pingedUsers[f"{username} ({firstname} {lastname})"] = ""
                bot.send_message(message.chat.id, "Відмітки скасовані!")
            else:
                pingedUsers[f"{username} ({firstname})"] = ""
                bot.send_message(message.chat.id, "Відмітки скасовані!")
        elif message.text in userPingBtn_labels[:-3]:
            if lastname:
                read_dict = pingedUsers.get(f"{username} ({firstname} {lastname})", "").replace("На всіх;", "")
                if message.text in read_dict:
                    bot.send_message(message.chat.id, "Ви вже тут відмітились.")
                else:
                    pingedUsers[f"{username} ({firstname} {lastname})"] = read_dict + f"{message.text};"
                    bot.send_message(message.chat.id, f"Вас успішно відмічено!")
            else:
                read_dict = pingedUsers.get(f"{username} ({firstname})", "").replace("На всіх;", "")
                if message.text in read_dict:
                    bot.send_message(message.chat.id, "Ви вже тут відмітились.")
                else:
                    pingedUsers[f"{username} ({firstname})"] = read_dict + f"{message.text};"
                    bot.send_message(message.chat.id, f"Вас успішно відмічено!")
        save_pinged()
    elif message.text == "Головне меню":
        bot.send_message(message.chat.id, "Надаю головне меню.", reply_markup=mainChoiceMarkup)
    elif message.text == "Грати :)":
        bot.send_message(message.chat.id, "Цей розділ ще в розробці, але тут точно має бути щось цікаве.")
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEt7rBm9IRQbWNsRub7NBhJhtGySSMuLQAC5xIAAkfS-EthvjzENdeqgzYE")
    elif message.text == "Конфідеційність та підтримка":
        bot.send_message(message.chat.id, "*Щодо використання ваших даних*\n\nРозробник ніяк не може отримати доступ до вашого акаунту, паролів або особистих повідомлень. Бот зберігає лише ваш *ID, юзернейм, ім’я та прізвище* для забезпечення коректної роботи сервісу в межах університетської групи.\n\nВаші дані залишаються конфіденційними та використовуються виключно для покращення взаємодії з ботом. Жодна інформація не передається третім сторонам або використовується для інших цілей.\n\nЯкщо у вас є питання стосовно збереження даних або ви хочете видалити вашу інформацію, будь ласка, звертайтеся до мене напряму — *@wzxcff*. Я завжди на зв'язку і готовий допомогти.", parse_mode="Markdown")
        bot.send_message(message.chat.id, "Дякую за вашу фінансову підтримку цього бота! Ваша допомога надзвичайно важлива для мене і дозволяє продовжувати покращувати сервіс.\n\nЯкщо є питання або пропозиції, не вагайтеся звертатися — *@wzxcff*.\n\nhttps://send.monobank.ua/jar/7yZdwvmNRf", disable_web_page_preview=True, parse_mode="Markdown")
    elif message.text == "/clear_log" and str(message.from_user.id) in admins:
        with open("log.txt", "w", encoding="utf-8") as file:
            file.write("Logs cleared")
        bot.send_message(message.chat.id, "Логування очищено!")
    else:
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEtq1Vm5B2UODG5XpeAZ8nCmzMtVRZjKAAC3z0AAgveiUtlDmDxoTKLODYE", message.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("okay:"))
def handle_okay_response(call):
    unique_id = call.data.split("okay:")[1]
    alert_text = alert_storage.get(unique_id)
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name

    if alert_text:
        if alert_text not in alerts_responses:
            alerts_responses[alert_text] = set()

    try:
        if call.from_user.last_name:
            alerts_responses[alert_text].add(f"{username} ({call.from_user.first_name} {call.from_user.last_name})")
        else:
            alerts_responses[alert_text].add(f"{username} ({call.from_user.first_name})")
    except KeyError:
        bot.answer_callback_query(call.id, "Оповістка вже видалена!")
        log("error", "Couldn't find 'None' in alerts_responses!")
    save_reacted()
    bot.answer_callback_query(call.id, "Відповідь зараховано!")


start_timer()
log("timer", "Timer started")

load_csv()
log("boot", "bot live")

bot.send_message(774380830, "Bot started successfully!")

try:
    bot.polling(non_stop=True)
except Exception as e:
    print(e)
    log("critical error, important", e)