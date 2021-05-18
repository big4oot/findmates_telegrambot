import random
import json
import telebot
import bot_config
import db
import time
import keyboard


'''
TODO:
markdown
upload CV
validation userinput during registration
choosing post(position) for user (like frontend dev, data scientist etc.)
edit profile
check user (exist?) before registration
change fun name???
'''

bot = telebot.TeleBot(bot_config.token)


class User():
    def __init__(self):
        self.name = None
        self.id = None
        self.tgname = None
        self.skills = []
        self.info = ''
        self.isActive = True

    def payload_to_db(self):
        payload = json.dumps({"user_name": self.name,
                              "user_id": self.id,
                              "user_tgname": self.tgname,
                              "user_skills": self.skills,
                              "users_info": self.info,
                              "user_isActive": self.isActive})
        db.Users_db.payload_data(payload)
        bot.send_message(self.id, "Регистрация завершена")
        show_main_kboard(self.id)


class Project():
    def __init__(self):
        self.id = None
        self.owner_username = None
        self.owner_id = None
        self.title = None
        self.description = None
        self.required_roles = {}
        self.isActive = True

    def payload_to_db(self):
        payload = json.dumps({"user_name": self.title,
                              "project_id": self.id, 	
                              "project_owner_username": self.owner_username,
                              "project_title" : self.title,
                              "project_description": self.description,
                              "project_required_roles": self.required_roles,
                              "project_isActive": self.isActive})
        db.Projects_db.payload_data(payload)
        bot.send_message(self.owner_id, "Регистрация завершена")
        show_main_kboard(owner_id)


user = None
project = None
user_data = None


def show_main_kboard(user_id):
	bot.send_message(user_id, text="Выберите действие", reply_markup=keyboard.main_kboard())


def edit_user(call):
    global user_data
    user_id = str(call.from_user.id)
    user_data = db.Users_db.get_user_info(user_id)
    if user_data == None:
        bot.send_message(user_id, text="Пользователь не найден")
    else:
        text = f"""Ваш профиль:
            Имя: {user_data["user_name"]}
            Telegram-ник: {user_data["user_tgname"]}
            Навыки: {user_data["user_skills"]}
            Доп. информация: {user_data["users_info"]}
            Анкета активна: {'Да' if user_data["user_isActive"] else 'Нет'}
            ____________________________
            Выберите поле для изменения
            """
        bot.send_message(user_id, text, reply_markup=keyboard.edit_choice_kboard())


def edit_name(call):
    msg = bot.send_message(call.from_user.id, "Введите новое имя")
    bot.register_next_step_handler(msg, edit_field_name)
    

def edit_field_name(message):
    db.Users_db.edit_field("user_name", user_data["_id"], message.text)
    bot.send_message(message.from_user.id, "Информация обновлена")
    show_main_kboard(message.from_user.id)

def edit_skills(call):
    text = "Укажите через запятую свои навыки, например: \n" \
           "Python, Django, HTML, CSS, SQL, Git"
    msg = bot.send_message(call.from_user.id, text)
    bot.register_next_step_handler(msg, edit_field_skills)


def edit_field_skills(message):
    skills = list(map(str.lower, message.text.replace(' ', '').split(',')))
    db.Users_db.edit_field("user_skills", user_data["_id"], skills)
    bot.send_message(message.from_user.id, "Информация обновлена")
    show_main_kboard(message.from_user.id)


def edit_info(call):
    msg = bot.send_message(call.from_user.id, "Введите новую информацию о себе")
    bot.register_next_step_handler(msg, edit_field_info)


def edit_field_info(message):
    db.Users_db.edit_field("users_info", user_data["_id"], message.text)
    bot.send_message(message.from_user.id, "Информация обновлена")
    show_main_kboard(message.from_user.id)


def edit_active(call):
    db.Users_db.edit_field("user_isActive", user_data["_id"], not(user_data["user_isActive"]))
    bot.send_message(call.from_user.id, "Информация обновлена")
    show_main_kboard(call.from_user.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'reg_user':
       reg_dev(call)
    elif call.data == 'reg_proj':
       reg_proj(call)
    elif call.data == 'show_users':
       show_users(call)
    elif call.data == 'show_projs':
       show_projects(call)
    elif call.data == 'find_users':
       pass
    elif call.data == 'find_proj':
       pass
    elif call.data == 'accept_u':
       accept('u')
    elif call.data == 'accept_p':
       accept('p')
    elif call.data == 'edit_user':
       edit_user(call)
    elif call.data == 'edit_name':
        edit_name(call)
    elif call.data == 'edit_skills':
        edit_skills(call)
    elif call.data == 'edit_info':
        edit_info(call)
    elif call.data == 'edit_active':
        edit_active(call)

@bot.message_handler(commands=['show_users'])
def show_users(message):
    bot.send_message(message.from_user.id, db.Users_db.get_users_page())
    show_main_kboard(message.from_user.id)


@bot.message_handler(commands=['show_projects'])
def show_projects(message):
    bot.send_message(message.from_user.id, db.Projects_db.get_projects_page())
    show_main_kboard(message.from_user.id)


@bot.message_handler(commands=['start'])
def start(message):
    text = "Привет!\nТы разработчик, который ищет возможность поучаствовать" \
           "в командной разработке?\nИли же ты руководитель проекта, " \
           "который нуждается в разработчиках?\nЭтот бот окажет содействие" \
           " в кооперации разработчиков и проектных команд."
    bot.send_message(message.from_user.id, text, parse_mode="HTML")
    show_main_kboard(message.from_user.id)


@bot.message_handler(commands=['reg_dev'])
def reg_dev(message):
    if message.from_user.username is None:
        text = "Внимание. У Вас не установлено имя пользователя. Без него" \
               " с Вами не смогут связаться другие люди. " \
               "Для продолжения, пожалуйста, установите имя пользователя" \
               "(username) в настройках Telegram, " \
               "после чего вызовите команду для регистрации снова."
        bot.send_message(message.from_user.id, text)
        return False

    global user
    text = "Предупреждение. Сведения, указанные вами при регистрации будут" \
           "доступны другим участникам бота. Но вы всегда можете" \
           "приостановить отображение своей анкеты (а также " \
           "отредактировть другие данные) при помощи команды /profile_edit"
    bot.send_message(message.from_user.id, text)
    time.sleep(2)
    user = User()
    user.id = message.from_user.id
    user.tgname = "@" + message.from_user.username

    msg = bot.send_message(message.from_user.id, "Введите Ваше имя")
    bot.register_next_step_handler(msg, reg_dev_name_step)


@bot.message_handler(commands=['reg_proj'])
def reg_proj(message):
    if message.from_user.username is None:
        text = "Внимание. У Вас не установлено имя пользователя. Без него" \
               " с Вами не смогут связаться другие люди. " \
               "Для продолжения, пожалуйста, установите имя пользователя" \
               "(username) в настройках Telegram, " \
               "после чего вызовите команду для регистрации снова."
        bot.send_message(message.from_user.id, text)
        return False

    global project
    text = "Предупреждение. Сведения, указанные вами при регистрации будут" \
           "доступны другим участникам бота. Но вы всегда можете" \
           "приостановить отображение своего проекта (а также " \
           "отредактировть другие данные) при помощи команды /project_edit"
    bot.send_message(message.from_user.id, text)
    time.sleep(2)
    project = Project()
    project.owner_id = message.from_user.id
    project.id = random.randint(100000,999999)
    project.owner_username = "@" + message.from_user.username

    msg = bot.send_message(message.from_user.id, "Введите название проекта")
    bot.register_next_step_handler(msg, reg_proj_title_step)


def reg_proj_title_step(message):
    global project
    title = message.text
    project.title = title
    text = "Опишите Ваш проект"
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, reg_proj_descr_step)


def reg_proj_descr_step(message):
    global project
    description = message.text
    project.description = description
    text = "Укажите (через запятую) требуемые в команду позиции. \n" \
           "Например, если вам требуется два frontend-разработчка " \
           "и один QA, то следует отправить боту текст: frontend, frontend, QA"
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, reg_proj_roles_step)


def reg_proj_roles_step(message):
    global project
    roles = list(map(str.lower,message.text.replace(' ', '').split(',')))
    project.required_roles = dict.fromkeys(roles, False)
    text = f'''Проверьте введенные данные:
               Ваш телеграм-никнейм: {project.owner_username}
               Название проекта: {project.title}
               Описание проекта: {project.description}
               Требуемые роли в проекте: {roles}
               Проект активен: {'Да' if project.isActive else 'Нет'}
               ____________________________
               Подтвердите регистрацию
            '''
    bot.send_message(message.from_user.id, text, reply_markup=keyboard.accept_kboard('proj'))


@bot.message_handler(commands=['accept'])
def accept(message):
    '''
    accept types:
    u - accept developer registration
    p - accept project registration
    '''
    accept_type = message
    if accept_type == 'u':
        user.payload_to_db()
    elif accept_type == 'p':
        project.payload_to_db()


def reg_dev_name_step(message):
    global User
    name = message.text
    print(name)
    user.name = name
    text = "Укажите через запятую свои навыки, например: \n" \
           "Python, Django, HTML, CSS, SQL, Git"
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, reg_dev_skills_step)


def reg_dev_skills_step(message):
    global user
    skills = list(map(str.lower, message.text.replace(' ', '').split(',')))
    user.skills = skills
    text = "Далее добавьте к своей анкете сопроводительный текст. " \
           "В нем можно указать, например, опыт работы или иную информацию, " \
           "которую считаете нужной и уместной."
    msg = bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(msg, reg_dev_info_step)


def reg_dev_info_step(message):
    global user
    info = message.text
    user.info = info
    text = f"""Проверьте введенные данные:
               Имя: {user.name}
               Telegram-ник: {user.tgname}
               Навыки: {user.skills}
               Доп. информация: {user.info}
               Анкета активна: {'Да' if user.isActive else 'Нет'}
               ____________________________
               Подтвердите регистрацию
            """
    bot.send_message(message.from_user.id, text, reply_markup=keyboard.accept_kboard("user"))


bot.polling(none_stop=True, interval=0)
