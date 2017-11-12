from kivy.uix.button import Button

class Wall(Button):

    def __init__(self, size_hint_x=1, size_hint_y=1, **kwargs):
        super(Wall, self).__init__(**kwargs)

        self.wall_color = [.627, .321, .094, 1]
        self.background_disabled_normal = ''
        self.disabled_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.background_color = self.wall_color

        self.size_hint = [size_hint_x, size_hint_y]