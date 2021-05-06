import bot_config
import requests
import json


class Users_db():
	_url = bot_config.url_finders

	def payload_data(payload):
		response = requests.request("POST", Users_db._url, data=payload, headers=bot_config.headers)

	def get_users_page():
		response = requests.request("GET", Users_db._url, headers=bot_config.headers)
		users_data = json.loads(response.text)
		text = ''
		for user in users_data:
			if user['user_isActive']:
				text += f"Имя: {user['user_name']} \n" \
						f"Telegram-ник: {user['user_tgname']} \n" \
						f"Навыки: {', '.join(user['user_skills'])} \n" \
						f"Доп. информация: {user['users_info']} \n\n" 		
		return text


class Projects_db():
	_url = bot_config.url_projects

	def payload_data(payload):
		response = requests.request("POST", Projects_db._url, data=payload, headers=bot_config.headers)

	def get_projects_page():
		response = requests.request("GET", Projects_db._url, headers=bot_config.headers)
		projects_data = json.loads(response.text)
		text = ''
		for project in projects_data:
			if project['project_isActive']:
				text += f"Название проекта: {project['project_title']} \n" \
						f"Telegram-ник руководителя: {project['project_owner_username']} \n" \
						f"Описание проекта: {project['project_description']} \n" \
						f"Требуемые роли: {', '.join([val[0] for val in project['project_required_roles'].items() if not val[1]])} \n\n" 
		return text

