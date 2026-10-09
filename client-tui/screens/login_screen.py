from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Button, Static, LoadingIndicator
from textual.css.scalar import ScalarOffset

from textual.screen import Screen

from widgets.terminalTyperLabel import TerminalTyperLabel
from widgets.cypherLabel import MultiColorCypherLabel
from widgets.matrixRain import MatrixRain
from widgets.effects import GlitchEffect

import asyncio

ASCII_ART = """
▄▄▄     ▄▄▄▄    ▄▄▄▄    ▄▄▄▄
▀ █        █       █    ▀  █
  █     ▀▀▀█    ▀▀▀█       █
 ▄█▄    ▄▄▄█    ▄▄▄█       █

"""

class LoginScreen(Screen):
    CSS_PATH = "../styles/login-screen.css"

    ID_LOGIN_DIALOG = "login-dialog"
    ID_BRAND_PANEL = "brand-panel"
    ID_FORM_PANEL = "form-panel"
    ID_APP_LOGO = "app-logo"
    ID_APP_TITLE = "app-title"
    ID_USERNAME_INPUT = "username-input"
    ID_TOKEN_INPUT = "token-input"
    ID_LOGIN_BTN = "login-button"
    ID_LOADING_PANEL = "loading-panel"
    ID_LOADER = "loader"
    ID_STATUS_TEXT = "status-text"
    
    def on_mount(self) -> None:
        self.theme = "theme-babel"

        self.styles.animate(
            attribute="opacity",
            value=1.0,
            duration=1.5,
            easing="out_cubic"
        )

    def compose(self) -> ComposeResult:
        with Horizontal(id=self.ID_LOGIN_DIALOG):

            with Vertical(id=self.ID_BRAND_PANEL):
                yield Static(ASCII_ART, id=self.ID_APP_LOGO)
                yield MultiColorCypherLabel([("< ", "white"),
                                             ("FUTURE:", "lime"),
                                             (" IS_", "gray"),
                                             (" LOADING />", "white")],
                                            id=self.ID_APP_TITLE)

            with Vertical(id=self.ID_FORM_PANEL):
                login_input: Input = Input(placeholder="ex : user", id=self.ID_USERNAME_INPUT)
                login_input.border_title = "login"

                token_input: Input = Input(placeholder="ex : Af23@", password=True, id=self.ID_TOKEN_INPUT)
                token_input.border_title = "token"

                yield login_input
                yield token_input
                yield Button("Connexion", variant="primary", id=self.ID_LOGIN_BTN, flat=True)

            with Vertical(id=self.ID_LOADING_PANEL):
                yield LoadingIndicator(id=self.ID_LOADER) 


    async def release_glitch(self) -> None:
        left_zone = self.query_one(f"#{self.ID_BRAND_PANEL}")
        GlitchEffect(left_zone, 2.0)
        
        def transition_callback():
            self.app.switch_screen("arena")

        self.styles.animate(
            attribute="opacity",
            value=0.0,
            duration=1.5,
            on_complete=transition_callback
        )

    async def loging_succes_animation(self) -> None:
        self.query_one(f"#{self.ID_FORM_PANEL}").remove()
        self.query_one(f"#{self.ID_LOADING_PANEL}").remove()
        self.query_one(f"#{self.ID_APP_TITLE}").remove()

        succes_message = TerminalTyperLabel(
                sequences=[
                    "Loged in succesfully!",
                    "Ready to do something?",
                    "bla bla bla bla!",
                    "hahaha!",
                    "IT'S TIME TO DUEL!"
                    ],
                id=self.ID_STATUS_TEXT,
                on_complete=self.release_glitch
                )
        await self.query_one(f"#{self.ID_BRAND_PANEL}", Vertical).mount(succes_message)

        logo = self.query_one(f"#{self.ID_BRAND_PANEL}", Vertical)
        centre_ecran = self.app.size.width // 2 
        logo_center = logo.region.x + (logo.region.width // 2)
        distance_x = centre_ecran - logo_center

        self.query_one(f"#{self.ID_BRAND_PANEL}", Vertical).styles.animate(
                attribute="offset",
                value=ScalarOffset.from_offset((distance_x, 0)),
                duration=1, easing="out_quad"
                )

    @work
    async def try_connexion(self) -> None:
        username = self.query_one(f"#{self.ID_USERNAME_INPUT}", Input).value
        password = self.query_one(f"#{self.ID_TOKEN_INPUT}", Input).value



        if username and password:
            self.notify("Authentification...", title="Authentification.", timeout=2)

            self.query_one(f"#{self.ID_FORM_PANEL}").styles.display = "none"
            self.query_one(f"#{self.ID_LOADING_PANEL}", Vertical).styles.display = "block"

            await asyncio.sleep(3)
            success = await self.app.api_client.login(username, password)

            if not success:
                self.query_one(f"#{self.ID_LOADING_PANEL}", Vertical).styles.display = "none"
                self.query_one(f"#{self.ID_FORM_PANEL}").styles.display = "block"

                self.query_one(f"#{self.ID_USERNAME_INPUT}", Input).focus()
                self.notify("Invalid ids!", title="Authentification error", severity="error")

                GlitchEffect(self.query_one(f"#{self.ID_FORM_PANEL}"), 0.5)
            else:
                await self.loging_succes_animation()

        else:
            self.notify("Fields can't be empty.", title="Authentification error",  severity="error")
            self.query_one(f"#{self.ID_LOADING_PANEL}", Vertical).styles.display = "block"
            login_box = self.query_one(f"#{self.ID_FORM_PANEL}")
            GlitchEffect(login_box, 0.5)


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == self.ID_LOGIN_BTN:
            self.try_connexion()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == self.ID_USERNAME_INPUT:
            self.query_one(f"#{self.ID_TOKEN_INPUT}", Input).focus()

        elif event.input.id == self.ID_TOKEN_INPUT:
            self.try_connexion()
