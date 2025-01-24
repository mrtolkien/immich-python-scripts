from textual.app import App
from textual.containers import Container
from textual.widgets import Footer, OptionList
from textual.widgets.option_list import Option, Separator

import immich_python_scripts.duplicates


class ImmichApp(App):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self):
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
        )

        yield Footer()

    def on_option_list_option_selected(self, event):
        return self.exit(event.option.id)


def main():
    app = ImmichApp()

    result = app.run()

    if result == "duplicates":
        immich_python_scripts.duplicates.run()
