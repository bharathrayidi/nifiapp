import requests
import pandas as pd
import time

class NiftyDataFetcher:
    def __init__(self):
        """Initialize the NiftyDataFetcher with required URLs, headers, and session cookies."""
        self.ni_origin_url = "https://www.nseindia.com/option-chain"
        self.origin_url = "https://www.nseindia.com/market-data/most-active-contracts"
        self.api_url = "https://www.nseindia.com/api/snapshot-derivatives-equity?index=contracts&limit=20"
        self.ni_url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
        }

        self.session = requests.Session()
        self.cookies = self.session.get(self.origin_url, headers=self.headers).cookies  # Store cookies
        self.ni_cookies = self.session.get(self.ni_origin_url, headers=self.headers).cookies  # Store cookies

    def fetch_data(self):
        """Fetches data from NSE API and returns a DataFrame."""
        try:
            time.sleep(1)  # Prevent rate-limiting
            response = self.session.get(self.api_url, headers=self.headers, cookies=self.cookies)
            data = response.json().get("value", {}).get("data", [])
            df = pd.DataFrame(data)

            if df.empty:
                print("⚠️ Warning: No data received from NSE API.")
                return pd.DataFrame()

            df.drop(columns=["identifier", "instrumentType", "instrument", "premiumTurnover"], inplace=True)
            return df

        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return pd.DataFrame()

    def fetch_nifty_options(self):
        """Fetches NIFTY option chain data and returns a DataFrame."""
        try:
            time.sleep(1)  # Prevent rate-limiting
            response = self.session.get(self.ni_url, headers=self.headers, cookies=self.ni_cookies)
            ni_data = response.json().get("filtered", {}).get("data", [])

            if not ni_data:
                print("⚠️ Warning: No NIFTY option chain data received.")
                return pd.DataFrame()

            return pd.DataFrame(ni_data).fillna(0)

        except Exception as e:
            print(f"❌ Error fetching NIFTY option chain data: {e}")
            return pd.DataFrame()
