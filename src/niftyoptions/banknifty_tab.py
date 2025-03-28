from .common import BaseTab

class BankNiftyTab(BaseTab):
    def __init__(self):
        headings = [
            "Underlying", "Expiry Date", "Option Type", 
            "Strike Price", "Last Price", "Open Interest", 
            "Underlying Value", "PChange"
        ]
        super().__init__("BankNifty", headings)