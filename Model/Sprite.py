from kivy.uix.image import Image
from Direction import Direction
from kivy.animation import Animation

class Sprite(Image):

    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.size_hint = [None, None]
        self.current_row = 0
        self.current_col = 0
        self.walk_length_y = 0
        self.walk_length_x = 0

    def move_left(self, direction):
        pass

    def animate(self):
        pos_x = self.pos[0] - self.walk_length_x
        pos_y = self.pos[1] - self.walk_length_y
        animation = Animation(pos=(pos_x, self.pos[1]))
        animation.start(self)
