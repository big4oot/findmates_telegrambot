import telebot
import bot_config
from telebot import types

def main_kboard():
	keyboard = types.InlineKeyboardMarkup()
	user_reg_btn = types.InlineKeyboardButton(text = "Регистрация (пользователь)", callback_data="reg_user")
	proj_reg_btn = types.InlineKeyboardButton("Регистрация (проект)", callback_data="reg_proj")
	show_proj_btn = types.InlineKeyboardButton("Показать все проекты", callback_data="show_projs")
	show_users_btn = types.InlineKeyboardButton("Показать всех пользователей", callback_data="show_users")
	find_users_btn = types.InlineKeyboardButton("Найти пользователей", callback_data="find_users")
	find_proj_btn = types.InlineKeyboardButton("Найти проект по тегам", callback_data="find_proj")
	edit_user_btn = types.InlineKeyboardButton("Редактировать профиль", callback_data="edit_user")
	edit_proj_btn = types.InlineKeyboardButton("Редактировать проект", callback_data="edit_proj")
	btns = [user_reg_btn, proj_reg_btn, show_proj_btn, show_users_btn,
	            find_users_btn,edit_user_btn, edit_proj_btn]
	for b in btns:
		keyboard.add(b)
	return keyboard
	
def accept_kboard(accept_type):
	keyboard = types.InlineKeyboardMarkup()
	if accept_type == "user":
		accept_button = types.InlineKeyboardButton("Подтвердить", callback_data="accept_u")
		keyboard.add(accept_button)
	else:
		accept_button = types.InlineKeyboardButton("Подтвердить", callback_data="accept_p")
		keyboard.add(accept_button)
	return keyboard

def edit_choice_kboard():
    keyboard = types.InlineKeyboardMarkup()
    edit_name_btn = types.InlineKeyboardButton(text = "Изменить имя", callback_data="edit_name")
    edit_skills_btn = types.InlineKeyboardButton(text = "Изменить список навыков", callback_data="edit_skills")
    edit_info_btn = types.InlineKeyboardButton(text = "Изменить информацию", callback_data="edit_info")
    edit_active_btn = types.InlineKeyboardButton(text = "Приостановить / возобновить профиль", callback_data="edit_active")
    btns = [edit_name_btn, edit_skills_btn, edit_info_btn, edit_active_btn]
    for b in btns:
        keyboard.add(b)
    return keyboard   
