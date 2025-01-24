from textual.app import App
from textual.containers import Container
from textual.widgets import DataTable, Footer, Header, OptionList
from textual.widgets.option_list import Option, Separator

import immich_python_scripts.duplicates


class ImmichApp(App):
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "app.css"

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
            self.sub_title = "The selected asset gets added to albums"
            immich_python_scripts.duplicates.run(self.query_one(DataTable))

        elif event.option.id == "exit":
            self.exit()

    def on_data_table_row_selected(self, event):
        print(event.row_key)
        self.exit()


def main():
    app = ImmichApp()
    app.run()
