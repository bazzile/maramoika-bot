import logging
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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = GoogleSheetsAPI(pkey=GOOGLE_BOT_PKEY)

sheet_manager = GroupSpreadSheetManager(
    # client.open_spreadsheet_by_name('maramoika_test'))
    client.open_spreadsheet_by_name('Maramoika test-773559972'))

payer_1 = Payer('vasily', 123456789)
payer_2 = Payer('serg', 987654321)
payer_3 = Payer('ira', 444454321)
# sheet_manager.payers.add_payer(payer_1)
# sheet_manager.payers.add_payer(payer_2)
# sheet_manager.payers.add_payer(payer_3)

payees = sheet_manager.payers.list_payers()
for payer in payees:
    logger.info(vars(payer))
# payer = sheet_manager.payers.get_payer_by_id(payer_1.id)
# payer = payer_1
# transaction = Transaction('apple', '200', payer, payees)
# sheet_manager.transactions.add_transaction(transaction)
