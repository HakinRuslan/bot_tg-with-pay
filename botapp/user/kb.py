from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from config import *
from db.models.ormmodels.models import *

def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Мои профиль", callback_data="my_profile")
    # kb.button(text="ℹ️ О нас", callback_data="about")
    if user_id in ADMINS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()


def catalog_kb(catalog_data: List[Typoftariffs]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for category in catalog_data:
        kb.button(text=Typoftariffs.type_tarif_name, callback_data=f"category_{Typoftariffs.id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()

def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Купленный тарифы", callback_data="purchases")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Купленный тарифы", callback_data="purchases")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()

def tariffs_kb(product_id, price) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Купить", callback_data=f"buy_{product_id}_{price}")
    kb.adjust(2)
    return kb.as_markup()



def product_kb(product_id, price) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Купить", callback_data=f"buy_{product_id}_{price}")
    kb.button(text="🛍 Назад", callback_data="catalog")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(2)
    return kb.as_markup()


def get_product_buy_kb(price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='Отменить', callback_data='home')]
    ])