from textual.app import App, ComposeResult
from textual.widgets import TextArea
from textual.containers import Vertical

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import TextArea
from textual.containers import Vertical

class ArenaTextArea(TextArea):
    BINDINGS = [
        Binding("ctrl+a", "select_all", "Select All", show=False),
        Binding("ctrl+shift+z", "redo", "Redo", show=False),
    ]


class CodeEditor(Vertical):
    def compose(self) -> ComposeResult:
        default_code = "def solve_arena_challenge(data: list[int]) -> int:\n    pass\n"
        
        editor = ArenaTextArea(
            text=default_code,
            language="python",
            theme="dracula",
            show_line_numbers=True,
            tab_behavior="indent",
            id="main-editor"
        )
        
        editor.indent_width = 4
        
        yield editor

class DemoEditorApp(App):
    """
    Main application to demonstrate the TextArea configuration.
    """
    CSS = """
    #editor-container {
        width: 100%;
        height: 100%;
        padding: 1;
        background: $surface-darken-1;
    }

    CodeEditor {
        width: 1fr;
        height: 1fr;
        border: solid $accent;
    }
    
    #main-editor {
        width: 100%;
        height: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="editor-container"):
            yield CodeEditor()

    def on_mount(self) -> None:
        editor = self.query_one("#main-editor", TextArea)
        editor.focus()

if __name__ == "__main__":
    DemoEditorApp().run()
