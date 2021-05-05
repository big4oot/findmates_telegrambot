import telebot
import bot_config
import db
import json
import time
import random

'''
TODO:
markdown
upload CV
fix some bugs
validation userinput during registration
buttons instead commands
choosing post(position) for user (like frontend dev, data scientist etc.)
edit profile
check user (exist?) before registration
help with commands
get users profiles

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
		payload = json.dumps( {"user_name": self.name,
				"user_id": self.id,
				"user_tgname": self.tgname,
				"user_skills":self.skills,
				"users_info": self.info,
				"user_isActive": self.isActive
			} 
		)
		db.Users_db.payload_data(payload)
		bot.send_message(self.id, "Регистрация завершена")


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
		payload = json.dumps( {"user_name": self.title,
				"project_id": self.id,
				"project_owner_username": self.owner_username,
				"project_title":self.title,
				"project_description": self.description,
				"project_required_roles": self.required_roles,
				"project_isActive": self.isActive
			} 
		)
		db.payload_data(payload, 'p')
		bot.send_message(self.owner_id, "Регистрация завершена")


user = None
project = None


@bot.message_handler(commands=['show_users'])
def show_users(message):
	bot.send_message(message.from_user.id, db.Users_db.get_users_page())


@bot.message_handler(commands=['show_projects'])
def show_users(message):
	bot.send_message(message.from_user.id, db.Projects_db.get_projects_page())


@bot.message_handler(commands=['start'])
def start(message):
	text = '''
		Привет. Ты разработчик, который ищет возможность поучаствовать в командной разработке?
		Или же ты руководитель проекта, который нуждается в разработчиках?
		Этот бот окажет содействие в кооперации разработчиков и проектных команд.
		Для начала зарегистрируйся:
			# /reg_dev - как разработчик
			# /reg_proj - как руководитель проектной команды
	'''
	bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['reg_dev'])
def reg_dev(message):
	if message.from_user.username is None:
		text = '''Внимание. У Вас не установлено имя пользователя. Без него с Вами не смогут связаться другие люди.
		Для продолжения, пожалуйста, установите имя пользователя (username) в настройках Telegram, после чего вызовите команду для регистрации снова.
		'''
		bot.send_message(message.from_user.id, text)
		return False

	global user
	text = '''
		Предупреждение. Сведения, указанные вами при регистрации будут доступны другим
		участникам бота. Но вы всегда можете приостановить отображение своей анкеты (а также 
		отредактировть другие данные) при помощи команды /profile_edit
		'''
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
		text = '''Внимание. У Вас не установлено имя пользователя. Без него с Вами не смогут связаться другие люди.
		Для продолжения, пожалуйста, установите имя пользователя (username) в настройках Telegram, после чего вызовите команду для регистрации снова.
		'''
		bot.send_message(message.from_user.id, text)
		return False

	global project
	text = '''
		Предупреждение. Сведения, указанные вами при регистрации будут доступны другим
		участникам бота. Но вы всегда можете приостановить отображение своего проекта (а также 
		отредактировть другие данные) при помощи команды /project_edit
		'''
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
	text = """ Укажите (через запятую) требуемые в команду позиции. 
		Например, если вам требуется два frontend-разработчка и один QA, то следует отправить
		боту текст: frontend, frontend, QA
	"""
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
			   Подтвердите регистрацию командой /accept 2
			'''
	bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['accept'])
def accept(message):
	'''
	accept types:
	1 - accept developer registration
	2 - accept project registration 
	'''
	accept_type = message.text.replace(' ','')[-1]
	if accept_type == '1':
		user.payload_to_db()
	elif accept_type == '2':
		project.payload_to_db()


def reg_dev_name_step(message):
	global User
	name = message.text
	print(name)
	user.name = name
	text = '''Укажите через запятую свои навыки, например:
		Python, Django, HTML, CSS, SQL, Git'''
	msg = bot.send_message(message.from_user.id, text)
	bot.register_next_step_handler(msg, reg_dev_skills_step)


def reg_dev_skills_step(message):
	global user
	skills = list(map(str.lower,message.text.replace(' ', '').split(',')))
	user.skills = skills
	text = '''
		Далее добавьте к своей анкете сопроводительный текст. В нем можно указать, 
		например, опыт работы или иную информацию, которую считаете нужной и уместной.
		'''
	msg = bot.send_message(message.from_user.id, text)
	bot.register_next_step_handler(msg, reg_dev_info_step)


def reg_dev_info_step(message):
	global user
	info = message.text
	user.info = info
	text = f'''Проверьте введенные данные:
			   Имя: {user.name}
			   Telegram-ник: {user.tgname}
			   Навыки: {user.skills}
			   Доп. информация: {user.info}
			   Анкета активна: {'Да' if user.isActive else 'Нет'}
			   ____________________________
			   Подтвердите регистрацию командой /accept 1
			'''
	bot.send_message(message.from_user.id, text)

bot.polling(none_stop=True, interval=0)