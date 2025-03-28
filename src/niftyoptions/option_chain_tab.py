from .common import BaseTab

class OptionChainTab(BaseTab):
    def __init__(self):
        headings = [
            "CALL_OI", "CALL_CHNG_OI", "CALL_BQ", "CALL_SA",
            "Current Price", "STP",
            "PUT_SA", "PUT_BQ", "PUT_CHNG_OI", "PUT_OI"
        ]
        super().__init__("Nifty Option Chain", headings)
        self.current_price = 0

    def update_data(self, option_df):
        """Update the table with new option chain data"""
        if option_df.empty:
            self.clear_table()
            return
            
        # Get current strike price
        self.current_price = int(option_df['current_stp'].iloc[0])
        
        # Filter for strikes around current price
        range_price = list(range(
            round(self.current_price/100)*100-250, 
            round(self.current_price/100)*100+250, 
            50
        ))
        filtered_df = option_df[option_df['strikePrice'].isin(range_price)]
        
        # Sort by strike price
        filtered_df = filtered_df.sort_values('strikePrice')
        
        # Convert to table data format expected by BaseTab
        self._original_data = []
        for _, row in filtered_df.iterrows():
            self._original_data.append([
                str(row['CALL_OI']),
                str(row['CALL_CHNG_OI']),
                str(row['CALL_BQ']),
                str(row['CALL_SA']),
                str(self.current_price),
                str(row['strikePrice']),
                str(row['PUT_SA']),
                str(row['PUT_BQ']),
                str(row['PUT_CHNG_OI']),
                str(row['PUT_OI']),
            ])
        
        # Apply sorting and filtering
        self.apply_filters_and_sort()

    def apply_filters_and_sort(self):
        """Sorts table data by Strike Price (STP) in ascending order"""
        self.table.data = sorted(self._original_data, key=lambda x: float(x[5]))
