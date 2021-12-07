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
