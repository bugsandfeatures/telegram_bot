from aiogram.types import Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, \
    LabeledPrice
from aiogram.dispatcher.filters import Command
from aiogram.types.message import ContentType
from aiogram.utils.callback_data import CallbackData

from src.services import DataBase
from src.bot import dp, bot
from src.config import Config

cb = CallbackData('btn', 'type', 'id')
db = DataBase('tgbot_database.db')

@dp.message_handler(Command('shop'))
async def shop(message: Message):
    data = await db.get_products()
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[2]}: {i[3]}р', callback_data=f'btn:buy:{i[1]}'))
    await message.answer('Что хотите купить?', reply_markup=keyboard)

@dp.message_handler(Command('empty'))
async def empty_cart(message: Message):
    await db.empty_cart(message.chat.id)
    await message.answer('Корзина пуста!')

@dp.callback_query_handler(cb.filter(type='buy'))
async def add_to_cart(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=30)

    user_id = call.message.chat.id
    product_id = callback_data.get('id')

    await db.add_to_cart(user_id, product_id)
    await call.message.answer('Добавил!')

@dp.message_handler(Command('pay'))
async def buy(message: Message):
    data = await db.get_cart(message.chat.id)
    new_data = []
    for i in range(len(data)):
        new_data.append(await db.get_user_product(data[i][2]))
    new_data = [new_data[i][0] for i in range(len(new_data))]
    prices = [LabeledPrice(label=i[2], amount=i[3]*100) for i in new_data]
    await bot.send_invoice(message.chat.id,
                           title='Cart',
                           description='Description',
                           provider_token=Config.pay_token,
                           currency='rub',
                           need_email=True,
                           prices=prices,
                           start_parameter='example',
                           payload='some_invoice')

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def s_pay(message: Message):
    await db.empty_cart(message.chat.id)
    await bot.send_message(message.chat.id, 'Платеж прошел успешно!!!')

