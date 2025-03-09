# from flask import Flask, request, jsonify
# import stripe
# from config import *
# from botapp.bot import *
# from botapp.quiz.kbs import *
# from loguru import logging
# from botapp.db.models.models.manager import *
# from botapp.db.database.database import get_async_session


# app = Flask(__name__)
# stripe.api_key = STRIPE_SECRET_KEY

# async def send_telegram_message_save_data(user_id, text, checkout_session):
#     async with get_async_session() as session:
#         payment_data = {
#             'user_id': checkout_session.payment_intent['metadata'].get('user_id'),
#             'payment_id': checkout_session.payment_intent,
#             'price': checkout_session.amount_total,
#             "active": True,
#             'tariff_id': checkout_session.payment_intent['metadata'].get('tariff_id')
#             }
#         await PurchaseDao.add(session=session_with_commit, values=PaymentData(**payment_data))


#     await bot.send_message(user_id, text)

# def send_message_sync(user_id, text):
#     asyncio.run(send_telegram_message(user_id, text))

# # Эндпоинт для успешной оплаты
# @app.route('/success', methods=['GET'])
# def success():
#     # Получаем session_id из query-параметров
#     session_id = request.args.get('session_id')

#     if not session_id:
#         return "Ошибка: session_id не указан.", 400

#     try:
#         checkout_session = stripe.checkout.Session.retrieve(session_id)


#         payment_intent_id = checkout_session.payment_intent
#         customer_email = checkout_session.customer_details.email
#         amount_total = checkout_session.amount_total / 100

#         # Отображаем страницу с благодарностью
#         return render_template('success.html',  # Шаблон страницы
#                                payment_intent_id=payment_intent_id,
#                                customer_email=customer_email,
#                                amount_total=amount_total)

#     except stripe.error.StripeError as e:
#         # Обработка ошибок Stripe
#         return f"Ошибка Stripe: {str(e)}", 500



# # Эндпоинт для вебхука
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     event = None
#     payload = request.data
#     sig_header = request.headers['STRIPE_SIGNATURE']

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, STRIPE_WEBHOOK_SECRET
#         )

#     except ValueError as e:
#         # Invalid payload
#         logging.error("Error")
#         raise e

#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         logging.error("Error")
#         raise e

#     logging.info("EVENT",str(event))

#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']
#         chat_id = payment_intent['metadata'].get('tg_chat_id')
#         logging.info(f"Оплата прошла user_id: {chat_id}")
#         if chat_id:
#             bot.send_message(chat_id, "Оплата прошла успешно! Спасибо за покупку.")

#     return jsonify(success=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=4242)

from fastapi import FastAPI, Request, HTTPException, Depends
from contextlib import asynccontextmanager
import stripe
from config import *
from aiogram import Bot
from loguru import logger
from db.models.models.manager import *
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PaymentData
from db import get_async_session
from models import *

@asynccontextmanager
async def lifespan():
    url_webhook = f"{SITE_URL}/webhook"
    await bot.set_webhook(url=url_webhook,
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    yield

app = FastAPI(lifespan=lifespan)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

stripe.api_key = STRIPE_SECRET_KEY

templates = Jinja2Templates(directory="temps")

# async def send_telegram_message(user_id, text):
#     await bot.send_message(user_id, text)

@app.get("/success", response_class=HTMLResponse)
async def success(session_id: str, request: Request, session: AsyncSession = Depends(get_async_session)):
    if not session_id:
        raise HTTPException(status_code=400, detail="Ошибка: session_id не указан.")

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = checkout_session.payment_intent
        customer_email = checkout_session.customer_details.email
        amount_total = checkout_session.amount_total / 100
        username = checkout_session.metadata.get('username')
        user_id = checkout_session.metadata.get('user_id')
        tariff_id = checkout_session.metadata.get('tariff_id')
        tarrif = checkout_session.metadata.get('tariff')
        expires = checkout_session.metadata.get('expires')

        payment_data = {
            'user_id': user_id,
            'payment_id': payment_intent_id,
            'price': amount_total,
            'expires': datetime.strptime(expires, '%d/%m/%y'),
            'active': True,
            'tariff_id': tariff_id
        }
        await PurchaseDao.add(session=session, values=PaymentData(**payment_data))
        await session.commit()

        for admin_id in ADMINS:
            try:
                user_info = f"@{username} ({user_id})" if username else f"c ID {user_id}"

                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f"💲 Пользователь c {user_info} купил тариф <b>{tarrif}</b> (ID: {tariff_id}) "
                        f"за <b>{amount_total} $</b>."
                    )
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке уведомления администраторам: {e}")

        return templates.TemplateResponse("success.html", {
            "request": request,
            "payment_intent_id": payment_intent_id,
            "customer_email": customer_email,
            "amount_total": amount_total
        })

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка Stripe: {str(e)}")

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('STRIPE_SIGNATURE')

    if not sig_header:
        logging.error("Missing Stripe signature header")
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        logging.error("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logging.error("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    logging.info(f"EVENT: {str(event)}")

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        chat_id = payment_intent['metadata'].get('tg_chat_id')
        logging.info(f"Оплата прошла user_id: {chat_id}")
        if chat_id:
            await bot.send_message(chat_id, "Оплата прошла успешно! Мы пришлем вам уведомление о том что срок вашего тарифа закончился. Спасибо за покупку.")

    return {"success": True}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4242)