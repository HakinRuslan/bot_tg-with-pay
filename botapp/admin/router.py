import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from config import *
from bot import bot
from user.user import UserDAO
from .kb import *
from .schemas import *
from db.models.models.manager import *
from utils.utils import *
from .form import *

admin_router = Router()

@admin_router.callback_query(F.data == "admin_panel", F.from_user.id.in_(ADMINS))
async def start_admin(call: CallbackQuery):
    await call.answer('Доступ в админ-панель разрешен!')
    await call.message.edit_text(
        text="Вам разрешен доступ в админ-панель. Выберите необходимое действие.",
        reply_markup=admin_kb()
    )

@admin_router.callback_query(F.data == 'statistic', F.from_user.id.in_(ADMINS))
async def admin_statistic(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')

    stats = await UserDAO.get_statistics(session=session_without_commit)
    total_summ = await PurchaseDao.get_full_summ(session=session_without_commit)
    stats_message = (
        "📈 Статистика пользователей:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых за сегодня: {stats['new_today']}\n"
        f"📅 Новых за неделю: {stats['new_week']}\n"
        f"📆 Новых за месяц: {stats['new_month']}\n\n"
        f"💰 Общая сумма заказов: {total_summ} руб.\n\n"
        "🕒 Данные актуальны на текущий момент."
    )
    await call.message.edit_text(
        text=stats_message,
        reply_markup=stat_kb()
    )


@admin_router.callback_query(F.data == "users", F.from_user.id.in_(ADMINS))
async def start_admin(call: CallbackQuery, session_without_commit: AsyncSession):
    users = await UserDAO.find_all(session=session_without_commit)
    user_data = await UserDAO.get_statistics(session=session_without_commit)
    text = (
        "👥 Зарегестрированные пользователи в базе:\n\n"
        "✅ Выберите в меню пользователя чтобы его изменить.\n"
        f"👥 Всего пользователей: {user_data['total_users']}\n"
    )
    for user in users:
        purchased_tar = await UserDAO.get_purchased_products(session=session_without_commit, telegram_id=user.telegram_id)
        text += f'👤 <code>{user.telegram_id} - @{user.username}</code>, активный платеж - {"<b>да</b>" if purchased_tar[0].active else "<b>нет</b>"}\n'
    await call.message.answer(
        text=text,
        reply_markup=await get_paginated_kb(page=0, session=session_without_commit)
    )

@admin_router.callback_query(F.data.startswith('about-user'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    user_id = int(call.data.split('_')[-1])
    user = await UserDAO.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=user_id))
    purchs = await UserDAO.get_purchased_products(session=session_without_commit, user_id=user.id)
    text = (
        f" 👤@{user.username}: { "Ограничения есть." if not user.active else "" }\n\n"
        f"История платежей:\n\n"
    )
    for i in purchs:
        text += f"💳 <i>{i.tariff.name}, цена - {i.price}</i>, активный платеж - {"<b>да</b>" if i.active else "<b>нет</b>"}, сделан - <i>{how_much_ago(i.created_at)}</i>\n"
    await call.message.edit_text(text=text, reply_markup=await admin_kb_user(user_id=user_id, session=session_without_commit))


@admin_router.callback_query(F.data.startswith('ogr-user'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    user_id = int(call.data.split('_')[-1])
    user_data = await UserDAO.find_one_or_none(session=session_with_commit, filters=UserBaseInDB(telegram_id=user_id))
    user = None
    if user_data.active:
        values = User_upd_active(
            active = False
        )
        user = await UserDAO.update(session=session_with_commit, values=values, record_id=user_id)
    else:
        values = User_upd_active(
            active = True
        )
        user = await UserDAO.update(session=session_with_commit, values=values, record_id=user_id)
    await call.answer(f"Вы ограничили, {user.username} в пользовании бота.", show_alert=True)
    purchs = await UserDAO.get_purchased_products(session=session_with_commit, user_id=user.id)
    print(user)
    text = (
        f"👤 {user.username}: { "Ограничения есть." if not user.active else "" }\n\n"
        f"История платежей:\n\n"
    )
    for i in purchs:
        text += f"💳 <i>{i.tariff.name}, цена - {i.price}</i>, активный платеж - {"<b>да</b>" if i.active else "<b>нет</b>"}, сделан - <i>{how_much_ago(i.created_at)}</i>\n"
    await call.message.edit_text(text=text, reply_markup=await admin_kb_user(user_id=user_id, session=session_with_commit))


@admin_router.callback_query(Pagination.filter())
async def products_pagination_callback(call: CallbackQuery, callback_data: dict,  session_without_commit: AsyncSession):
    page =  callback_data.page
    print(page)
    await call.message.edit_reply_markup(  
    reply_markup=await get_paginated_kb(page=page, session=session_without_commit)  
)

@admin_router.callback_query(F.data == "cancel", F.from_user.id.in_(ADMINS))
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена сценария добавления')
    await call.message.delete()
    await call.message.answer(
        text="Отмена добавления",
        reply_markup=admin_kb_back()
    )

@admin_router.callback_query(F.data == 'process_products', F.from_user.id.in_(ADMINS))
async def admin_process_products(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления')
    all_tariff_count = await TarrifDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"📂 На данный момент в базе данных {all_tariff_count} тарифов. что вы собираетесь сделать с ними?",
        reply_markup=product_management_kb()
    ) 


@admin_router.callback_query(F.data == 'process_category', F.from_user.id.in_(ADMINS))
async def admin_process_cats(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим управления')
    all_types_count = await TypeiftariffsDAO.count(session=session_without_commit)
    await call.message.edit_text(
        text=f"📂 На данный момент в базе данных {all_types_count} типов тариффов. что вы собираетесь сделать с ними?",
        reply_markup=category_management_kb()
    )

@admin_router.callback_query(F.data == 'delete_cat', F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления')
    all_types = await TypeiftariffsDAO.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"📂 На данный момент в базе данных {len(all_types)} типов тарифов. Для удаления нажмите на кнопку ниже"
    )
    for product_data in all_cats:
        product_text = (f'<b> тип тарифа:</b> <b>{product_data.category_name}</b>\n')
        await call.message.answer(text=product_text, reply_markup=dell_cat_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell-cat'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await TypeiftariffsDAO.delete(session=session_with_commit, filters=ProductCategoryIDModel(id=product_id))
    await call.answer(f"Тип тарифа с ID {product_id} удален!", show_alert=True)
    await call.message.delete()

@admin_router.callback_query(F.data == 'add_cat', F.from_user.id.in_(ADMINS))
async def admin_process_add_type_tariff(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен добавления типа тарифа.')
    await call.message.delete()
    msg = await call.message.answer(text="Укажите название для типа тарифа: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtypeoftariff.type_tarif_name)

@admin_router.callback_query(F.text, F.from_user.id.in_(ADMINS), Addtypeoftariff.type_tarif_name)
async def admin_process_add_how_much_days(call: CallbackQuery, state: FSMContext):
    await state.update_data(type_tarif_name=message.text)
    await call.message.delete()
    msg = await call.message.answer(text="Укажите в днях(только числом), то сколько будут актуальны тарифы, для этого типа тарифов: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtypeoftariff.how_much_days)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), Addtypeoftariff.how_much_days)
async def admin_process_name(message: Message, state: FSMContext):
    try:
        days = int(message.text)
        await state.update_data(how_much_ago=days)
        cat_data = await state.get_data()
        cat_text = (
            f'Проверьте, все ли корректно:\n\n'
            f'<b>Тип тарифа:</b> <b>{cat_data["category_name"]}</b>\n'
            f'Заданный промежуток в днях, насколько будет актуальны тарифы для этого типа - {days} д.'
            )
        await process_dell_text_msg(message, state)
        msg = await message.answer(text=cat_text, reply_markup=admin_confirm_kb())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(Addtypeoftariff.confirm_add)
    except ValueError:
        await message.answer(text="Ошибка! Необходимо ввести числовое значение для цены.")
        return

@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(ADMINS), Addtypeoftariff.confirm_add)
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    type_tariff_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=type_tariff_data["last_msg_id"])
    del type_tariff_data["last_msg_id"]
    await TypeiftariffsDAO.add(session=session_with_commit, values=CategoryModel(**type_tariff_data))
    await call.message.answer(text="🆗 Тип тарифа успешно добавлен в базу данных!", reply_markup=admin_kb())


@admin_router.callback_query(F.data == 'add_product', F.from_user.id.in_(ADMINS))
async def admin_process_add_tariff(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен сценарий добавления тарифа.')
    await call.message.delete()
    msg = await call.message.answer(text="Для начала укажите название тарифа: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtariff.name)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), Addtariff.name)
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(text="Теперь дайте короткое описание тарифу: ", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtariff.description)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), Addtariff.description)
async def admin_process_description(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.update_data(description=message.html_text)
    await process_dell_text_msg(message, state)
    cat_type_tariffs_data = await TypeiftariffsDAO.find_all(session=session_without_commit)
    msg = await message.answer(text="Теперь выберите категорию тарифа: ", reply_markup=catalog_admin_kb(cat_type_tariffs_data))
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtariff.type_of_tarrifs_id)


@admin_router.callback_query(F.data.startswith("add_category_"),
                             F.from_user.id.in_(ADMINS),
                             Addtariff.type_of_tarrifs_id)
async def admin_process_type_tariff(call: CallbackQuery, state: FSMContext):
    type_of_tarrifs_id = int(call.data.split("_")[-1])
    await state.update_data(type_of_tarrifs_id=type_of_tarrifs_id)
    await call.answer('Тип тарифа успешно выбран.')
    msg = await call.message.edit_text(text="Введите цену тарифа в долларах, например: 10", reply_markup=cancel_kb_inline())
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(Addtariff.price)


@admin_router.message(F.text, F.from_user.id.in_(ADMINS), Addtariff.price)
async def admin_before_add(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        tariff_data = await state.get_data()
        type_of_tariff_info = await TypeiftariffsDAO.find_one_or_none_by_id(session=session_without_commit,
                                                                data_id=tariff_data.get("type_of_tarrifs_id"))

        tariff_add_text = (f'🛒 Проверьте, все ли корректно:\n\n'
                        f'🔹 <b>Название товара:</b> <b>{tariff_data["name"]}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>{tariff_data["description"]}</b>\n\n'
                        f'🔹 <b>Cрок тарифа:</b>\n\n<b>{type_of_tariff_info.how_much_days} д.</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{ttariff_data["price"]} ₽</b>\n'
                        f'🔹 <b>Тип тарифа:</b> <b>{type_of_tariff_info.type_tarif_name} (ID: {type_of_tariff_info.id})</b>\n\n'
        )
        await process_dell_text_msg(message, state)
        msg = await message.answer(text=product_text, reply_markup=admin_confirm_kb())
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(Addtariff.confirm_add)
    except ValueError:
        await message.answer(text="Ошибка! Необходимо ввести числовое значение для цены.")
        return

@admin_router.callback_query(F.data == "confirm_add", F.from_user.id.in_(ADMINS), Addtariff.confirm_add)
async def admin_process_confirm_add(call: CallbackQuery, state: FSMContext, session_with_commit: AsyncSession):
    tariff_data = await state.get_data()
    await bot.delete_message(chat_id=call.from_user.id, message_id=tariff_data["last_msg_id"])
    del product_data["last_msg_id"]
    await TarrifDao.add(session=session_with_commit, values=ProductModel(**tariff_data))
    await state.clear()
    await call.message.answer(text="🆗 Тариф успешно добавлен в базу данных!", reply_markup=admin_kb())

@admin_router.callback_query(F.data == 'delete_product', F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer('Режим удаления')
    all_tariffs = await TarrifDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f"На данный момент в базе данных {len(all_tariffs)} тарифов. Для удаления нажмите на кнопку ниже"
    )

    for product_data in all_tariffs:

        product_text = (f'🛒 Описание товара:\n\n'
                        f'🔹 <b>Название товара:</b> <b>{product_data.name}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>{product_data.description}</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{product_data.price} ₽</b>\n')

        await call.message.answer(text=product_text, reply_markup=dell_product_kb(product_data.id))

@admin_router.callback_query(F.data.startswith('dell-prod'), F.from_user.id.in_(ADMINS))
async def admin_process_start_dell(call: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(call.data.split('_')[-1])
    await TarrifDao.delete(session=session_with_commit, filters=ProductCategoryIDModel(id=product_id))
    await call.answer(f"🆗Тариф с ID {product_id} удален!", show_alert=True)
    await call.message.delete()
