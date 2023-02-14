import logging
import datetime
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set up the bot and dispatcher
bot = Bot(token='5920174797:AAH12J2YLjYdzcEhO0ok05RtBNGZVz118KY')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Define a list to store tasks
tasks = []

# Define a state to keep track of the process of adding a task
class AddTask(StatesGroup):
    waiting_for_task = State()
    waiting_for_date = State()



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_task_button = types.KeyboardButton('📝Добавить задачу')
    task_list_button = types.KeyboardButton('📅Список задач')
    profile_button = types.KeyboardButton('👤Профиль')
    help_button = types.KeyboardButton('🤗Помощь')
    keyboard.add(add_task_button, task_list_button)
    keyboard.add(profile_button, help_button)
    await message.reply("Привет!\nПоздравляю с днём Св.Валентина 💌 \nЯ бот для составления списка дел. Что бы ты хотел сделать?", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == '🤗Помощь')
async def process_help_command(message: types.Message):
    help_text = "Вот что я могу сделать:\n\n"
    help_text = 'За поддержкой можешь обращаться к администратору: @shooinj\n'
    help_text += "/start - Запуск бота\n"
    help_text += "/help - Получить помощь\n"
    help_text += "/add_task - Добавить задачу\n"
    help_text += "/task_list - Список задач\n"
    help_text += "/profile - Информация о пользователе\n"
    await message.reply(help_text)


# Define a function to create an inline keyboard with "delete" and "done" buttons for a task
def create_task_inline_keyboard(task_id):
    keyboard = InlineKeyboardMarkup()
    delete_button = InlineKeyboardButton("Удалить", callback_data=f"delete:{task_id}")
    done_button = InlineKeyboardButton("Сделано", callback_data=f"done:{task_id}")
    keyboard.add(delete_button, done_button)
    return keyboard

# Define a function to send a task reminder to a user
async def send_task_reminder(task):
    task_id = task['id']
    task_text = task['text']
    user_id = task['user_id']
    message_text = f"Напоминание: {task_text}"
    await bot.send_message(chat_id=user_id, text=message_text)
    task['done'] = True

# Define a command handler to show the user's task list
@dp.message_handler(lambda message: message.text == '📅Список задач')
async def process_task_list_command(message: types.Message):
    unfinished_tasks = [task for task in tasks if task['user_id'] == message.from_user.id and not task['done']]
    if unfinished_tasks:
        task_list_text = "Ваши текущие задачи:"
        for task in unfinished_tasks:
            task_list_text = f"\n- {task['text']} (due on {task['date'].strftime('%Y-%m-%d %H:%M')})"
            keyboard = create_task_inline_keyboard(task['id'])
            await bot.send_message(chat_id=message.from_user.id, text=task_list_text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Нет задач.")

# Define a callback query handler for the "delete" and "done" buttons
@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_query(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data.startswith("delete:"):
        task_id = uuid.UUID(data[len("delete:"):])
        task = next((task for task in tasks if task['id'] == task_id), None)
        if task:
            tasks.remove(task)
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="Задача удалена.")
    elif data.startswith("done:"):
        task_id = uuid.UUID(data[len("done:"):])
        task = next((task for task in tasks if task['id'] == task_id), None)
        if task:
            task['done'] = True
            await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text="Задание отмечено как выполненное.")

# Define a message handler for the "Add Task" button
@dp.message_handler(Text(equals="📝Добавить задачу"))
async def process_add_task_button(message: types.Message):
    # Ask the user to enter the task text
    await message.reply("Пожалуйста, введите задание, которое вы хотите добавить:")
    await AddTask.waiting_for_task.set()

    # Define a message handler to get the task text from the user


@dp.message_handler(state=AddTask.waiting_for_task)
async def process_task_text(message: types.Message, state: FSMContext):
    task_text = message.text
    # Ask the user to enter the task date
    await message.reply("Пожалуйста, введите дату и время выполнения задания (в формате ГГГГ-ММ-ДД ЧЧ:ММ).:")
    await state.update_data(task_text=task_text)
    await AddTask.waiting_for_date.set()


# Define a message handler to get the task date from the user and add the task to the list
@dp.message_handler(state=AddTask.waiting_for_date)
async def process_task_date(message: types.Message, state: FSMContext):
    task_text = (await state.get_data())['task_text']
    try:
        task_date = datetime.datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        task_id = uuid.uuid4()
        task = {'id': task_id, 'text': task_text, 'date': task_date, 'user_id': message.from_user.id, 'done': False}
        tasks.append(task)
        await message.reply(f"Задача добавлена: {task_text} (в срок {task_date.strftime('%Y-%m-%d %H:%M')})")

        # Set up a job to send a reminder for the task
        delta = task_date - datetime.datetime.now()
        if delta.total_seconds() > 0:
            job = bot.loop.create_task(asyncio.sleep(delta.total_seconds()))
            job.add_done_callback(lambda _: asyncio.ensure_future(send_task_reminder(task)))
    except ValueError:
        await message.reply(
            "Неверный формат даты. Пожалуйста, введите дату и время выполнения задания (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")
        return
    finally:
        await state.finish()


# @dp.message_handler(state=AddTask.waiting_for_date)
# async def process_task_date(message: types.Message, state: FSMContext):
#     task_text = (await state.get_data())['task_text']
#     task_date = datetime.datetime.strptime(message.text, '%Y-%m-%d %H:%M')
#     # Set up a job to send a reminder for the task
#     delta = task_date - datetime.datetime.now()
#     if delta.total_seconds() > 0:
#         job = bot.loop.create_task(asyncio.sleep(delta.total_seconds()))
#         job.add_done_callback(lambda _: asyncio.ensure_future(send_task_reminder(task)))


# Define a message handler for the "Profile" button
@dp.message_handler(Text(equals="👤Профиль"))
async def process_profile_button(message: types.Message):
    unfinished_tasks = [task for task in tasks if task['user_id'] == message.from_user.id and not task['done']]
    if unfinished_tasks:
        profile_text = f"Имя: {message.from_user.first_name}\nID: {message.from_user.id}\nНезавершенные задачи:"
        for task in unfinished_tasks:
            profile_text += f"\n- {task['text']} (в срок {task['date'].strftime('%Y-%m-%d %H:%M')})"
        await message.reply(profile_text)#, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await message.reply(
            f"Name: {message.from_user.first_name} {message.from_user.last_name}\nID: {message.from_user.id}\nНезавершенные задачи.")



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True, loop=loop)
