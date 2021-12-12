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
    # def create_new_sheet_if_not_exist(self, title):
    #     if title not in [sh.title for sh in gc.openall()]:
    #         gc.create(title)
    #     print([sh.title for sh in gc.openall()])

    # def publish_spreadsheet(self):

    # self.shared_transactions_sheet = spreadsheet.get_worksheet(0)  # orders


class GroupSpreadSheetManager:
    def __init__(self, spreadsheet):
        self.payers = PayerSheet(spreadsheet, PARTICIPANT_SHEET_NAME)
        self.transactions = PayerSheet(spreadsheet, TRANSACTION_SHEET_NAME)


class Sheet:
    def __init__(self, sheet, sheet_name):
        self.sheet = sheet.worksheet(sheet_name)


class PayerSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)
        # self.payers = []

    def list_payers(self):
        return self.sheet.get_all_records()

    def get_payer_by_id(self, payer_id):
        payers = self.list_payers()
        selected_payers = [payer for payer in payers if payer['telegram_id'] == payer_id]
        if selected_payers:
            return selected_payers[0]

    def payer_exists(self, payer_id):
        payer = self.get_payer_by_id(payer_id)
        if payer:
            return True

    def add_payer(self, name, telegram_id):
        self.sheet.append_row([name, telegram_id])
        logger.info(f'Successfully inserted user {name} ({telegram_id})')
        # self.payers.append(telegram_id)
        # self.add_value(row_num=self.last_row, col_num=1, value=name)
        # self.add_value(row_num=self.last_row, col_num=2, value=telegram_id)


class Transaction:
    def __init__(self, item, price, payer, payees):
        self.item = item
        self.price = price
        self.payer = payer
        self.payees = payees
        self.is_valid = self.check_validity()
        self.set_all_payees_selected()

    def check_validity(self):
        if re.match(r'^\d+([.,]\d{0,2}?)?$', self.price) and re.match(r'^\D{2,}$', self.item):
            return True

    def set_all_payees_selected(self):
        for payer in self.payees:
            payer['is_selected'] = True

    def toggle_payee(self, payee_id):
        for payee in self.payees:
            if payee['telegram_id'] == int(payee_id):
                payee['is_selected'] = not payee['is_selected']
                break


class TransactionSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)

    def add_transaction(self, transaction):
        payee_mark_list = ['X' if payee['isSelected'] else '' for payee in transaction.payees]
        self.sheet.append_row(
            values=[transaction.item, '', transaction.price, '', transaction.payer, payee_mark_list],
            table_range='B4')
        # self.sheet.append_row(values=['cake1', '', 1123, '', 'user2'], table_range='B4')
        # logger.info(self.sheet.get_all_records(head=3))
