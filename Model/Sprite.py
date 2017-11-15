from kivy.uix.image import Image
from Direction import Direction
from kivy.animation import Animation


class Sprite(Image):

    def __init__(self, current_row, current_col, keyboard, _on_keyboard_down, **kwargs):
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

        # How fast to animate the walking
        self.anim_delay = 0.025

        # Setting the source defaultint to standing
        self.source = self.stand_source

        # Set up the keyboard and the binding method
        self._keyboard = keyboard
        self._on_keyboard_down = _on_keyboard_down

    def animate_bump_wall(self, direction):
        '''
        This function takes the direction of where the
        sprite would like to move and then calculate the
        distance to "bump" into the wall.
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
        attempt_animation = Animation(pos=(attempt_x, attempt_y), duration=0.25)
        # Move back to original position
        original_animation = Animation(pos=(self.pos[0], self.pos[1]), duration=0.25)
        # Do the animation sequentially
        animation = attempt_animation + original_animation
        # When animation is complete, switch back to standing
        animation.bind(on_complete=self.end_animation)

        # Start the walking animation
        self.source = self.walk_source
        animation.start(self)

        # Unbind keyboard to stop action in middle of animation
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)

    def animate_walk(self, direction):
        '''
        This function servers the purpose of animating the
        sprite's walk in one direction.
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
        animation = Animation(pos=(pos_x, pos_y), duration=1)
        animation.bind(on_complete=self.end_animation)

        # Start walking animation
        self.source = self.walk_source
        animation.start(self)

        # Unbind keyboard to stop action in middle of animation
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)

    def end_animation(self, widget, item):
        '''
        - This binding method is used to stop the walking animation
         and switch back to the standing animation when it is done
         walking from point A to B.
        - It rebinds the keyboard again as well. Keyboard is unbinded
        earlier to stop actions in middle of animation
        '''

        # Switches back to just standing
        self.source = self.stand_source

        # Bind keyboard again after animation is done
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

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
        attempt_animation = Animation(pos=(attempt_x, attempt_y), duration=0.25)
        # Move back to original position
        original_animation = Animation(pos=(self.pos[0], self.pos[1]), duration=0.25)
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
        animation = Animation(pos=(pos_x, pos_y), duration=1)

        # Start the walking animation
        self.source = self.walk_source

        return animation

    def set_standing(self):
        self.source = self.stand_source

    def set_walking(self):
        self.source = self.walk_source