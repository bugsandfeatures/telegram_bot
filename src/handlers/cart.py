from aiogram.types import Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, \
    LabeledPrice
from aiogram.dispatcher.filters import Command
from aiogram.types.message import ContentType
from aiogram.utils.callback_data import CallbackData

from src.services import DataBase
from src.bot import dp, bot
from src.config import Config

cb = CallbackData('btn', 'type', 'product_id', 'category_id')
db = DataBase('tgbot_database.db')

async def gen_products(data, user_id):
    keyboard = InlineKeyboardMarkup()
    for i in data:
        count = await db.get_count_in_cart(user_id, i[1])
        count = 0 if not count else sum(j[0] for j in count)
        keyboard.add(InlineKeyboardButton(text=f'{i[2]}: {i[3]}p - {count}шт',
                                          callback_data=f'btn:plus:{i[1]}:{i[5]}'))
        keyboard.add(InlineKeyboardButton(text='🔽', callback_data=f'btn:minus:{i[1]}:{i[5]}'),
                     InlineKeyboardButton(text='🔼', callback_data=f'btn:plus:{i[1]}:{i[5]}'),
                     InlineKeyboardButton(text='❌', callback_data=f'btn:del:{i[1]}:{i[5]}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'btn:back:-:-'))

    return keyboard

@dp.message_handler(Command('shop'))
async def shop(message: Message):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:-:{i[1]}'))

    await message.answer('Что хотите купить?', reply_markup=keyboard)

@dp.callback_query_handler(cb.filter(type='category'))
async def goods(call: CallbackQuery, callback_data: dict):
    data = await db.get_products(callback_data.get('category_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(cb.filter(type='back'))
async def back(call: CallbackQuery):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:-:{i[1]}'))

    await call.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(cb.filter(type='minus'))
async def minus(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    if not count_in_cart or count_in_cart[0][0] == 0:
        await call.message.answer('Товар в  корзине отсутсвует!')
        return 0
    elif count_in_cart[0][0] == 1:
        await db.remove_one_item(product_id, call.message.chat.id)
    else:
        await db.change_count(count_in_cart[0][0] - 1, product_id, call.message.chat.id)

    data = await db.get_products(callback_data.get('category_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(cb.filter(type='plus'))
async def plus(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    count_in_stock = await db.get_count_in_stock(product_id)
    if count_in_stock[0][0] == 0:
        await call.message.answer('Товара нет в наличии :(')
        return 0
    elif not count_in_cart or count_in_cart[0][0] == 0:
        await db.add_to_cart(call.message.chat.id, product_id)
        await call.message.answer('Добавил!')
    elif count_in_cart[0][0] < count_in_stock[0][0]:
        await db.change_count(count_in_cart[0][0] + 1, product_id, call.message.chat.id)
    else:
        await call.message.answer('Больше нет в наличии')
        return 0

    data = await db.get_products(callback_data.get('category_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)

@dp.callback_query_handler(cb.filter(type='del'))
async def delete(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    if not count_in_cart:
        await call.message.answer('Товар в корзине отсутствует!')
        return 0
    else:
        await db.remove_one_item(product_id, call.message.chat.id)

    data = await db.get_products(callback_data.get('category_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)

@dp.message_handler(Command('empty'))
async def empty_cart(message: Message):
    await db.empty_cart(message.chat.id)
    await message.answer('Корзина пуста!')

# @dp.callback_query_handler(cb.filter(type='buy'))
# async def add_to_cart(call: CallbackQuery, callback_data: dict):
#     await call.answer(cache_time=30)
#
#     user_id = call.message.chat.id
#     product_id = callback_data.get('id')
#
#     await db.add_to_cart(user_id, product_id)
#     await call.message.answer('Добавил!')

@dp.message_handler(Command('pay'))
async def buy(message: Message):
    data = await db.get_cart(message.chat.id)
    new_data = []
    for i in range(len(data)):
        new_data.append(await db.get_user_product(data[i][2]))
    new_data = [new_data[i][0] for i in range(len(new_data))]
    prices = [LabeledPrice(label=new_data[i][2]+f' x {data[i][3]}',
                           amount=new_data[i][3]*100*data[i][3]) for i in range(len(new_data))]
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
