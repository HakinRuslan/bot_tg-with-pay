# from flask import Flask, request, jsonify
# import stripe
# from config import *
# from aiogram import Bot
# import logging

# logging.basicConfig(level=logging.INFO)

# app = Flask(__name__)

# # Ваш секретный ключ Stripe
# #STRIPE_SECRET_KEY = 'YOUR_STRIPE_SECRET_KEY'
# stripe.api_key = STRIPE_SECRET_KEY



# # Инициализация бота
# # BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
# bot = Bot(token=BOT_TOKEN)


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

#     # # Обработка события
#     # if event['type'] == 'payment_intent.succeeded':
#     #     payment_intent = event['data']['object']
#     #     # Логика обработки успешной оплаты
#     #     print(f"Payment succeeded: {payment_intent['id']}")

#     logging.info("EVENT",str(event))
#     #
#     # В обработчике вебхука
#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']

#         user_id = payment_intent['metadata'].get('user_id')  # Сохраняйте user_id в метаданных
#         logging.info(f"Оплата прошла user_id {user_id}")
#         if user_id:
#              bot.send_message(user_id, "Оплата прошла успешно! Спасибо за покупку.")

#     return jsonify(success=True)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=4242)