from table import GoogleSheetsAPI, Sheet, PayerSheet, TransactionSheet
from postgresql import Database
from helpers import Payment, PayerManager

from config import (
    TELEGRAM_BOT_TOKEN,
    ENV_IS_SERVER,
    PORT,
    DATABASE_URL,
    GOOGLE_BOT_PKEY,
    TEMPLATE_SPREADSHEET_ID
)

google_sheets_api = GoogleSheetsAPI(pkey=GOOGLE_BOT_PKEY)
# new_sheet = google_sheets_api.create_spreadsheet_from_template(
#     template_spreadsheet_id=TEMPLATE_SHEET_ID, new_name='NEW_TEST')

# payers = PayerSheet(new_sheet, 'payers')
# payers.add_payer('хуй', '008')
# TransactionSheet(new_sheet, 'Shared Expenses')