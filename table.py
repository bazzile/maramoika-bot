import logging
import gspread
# from gdata.spreadsheet.service import SpreadsheetsService
import ast

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsAPI:
    def __init__(self, pkey):
        pkey = ast.literal_eval(pkey)
        self.api_client = gspread.service_account_from_dict(pkey)
        self.spreadsheet = None

    def create_spreadsheet_from_template(self, template_spreadsheet_id, new_name):
        # ToDo https://www.programcreek.com/python/?code=wncc%2Finstiapp-api%2Finstiapp-api-master%2Fmessmenu%2Fmanagement%2Fcommands%2Fmess_chore.py
        # authorize both gspread and google api to duplicate with the same creds
        new_worksheet = self.api_client.copy(template_spreadsheet_id, title=new_name, copy_permissions=True)
        # new_worksheet = self.api_client.open(new_name)
        self.spreadsheet = new_worksheet
        return new_worksheet

    # def publish_spreadsheet(self):

        # self.shared_transactions_sheet = spreadsheet.get_worksheet(0)  # orders


class Sheet:
    def __init__(self, sheet, sheet_name):
        self.sheet = sheet.worksheet(sheet_name)
        # self.last_row = len(self.sheet.row_values(1))

    # def add_value(self, row_num, col_num, value):
    #     self.sheet.update_cell(row_num, col_num, value)


class PayerSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)
        # self.payers = []

    def list_payers(self):
        return self.sheet.get_all_records()

    def get_payer_by_id(self, payer_id):
        payers = self.list_payers()
        selected_payer = [payer for payer in payers if payer['telegram_id'] == payer_id][0]
        return selected_payer

    # def payer_exists(self, payer_id):
    #     payers = self.list_payers()
    #     if payer_id in [payer['telegram_id'] for payer in payers]:
    #         return True

    def add_payer(self, name, telegram_id):
        self.sheet.append_row([name, telegram_id])
        # self.payers.append(telegram_id)
        # self.add_value(row_num=self.last_row, col_num=1, value=name)
        # self.add_value(row_num=self.last_row, col_num=2, value=telegram_id)


class TransactionSheet(Sheet):
    def __init__(self, sheet, sheet_name):
        super().__init__(sheet, sheet_name)

        self.sheet.append_row(values=['cake', '', 123, '', 'user'], table_range='B4')
        self.sheet.append_row(values=['cake1', '', 1123, '', 'user2'], table_range='B4')
        # logger.info(self.sheet.get_all_records(head=3))

