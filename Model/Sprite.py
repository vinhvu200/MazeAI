from kivy.uix.image import Image
from Direction import Direction
from kivy.animation import Animation

class Sprite(Image):

    def __init__(self, stand_source, walk_source, **kwargs):
        super(Sprite, self).__init__(**kwargs)

        # Must have this so it can be placed anywhere on
        # the board without restriction of FloatLayout
        self.size_hint = [None, None]

        # This is to reference the maze_board_mat to
        # know where the character is
        self.current_row = 0
        self.current_col = 0

        # This is how far to walk in the x,y direction
        # to land in the middle of each square
        self.walk_length_y = 0
        self.walk_length_x = 0

        # How fast to animate the walking
        self.anim_delay = 0.035

        # Two image source to determine whether the
        # sprite is standing or walking
        self.stand_source = stand_source
        self.walk_source = walk_source

        # Setting the source defaultint to standing
        self.source = self.stand_source

    def animate_walk(self, direction):
        '''
        This function servers the purpose of animating the
        sprite's walk in one direction.
        :param direction:
        :return:
        '''
        self.source=self.walk_source

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

        # Set the positions for the animation, and bind on_complete
        # so that we know when to switch back to self.stand_source
        animation = Animation(pos=(pos_x, pos_y), duration=1)
        animation.bind(on_complete=self.end_animation)
        animation.start(self)

    def end_animation(self, widget, item):
        # Switches back to just standing
        self.source = self.stand_source
