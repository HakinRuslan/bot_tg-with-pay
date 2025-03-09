from typing import List
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from conf import *

def dasdads():
    pass

def buy_kb(product_id, price) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Купить", callback_data=f"buy_{product_id}_{price}")
    kb.adjust(2)
    return kb.as_markup()


def kb_extend() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Продлить", callback_data="extend")
    return kb.as_markup()

def kb_extend_or_other() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Продлить", callback_data="extend_this")
    kb.button(text="Другой", callback_data="tariffs")
    return kb.as_markup()

def kb_return() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Продолжить", callback_data="return")
    return kb.as_markup()

def kb_tarrif() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 Тарифы", callback_data="tariffs")
    return kb.as_markup()

def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Мои профиль", callback_data="my_profile")
    if user_id in ADMINS:
        kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()