from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.dispatcher.filters import Text

HELP_COMMANDS = """
/start - начать работу с ботом
/help - список комманд
/description - описание бота
/creation_process - процесс создания бота
/evaluate_the_bot - оцени бота
/donate - админу на сервера и на поесть
"""


kb_base = ReplyKeyboardMarkup(resize_keyboard=True,
                         one_time_keyboard=True)

addtask = KeyboardButton('/Добавить_Задачу')
tasklist = KeyboardButton('/Список_Задач')
help = KeyboardButton('/help')
descrip = KeyboardButton('/description')
profile = KeyboardButton('/👤Профиль')


kb_base.add(profile)
kb_base.add(addtask, tasklist)
kb_base.add(help, descrip)
