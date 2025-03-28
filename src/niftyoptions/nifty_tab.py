from .common import BaseTab

class NiftyTab(BaseTab):
    def __init__(self):
        headings = [
            "Expiry Date", "Option Type", "Strike Price", 
            "Last Price", "Underlying Value", "OI", "COI", "Buy Q", "Sell Q"
        ]
        super().__init__("Nifty", headings)