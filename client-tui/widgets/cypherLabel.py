from textual.widgets import Label
import string
import random


class MultiColorCypherLabel(Label):
    def __init__(self, segments: list[tuple[str, str]], **kwargs) -> None:
        """
        segments: pairs list (text, color).
        Ex: [("foo", "white"), ("bar", "white"), ("buz", "red")]
        """
        super().__init__("", **kwargs)

        self.segments = segments
        self.target_text = "".join(texte for texte, _ in segments)

        self.split_point = []
        total_len = 0
        for text, color in segments:
            total_len += len(text)
            self.split_point.append((total_len, color))

    def on_mount(self) -> None:
        self.current_index = 0
        self.pool = string.ascii_uppercase + string.digits + "!@#$%^&*"
        self.backspace_mod = False
        self.main_timer = self.set_interval(0.05, self.tick)

    def apply_multicolor(self, text: str) -> str:
        if not text:
            return ""

        result = ""
        current_index = 0

        for limit, color in self.split_point:
            if current_index >= len(text):
                break

            split = text[current_index:limit]
            if split:
                result += f"[{color}]{split}[/{color}]"

            current_index = limit

        if current_index < len(text):
            left_over = text[current_index:]
            last_color = self.split_point[-1][1]
            result += f"[{last_color}]{left_over}[/{last_color}]"

        return result

    def tick(self) -> None:
        if self.backspace_mod:
            self.current_index -= 1
            text = self.target_text[:self.current_index]
            self.update(self.apply_multicolor(text))

            if self.current_index <= 0:
                self.main_timer.pause()
                self.backspace_mod = False
                self.set_timer(0.5, self.main_timer.resume)
            return
        else:
            if self.current_index >= len(self.target_text):
                self.update(self.apply_multicolor(self.target_text))
                self.main_timer.pause()
                self.backspace_mod = True
                self.set_timer(2.0, self.main_timer.resume)
                return

            reamaining_len = len(self.target_text) - self.current_index
            nois = "".join(random.choice(self.pool) for _ in range(reamaining_len))
            text = self.target_text[:self.current_index] + nois
            self.update(self.apply_multicolor(text))

            self.current_index += 1
