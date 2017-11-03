from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class BorderLabel(Label):
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 0.25)
            Rectangle(pos=self.pos, size=self.size)