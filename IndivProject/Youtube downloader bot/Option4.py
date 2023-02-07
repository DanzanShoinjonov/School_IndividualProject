import logging
import emoji
import os
from pytube import YouTube
from aiogram import Bot, Dispatcher, executor, types
from constants4 import *
from keyboards4 import *
import datetime
from datetime import timedelta

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
    await message.answer(text=emoji.emojize('Привет!\nДанный бот создан для Индивидуального проекта с помощью языка программирования Python и библиотеки aiogram.!:raised_hand:\nБот умеет скачивать видео с Ютуба, в дальнейшем я планирую добавить функцию сжатия изображений!'),
                         parse_mode='HTML',
                         reply_markup=kb_base)
    await message.delete()


@dp.message_handler(commands=['description'])
async def descrip_command(message: types.Message):
    await message.answer(text='Этот бот проект для индивидуального проекта и его автором является Шойнжонов Данзан.',
                         parse_mode='HTML')


@dp.message_handler(commands=['Youtube_video_download'])
async def a_answer(message: types.Message):
    await message.answer(text='Скинь ссылку видео с ютуба, которое хочешь скачать.', parse_mode='HTML')


@dp.message_handler()
async def y_download(message: types.Message):
    text = message.text
    if text == message.text.startswith('https://youtube.be/') or message.text.startswith(
            'https://www.youtube.com/') or message.text.startswith('https://youtu.be/'):
        url = message.text
        yt = YouTube(url)
        title = yt.title
        resolution = yt.streams.get_highest_resolution().resolution
        file_size = yt.streams.get_highest_resolution().filesize
        picture = yt.thumbnail_url

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Скачать", callback_data="download"))
        await message.answer_photo(f'{picture}', caption=f"📹 <b>{title}</b> <a href='{url}'>→</a> \n"
                                                         f"⚙️ <b>Расширение —</b> <code>{resolution}</code> \n"
                                                         f"🗂 <b>Размер видео —</b> <code>{round(file_size * 0.000001, 2)}MB</code>",
                                   parse_mode='HTML', reply_markup=keyboard)
    else:
        await message.answer(f"❗️<b>Это не похоже на ссылку!</b>", parse_mode='HTML')


@dp.callback_query_handler(text="download")
async def button_download(call: types.CallbackQuery):
    url = call.message.html_text
    yt = YouTube(url)
    title = yt.title
    author = yt.author
    resolution = yt.streams.get_highest_resolution().resolution
    stream = yt.streams.filter(progressive=True, file_extension="mp4")
    stream.get_highest_resolution().download(f'{call.message.chat.id}', f'{call.message.chat.id}_{yt.title}')
    with open(f"{call.message.chat.id}/{call.message.chat.id}_{yt.title}", 'rb') as video:
        await bot.send_video(call.message.chat.id, video, caption=f"📹 <b>{title}</b> \n"  # Title#
                                                                  f"👤 <b>{author}</b> \n\n"  # Author Of Channel#
                                                                  f"⚙️ <b>Расширения —</b> <code>{resolution}</code> \n"
                                                                  f"📥 <b>Скачано с помощью @Individual_Project_product_bot</b>",
                             parse_mode='HTML')
        os.remove(f"{call.message.chat.id}/{call.message.chat.id}_{yt.title}")



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