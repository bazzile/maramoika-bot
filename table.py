import logging
import gspread
import re
# from gdata.spreadsheet.service import SpreadsheetsService
import ast

from config import TRANSACTION_SHEET_NAME, PARTICIPANT_SHEET_NAME

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsAPI:
    def __init__(self, pkey):
        pkey = ast.literal_eval(pkey)
        self.api_client = gspread.service_account_from_dict(pkey)
        self.spreadsheet = None

        # logger.info(self.api_client.list_spreadsheet_files())

    def create_spreadsheet_from_template(self, template_spreadsheet_id, new_name):
        # ToDo https://www.programcreek.com/python/?code=wncc%2Finstiapp-api%2Finstiapp-api-master%2Fmessmenu%2Fmanagement%2Fcommands%2Fmess_chore.py
        # authorize both gspread and google api to duplicate with the same creds
        new_worksheet = self.api_client.copy(template_spreadsheet_id, title=new_name, copy_permissions=True)
        # new_worksheet = self.api_client.open(new_name)
        self.spreadsheet = new_worksheet
        return new_worksheet

    def group_spreadsheet_exists(self, group_id):
        existing_sheet_names = self.list_existing_spreadsheet_names()
        for name in existing_sheet_names:
            if name.endswith(group_id):
                return True

    def list_existing_spreadsheet_names(self):
        existing_spreadsheets = self.api_client.list_spreadsheet_files()
        return [spreadsheet['name'] for spreadsheet in existing_spreadsheets]

    def open_spreadsheet_by_name(self, name):
        return self.api_client.open(name)


class GroupSpreadSheetManager:
    def __init__(self, spreadsheet):
        self.payers = PayerSheet(spreadsheet, PARTICIPANT_SHEET_NAME)
        self.transactions = TransactionSheet(spreadsheet, TRANSACTION_SHEET_NAME)


class Sheet:
    def __init__(self, sheet, sheet_name):
        self.sheet = sheet.worksheet(sheet_name)


class Payer:
    def __init__(self, name, telegram_id):
        self.name = name
        self.id = telegram_id
        self.is_selected = True

    def toggle_payee_status(self):
        self.is_selected = not self.is_selected

    def __eq__(self, other):
        if not isinstance(other, Payer):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id


class PayerSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)
        # self.payers = []

    def list_payers(self):
        logger.info(self.sheet.get_all_records())
        payer_list = [Payer(record['name'], record['telegram_id']) for record in self.sheet.get_all_records()]
        return payer_list

    def get_payer_by_id(self, payer_id):
        payers = self.list_payers()
        payer = [payer for payer in payers if payer.id == payer_id]
        if payer:
            return payer

    def payer_exists(self, payer):
        payer = self.get_payer_by_id(payer.id)
        if payer:
            return True

    def add_payer(self, payer):
        if self.payer_exists(payer):
            raise Exception('payer already exists')
        self.sheet.append_row([payer.name, payer.id])
        logger.info(f'Successfully inserted user {payer.name} ({payer.id})')
        return payer


class Transaction:
    def __init__(self, item, price, payer, payees):
        self.item = item
        self.price = price
        self.payer = payer
        self.payees = payees
        self.is_valid = self.check_validity()
        # self.set_all_payees_selected()

    def check_validity(self):
        if re.match(r'^\d+([.,]\d{0,2}?)?$', self.price) and re.match(r'^\D{2,}$', self.item):
            return True


class TransactionSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)

    def add_transaction(self, transaction):
        payee_mark_list = ['X' if payee.is_selected else '' for payee in transaction.payees]
        self.sheet.append_row(
            values=[transaction.item, '', float(transaction.price), '', transaction.payer.name, '', '', *payee_mark_list],
            table_range='C4')

