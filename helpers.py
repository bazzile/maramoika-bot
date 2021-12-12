class PayerManager:
    def __init__(self, payers):
        self.payers = payers
        self.set_payers_selected()

    def set_payers_selected(self):
        for payer in self.payers:
            payer['is_selected'] = True

    def toggle_payee(self, payee_id):
        for payee in self.payers:
            if payee['id'] == int(payee_id):
                payee['is_selected'] = not payee['is_selected']
                break

    def get_selected_payee_ids(self):
        return [payee['id'] for payee in self.payers if payee['is_selected']]
    # def list_names(self):
    #     names = [payer['name'] for payer in self.payers]
    #     return names


class Payment:
    def __init__(self, item, price):
        self.item = item
        self.price = price


# class User:
#     def __init__(self, user_name, user_id):
#         self.user_name = user_name
#         self.user_id = user_id
#
#     def is_in_group(self, group_id):

# ====================================


class Group:
    def __init__(self, group_id, group_name):
        self.group_id = str(group_id)
        self.group_name = group_name
        self.group_spreadsheet_name = self.group_id + self.group_name

    def validate_group(self, sheets_api_client):
        if not sheets_api_client.group_spreadsheet_exists(self.group_id):
            return
            # sheets_api_client.create_spreadsheet_from_template(
            #     template_spreadsheet_id=TEMPLATE_SPREADSHEET_ID, new_name=self.group_spreadsheet_name)
