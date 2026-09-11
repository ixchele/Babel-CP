from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static
from textual.containers import Vertical, Horizontal
from rich.text import Text

class ArenaLeaderboard(Vertical):
    """
    Displays the live ranking with styled headers and cells using Rich.
    """
    def compose(self) -> ComposeResult:
        yield DataTable(id="leaderboard-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = False

        table.add_columns(
                Text("Rank", style="bold #ccff00"),
                Text("User", style="bold #ccff00"),
                Text("Score", style="bold #ccff00"),
                Text("Time", style="bold #ccff00")
                )

        self._load_dummy_data()

    def _load_dummy_data(self) -> None:
        table = self.query_one(DataTable)

        row_first = (
                Text("1 👑", style="bold gold1"), 
                Text("ixchele", style="bold white"), 
                Text("1050", style="bold #39ff14"), 
                Text("12:04", style="dim")
                )
        row_second = (
                Text("2", style="silver"), 
                Text("neo"), 
                Text("980", style="#00ff00"), 
                Text("14:22", style="dim")
                )
        row_third = (
                Text("3", style="dark_orange"), 
                Text("trinity"), 
                Text("890", style="#00ff00"), 
                Text("15:10", style="dim")
                )

        table.add_rows([row_first, row_second, row_third])


class DemoApp(App):
    """
    Main application to demonstrate placement of the leaderboard.
    """
    CSS = """
    #main-container {
            width: 100%;
            height: 100%;
            }

    #code-editor-placeholder {
            width: 2fr;
            height: 100%;
            background: $surface;
            content-align: center middle;
            }

    ArenaLeaderboard {
            width: 1fr;
            height: 100%;
            border-left: solid $accent;
            background: $panel;
            }

    #leaderboard-table {
            height: 100%;
            border: none;
            }

    DataTable > .datatable--header {
            text-style: bold;
            background: $secondary;
            color: $background;
            }

    DataTable > .datatable--cursor {
            background: $primary 20%;
            color: $foreground;
            text-style: bold;
            }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            yield Static("CODE EDITOR ZONE\n(Width: 2fr)", id="code-editor-placeholder")
            yield ArenaLeaderboard()


if __name__ == "__main__":
    DemoApp().run()
