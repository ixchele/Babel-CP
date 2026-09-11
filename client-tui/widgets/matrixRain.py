from textual.app import App, ComposeResult
from textual.widgets import Static
import random


class MatrixRain(Static):
    def on_mount(self) -> None:
        self.caracteres = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789!@#$%^&*"

        self.col = []
        self.width = 0
        self.height = 0

        self.matrix_timer = self.set_interval(0.08, self.tick)

    def on_resize(self, event) -> None:
        old_widht = self.width
        new_widht = event.size.width

        self.width = new_widht
        self.height = event.size.height

        if not self.col:
            self.col = [random.randint(-self.height * 2, 0) for _ in range(self.width)]
            return

        if new_widht > old_widht:
            missing_col = new_widht - old_widht
            new_drop = [random.randint(-self.height * 2, 0) for _ in range(missing_col)]
            self.col.extend(new_drop)

        elif new_widht < old_widht:
                self.col = self.col[:new_widht]

    def tick(self) -> None:
        if not self.col or self.height <= 0:
            return

        lines = [[" " for _ in range(self.width)] for _ in range(self.height)]

        trail_size = 15

        for x in range(self.width):
            y = self.col[x]

            for i in range(trail_size):
                pos_y = y - i
                if 0 <= pos_y < self.height:
                    lines[pos_y][x] = random.choice(self.caracteres)

            self.col[x] += 1

            if self.col[x] - trail_size > self.height:
                self.col[x] = random.randint(-15, 0)

        result = "\n".join("".join(ligne) for ligne in lines)
        self.update(result)


class AppConsole(App):

    CSS = """
    MatrixRain {
            width: 100%;
            height: 100%;
            color: #39ff14;
            background: #050a05;
            text-style: bold;
            }
    """

    def compose(self) -> ComposeResult:
        yield MatrixRain()


if __name__ == "__main__":
    app = AppConsole()
    app.run()
