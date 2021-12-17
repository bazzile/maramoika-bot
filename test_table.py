from table import GoogleSheetsAPI, Transaction, GroupSpreadSheetManager
from postgresql import Database
from helpers import Payment, PayerManager

from config import (
    TELEGRAM_BOT_TOKEN,
    ENV_IS_SERVER,
    PORT,
    DATABASE_URL,
    GOOGLE_BOT_PKEY,
    TEMPLATE_SPREADSHEET_ID,
)

client = GoogleSheetsAPI(pkey=GOOGLE_BOT_PKEY)

sheet_manager = GroupSpreadSheetManager(
    client.open_spreadsheet_by_name('maramoika_test'))

# sheet_manager.payers.add_payer('vasily', '123456789')
# payer_id = sheet_manager.payers.add_payer('serg', 987654321)
payer_id = 987654321
payer = sheet_manager.payers.get_payer_by_id(payer_id)
payers = sheet_manager.payers.list_payers()
transaction = Transaction('apple', '120', payer, payers)
sheet_manager.transactions.add_transaction(transaction)
