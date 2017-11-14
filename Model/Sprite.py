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

    def animate_walk(self, direction):
        '''
        This function servers the purpose of animating the
        sprite's walk in one direction.
        :param direction:
        :return:
        '''

        # Get the current x,y postion
        pos_x = self.pos[0]
        pos_y = self.pos[1]

        # Conditions to properly calculate position to move
        # NORTH
        if direction == Direction.NORTH:
            self.current_row += 1
            pos_y = self.pos[1] + self.walk_length_y
        # WEST
        elif direction == Direction.WEST:
            self.current_col -= 1
            pos_x = self.pos[0] - self.walk_length_x
        # SOUTH
        elif direction == Direction.SOUTH:
            self.current_row -= 1
            pos_y = self.pos[1] - self.walk_length_y
        # EAST
        elif direction == Direction.EAST:
            self.current_col += 1
            pos_x = self.pos[0] + self.walk_length_x

        # Set the positions for the animation and start it
        animation = Animation(pos=(pos_x, pos_y))
        animation.start(self)