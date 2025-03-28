import pandas as pd
import numpy as np

class NiftyDataProcessor:
    """Processes and merges market data with option chain data."""

    @staticmethod
    def transform_option_chain(df):
        """Converts option chain data into a structured DataFrame."""
        ni_data = []
        for i in range(len(df)):
            stp = df["strikePrice"][i]
            calloi = callcoi = putoi = putcoi = ctotalBellq = ptotalSellq = 0
            cstp = 0  # Default for underlyingValue

            if df["CE"][i] != 0:
                calloi = float(df["CE"][i].get("openInterest", 0))
                callcoi = float(df["CE"][i].get("changeinOpenInterest", 0))
                ctotalBellq = float(df["CE"][i].get("totalBuyQuantity", 0))
                ctotalSellq = float(df["CE"][i].get("totalSellQuantity", 0))
                cstp = float(df["CE"][i].get("underlyingValue", 0))

            if df["PE"][i] != 0:
                putoi = float(df["PE"][i].get("openInterest", 0))
                putcoi = float(df["PE"][i].get("changeinOpenInterest", 0))
                ptotalBellq = float(df["PE"][i].get("totalBuyQuantity", 0))
                ptotalSellq = float(df["PE"][i].get("totalSellQuantity", 0))

            opdata = {
                "CALL_OI": calloi, "CALL_CHNG_OI": callcoi,
                "CALL_BQ": ctotalBellq, "CALL_SA": ctotalSellq, "strikePrice": stp,
                "PUT_SA": ptotalSellq, "PUT_BQ": ptotalBellq, "PUT_CHNG_OI": putcoi, "PUT_OI": putoi, "current_stp": cstp
            }
            ni_data.append(opdata)

        return pd.DataFrame(ni_data)

    @staticmethod
    def process_nifty_options(df, option_df):
        """Processes NIFTY options data by merging it with market data."""

        df = df[df["underlying"] == "NIFTY"].sort_values(by=["strikePrice", "openInterest"], ascending=True)
        join_df = df.merge(option_df, on="strikePrice", how="left")

        common_cols = [
            "expiryDate", "optionType", "strikePrice", "lastPrice",
            "numberOfContractsTraded", "totalTurnover", "openInterest",
            "underlyingValue", "pChange", "current_stp"
        ]

        call_cols = ["CALL_OI", "CALL_CHNG_OI", "CALL_BQ", "CALL_SA"]
        put_cols = ["PUT_SA", "PUT_BQ", "PUT_CHNG_OI", "PUT_OI"]

        rename_mapping = {
            "CALL_OI": "oi", "CALL_CHNG_OI": "coi", "CALL_BQ": "buy_q", "CALL_SA": "sell_q",
            "PUT_OI": "oi", "PUT_CHNG_OI": "coi", "PUT_BQ": "buy_q", "PUT_SA": "sell_q"
        }

        for call_col, put_col in zip(call_cols, put_cols):
            join_df[rename_mapping[call_col]] = np.where(
                join_df["optionType"].str.lower() == "call", join_df[call_col], join_df[put_col]
            )
        final_cols = ["expiryDate", "optionType", "strikePrice", "lastPrice","underlyingValue","oi", "coi", "buy_q", "sell_q"]

        
        return join_df[final_cols]
