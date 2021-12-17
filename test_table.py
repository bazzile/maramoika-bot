from table import GoogleSheetsAPI, Transaction, GroupSpreadSheetManager, Payer
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

payer_1 = Payer('vasily', 123456789)
payer_2 = Payer('serg', 987654321)
payer_3 = Payer('ira', 444454321)
# sheet_manager.payers.add_payer(payer_1)
# sheet_manager.payers.add_payer(payer_2)
# sheet_manager.payers.add_payer(payer_3)

payers = sheet_manager.payers.list_payers()
# payer = sheet_manager.payers.get_payer_by_id(payer_1.id)
payer = payer_1
transaction = Transaction('apple', '200', payer, payers)
sheet_manager.transactions.add_transaction(transaction)
