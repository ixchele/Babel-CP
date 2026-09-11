from textual.widgets import Label
import string
import inspect
import random

class TerminalTyperLabel(Label):

    def __init__(self, sequences: list[str], loop: bool = False, on_complete=None, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.sequences = sequences
        self.loop = loop 
        self.on_complete = on_complete

        self.index_sequence = 0
        self.index_char = 0
        self.state = "TYPING"
        self.cursor = "█"
        self.show_cursor = True
        self.pool_glitch = string.ascii_uppercase + string.digits + "!@#$%^&*"

    def on_unmount(self) -> None:
        if hasattr(self, 'timer_action'):
            self.timer_action.stop()

        if hasattr(self, 'timer_curseur'):
            self.timer_curseur.stop()

    def on_mount(self) -> None:
        self.timer_action = self.set_interval(0.04, self.tick)
        self.timer_curseur = self.set_interval(0.4, self.flash_cursor)

    def flash_cursor(self) -> None:
        self.show_cursor = not self.show_cursor
        if self.state == "PAUSED":
            self.draw_text()

    def draw_text(self, char_glitch: str = "") -> None:
        current_sequence = self.sequences[self.index_sequence]
        clean_text = current_sequence[:self.index_char]
        visual_cursor = self.cursor if self.show_cursor else " "
        self.update(f"{clean_text}{char_glitch}{visual_cursor}")

    def tick(self) -> None:
        current_sequence = self.sequences[self.index_sequence]

        if self.state == "TYPING":
            self.show_cursor = True 

            if self.index_char >= len(current_sequence):
                self.state = "PAUSED"
                self.draw_text()
                self.timer_action.pause()

                last_sequence = (self.index_sequence == len(self.sequences) - 1)

                if not self.loop and last_sequence:
                    self._start_on_complete()
                    return

                self.set_timer(2.0, self.start_backspace)
            else:
                glitch = random.choice(self.pool_glitch)
                self.index_char += 1
                self.draw_text(char_glitch=glitch)

        elif self.state == "ERASING":
            self.show_cursor = True 

            if self.index_char <= 0:
                self.state = "PAUSED"
                self.draw_text()
                self.timer_action.pause()

                self.index_sequence = (self.index_sequence + 1) % len(self.sequences)
                self.set_timer(0.5, self.start_typing)
            else:
                self.index_char -= 1
                self.draw_text()

    def start_backspace(self) -> None:
        self.state = "ERASING"
        self.timer_action.resume()

    def start_typing(self) -> None:
        self.state = "TYPING"
        self.timer_action.resume()

    def _start_on_complete(self) -> None:
        if self.on_complete:
            if inspect.iscoroutinefunction(self.on_complete):
                self.run_worker(self.on_complete())
            else:
                self.on_complete()
