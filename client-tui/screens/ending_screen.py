import random
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.widgets import Label, Button

# Import the glitch effect
from widgets.effects import GlitchEffect
from widgets.matrixRain import MatrixRain

class EndingScreen(Screen):

    DEFAULT_CSS = """
    EndingScreen {
        align: center middle;
        background: $boost;
        opacity: 0.0;
    }
    
    #ending-box {
        background: $panel;
        align: center middle;
        content-align: center middle;
    }
    
    #ending-title {
        text-style: bold;
        color: $error;
        margin-bottom: 2;
    }
    
    #btn-exit {
        margin-top: 2;
    }
    MatrixRain {
    width: 100%;
    height: 100%;
    background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="ending-box"):
            yield MatrixRain()
            # yield Label("SYSTEM HALTED : CONTEST OVER", id="ending-title")
            # yield Label("Fetching final evaluation...", id="ending-stats")
            # yield Button("Exit Arena", id="btn-exit", variant="error")

    async def on_mount(self) -> None:
        self.styles.animate(
            attribute="opacity",
            value=1.0,
            duration=1.5,
            easing="out_cubic"
        )

        # Setup the background task for random glitches
        # self.set_interval(2.0, self.apply_random_glitch)
        #
        # try:
        #     profile = await self.app.api_client.get_my_profile()
        #     score = profile.get("score", 0)
        #     rank = profile.get("rank", "--")
        #     self.query_one("#ending-stats", Label).update(
        #         f"Final Score: {score} pts  |  Final Rank: #{rank}"
        #     )
        # except Exception:
        #     self.query_one("#ending-stats", Label).update("Connection lost. Final stats unavailable.")

    # def apply_random_glitch(self) -> None:
    #     # 25% chance to trigger a glitch every 2 seconds
    #     if random.random() < 0.25:
    #         box = self.query_one("#ending-box")
    #         # Keep the glitch duration short for a realistic electrical failure feel
    #         GlitchEffect(box, 0.4)

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     if event.button.id == "btn-exit":
    #         self.app.exit()
