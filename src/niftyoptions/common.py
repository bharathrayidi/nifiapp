import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class BaseTab:
    def __init__(self, title, headings):
        self.title = title
        self.headings = headings
        self._original_data = []

        self.table = toga.Table(
            headings=headings,
            style=Pack(flex=1, width=1500, height=600),
            missing_value=""
        )

        self.table_scroll = toga.ScrollContainer(horizontal=True, vertical=True, style=Pack(flex=1))
        self.table_scroll.content = self.table

        self.content_box = toga.Box(
            children=[self.table_scroll],
            style=Pack(direction=COLUMN, flex=1)
        )

    def get_content(self):
        """Returns the tab content."""
        return self.content_box

    def update_data(self, data):
        """Updates table data."""
        self._original_data = [list(row) for _, row in data.iterrows()]
        self.table.data = self._original_data

    def clear_table(self):
        """Clears table data."""
        self._original_data = []
        self.table.data = []

    def apply_filters_and_sort(self):
        """Sort table by first column (default behavior). Override in child classes."""
        self.table.data = sorted(self._original_data, key=lambda x: x[0])
