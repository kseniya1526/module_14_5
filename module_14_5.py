from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import crud_functions
from crud_functions import *


crud_functions.initiate_db()
products = crud_functions.get_all_products()


api = "7689512789:AAHgPkfxoHEfc2Yr2MCe8g-6FnRJsYLeADY"

bot = Bot(token=api)

dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Рассчитать')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.add(button1, button2, button3, button4)

kb1 = InlineKeyboardMarkup()
button5 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button6 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb1.add(button5, button6)

kb2 = InlineKeyboardMarkup()
button7 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button8 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button9 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button10 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb2.add(button7, button8, button9, button10)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb1)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


# 1.1. Класс состояний для расчета нормы калорий
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age1=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth1=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight1=message.text)
    data = await state.get_data()
    # Упрощенный вариант формулы Миффлина-Сан Жеора для женщин:
    # 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.
    norma_calories = 10 * float(data["weight1"]) + 6.25 * float(data['growth1']) - 5 * float(data['age1']) - 161
    await message.answer(f'Ваша норма калорий: {norma_calories}')
    await state.finish()


# 2. Кнопка начала
@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


# 3. Класс состояний для регистрации
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя:')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    datauser = await state.get_data()
    add_user(**datauser)
    await message.answer('Регистрация прошла успешно!')
    await state.finish()


# 4. Кнопка информации
@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Это бот, позволяющий рассчитать норму калорий по формуле Миффлина-Сан Жеора для женщин')


# 5. Кнопка покупки товара
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for pr in products:
        await message.answer(f"Название: {pr[1]} | "
                             f"Описание: Описание {pr[2]} | "
                             f"Цена: {pr[3]}")
        with open(f"images (1).jpeg", "rb") as img:
            await message.answer_photo(img)
    await message.answer("Выберите продукт для покупки:", reply_markup=kb2)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


# 6. Кнопка на все остальное
@dp.message_handler()
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)