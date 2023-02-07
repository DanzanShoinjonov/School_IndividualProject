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

timetable_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
tadd= KeyboardButton(text='Добавить дело',
                     callback_data='afdsa')
tdel = KeyboardButton(text='Удалить дело')
tbase = KeyboardButton(text='Моё расписание')

help = KeyboardButton('/help')
descrip = KeyboardButton('/description')
profile = KeyboardButton('👤Профиль')
timetable = KeyboardButton('📆 Расписание')
todo = KeyboardButton('TO-DO')


e0 = InlineKeyboardMarkup(row_width=5, one_time_keyboard=True)      #inline клавиатура оценки бота
e1 = InlineKeyboardButton(text='1',
                          callback_data='very bad')
e2 = InlineKeyboardButton(text='2',
                          callback_data='bad')
e3 = InlineKeyboardButton(text='3',
                          callback_data='not good')
e4 = InlineKeyboardButton(text='4',
                          callback_data='good')
e5 = InlineKeyboardButton(text='5',
                          callback_data='very good')

going = InlineKeyboardMarkup(row_width=2)
go = InlineKeyboardButton(text='Вперёд',
                          callback_data='g')
back = InlineKeyboardButton(text='Назад',
                            callback_data='b')

timetable_keyboard.add(tdel, tadd)
timetable_keyboard.add(tbase)
kb_base.add(profile)
kb_base.add(timetable, todo)
kb_base.add(help, descrip)

going.add(back,going)
e0.add(e1, e2, e3, e4, e5)