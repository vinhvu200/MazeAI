from kivy.uix.button import Button


class Path(Button):
    '''
    - This class sets up a button as either a wall or a path.
    - Walls and Paths are indicated by just their background image
    - Remember to disable the button after it is initialized.
    It does not work when you try to disable it in the constructor
    '''

    def __init__(self, size_hint_x=1, size_hint_y=1, wall=False, **kwargs):
        super(Path, self).__init__(**kwargs)

        # Image source for either path or wall
        self.path_source = 'Images/path.png'
        self.wall_source = 'Images/wall.png'

        # Set up for button
        self.background_disabled_normal = ''
        self.background_disabled_normal = self.path_source
        self.disabled_color = [0, 0, 0, 1]
        self.background_normal = ''
        self.size_hint = [size_hint_x, size_hint_y]

        # If wall condition is True, then change to wall_source
        if wall is True:
            self.background_disabled_normal = self.wall_source

    def set_path_background(self):
        '''
        This function sets the background_image to path image
        :return: None
        '''
        self.background_disabled_normal = self.path_source

    def set_wall_background(self):
        '''
        This function sets the background_image to wall image
        :return: None
        '''
        self.background_disabled_normal = self.wall_source