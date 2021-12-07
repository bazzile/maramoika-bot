class PayerManager:
    def __init__(self, payers):
        self.payers = payers
        self.set_payers_selected()

    def set_payers_selected(self):
        for payer in self.payers:
            payer['is_selected'] = True
    # def list_names(self):
    #     names = [payer['name'] for payer in self.payers]
    #     return names


class Payment:
    def __init__(self, item, price):
        self.item = item
        self.price = price
