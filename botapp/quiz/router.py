import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession
from config import *
import datetime
from bot import bot
from aiogram.filters import CommandStart
from db.models.models.manager import *
from aiohttp import ClientSession
from utils.utils import *
from .schemas import *
from .form import *
from user.user import UserDAO


quiz_router = Router()


@quiz_router.callback_query(F.data == "extend")
async def surv_process(call: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    await call.message.answer("Вы хотите продлить, или выбрать новый?", reply_markup=kb_extend_or_other())

@quiz_router.callback_query(F.data == "extend_this")
async def surv_process(call: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    purch = await PurchaseDao.find_one_or_none(session=session_without_commit, filters=UserPurch(telegram_id=call.from_user.id))
    tariff = await TarrifDao.find_one_or_none(session=session_without_commit, filters=TariffIDModel(id=purch.id))
    product_text = (
                f"📦 <b>Название тарифа:</b> {tariff.name}\n\n"
                f"💰 <b>Цена:</b> {tariff.price} руб.\n\n"
                f"📝 <b>Описание:</b>\n<i>{tariff.description}</i>\n\n"
                f"📝 <b>Тип тарифа:</b>\n<i>{tariff.type_tariff}</i>\n\n"
                f"━━━━━━━━━━━━━━━━━━"
    )
    await call.message.answer(product_text, reply_markup=tariffs_kb(tariff.id, tariff.price))
    

@quiz_router.callback_query(F.data == "return")
async def surv_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Здравствуйте, введите ваше ФИО")
    await state.set_state(Useradd.fio)

    

@quiz_router.message(Useradd.fio)
async def surv_process(message: Message, state: FSMContext):
    if validate_text(message.text):
        await state.update_data(fio=message.text)
        await message.answer("Пожайлуста не допуская ошибок! введите вашу дату рождения в формате - 'ДД/ММ/ГГ', например 01/03/25")
        await state.set_state(Useradd.date_birth)
    else:
        await message.answer("Введите корректно ваше ФИО пожайлуста.")
        return

@quiz_router.message(Useradd.date_birth)
async def surv_process(message: Message, state: FSMContext, session_with_commit: AsyncSession):
    if validate_birth_date(message.text):
        await state.update_data(date_birth=message.text)
        data = await state.get_data()
        print(data)
        values = User_upd(
            telegram_id = message.from_user.id,
            username = message.from_user.username,
            fio = data["fio"],
            data_birth = datetime.date(data["date_birth"])
        )
        await UserDAO.add(session=session_with_commit, values=values)
        await message.answer("Вот наши тарифы, нажмите на кнопку чтобы посмотреть.", reply_markup=kb_tarrif())
    else:
        await message.answer("Пожайлуста не допуская ошибок! введите вашу дату рождения в формате - 'ДД/ММ/ГГ', например 01/03/25")
        return

@quiz_router.callback_query(F.data == "tariffs")
async def surv_process(call: CallbackQuery, session_without_commit: AsyncSession):
    products_by_cat = await ProductDao.find_all(session=session_without_commit)
    await call.answer('Все тарифы.')
    count_prods = len(products_by_cat)
    if count_prods:
        print(products_by_cat[0].name)
        for i in products_by_cat:
            typetariff = await TypeiftariffsDAO.find_one_or_none(session=session_without_commit, filters=TypeoftariffIDModel(type_of_tarrifs_id=i.type_tariff.id))
            product_text = (
                f"📦 <b>Название тарифа:</b> {i.name}\n\n"
                f"💰 <b>Цена:</b> {i.price} руб.\n\n"
                f" <b>Описание:</b>\n<i>{i.description}</i>\n\n"
                f"📝 <b>Тип тарифа:</b>\n<i>{i.type_tariff.type_tarif_name}</i>\n\n"
                f" <b>На сколько:</b>\n<i>{typetariff.how_much_days} д.</i>\n\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            await call.message.answer(
                product_text,
                reply_markup=buy_kb(i.id, i.price)
            )

        await call.message.answer("Купите какой либо тариф, чтобы продолжить.")
    else:
        await call.answer("На данный моент нету тарифов.")


@quiz_router.callback_query(lambda message: F.data.startswith('buy_'))
async def process_payment(call: CallbackQuery, session_without_commit: AsyncSession):
    user_info = await UserDAO.find_one_or_none(
    session=session_without_commit,
    filters=UserBaseInDB(telegram_id=call.from_user.id)
    )
    _, product_id, price = call.data.split('_')
    tarifа = await TarrifDao.find_one_or_none_by_id(session=session_without_commit, data_id=product_id)
    # await bot.send_invoice(
    #     chat_id=call.from_user.id,
    #     title=f'Оплата 👉 {price}₽',
    #     description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы открыть доступ к выбранному тарифу.',
    #     payload=f"{user_info.id}_{product_id}",
    #     provider_token=YTOKEN,
    #     currency='rub',
    #     prices=[LabeledPrice(
    #         label=f'Оплата {price}',
    #         amount=int(price) * 100
    #     )],
    #     reply_markup=get_product_buy_kb(price)
    # )
    checkout_session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': f'{tariff.name}',
                'description': f'Пожалуйста, завершите оплату в размере {price}$, чтобы открыть доступ к выбранному тарифу.',
            },
            'unit_amount': int(price) * 100
        },
        'quantity': 1,
    }],
    metadata={
        'tg_chat_id': user_info.telegram_id,
        'user_id': user_info.id,
        'product_id': product_id
    },
        mode='payment',
        success_url=f'{SITE_URL}/success',
        cancel_url=f'{SITE_URL}/cancel',
        client_reference_id=user_info.id
    )
    await call.message.answer(f"✅Нажмите чтобы оплатить{price} USD: {checkout_session.url}")

@quiz_router.callback_query(F.data.startswith('buy_'))
async def process_about(call: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    user_info = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=UserBaseInDB(telegram_id=call.from_user.id)
    )
    _, product_id, price = call.data.split('_')
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оплата 👉 {price}₽',
        description=f'Пожалуйста, завершите оплату в размере {price}₽, чтобы открыть доступ к выбранному тарифу.',
        payload=f"{user_info.id}_{product_id}",
        provider_token=YTOKEN,
        currency='rub',
        prices=[LabeledPrice(
            label=f'Оплата {price}',
            amount=int(price) * 100
        )],
        reply_markup=get_product_buy_kb(price)
    )
    await call.message.delete()

@quiz_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@quiz_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def surv_successful_payment(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    payment_info = message.successful_payment
    user_id, product_id = payment_info.invoice_payload.split('_')
    payment_data = {
        'user_id': int(user_id),
        'payment_id': payment_info.telegram_payment_charge_id,
        'price': payment_info.total_amount / 100,
        'product_id': int(product_id)
    }
    await PurchaseDao.add(session=session_with_commit, values=PaymentData(**payment_data))
    product_data = await ProductDao.find_one_or_none_by_id(session=session_with_commit, data_id=int(product_id))

    for admin_id in ADMINS:
        try:
            username = message.from_user.username
            user_info = f"@{username} ({message.from_user.id})" if username else f"c ID {message.from_user.id}"

            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💲 Пользователь {user_info} купил товар <b>{product_data.name}</b> (ID: {product_id}) "
                    f"за <b>{product_data.price} ₽</b>."
                )
            )
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

    file_text = "📦 <b>Товар включает файл:</b>" if product_data.file_id else "📄 <b>Товар не включает файлы:</b>"
    product_text = (
        f"🎉 <b>Спасибо за покупку тарифа!</b>\n\n"
        f"🛒 <b>Информация о вашем тарифе:</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔹 <b>Название:</b> <b>{product_data.name}</b>\n"
        f"🔹 <b>Описание:</b>\n<i>{product_data.description}</i>\n"
        f"🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{file_text}\n\n"
        f"ℹ️ <b>Информацию о купленных тарифах вы можете найти в личном профиле.</b>"
    )
    await message.answer(
        text=product_text,
        reply_markup=main_user_kb(message.from_user.id)
        )

