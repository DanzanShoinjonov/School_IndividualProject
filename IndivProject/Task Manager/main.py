import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)

# Replace with your actual Telegram bot token
BOT_TOKEN = "5920174797:AAH12J2YLjYdzcEhO0ok05RtBNGZVz118KY"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

tasks = []

# Callback data constants
DELETE_TASK_CB = "delete"
MARK_TASK_DONE_CB = "done"

class AddTask(StatesGroup):
    waiting_for_task = State()

def get_task_keyboard(task_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    delete_button = InlineKeyboardButton(text="Удалить", callback_data=f"{DELETE_TASK_CB}:{task_id}")
    mark_done_button = InlineKeyboardButton(text="MОтметить как выполненное", callback_data=f"{MARK_TASK_DONE_CB}:{task_id}")
    keyboard.add(delete_button, mark_done_button)
    return keyboard

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_task_button = types.KeyboardButton('📝Добавить задачу')
    profile_button = types.KeyboardButton('👤Профиль')
    task_list_button = types.KeyboardButton('📅Список задач')
    keyboard_markup.add(add_task_button, task_list_button)
    keyboard_markup.add(profile_button)
    await message.reply("Привет, я ваш бот для списка дел. Как я могу помочь вам?", reply_markup=keyboard_markup)

@dp.message_handler(lambda message: message.text == 'Add Task')
async def process_add_task_command(message: types.Message):
    await message.reply("Пожалуйста, введите описание задания и дату выполнения (формат: ГОД-МОНЕТ-ДЕНЬ-ЧАС-МИНУТЫ).:")

    # Set state to wait for task description
    await AddTask.waiting_for_task.set()

@dp.message_handler(state=AddTask.waiting_for_task)
async def process_task_description(message: types.Message, state: FSMContext):
    try:
        task_text, task_date_str = message.text.split(maxsplit=1)
        task_date = datetime.strptime(task_date_str, "%Y-%m-%d %H:%M")

        tasks.append({
            "id": len(tasks),
            "text": task_text,
            "date": task_date,
            "user_id": message.from_user.id
        })

        await message.reply(f"Задача добавлена: {task_text}")

    except ValueError:
        await message.reply("Неверный формат даты. Пожалуйста, попробуйте еще раз.")

    finally:
        # Reset state
        await state.finish()

@dp.message_handler(lambda message: message.text == 'Task List')
async def process_task_list_command(message: types.Message):
    unaccomplished_tasks = [task for task in tasks if task["user_id"] == message.from_user.id and task["date"] > datetime.now()]

    if unaccomplished_tasks:
        tasks_text = ""
        for task in unaccomplished_tasks:
            tasks_text += f"{task['id']}. {task['text']} (за {task['date'].strftime('%Y-%m-%d %H:%M')})\n"
            tasks_text += f"  (id: {task['id']})\n"
            tasks_text += f"  (user_id: {task['user_id']})\n\n"

            keyboard = get_task_keyboard(task['id'])
            await message.reply(tasks_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Нет невыполненных задач")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('delete:'))
async def delete_task(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    task_index = next((index for (index, d) in enumerate(tasks) if d["id"] == task_id), None)
    if task_index is not None:
        del tasks[task_index]
        await bot.answer_callback_query(callback_query.id, text="Задача удалена")
    else:
        await bot.answer_callback_query(callback_query.id, text="Задание не найдено")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('done:'))
async def mark_task_done(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split(":")[1])
    task_index = next((index for (index, d) in enumerate(tasks) if d["id"] == task_id), None)
    if task_index is not None:
        tasks[task_index]["date"] = datetime.now()
        await bot.answer_callback_query(callback_query.id, text="Задание отмечено как выполненное")
    else:
        await bot.answer_callback_query(callback_query.id, text="Задание не найдено")

@dp.message_handler(lambda message: message.text == 'Profile')
async def process_profile_command(message: types.Message):
    unaccomplished_tasks = [task for task in tasks if task["user_id"] == message.from_user.id and task["date"] > datetime.now()]

    profile_text = f"Имя: {message.from_user.full_name}\n"
    profile_text += f"ID: {message.from_user.id}\n\n"
    if unaccomplished_tasks:
        profile_text += "Невыполненные задачи:\n"
        for task in unaccomplished_tasks:
            profile_text += f"{task['id']}. {task['text']} (за {task['date'].strftime('%Y-%m-%d %H:%M')})\n"
    else:
        profile_text += "Нет невыполненных задач"

    await message.reply(profile_text)






if __name__ == '__main__':
    from aiogram.dispatcher.filters.state import State, StatesGroup
    from aiogram.dispatcher import FSMContext

    # Define states for FSM
    class AddTask(StatesGroup):
        waiting_for_task = State()

    dp.register_callback_query_handler(delete_task, lambda c: c.data and c.data.startswith(DELETE_TASK_CB))
    dp.register_callback_query_handler(mark_task_done, lambda c: c.data and c.data.startswith(MARK_TASK_DONE_CB))
    executor.start_polling(dp, skip_updates=True)


