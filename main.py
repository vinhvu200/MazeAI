from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from Model.Direction import Direction
from Model.Sprite import Sprite
from Model.Path import Path
from Model.TDSquare import TDSquare
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.config import Config
from kivy.animation import Animation
import time
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '500')
from kivy.core.window import Window


class RootWidgit(FloatLayout):

    maze1 = 'maze1.txt'
    INITIAL_ROW = 0
    INITIAL_COL = 2
    END_ROW = 4
    END_COL = 2
    maze_board_children_size = 0
    walk_length = 0
    animate = Animation()
    learn_flag = False

    def __init__(self, **kwargs):
        super(RootWidgit, self).__init__(**kwargs)

        # Get the maze_board and value_board GridLayout from .kv file
        self.maze_board = self.ids.maze_board
        self.value_board = self.ids.value_board

        # Get Buttons from .kv file
        self.start_button = self.ids.start_button
        self.test_button = self.ids.test_button

        # Bind Buttons from .kv file
        self.start_button.bind(on_press=self._start)
        self.test_button.bind(on_press=self._test)

        # Set up the keyboard and bind it
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Create main character
        self.character = Sprite(current_row=self.INITIAL_ROW,
                                current_col=self.INITIAL_COL)

        # Generate the 3D matrix containing the walls along with ROWS
        # and COLS of the board
        self.mat_walls, self.ROWS, self.COLS = self._build_matrix_walls(self.maze1)

        # Readjust rows and columns to fit walls in between for the board rows
        self.MAZE_BOARD_ROWS = self.ROWS * 2 + 1
        self.MAZE_BOARD_COLS = self.COLS * 2 + 1

        # Initialize the 2D maze matrix where 1 will indicate where the user is
        self.maze_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]
        self.maze_board_mat[0][2] = 1

        # Populate value_board with the appropriate matrices
        self._populate_value_board()

        # Populate maze_boards with the current matrices and update
        # the maze_board_children_size
        self._populate_maze_board()

        # Fill the walls in for maze_board
        self._populate_walls()

    def _test(self, dt):

        self.remove_widget(self.character)
        self.character = Sprite(current_row=self.INITIAL_ROW,
                                current_col=self.INITIAL_COL)
        self.callback_setup(None)

    def callback_setup(self, dt):
        '''
        This function servers the purpose of getting the walk_length for the character
        and placing the character. It is a callback because it needs the GridLayout to
        finish calculating everything first.
        :param dt:
        :return:
        '''
        self._get_walk_length()
        self._place_character()

    def learn(self, dt):
        '''
        This function should be continuously call for the character to slowly learn the maze.
        It is scheduled again in self._end_animation binding.
        :param dt:
        :return:
        '''

        if self.character.current_row == self.END_ROW and self.character.current_col == self.END_COL:
            self.remove_widget(self.character)
            self.character = Sprite(current_row=self.INITIAL_ROW,
                                    current_col=self.INITIAL_COL)
            self.callback_setup(None)

        # Get child_index to obtain the td_square from the value_board
        child_index = self._get_child_index_value_board(self.character.current_row,
                                                        self.character.current_col)
        current_td_square = self.value_board.children[child_index]

        # Find the max_value of the direction_values and its index of the current_td_square
        current_max_value = max(current_td_square.direction_values)
        current_max_index = current_td_square.direction_values.index(current_max_value)

        # Choose appropriate animation based on max_index
        # IMPORTANT: After this is called, the character will
        # have updated its rows and columns
        valid_flag = self._animate(current_max_index)

        # Get the new updated td_square
        child_index = self._get_child_index_value_board(self.character.current_row,
                                                        self.character.current_col)
        new_td_square = self.value_board.children[child_index]

        # Calculate updates for the current_td_square
        self._calculate_update(current_td_square, new_td_square, current_max_index, valid_flag)

    def _animate(self, max_index):
        '''
        - This function takes the max_index which is the "best" move
        of the four on the current td_square and then animates what
        that move would look like.
        - Returns a valid_flag to determine whether the move made was
        valid. Valid means it did not bump into a wall. Invalid means
        bumping into a wall.
        :param max_index:
        :return: Boolean
        '''

        valid_flag = True
        # Calculate animation
        if Direction.NORTH.value == max_index:

            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.NORTH)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.NORTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.NORTH)
                valid_flag = False
        elif Direction.EAST.value == max_index:

            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.EAST)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.EAST)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.EAST)
                valid_flag = False
        elif Direction.SOUTH.value == max_index:
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.SOUTH)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.SOUTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.SOUTH)
                valid_flag = False
        elif Direction.WEST.value == max_index:
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.WEST)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.WEST)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.WEST)
                valid_flag = False

        self.animate.bind(on_complete=self._end_animation)
        self.animate.start(self.character)
        return valid_flag

    def _build_matrix_walls(self, filename):
        '''
        This function serves the purpose of generating a 3D matrix
        which tells where the walls are indicated for each square on
        the board. The walls are NORTH, EAST, SOUTH, and WEST respectively.

        EXAMPLE: [1, 0, 0, 1]
        - This tells us there is a wall NORTH and SOUTH of the square

        :return: matrix_walls, rows, cols
        '''

        # Open maze file
        maze_file = open(filename, 'r')

        # Read and split lines by space
        line = maze_file.readline()
        line_by_space = line.split(' ')

        # First two values indicate rows and cols respectively
        rows = int(line_by_space[0])
        cols = int(line_by_space[1])

        # Initialize matrix[ROWS][COLS][4]
        # The number 4 is number of directions for walls: NORTH, EAST, SOUTH, WEST respectively
        mat_walls = [[[0 for _ in xrange(4)] for _ in xrange(cols)] for _ in xrange(rows)]

        # Loops through matrix to assign the wall direction
        for x in range(int(rows)):
            for y in range(int(cols)):

                # Read line
                line = maze_file.readline()

                # If line is only a new line, then read onto next line
                if line == '\n':
                    line = maze_file.readline()

                # split line by space
                line_by_space = line.split(' ')

                # Assign wall values for board position (x,y)
                mat_walls[x][y][0] = int(line_by_space[0])
                mat_walls[x][y][1] = int(line_by_space[1])
                mat_walls[x][y][2] = int(line_by_space[2])
                mat_walls[x][y][3] = int(line_by_space[3].rstrip())

        # return matrix, rows, cols
        return mat_walls, rows, cols

    def _calculate_update(self, current_td_square, new_td_square, current_max_index, valid_flag):
        '''
        - Using Q-learning, the character updates its current td_square direction_values
        accordingly so that the next move can be chosen.
        - Valid flag used to increase penalty when bumping walls
        :param current_td_square: TDSquare
        :param new_td_square: TDSquare
        :param current_max_index: integer
        :return:
        '''

        # learning_rate, discount, and cost
        lr = 0.5
        d = 1
        cost = 0.04
        if valid_flag is False:
            cost *= 2

        # Current td_square value of the "best" move grabbed from the current_max_index
        current_val = current_td_square.direction_values[current_max_index]

        # new td_square reward
        reward = new_td_square.reward

        # Find the max_value of the direction_values and its index of new_td_square
        new_max_val = max(new_td_square.direction_values)

        # Q-learning equation
        current_td_square.direction_values[current_max_index] += lr * (reward + d*new_max_val - current_val - cost)

        # Update the value_board text to see what is happening
        current_td_square.update()

    def _end_animation(self, widget, item):
        '''
        - This binding method is used to stop the walking animation
         and switch back to the standing animation when it is done
         walking from point A to B.
        - It rebinds the keyboard again as well. Keyboard is unbinded
        earlier to stop actions in middle of animation
        '''

        # Switches back to just standing
        self.character.set_standing()

        # Bind keyboard again after animation is done
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        if self.learn_flag is True:
            self.learn(None)

    def _get_child_index_maze_board(self, row, col):
        '''
        - This function serves the purpose of getting the child_index for
        maze_board gridlayout.
        :param row:
        :param col:
        :return:
        '''

        # Calculate how many rows to go down and
        # columns to go over
        row = (2 * row + 1) * self.MAZE_BOARD_ROWS
        col = (2 * col + 1) % self.MAZE_BOARD_COLS

        # Add the rows and columns to get a pseduo position
        pos = row + col

        # Position has to be readjusted because child[0]
        # starts on bottom right
        real_pos = self.maze_board_children_size - pos - 1
        return real_pos

    def _get_child_index_value_board(self, row, col):
        '''
        This function gets the child index for self.value_board,
        given a row and column. This is needed because the GridLayout
        children starts [0] at the bottom right which is not what
        we need.
        :param row: integer
        :param col: integer
        :return: integer, child_index
        '''

        # Determines how many rows to go down and columns to go across
        row = row * self.ROWS
        col = col % self.COLS

        # Add the two
        pos = row + col

        # Adjust it by subtracting the total children_size
        value_board_children_size = self.ROWS * self.COLS
        child_index = value_board_children_size - pos - 1

        # return proper index
        return child_index

    def _get_walk_length(self):
        '''
        This function serves the purpose of getting the walk length from
        one square to the next both in x and y direction.
        :param dt:
        :return:
        '''

        # Get initial index
        initial_index = self._get_child_index_maze_board(self.INITIAL_ROW, self.INITIAL_COL)

        # Get end index for x direction
        end_index_x = self._get_child_index_maze_board(self.INITIAL_ROW, self.INITIAL_COL-1)

        # Get the two x coordinates for those indices
        x1 = self.maze_board.children[initial_index].pos[0]
        x2 = self.maze_board.children[end_index_x].pos[0]

        # Calculate the walk_length in x direction
        self.character.walk_length_x = x1 - x2

        # Get end index for y direction
        end_index_y = self._get_child_index_maze_board(self.INITIAL_ROW + 1, self.INITIAL_COL)

        # Get the two y coordinates for those indices
        y1 = self.maze_board.children[initial_index].pos[1]
        y2 = self.maze_board.children[end_index_y].pos[1]

        # Calculate the walk_length in y direction
        self.character.walk_length_y = y1 - y2

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        This function serves the purpose of handling keyboard events
        to move the character based on the keys: w, a, s, d.
        '''

        # Conditions to determine which direction to move character
        # Three options for validity of move: True, False, None
        # True: There are no walls; therefore, you can walk through
        # False: There is a wall; animate "bumping" into wall
        # None: Character is now out of bound
        # NORTH CONDITION
        if keycode[1] == 'w':
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                Direction.NORTH)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.NORTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.NORTH)
        # WEST
        elif keycode[1] == 'a':
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.WEST)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.WEST)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.WEST)
        # SOUTH
        elif keycode[1] == 's':
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.SOUTH)
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.SOUTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.SOUTH)
        # EAST
        elif keycode[1] == 'd':
            if self._valid_move(self.character.current_row, self.character.current_col,
                                Direction.EAST) is True:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.EAST)
            else:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.EAST)

        # Bind the animation
        self.animate.bind(on_complete=self._end_animation)

        # Start animation
        self.animate.start(self.character)

        # Unbind keyboard to stop action in middle of animation
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _place_character(self):
        '''
        This callback serves the purpose of calculating the character's position
        and then placing the character there.
        :param dt:
        :return:
        '''

        # Get the index for initial position of where the position is
        # supposed to be
        index = self._get_child_index_maze_board(self.INITIAL_ROW, self.INITIAL_COL)

        # Get the x,y size of the gridlayout square
        # and use that to calculate the x,y adjustments
        square_size = self.maze_board.children[index].size
        square_x_adjust = square_size[0] / 2
        square_y_adjust = square_size[1] / 2

        # Get the sprite x,y size based on ratio
        # of the actual square
        ratio = 0.8
        sprite_size_x = square_size[0] * ratio
        sprite_size_y = square_size[1] * ratio

        # Use the sprite size to calculate x,y
        # adjustment position
        sprite_x_adjust = sprite_size_x / 2
        sprite_y_adjust = sprite_size_y / 2

        # Get the x,y position of the initial square
        initial_pos = self.maze_board.children[index].pos
        initial_x = initial_pos[0]
        initial_y = initial_pos[1]

        # Calculate the x,y position to place the character
        x = initial_x + square_x_adjust - sprite_x_adjust
        y = initial_y + square_y_adjust - sprite_y_adjust

        self.character.size = [sprite_size_x, sprite_size_y]
        self.character.pos = [x, y]
        self.add_widget(self.character)

    def _populate_maze_board(self):
        '''
        This function serves the purpose of populating the GridLayouts set up in
        the .kv file.
        - The maze_board is adjusted to add walls in between them and then fill
        them according to the maze_board_mat

        :return: None
        '''

        # setting columns for the GridLayout
        self.maze_board.cols = self.MAZE_BOARD_COLS

        # populate maze_board GridLayout
        for x in xrange(self.MAZE_BOARD_ROWS):

            # Creates the actual vertical path
            if x % 2 == 1:
                # Handles horizontal wall widgits as well as the actual path
                for y in xrange(self.MAZE_BOARD_COLS):

                    # Creates actual path
                    if y % 2 == 1:

                        # Create path block
                        path = Path()

                        # Paths are buttons which need to be disabled
                        path.disabled = True

                        # update maze_board children size
                        self.maze_board_children_size += 1

                        # Add to the board
                        self.maze_board.add_widget(path)

                    # Creates wall
                    else:

                        # Create and add wall into the GridLayout
                        # Walls are Buttons which need to be disabled
                        wall = Path(wall=True, size_hint_x=0.1, size_hint_y=1)
                        wall.disabled = True

                        # update maze_board children size
                        self.maze_board_children_size += 1

                        # Add to board
                        self.maze_board.add_widget(wall)

            # create the vertical walls
            else:
                for y in xrange(self.maze_board.cols):
                    # Creating the wall and adding it
                    # Walls are Buttons which need to be disabled
                    wall = Path(wall=True, size_hint_x=0.1, size_hint_y=0.1)
                    wall.disabled = True

                    # update maze_board children size
                    self.maze_board_children_size += 1

                    # Add to board
                    self.maze_board.add_widget(wall)

    def _populate_value_board(self):
        '''
        This function serves the purpose of populating the value board (GridLayout)
        with TDSquare objects (which inherit from Button). It will set
        the rewards for the completion square as well which will be 1
        :return:
        '''

        # Set up the columns
        self.value_board.cols = self.COLS

        for x in xrange(self.ROWS):
            for y in xrange(self.COLS):

                # Create a td_square to add
                td_square = TDSquare()

                # TDSquares are button that need to be disabled
                td_square.disabled = True

                # Add td_square to our value_board gridlayout
                self.value_board.add_widget(td_square)

        # Find the end square and set its reward to 1
        child_index = self._get_child_index_value_board(self.END_ROW, self.END_COL)
        self.value_board.children[child_index].reward = 1
        self.value_board.children[child_index].update()

        # Change value direction of value of initial square
        # to negative so that it can't move up
        child_index = self._get_child_index_value_board(self.INITIAL_ROW, self.INITIAL_COL)
        self.value_board.children[child_index].direction_values[0] = -1


    def _populate_walls(self):
        '''
        This function serves the purpose of populating walls and the
        intermediate paths between squares. This is done using the
        mat_wall matrix which tells you whether there is a wall NORTH,
        EAST, SOUTH, or WEST.

        IMPORTANT: The walls to be filled are children of the maze_board
        GridLayout. Position 0 is the bottom right square NOT the top RIGHT
        so adjustments are made accordingly.
        :return:
        '''

        # Looping through rows and columns of the ROWS and COLS of the board
        # NOT the maze_board ROWS and COLS. maze_board rows and cols include
        # walls itself which we are trying to fill
        for row in xrange(self.ROWS):
            for col in xrange(self.COLS):

                # This is the current position for the maze_board GridLayout
                current_pos = self._get_child_index_maze_board(row, col)

                # NORTH wall condition
                # If exists, find the adjusted position
                # then call .set_path_background() to change the background image
                # otherwise call .set_wall_background() to change to wall_color
                if self.mat_walls[row][col][Direction.NORTH.value] == 1:
                    adjusted_pos = current_pos + self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].set_wall_background()
                else:
                    adjusted_pos = current_pos + self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].set_path_background()

                # EAST wall condition
                if self.mat_walls[row][col][Direction.EAST.value] == 1:
                    adjusted_pos = current_pos - 1
                    self.maze_board.children[adjusted_pos].set_wall_background()
                else:
                    adjusted_pos = current_pos - 1
                    self.maze_board.children[adjusted_pos].set_path_background()

                # SOUTH wall condition
                if self.mat_walls[row][col][Direction.SOUTH.value] == 1:
                    adjusted_pos = current_pos - self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].set_wall_background()
                else:
                    adjusted_pos = current_pos - self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].set_path_background()

                # WEST wall condition
                if self.mat_walls[row][col][Direction.WEST.value] == 1:
                    adjusted_pos = current_pos + 1
                    self.maze_board.children[adjusted_pos].set_wall_background()
                else:
                    adjusted_pos = current_pos + 1
                    self.maze_board.children[adjusted_pos].set_path_background()

    def _start(self, dt):
        self.learn_flag = True
        self.learn(None)

    def _valid_move(self, current_row, current_col, direction):
        '''
        This function takes character's current row and columns and
        determine whether there is a wall blocking the direction that
        they intend to move in
        :param current_row: sprite's current row
        :param current_col: sprite's current col
        :param direction: sprite's intended direction (Direction enum)
        :return:
        '''

        # If the character is out of bound, return None
        if current_row >= self.ROWS:
            return None
        if current_col >= self.COLS:
            return None

        # If there is no wall; the move is valid
        if self.mat_walls[current_row][current_col][direction.value] == 0:
            return True
        # If there is a wall; move is invalid
        else:
            return False

class MazeApp(App):

    def build(self):
        root = RootWidgit()
        Clock.schedule_once(root.callback_setup, 1)
        #Clock.schedule_once(root.learn, 1.5)
        return root

if __name__ == "__main__":
    MazeApp().run()