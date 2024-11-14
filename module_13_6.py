from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    sex = State()


keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_count = KeyboardButton(text='Рассчитать')
button_info = KeyboardButton(text='Информация')
keyboard.row(button_count, button_info)

keyboard_inline = InlineKeyboardMarkup()
button_info_inline = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_count_inline = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
keyboard_inline.row(button_count_inline, button_info_inline)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=keyboard)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Введите опцию:', reply_markup=keyboard_inline)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(
        'Формула расчета калорий для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5 \n'
        'Формула расчет калорий для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст (лет):')
    await call.answer()
    await  UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=float(message.text))
    await message.answer('Введите свой рост (см):')
    await  UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=float(message.text))
    await message.answer('Введите свой вес (кг):')
    await  UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_weight(message, state):
    await state.update_data(weight=float(message.text))
    await message.answer('Введите свой пол ("м" или "ж"):')
    await  UserState.sex.set()


@dp.message_handler(state=UserState.sex)
async def send_calories(message, state):
    await state.update_data(sex=message.text)
    data = await state.get_data()
    if data.get('sex').lower() == 'м':
        normal_calories = 10 * data.get('weight') + 6.25 * data.get('growth') - 5 * data.get('age') + 5
    else:
        normal_calories = 10 * data.get('weight') + 6.25 * data.get('growth') - 5 * data.get('age') - 161
    await message.answer(f'Ваша норма калорий: {normal_calories}')
    await  state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
