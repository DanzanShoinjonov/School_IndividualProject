import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.types import CallbackQuery
import logging
from constants import *
from keyboards import *
import datetime




API_TOKEN = '5920174797:AAH12J2YLjYdzcEhO0ok05RtBNGZVz118KY'

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)

# Adding task list to the bot
task_list = []
tasks = []

# Command to start the bot
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    keyboard.add("Да", "Нет")
    keyboard.add("Может", "Я не знаю")
    await bot.send_message(
        chat_id=message.chat.id,
        text="Привет! Нравится ли вам этот бот?",
        reply_markup=keyboard
    )


@dp.message_handler(commands='add')
async def cmd_add(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="What task would you like to add?"
    )

    # Wait for task description
    task_desc = await dp.register_message_handler(lambda message: True, chat_id=message.chat.id)

    await bot.send_message(
        chat_id=message.chat.id,
        text="What date is the task due? (YYYY-MM-DD)"
    )

    # Wait for due date
    task_due_date = await dp.register_message_handler(lambda message: True, chat_id=message.chat.id)

    await bot.send_message(
        chat_id=message.chat.id,
        text="What time is the task due? (HH:MM)"
    )

    # Wait for due time
    task_due_time = await dp.register_message_handler(lambda message: True, chat_id=message.chat.id)

    # Store task in tasks list
    due_date = datetime.datetime.strptime(task_due_date.text + " " + task_due_time.text, "%Y-%m-%d %H:%M")
    tasks.append({
        'description': task_desc.text,
        'due_date': due_date
    })

    await bot.send_message(
        chat_id=message.chat.id,
        text="Task added successfully!"
    )


# Command to display all the tasks in the list
@dp.message_handler(commands='list')
async def cmd_list(message: types.Message):
    if task_list:
        text = "Твой TO-DO list:\n"
        for i, task in enumerate(task_list):
            text += f"{i + 1}. {task}\n"
        await bot.send_message(
            chat_id=message.chat.id,
            text=text
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Ваш список дел пуст. Добавьте несколько задач с помощью команды /add."
        )

# Command to clear the task list
@dp.message_handler(commands='clear')
async def cmd_clear(message: types.Message):
    task_list.clear()
    await bot.send_message(
        chat_id=message.chat.id,
        text="Ваш список дел очищен."
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
