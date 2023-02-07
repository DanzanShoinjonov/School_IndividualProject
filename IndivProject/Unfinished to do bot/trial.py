import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import ParseMode
from aiogram.utils import markdown
from aiogram.dispatcher import FSMContext
from aiogram.types import Message


API_TOKEN = ''

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.append(LoggingMiddleware())

class Task:
    def __init__(self, task_name: str, due_date: str):
        self.task_name = task_name
        self.due_date = due_date

    def __str__(self):
        return f'{self.task_name} is due on {self.due_date}'

tasks = []

# States
class Form(states.Form):
    task_name = states.String(
        'Task name',
        validators=[validators.DataRequired()]
    )
    due_date = states.String(
        'Due date (format: yyyy-mm-dd)',
        validators=[validators.DataRequired()]
    )
    ...

# You can use state '*' if you need to handle all states
@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(commands='cancel', state='*')
@dp.message_handler(lambda message: message.text == 'cancel', state='*')
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.info('Cancelling state %r', current_state)
    current_state = await state.get_state()
    logging.info('Cancelling state %r', current_state)
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    if current_state.key in ('Form'):
        logging.info('Cancelling state %r', current_state)
        current_state.cancelled = True
        _ = await state.finish()
        current_state = await state.get_state()
        logging.info('Cancelled state %r', current_state)

@dp.message_handler(commands='add_task', state='*')
async def cmd_add_task(message: Message):
    """
    Conversation's entry point
    """
    # Start conversation
    await Form.first()

# You can use state '*' if you need to handle all states
@dp.message_handler(commands='task_list', state='*')
async def cmd_show_task_list(message: Message):
    """
    Show all tasks in the task list.
    """
    if tasks:
        msg = '\n'.join([str(task)
        for task in tasks])
        await bot.send_message(message.chat.id, msg)
    else:
        await bot.send_message(message.chat.id, 'Task list is empty.')

@ dp.message_handler(commands='profile', state='*')
async   def cmd_show_profile(message: Message):
    """
    Display the user's profile information.
    """
    user = message.from_user
    await bot.send_message(message.chat.id, f'User: {user.full_name} \nUsername: @{user.username}')

# If the user ever sent a message, it will trigger this state.
@dp.message_handler(lambda message: message.text == 'delete', state='task_list')
@dp.message_handler(lambda message: message.text == 'cancel', state='*')
async def cmd_delete_task(message: Message):
    """
    Allow the user to delete a task.
    """
    global tasks
    if tasks:
        msg = '\n'.join([f'{i + 1}. {task}' for i, task in enumerate(tasks)])
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
        itembtns = [types.KeyboardButton(f'{i + 1}') for i, task in enumerate(tasks)]
        markup.add(*itembtns)
        await bot.send_message(
            message.chat.id,
            'Select the task number you want to delete:',
            reply_markup=markup
        )
        # Set state
        await Form.next()
    else:
        await bot.send_message(
            message.chat.id,
            'Task list is already empty.'
        )
        return

# If the user entered a digit, it will trigger this state.
@dp.message_handler(lambda message: message.text.isdigit(), state='task_list')
async def process_task_number(message: Message, state: FSMContext):
    async with state.proxy() as data:
        task_number = int(message.text)
        if task_number <= len(tasks):
            del tasks[task_number - 1]
            await bot.send_message(
                message.chat.id,
                f'Task {task_number} has been deleted from the task list.'
            )
        else:
            await bot.send_message(
                message.chat.id,
                'Invalid task number, please try again.'
            )
        # Cancel state and inform user
        return await state.cancel()

@dp.message_handler(state=Form.task_name)
async def process_task_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['task_name'] = message.text

        # Update state and data
        await Form.next()

@dp.message_handler(state=Form.due_date)
async def process_due_date(message: Message, state: FSMContext):
    async with state.proxy() as data:
        due_date = message.text

        # Validate the due date
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return await bot.send_message(
                message.chat.id,
                'Invalid date format, use YYYY-MM-DD.'
            )

        # Add the task to the list
        global tasks
        task = f"{data['task_name']} due on {due_date.strftime('%Y-%m-%d')}"
        tasks.append(task)

        # Notify the user of the due date
        await bot.send_message(
            message.chat.id,
            f'Task "{data["task_name"]}" with due date {due_date.strftime("%Y-%m-%d")} added to the task list.'
        )

        # Reset the state
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)





