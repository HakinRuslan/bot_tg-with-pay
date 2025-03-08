import os
from dotenv import load_dotenv

load_dotenv()


adm = os.environ.get("ADMINS")
ADMINS = [int(admin_id) for admin_id in adm.split(',')]
TOKEN = os.environ.get("TOKEN")
url = os.getenv('url')
STRIPE_PUBLIC_KEY=os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET')
SITE_URL=os.getenv('SITE_URL')