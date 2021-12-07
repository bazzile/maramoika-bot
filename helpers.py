class PayerManager:
    def __init__(self, payers):
        self.payers = payers

    # def list_names(self):
    #     names = [payer['name'] for payer in self.payers]
    #     return names


class Payment:
    def __init__(self, item, price):
        self.item = item
        self.price = price
