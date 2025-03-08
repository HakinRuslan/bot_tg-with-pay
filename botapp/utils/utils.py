import asyncio
from aiogram.types import ContentType
from admin.kb import *
from conf import *
from datetime import datetime
import re
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from bot import bot
import time
import os
from aiogram.enums import ContentType, ChatMemberStatus


def generate_fake_telegram_id():
    return random.randint(100000000, 9999999999)

def how_much_ago(date):
    now = datetime.now()
    delta = now - date
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} секунд назад"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} минут назад" if minutes > 1 else "1 минута назад"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} часа назад" if hours > 1 else "1 час назад"
    elif seconds < 2592000:
        days = int(seconds // 86400)
        return f"{days} д назад" if days > 1 else "1 д назад"
    elif seconds < 31536000:
        months = int(seconds // 2592000)
        return f"{months} мес назад" if months > 1 else "1 мес назад"
    else:
        years = int(seconds // 31536000)


async def process_dell_text_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Ошибка: Не удалось найти идентификатор последнего сообщения для удаления.")
        await message.delete()

    except Exception as e:
        logger.error(f"Произошла ошибка при удалении сообщения: {str(e)}")

def validate_birth_date(date_text):
    try:
        # Проверяем формат ДД/ММ/ГГ
        datetime.strptime(date_text, '%d/%m/%y')
        return True
    except ValueError:
        return False

# Валидация места жительства
def validate_residence(residence_text):
    return len(residence_text.strip()) > 0  # Простая проверка на пустоту

# Валидация email
def validate_email(email_text):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email_text) is not None

# Валидация номера телефона
def validate_phone(phone_text):
    phone_regex = r'^\+?\d{1,3}?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
    return re.match(phone_regex, phone_text) is not None

# Валидация остальных текстовых полей
def validate_text(text):
    return len(text.strip()) > 0  # Простая проверка на пустоту

# Общая функция валидации
def validate_and_save(user_id, field, value, validation_func, message_chat_id, error_message):
    if validation_func(value):
        save_to_excel(user_id, field, value)
        return True
    else:
        bot.send_message(message_chat_id, f"<b>{error_message}</b>", parse_mode='html')
        return False



async def process_dell_text_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data.get('last_msg_id')

    try:
        if last_msg_id:
            await bot.delete_message(chat_id=message.from_user.id, message_id=last_msg_id)
        else:
            logger.warning("Ошибка: Не удалось найти идентификатор последнего сообщения для удаления.")
        await message.delete()

    except Exception as e:
        logger.error(f"Произошла ошибка при удалении сообщения: {str(e)}")

async def broadcast_message(users_data: list, text: str = None, photo_id: int = None, document_id: int = None,
                            video_id: int = None, audio_id: int = None, caption: str = None, content_type: str = None):
    good_send = 0
    bad_send = 0
    for user in users_data:
        try:
            chat_id = user.get('telegram_id')
            if content_type == ContentType.TEXT:
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=main_contact_kb(chat_id))
            elif content_type == ContentType.PHOTO:
                await bot.send_photo(chat_id=chat_id, photo=photo_id, caption=caption,
                                     reply_markup=main_contact_kb(chat_id))
            elif content_type == ContentType.DOCUMENT:
                await bot.send_document(chat_id=chat_id, document=document_id, caption=caption,
                                        reply_markup=main_contact_kb(chat_id))
            elif content_type == ContentType.VIDEO:
                await bot.send_video(chat_id=chat_id, video=video_id, caption=caption,
                                     reply_markup=main_contact_kb(chat_id))
            elif content_type == ContentType.AUDIO:
                await bot.send_audio(chat_id=chat_id, audio=audio_id, caption=caption,
                                     reply_markup=main_contact_kb(chat_id))
            good_send += 1
        except Exception as e:
            print(e)
            bad_send += 1
        finally:
            await asyncio.sleep(1)
    return good_send, bad_send