import os
from dotenv import load_dotenv

load_dotenv()

STRIPE_PUBLIC_KEY=os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET')
SITE_URL=os.getenv('SITE_URL')