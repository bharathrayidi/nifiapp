import toga
import asyncio
import pandas as pd
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .nifty_fetcher import NiftyDataFetcher
from .nifty_processor import NiftyDataProcessor
from .nifty_tab import NiftyTab
from .banknifty_tab import BankNiftyTab
from .other_stocks_tab import OtherStocksTab
from .option_chain_tab import OptionChainTab

class NiftyApp(toga.App):
    def __init__(self):
        super().__init__()
        self.refresh_task = None
        self.is_refreshing = False
        self.sidebar_expanded = True
        self.fetcher = NiftyDataFetcher()
        self.processor = NiftyDataProcessor()

    def startup(self):
        """Initialize the application."""
        self.nifty_tab = NiftyTab()
        self.banknifty_tab = BankNiftyTab()
        self.other_stocks_tab = OtherStocksTab()
        self.option_chain_tab = OptionChainTab()

        self.tabs = {
            "Nifty": self.nifty_tab,
            "BankNifty": self.banknifty_tab,
            "Other Stocks": self.other_stocks_tab,
            "Option Chain": self.option_chain_tab
        }

        self.main_window = toga.MainWindow(title="Nifty Tracker", size=(1200, 800))
        self.create_ui()
        self.main_window.show()
        self.start_auto_refresh()

    def create_ui(self):
        """Create a left sidebar with collapsible navigation and dynamic tab content."""
        self.sidebar = toga.Box(style=Pack(direction=COLUMN, width=60, padding=5))
        self.content_area = toga.Box(style=Pack(flex=1, padding=20))
        
        self.scroll_container = toga.ScrollContainer(content=self.content_area, style=Pack(flex=1))

        self.tab_buttons = []
        for tab_name in self.tabs:
            btn = toga.Button(
                text=tab_name,
                on_press=self.switch_tab,
                style=Pack(padding=5, width=140)
            )
            self.sidebar.add(btn)
            self.tab_buttons.append((btn, tab_name))

        self.toggle_button = toga.Button(
            "⬅ Collapse",
            on_press=self.toggle_sidebar,
            style=Pack(padding=5, width=140)
        )
        self.sidebar.add(self.toggle_button)

        self.refresh_button = toga.Button(
            "Refresh Now",
            on_press=self.on_refresh_press,
            style=Pack(padding=10, width=140, alignment="center")
        )
        self.sidebar.add(self.refresh_button)
        
        self.sidebar_container = toga.Box(style=Pack(direction=COLUMN, width=150))
        self.sidebar_container.add(self.sidebar)
        
        self.expand_button = toga.Button(
            "➡ Expand",
            on_press=self.toggle_sidebar,
            style=Pack(padding=5, width=30, visibility="hidden")
        )

        self.main_container = toga.Box(style=Pack(direction=ROW, flex=1))
        self.main_container.add(self.sidebar_container)
        self.main_container.add(self.expand_button)
        self.main_container.add(self.scroll_container)

        self.main_window.content = self.main_container
        self.switch_tab(None, "Nifty")

    def switch_tab(self, widget, tab_name=None):
        """Switch the content area to the selected tab."""
        if not tab_name:
            tab_name = widget.text
        
        self.content_area.clear()
        self.content_area.add(self.tabs[tab_name].get_content())
        
    def toggle_sidebar(self, widget):
        """Expand/Collapse the sidebar."""
        if self.sidebar_expanded:
            self.sidebar_container.style.width = 0
            self.toggle_button.style.visibility = "hidden"
            self.expand_button.style.visibility = "visible"
        else:
            self.sidebar_container.style.width = 150
            self.toggle_button.style.visibility = "visible"
            self.expand_button.style.visibility = "hidden"
        self.sidebar_expanded = not self.sidebar_expanded

    def start_auto_refresh(self):
        """Start auto-refreshing data."""
        if self.refresh_task:
            self.refresh_task.cancel()
        self.refresh_task = asyncio.create_task(self.auto_refresh())

    async def auto_refresh(self):
        """Refresh data every 10 seconds."""
        while True:
            try:
                if not self.is_refreshing:
                    await self.refresh_data()
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Refresh error: {e}")
                await asyncio.sleep(10)

    async def on_refresh_press(self, widget):
        """Handle manual refresh button press."""
        if self.is_refreshing:
            return

        self.is_refreshing = True
        self.refresh_button.enabled = False
        self.refresh_button.text = "Refreshing..."

        if self.refresh_task:
            self.refresh_task.cancel()

        await self.refresh_data()
        self.start_auto_refresh()

        self.is_refreshing = False
        self.refresh_button.text = "Refresh Now"
        self.refresh_button.enabled = True

    async def refresh_data(self):
        """Fetch and process data for all tabs."""
        try:
            for tab in self.tabs.values():
                tab.clear_table()

            df, ni_df = await asyncio.gather(
                asyncio.to_thread(self.fetcher.fetch_data),
                asyncio.to_thread(self.fetcher.fetch_nifty_options)
            )

            if df.empty or ni_df.empty:
                return

            option_df = await asyncio.to_thread(self.processor.transform_option_chain, ni_df)
            processed_df = await asyncio.to_thread(self.processor.process_nifty_options, df, option_df)

            self.nifty_tab.update_data(self.add_scoring(processed_df))
            self.banknifty_tab.update_data(self.add_scoring(df[df["underlying"] == "BANKNIFTY"]))
            self.other_stocks_tab.update_data(self.add_scoring(df[(df["underlying"] != "NIFTY") & (df["underlying"] != "BANKNIFTY")]))
            self.option_chain_tab.update_data(self.add_scoring(option_df))

        except Exception as e:
            await self.main_window.dialog(toga.ErrorDialog("Error", f"Failed to refresh data: {str(e)}"))

    def add_scoring(self, df):
        """Add a scoring column based on price and volume."""
        if "price" in df.columns and "volume" in df.columns:
            df["Score"] = (df["price"] * df["volume"]).rank(ascending=False)
        return df

def main():
    return NiftyApp()

if __name__ == "__main__":
    app = NiftyApp()
    app.main_loop()
