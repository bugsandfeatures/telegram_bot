from aiogram.types import LabeledPrice, Message, PreCheckoutQuery, ContentType, ShippingQuery, ShippingOption
from aiogram.dispatcher.filters import Command

from src.bot import bot, dp
from src.config import Config

price = [LabeledPrice(label='Ноутбук', amount=1000000)]

fast_shipping_option = ShippingOption(id='fast', title='Быстрая').add(LabeledPrice('Быстрая', 50000))

@dp.message_handler(Command('start'))
async def start(message: Message):
    await bot.send_message(message.chat.id, 'Добро пожаловать!!!')

@dp.message_handler(Command('buy'))
async def buy_process(message: Message):
    await bot.send_invoice(message.chat.id,
                           title='Laptop',
                           description='Description',
                           provider_token=Config.pay_token,
                           currency='rub',
                           need_email=True,
                           is_flexible=True,
                           prices=price,
                           start_parameter='example',
                           payload='some_invoice')

@dp.shipping_query_handler(lambda query: True)
async def shipping_process(shipping_query: ShippingQuery):
    if shipping_query.shipping_address.country_code == 'MG':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message='Сюда не доставляем!'
        )
    shipping_options = [ShippingOption(id='regular',
                                       title='Обычная доставка').add(LabeledPrice('Обычная доставка', 10000))]

    if shipping_query.shipping_address.country_code == 'RU':
        shipping_options.append(fast_shipping_option)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_options
    )

# @dp.pre_checkout_query_handler(lambda query: True)
# async def pre_checkout_process(pre_checkout: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)
#
# @dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
# async def successful_payment(message: Message):
#     await bot.send_message(message.chat.id, 'Платеж прошел успешно!')
