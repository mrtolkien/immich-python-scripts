from textual.app import App
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, OptionList
from textual.widgets.option_list import Option, Separator

from immich_python_scripts.duplicates import DuplicatesHandler


class ImmichApp(App):
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "app.css"

    def __init__(self):
        super().__init__()
        self.duplicates_handler = None

    def compose(self):
        yield Header(show_clock=True, name="Immich")

        yield Container(
            OptionList(
                Option(
                    "Remove duplicates",
                    id="duplicates",
                ),
                Separator(),
                Option("Exit", id="exit"),
                id="menu",
            ),
            DataTable(cursor_type="row", show_cursor=True),
            id="content",
        )

        yield Footer()

    def on_mount(self):
        self.query_one("#menu").focus()
        self.title = "Immich Python Scripts"

    def on_option_list_option_selected(self, event):
        self.query_one("#menu").remove()

        if event.option.id == "duplicates":
            self.title = "Duplicates removal"
            self.sub_title = "The selected asset gets added to all albums"
            self.duplicates_handler = DuplicatesHandler()
            # TODO Loading state with async/await
            self.duplicates_handler.load_next(self.query_one(DataTable))

        elif event.option.id == "exit":
            self.exit()

    def on_data_table_row_selected(self, event):
        if self.duplicates_handler:
            self.duplicates_handler.handle_selection(event.row_key)
            self.duplicates_handler.load_next(self.query_one(DataTable))


def main():
    app = ImmichApp()
    app.run()
