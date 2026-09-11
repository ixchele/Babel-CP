import random
from textual.widget import Widget


class GlitchEffect:
    """
    Applies a temporary visual glitch effect to a Textual widget.
    Requires corresponding CSS classes for the colors parameter.
    """
    def __init__(self, target: Widget, duration: float = 1.0, colors: list[str]|None = None) -> None:
        self.target = target
        self.ticks = int(duration / 0.05)
        self.colors = colors or ["glitch-cyan", "glitch-magenta"]
        
        self.base_x = self.target.styles.offset.x.value
        self.base_y = self.target.styles.offset.y.value
        
        self.timer = self.target.set_interval(0.05, self._tick)

    def _tick(self) -> None:
        try:
            if self.ticks <= 0:
                self.timer.stop()
                self.target.styles.offset = (int(self.base_x), int(self.base_y))
                self.target.remove_class(*self.colors)
                return

            dx = random.choice([-3, -2, 2, 3])
            dy = random.choice([-1, 0, 1])
            
            self.target.styles.offset = (int(self.base_x) + dx, int(self.base_y) + dy)

            self.target.remove_class(*self.colors)
            random_color = random.choice([""] + self.colors + [""])
            
            if random_color:
                self.target.add_class(random_color)

            self.ticks -= 1
            
        except Exception:
            self.timer.stop()
