import os

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ENV_IS_SERVER = os.environ.get('ENV_IS_SERVER', False)
PORT = int(os.environ.get('PORT', '8443'))
DATABASE_URL = os.environ.get('DATABASE_URL')
