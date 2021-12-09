import gspread
# from gdata.spreadsheet.service import SpreadsheetsService
import ast


class GoogleSheetsAPI:
    def __init__(self, pkey):
        pkey = ast.literal_eval(pkey)
        self.api_client = gspread.service_account_from_dict(pkey)
        self.spreadsheet = None

    def create_spreadsheet_from_template(self, template_spreadsheet_id, new_name):
        new_worksheet = self.api_client.copy(template_spreadsheet_id, title=new_name, copy_permissions=True)
        # new_worksheet = self.api_client.open(new_name)
        self.spreadsheet = new_worksheet
        return new_worksheet

    # def publish_spreadsheet(self):

        # self.shared_transactions_sheet = spreadsheet.get_worksheet(0)  # orders


class Sheet:
    def __init__(self, sheet, sheet_name):
        self.sheet = sheet.worksheet(sheet_name)
        self.last_row = len(self.sheet.row_values(1))

    def add_value(self, row_num, col_num, value):
        self.sheet.update_cell(row_num, col_num, value)


