from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse


class TDIndicator(Widget):

    def __init__(self, **kwargs):
        super(TDIndicator, self).__init__(**kwargs)
        self.color = [0, 1, 0, 0.65]
        self.strength = 0

    def draw(self):

        with self.canvas:
            Color(0, 1, 0, 0.65)
            Ellipse(pos=self.pos, size=self.size)
