import logging
import emoji
import os
from pytube import YouTube
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from constants import *
from keyboards import *
from aiogram.types import CallbackQuery
import datetime
from datetime import timedelta
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
import telebot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import ParseMode
import time
import aiogram.utils.markdown as md
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = ''

# Configure logging
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# A list to store tasks
tasks = []

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот. Как я могу помочь вам сегодня?")
    await message.answer("/start: начинает разговор с ботом\n/help: отображает справочную информацию\n/profile: отображает информацию о профиле пользователя\n/addtask: добавляет задачу\n/listtasks: список задач пользователя с возможностью удаления задачи",
                         reply_markup=kb_base)

@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    await message.answer("Я могу ответить на ваши вопросы и предоставить информацию. Просто спросите! Если что это админ: @shooinj")

@ dp.message_handler(commands='👤Профиль', state='*')
async   def cmd_show_profile(message: Message):
    user = message.from_user
    await bot.send_message(message.chat.id, f'User: {user.full_name} \nUsername: @{user.username}')


@dp.message_handler(commands='Добавить_Задачу')
async def cmd_add_task(message: types.Message):
    args = message.get_args().split(' ', 2)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите текст задания и срок выполнения")
        return
    task_text = " ".join(args[:-1])
    deadline = args[-1]
    deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d %H:%M')
    task = (task_text, deadline)
    tasks.append(task)
    await message.answer(f"Задача добавлена: {task_text} со сроком {deadline}")
    asyncio.create_task(notify_about_task(task, bot, message.from_user.id))


# @dp.message_handler(commands='addtask')                                 !!!!!!!!!!!!!BAD WORKING!!!!!!!!!!!!
# async def cmd_add(message: types.Message):
#     args = message.get_args().split()
#     if len(args) < 2:
#         await message.answer("Недостаточно параметров")
#         return
#
#     task_text = ' '.join(args[:-1])
#     deadline = args[-1]
#
#     try:
#         deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
#     except ValueError:
#         await message.answer("Неверный формат крайнего срока, используйте YYYY-MM-DD HH:MM")
#         return
#
#     task = {'text': task_text, 'deadline': deadline}
#     tasks.append(task)
#
#     await message.answer("Task added: {} (deadline: {})".format(task_text, deadline.strftime('%Y-%m-%d %H:%M')))
#
#     async def notify_about_deadline(task):
#         now = datetime.now()
#         if task['deadline'] - now < timedelta(seconds=0):
#             return
#
#         await asyncio.sleep((task['deadline'] - now).total_seconds())
#         await bot.send_message(chat_id=message.from_user.id,
#                                text="Deadline for '{}' is approaching".format(task['text']))
#
#     asyncio.create_task(notify_about_deadline(task))

# async def send_notifications():
#     while True:
#         for user_id, task in tasks.copy().items():
#             task_text, deadline = task
#             if time.time() >= deadline:
#                 await bot.send_message(
#                     chat_id=user_id,
#                     text=f"Срок выполнения задания '{task_text}' достигнут!"
#                 )
#                 del tasks[user_id]
#         time.sleep(60)  # проверять каждуй минуту

@dp.message_handler(commands='Список_Задач')
async def cmd_list_tasks(message: types.Message):
    response = "\n".join([f"{task[0]} со сроком {task[1]}" for task in tasks])
    await message.answer(f"Вот ваши задачи:\n{response}")

@dp.message_handler(commands='Список_Задач')
async def cmd_list_tasks(message: types.Message):
    task_keyboard = []
    for i, task in enumerate(tasks):
        task_keyboard.append([
            InlineKeyboardButton(
                f"{task[0]} со сроком {task[1]}",
                callback_data=f"delete_task_{i}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(task_keyboard)
    await message.answer("Вот ваши задачи:", reply_markup=reply_markup)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete_task_'))
async def process_callback_delete_task(callback_query: CallbackQuery):
    task_index = int(callback_query.data.split("_")[-1])
    task = tasks.pop(task_index)
    await callback_query.answer(f"Задача {task[0]} с периодом выполнения {task[1]} удалена")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Here are your tasks:",
        reply_markup=InlineKeyboardMarkup([])
    )

async def notify_about_task(task, bot, user_id):
    await asyncio.sleep((task[1] - datetime.now()).total_seconds())
    await bot.send_message(chat_id=user_id, text=f"Напоминание о задании: {task[0]}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    #executor.run_task(send_notifications)