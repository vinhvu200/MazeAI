from kivy.animation import Animation
from kivy.uix.image import Image

from Model.Enum.Direction import Direction
from Model.Enum.Speed import Speed
from Model.Enum.State import State


class Sprite(Image):

    def __init__(self, current_row, current_col, speed, state=State.MANUAL, **kwargs):
        super(Sprite, self).__init__(**kwargs)

        # Declare the image path for sprite standing/walking
        self.stand_source = 'Images/p1_stand.png'
        self.walk_source = 'Images/p1_walk.zip'

        # Must have this so it can be placed anywhere on
        # the board without restriction of FloatLayout
        self.size_hint = [None, None]

        # This is to reference the maze_board_mat to
        # know where the character is
        self.current_row = current_row
        self.current_col = current_col

        # This is how far to walk in the x,y direction
        # to land in the middle of each square
        self.walk_length_y = 0
        self.walk_length_x = 0

        # Default variables to control how fast
        # the walk animation is
        self.anim_delay = 0.025
        self.walk_duration = 1
        self.bump_wall_duration = 0.25

        # Determines which speed to set the character to
        if speed == Speed.NORMAL:
            self.set_speed_normal()
        elif speed == Speed.FAST:
            self.set_speed_fast()
        elif speed == Speed.HYPER:
            self.set_speed_hyper()

        # Determine the state the character is in
        self.state = state

        # Setting the source defaultint to standing
        self.source = self.stand_source

    def get_bump_wall_animation(self, direction):
        '''
        - This function takes the direction of where the
        sprite would like to move and then calculate the
        distance to "bump" into the wall.
        :param direction: Direction enum
        :return: Animation
        '''

        # These attempt positions are to be changed
        # depending on which direction the character
        # is moving in
        attempt_x = self.pos[0]
        attempt_y = self.pos[1]

        # Adjust the walk_length to make the character walk
        # far enough to "bump" into a wall
        ratio = .1
        adjusted_walk_length_x = ratio * self.walk_length_x
        adjusted_walk_length_y = ratio * self.walk_length_y

        # Conditions to determine how the attempted position will
        # be changed based on Direction
        if direction == Direction.NORTH:
            attempt_y = attempt_y + adjusted_walk_length_y
        if direction == Direction.WEST:
            attempt_x = attempt_x - adjusted_walk_length_x
        if direction == Direction.SOUTH:
            attempt_y = attempt_y - adjusted_walk_length_y
        if direction == Direction.EAST:
            attempt_x = attempt_x + adjusted_walk_length_x

        # Move a minimal distance to "bump" a wall
        attempt_animation = Animation(pos=(attempt_x, attempt_y), duration=self.bump_wall_duration)
        # Move back to original position
        original_animation = Animation(pos=(self.pos[0], self.pos[1]), duration=self.bump_wall_duration)
        # Do the animation sequentially
        animation = attempt_animation + original_animation

        # Start the walking animation
        self.source = self.walk_source

        return animation

    def get_walk_animation(self, direction):
        '''
        This function servers the purpose of animating the
        sprite's walk in one direction.

        :param direction: Direction enum
        :return: Animation
        '''

        # Get the current x,y postion
        pos_x = self.pos[0]
        pos_y = self.pos[1]

        # Conditions to properly calculate position to move
        # NORTH
        if direction == Direction.NORTH:
            self.current_row -= 1
            pos_y = self.pos[1] + self.walk_length_y
        # WEST
        elif direction == Direction.WEST:
            self.current_col -= 1
            pos_x = self.pos[0] - self.walk_length_x
        # SOUTH
        elif direction == Direction.SOUTH:
            self.current_row += 1
            pos_y = self.pos[1] - self.walk_length_y
        # EAST
        elif direction == Direction.EAST:
            self.current_col += 1
            pos_x = self.pos[0] + self.walk_length_x

        # Set the positions for the animation, and bind on_complete
        # so that we know when to switch back to self.stand_source
        animation = Animation(pos=(pos_x, pos_y), duration=self.walk_duration)

        # Start the walking animation
        self.source = self.walk_source

        return animation

    def set_speed_fast(self):
        self.anim_delay = 0.0125
        self.walk_duration = 0.5
        self.bump_wall_duration = 0.125

    def set_speed_hyper(self):
        self.anim_delay = 0.001
        self.walk_duration = 0.15
        self.bump_wall_duration = 0.01

    def set_speed_normal(self):
        self.anim_delay = 0.025
        self.walk_duration = 1
        self.bump_wall_duration = 0.25

    def set_standing(self):
        self.source = self.stand_source

    def set_walking(self):
        self.source = self.walk_source