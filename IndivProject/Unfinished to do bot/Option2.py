import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.types import CallbackQuery
import logging
from constants2 import *
from keyboards2 import *




logging.basicConfig(level=logging.INFO)
bot = Bot(API)
dp = Dispatcher(bot)


async def on_startup(_):
    print(emoji.emojize('Бот успешно запущен!:rocket: :rocket: :rocket:'))




@dp.message_handler(commands=['help'])            #(Реагирование на команду - '/help') Приветствие и описание бота
async def help_command(message: types.Message):
    await message.reply(text=emoji.emojize('Если что-то не понятно, то можешь написать администратору в личные сообщения: 👉 @shooinj'))
    await message.answer(text=HELP_COMMANDS,
                        parse_mode='HTML')


@dp.message_handler(commands=['start'])            #(Реагирование на команду - '/start') Приветствие и описание бота
async def send_welcome(message: types.Message):
    await message.answer(text=emoji.emojize('Привет!\nДанный бот создан для Индивидуального проекта с помощью языка программирования Python и библиотеки aiogram.!:raised_hand:'),
                         parse_mode='HTML',
                         reply_markup=kb_base)
    await message.delete()


@dp.message_handler(commands=['description'])
async def descrip_command(message: types.Message):
    await message.answer(text='Этот бот проект для индивидуального проекта и его автором является Шойнжонов Данзан.\nДанный бот может осуществлять различные\
                        функции и поможет тебе в осуществлении дел!',
                         parse_mode='HTML')
    await message.delete()


@dp.message_handler(lambda message: message.text == "👤Профиль")
async def profile_button_press(message: Message):
    username = message.from_user.username
    await message.answer(text='Твоё имя: @{}'.format(username))
    await message.answer(text='Количество не выполненных дел:')
    await message.answer(text='Общая эффективность:')


@dp.message_handler(lambda message: message.text == "📆 Расписание")
async def timetable_button_press(message: Message):
    await message.answer(text='Твоё расписание:', reply_markup=timetable_keyboard)




@dp.message_handler(commands=['evaluate_the_bot'])     #оценивание бота по 5-ти бальной шкале
async def evaluate(message: types.Message):

    await message.answer(text='Пожалуйста, оцени бота по шкале от 1 до 5',
                        reply_markup =e0)




@dp.callback_query_handler()
async def evaluate_callback(callback: types.CallbackQuery):
    if callback.data == 'very bad':
        await callback.answer(text='☹☹☹')
    if callback.data == 'bad':
        await callback.answer('😢 я буду стараться...')
    if callback.data == 'not good':
        await callback.answer('㋛ Значит, мне нужно делать лучше ㋛')
    if callback.data == 'good':
        await callback.answer('Спасибо, стараюсь дальше.')
    if callback.data == 'very good':
        await callback.answer('😁 Идеально? Ура!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)