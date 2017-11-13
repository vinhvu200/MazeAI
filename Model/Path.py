from kivy.uix.button import Button


class Path(Button):
    '''
    - This class sets up a button as either a wall or a path.
    - Walls and Paths are indicated by just their color
    - Remember to disable the button after it is initialized.
    It does not work when you try to disable it in the constructor
    '''

    def __init__(self, size_hint_x=1, size_hint_y=1, wall=False, **kwargs):
        super(Path, self).__init__(**kwargs)

        # Two colors to identify wall or path
        self.wall_color = [.627, .321, .094, 1]
        self.path_color = [0, 0, 1, 1]

        # Set up for button
        self.background_disabled_normal = ''
        self.disabled_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.background_color = self.path_color
        self.size_hint = [size_hint_x, size_hint_y]

        # Defaults as a path
        if wall is True:
            self.background_color = self.wall_color

    def set_path(self):
        '''
        This function sets the background_color to the path_color
        :return:
        '''
        self.background_color = self.path_color

    def set_wall(self):
        '''
        This function sets the background_color to the wall_color
        :return:
        '''
        self.background_color = self.wall_color