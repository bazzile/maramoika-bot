import os

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ENV_IS_SERVER = os.environ.get('ENV_IS_SERVER', False)
PORT = int(os.environ.get('PORT', '8443'))
DATABASE_URL = os.environ.get('DATABASE_URL')
GOOGLE_BOT_PKEY = os.environ.get('GOOGLE_BOT_PKEY')

TEMPLATE_SPREADSHEET_ID = '1YND1gAfQnyH7MeG-yLtq6KQSgIyUWMLbFnrScmAAA-8'
TRANSACTION_SHEET_NAME = 'траты'
PARTICIPANT_SHEET_NAME = 'участники'
