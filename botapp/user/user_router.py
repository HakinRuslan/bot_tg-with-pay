from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from .user import UserDAO
from .kb import *
from .schemas import *
from admin.kb import *
from quiz.kbs import *
from db.models.models.manager import *

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=UserBaseInDB(telegram_id=user_id)
    )

    # users_active = await UserDAO.get_active_users(session=session_with_commit)
    # print(session_with_commit)
    # for i in users_active:
    #     if i == user_id:
    #         return await message.answer(
    #         f"👋 Привет, {message.from_user.full_name}! Выберите необходимое действие",
    #         reply_markup=main_user_kb(user_id)
    #         )
    #         return

    # await message.answer(f"🎉 <b>Приветствуем</b>. Теперь выберите необходимое действие.",
    #                      reply_markup=kb_return())
    if user_info:
        if user_info.active:
            return await message.answer(
                f"👋 Привет, {message.from_user.full_name}! Выберите необходимое действие",
                reply_markup=main_user_kb(user_id)
            )
        else:
            await message.answer(f"🎉 <b>Приветствуем</b>. Продлите ваш тариф, или купите новый.",
                         reply_markup=kb_extend())
    else:
        await message.answer(f"🎉 <b>Приветствуем</b>. Теперь выберите необходимое действие.",
                         reply_markup=kb_return())
    # values = User(
    #     telegram_id=user_id,
    #     username=message.from_user.username
    # )
    # await UserDAO.add(session=session_with_commit, values=values)
    # await message.answer(f"🎉 <b>Приветствуем</b>. Теперь выберите необходимое действие.",
    #                      reply_markup=kb_return())
    
@user_router.callback_query(F.data == "home")
async def page_home(call: CallbackQuery):
    await call.answer("Главная страница")
    return await call.message.answer(
        f"👋 Привет, {call.from_user.full_name}! Выберите необходимое действие",
        reply_markup=main_user_kb(call.from_user.id)
    )

@user_router.callback_query(F.data == "my_profile")
async def page_about(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Профиль")

    # Получаем статистику покупок пользователя
    purchases = await PurchaseDao.find_one_or_none(session=session_without_commit, filters=UserBaseInDB(telegram_id=call.from_user.id))
    # total_amount = purchases.get("total_amount", 0)
    # total_purchases = purchases.get("total_purchases", 0)

    # Формируем сообщение в зависимости от наличия покупок
    # if total_purchases == 0:
    #     await call.message.answer(
    #         text="🔍 <b>У вас пока нет купленных тарифов.</b>\n\n"
    #              "Откройте тарифы и выберите.",
    #         reply_markup=main_user_kb(call.from_user.id)
    text = (
        f"🛍 <b>Ваш профиль:</b>\n\n"
        f"Купленный тариф: <b>{purchases.tarrif}</b>\n"
        "Желаете посмотреть детали купленного вами тарифа?"
    )
    await call.message.answer(
        text=text,
        reply_markup=purchases_kb()
    )

@user_router.callback_query(F.data == "purchases")
async def page_user_purchases(call: CallbackQuery, session_without_commit: AsyncSession):
    await call.answer("Мой тариф")

    # Получаем список покупок пользователя
    purchases = await UserDAO.get_purchased_products(session=session_without_commit, telegram_id=call.from_user.id)

    if not purchases:
        await call.message.edit_text(
            text=f"🔍 <b>Вы пока не приобрели тариф.</b>\n\n"
                 f"Откройте тарифы, и выберите.",
            reply_markup=main_user_kb(call.from_user.id)
        )
        return

    # Для каждой покупки отправляем информацию
    for purchase in purchases:
        product = purchase.product

        product_text = (
            f"🛒 <b>Информация о вашем Тарифе:</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔹 <b>Название:</b> <i>{product.name}</i>\n"
            f"🔹 <b>Описание:</b>\n<i>{product.description}</i>\n"
            f"🔹 <b>Цена:</b> <b>{product.price} ₽</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
        )
        await call.message.answer(
            text=product_text,
        )

    await call.message.answer(
        text="🙏 Спасибо за доверие!",
        reply_markup=main_user_kb(call.from_user.id)
    )

@user_router.callback_query(F.data == "about")
async def page_about(call: CallbackQuery):
    await call.answer("О магазине")
    await call.message.answer(
        text=(
            # "🎓 Добро пожаловать в наш учебный магазин!\n\n"
            # "🚀 Этот бот создан как демонстрационный проект для статьи на Хабре.\n\n"
            # "👨‍💻 Автор: Яковенко Алексей\n\n"
            # "🛍️ Здесь вы можете изучить принципы работы телеграм-магазина, "
            # "ознакомиться с функциональностью и механизмами взаимодействия с пользователем.\n\n"
            # "📚 Этот проект - это отличный способ погрузиться в мир разработки ботов "
            # "и электронной коммерции в Telegram.\n\n"
            # "💡 Исследуйте, учитесь и вдохновляйтесь!\n\n"
            # "Данные для тестовой оплаты:\n\n"
            # "Карта: 1111 1111 1111 1026\n"
            # "Годен до: 12/26\n"
            # "CVC-код: 000\n"
            "dev withoutopps"
        ),
        reply_markup=call.message.reply_markup
    )