from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from db.models.ormmodels.models import *
from db.models.models.manager import *
from user.user import UserDAO
from .form import Pagination
from .schemas import *

async def get_paginated_kb(session: AsyncSession, page: int) -> InlineKeyboardMarkup:

    products = await UserDAO.find_all(session=session)
    builder = InlineKeyboardBuilder()
    start_offset = page * 5
    end_offset = start_offset + 5

    for product in products[start_offset:end_offset]:  
        builder.row(InlineKeyboardButton(text=product.username, callback_data=f"about-user_{product.telegram_id}"))

    buttons_row = []
    if page > 0:  
        buttons_row.append(  
            InlineKeyboardButton(  
                text="⬅️",  
                callback_data=Pagination(page=page - 1).pack(), 
            )  
        )  
    if end_offset < len(products):
        print(page)
        buttons_row.append(  
            InlineKeyboardButton(  
                text="➡️",  
                callback_data=Pagination(page=page + 1).pack()
            )  
        )
    builder.row(*buttons_row)

    return builder.as_markup()

def catalog_admin_kb(catalog_data: List[Typoftariffs]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=Typoftariffs.type_tarif_name, callback_data=f"add_category_{Typoftariffs.id}")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()


def admin_send_file_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Без файла", callback_data="without_file")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()

def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Статистика", callback_data="statistic")
    kb.button(text="🛍️ Управлять тарифами", callback_data="process_products")
    kb.button(text="🎁 Управлять типами тарифов", callback_data="process_category")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

async def admin_kb_user(user_id, session: AsyncSession) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    user = await UserDAO.find_one_or_none(session=session, filters=UserBaseInDB(telegram_id=user_id))
    if user.active:
        kb.button(text="⚙️ Ограничить", callback_data=f"ogr-user_{user_id}")
    else:
        kb.button(text="⚙️ Снять огранечения", callback_data=f"ogr-user_{user_id}")
    kb.button(text="⚙️ Назад", callback_data="users")
    kb.button(text="🏠 В админ панель", callback_data="admin_panel")
    kb.adjust(2)
    return kb.as_markup()


def stat_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Управлять пользователями", callback_data="users")
    kb.button(text="⚙️ Назад", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()



def admin_kb_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def dell_product_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Удалить", callback_data=f"dell-prod_{product_id}")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def dell_cat_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑️ Удалить", callback_data=f"dell-cat_{product_id}")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def product_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить товар", callback_data="add_product")
    kb.button(text="🗑️ Удалить товар", callback_data="delete_product")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def category_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ add category", callback_data="add_cat")
    kb.button(text="🗑️ del category", callback_data="delete_cat")
    kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
    return kb.as_markup()


def admin_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Все верно", callback_data="confirm_add")
    kb.button(text="Отмена", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()