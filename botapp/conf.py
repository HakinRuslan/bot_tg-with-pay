import os
from dotenv import load_dotenv

load_dotenv()

# BOT_TOKEN = os.getenv('BOT_TOKEN')
# PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
# PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
STRIPE_PUBLIC_KEY=os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET')
SITE_URL=os.getenv('SITE_URL')
adm = os.environ.get("ADMINS")
ADMINS = [int(admin_id) for admin_id in adm.split(',')]
url = os.environ.get("url")
TOKEN = os.environ.get("TOKEN")