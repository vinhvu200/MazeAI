from kivy.uix.button import Button


class Path(Button):

    def __init__(self, size_hint_x=1, size_hint_y=1, wall=False, **kwargs):
        super(Path, self).__init__(**kwargs)

        self.wall_color = [.627, .321, .094, 1]
        self.path_color = [0, 0, 1, 1]
        self.background_disabled_normal = ''
        self.disabled_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.background_color = self.path_color

        self.size_hint = [size_hint_x, size_hint_y]

        if wall is True:
            self.background_color = self.wall_color

    def set_path(self):
        self.background_color = self.path_color

    def set_wall(self):
        self.background_color = self.wall_color