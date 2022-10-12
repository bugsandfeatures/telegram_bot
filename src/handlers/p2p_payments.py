from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.filters import Command
from aiogram.utils.callback_data import CallbackData

from src.messages import MESSAGES
from src.config import Config
from src.bot import bot, dp
from src.services import DataBase

import string
import random
from yoomoney import Quickpay, Client

db = DataBase('tgbot_database.db')
cb = CallbackData('btn', 'action')

@dp.message_handler(Command('p2p_start'))
async def p2p_start(message: Message):
    try:
        await db.add_users(message.chat.id, message.chat.first_name)
    except Exception as e:
        pass
    finally:
        await message.reply('Привет!!!')

@dp.message_handler(Command('p2p_buy'))
async def p2p_buy(message: Message):
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, 10))
    quickpay = Quickpay(
        receiver='4100117963448557',
        quickpay_form='shop',
        targets='Test',
        paymentType='SB',
        sum=2,
        label=rand_string
    )

    await db.update_label(rand_string, message.chat.id)

    claim_keyboard = InlineKeyboardMarkup(inline_keyboard=[[]])
    claim_keyboard.add(InlineKeyboardButton(text='Перейти к оплате!',
                                            url=quickpay.redirected_url))
    claim_keyboard.add(InlineKeyboardButton(text='Получить товар!',
                                            callback_data='btn:claim'))
    await bot.send_message(message.chat.id,
                           MESSAGES['buy'],
                           reply_markup=claim_keyboard)

@dp.callback_query_handler(cb.filter(action='claim'))
async def check_payment(call: CallbackQuery):
    data = await db.get_payment_status(call.message.chat.id)
    bought = data[0][0]
    label = data[0][1]
    if bought == 0:
        client = Client(Config.token_p2p)
        history = client.operation_history(label=label)
        try:
            operation = history.operations[-1]
            if operation.status == 'success':
                await db.update_payment_status(call.message.chat.id)
                await bot.send_message(call.message.chat.id,
                                       MESSAGES['successful_payment'])
        except Exception as e:
            await bot.send_message(call.message.chat.id,
                                   MESSAGES['wait_message'])

    else:
        await bot.send_message(call.message.chat.id,
                               MESSAGES['successful_payment'])
