from textual.app import App
from textual.theme import Theme
from screens.login_screen import LoginScreen
from screens.arena_screen import ArenaScreen
from screens.ending_screen import EndingScreen

from api_client import BabelAPIClient

class BabelArenaApp(App):
    """
    Main orchestrator application.
    Registers and manages navigation between different screens.
    """
    CSS_PATH = "./styles/global-style.css"

    THEME_BABEL = Theme(
            name="theme-babel",
            primary="#39ff14",
            secondary="#008f11",
            accent="#ccff00",
            foreground="#aaffaa",
            background="#050a05",
            surface="#0a140a",
            panel="#0a140a",
            success="#00ff00",
            error="#ff003c",
            warning="#bfff00",
            dark=True
            )
    
    SCREENS = {
        "login": LoginScreen,
        "arena": ArenaScreen,
        "ending": EndingScreen,
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = BabelAPIClient(base_url="http://127.0.0.1:8000/api")

    def on_mount(self) -> None:
        self.register_theme(self.THEME_BABEL)
        self.theme = "theme-babel"

        self.push_screen("login")
        # self.push_screen("arena")


if __name__ == "__main__":
    BabelArenaApp().run()
