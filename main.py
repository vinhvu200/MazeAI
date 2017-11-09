from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from Model.Direction import Direction
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from kivy.config import Config
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '500')


class RootWidgit(FloatLayout):

    maze1 = 'maze1.txt'
    INITIAL_ROW = 0
    INITIAL_COL = 2
    wall_color = [.627, .321, .094, 1]
    path_color = [0, 0, 1, 1]
    MAZE_BOARD_CHILDREN_SIZE = 0
    walk_length = 0

    def __init__(self, **kwargs):
        super(RootWidgit, self).__init__(**kwargs)

        # Get the maze_board and value_board GridLayout from .kv file
        self.maze_board = self.ids.maze_board
        self.value_board = self.ids.value_board

        # Get the character image
        self.character = self.ids.character

        # Generate the 3D matrix containing the walls along with ROWS
        # and COLS of the board
        self.mat_walls, self.ROWS, self.COLS = self._build_matrix_walls(self.maze1)

        # Readjust rows and columns to fit walls in between for the board rows
        self.MAZE_BOARD_ROWS = self.ROWS * 2 + 1
        self.MAZE_BOARD_COLS = self.COLS * 2 + 1

        # Initialize the 2D maze matrix where 1 will indicate where the user is
        self.maze_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]
        self.maze_board_mat[0][2] = 1

        # Initialize the 2D value matrix to perform reinforcement learning on
        self.value_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]

        # Populate value_board with the appropriate matrices
        self._populate_value_board()

        # Populate maze_boards with the current matrices and update
        # the maze_board_children_size
        self._populate_maze_board()

        # Fill the walls in for maze_board
        self._populate_walls()

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

    def _populate_value_board(self):
        '''
        This function serves the purpose of setting up the value_board
        GridLayout to match the value_board_mat
        :return:
        '''
        
        # Set up the columns
        self.value_board.cols = self.COLS

        # populate value_board GridLayout
        for x in xrange(self.ROWS):
            for y in xrange(self.COLS):
                # Creating buttons for the widgits inside of gridlayouts
                # because they are more flexible to work with
                button = Button(text=str(self.value_board_mat[x][y]),
                                background_disabled_normal='',
                                disabled_color=[1, 1, 1, 1],
                                background_normal='',
                                background_color=[0, 0, 1, 0.65])

                # Disable button after creation because background_colors and such
                # would not save otherwise
                button.disabled = True

                # Add button to our value_board gridlayout
                self.value_board.add_widget(button)

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

                        # Creating buttons for the widgits inside of gridlayouts
                        # because they are more flexible to work with
                        button = Button(text=str(self.maze_board_mat[x/2][y/2]),
                                        background_disabled_normal='',
                                        disabled_color=[1, 1, 1, 1],
                                        background_normal='',
                                        background_color=[0, 0, 1, 0.65])

                        # Disable button after creation because background_colors and such
                        # would not save otherwise
                        button.disabled = True

                        # update maze_board children size
                        self.MAZE_BOARD_CHILDREN_SIZE += 1

                        # Add to the board
                        self.maze_board.add_widget(button)

                    # Creates wall
                    else:

                        # Creating buttons for the widgits inside of gridlayouts
                        # because they are more flexible to work with
                        button = Button(background_disabled_normal='',
                                        disabled_color=[0, 0, 0, 1],
                                        background_normal='',
                                        background_color=[1, 1, 1, 1],
                                        size_hint=[0.1, 1])

                        # Disable button after creation because background_colors and such
                        # would not save otherwise
                        button.disabled = True

                        # update maze_board children size
                        self.MAZE_BOARD_CHILDREN_SIZE += 1

                        # Add to board
                        self.maze_board.add_widget(button)

            # create the vertical walls
            else:
                for y in xrange(self.maze_board.cols):
                    # Creating buttons for the widgits inside of gridlayouts
                    # because they are more flexible to work with
                    button = Button(background_disabled_normal='',
                                    disabled_color=[0, 0, 0, 1],
                                    background_normal='',
                                    background_color=self.wall_color,
                                    size_hint=[0.1, 0.1])

                    # Disable button after creation because background_colors and such
                    # would not save otherwise
                    button.disabled = True

                    # update maze_board children size
                    self.MAZE_BOARD_CHILDREN_SIZE += 1

                    # Add to board
                    self.maze_board.add_widget(button)

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

        #pos = self._get_child_index(3, 3)
        #print(self.maze_board.children[pos].pos)
        #print(self.MAZE_BOARD_ROWS)

        # Looping through rows and columns of the ROWS and COLS of the board
        # NOT the maze_board ROWS and COLS. maze_board rows and cols include
        # walls itself which we are trying to fill
        for row in xrange(self.ROWS):
            for col in xrange(self.COLS):

                # This is the current position for the maze_board GridLayout
                current_pos = self._get_child_index(row, col)

                # NORTH wall condition
                # If exists, find the adjusted position
                # then fill it with self.wall_color otherwise self.path_color
                # This applies for the rest of the wall conditions
                if self.mat_walls[row][col][Direction.NORTH.value] == 1:
                    adjusted_pos = current_pos + self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].background_color = self.wall_color
                else:
                    adjusted_pos = current_pos + self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].background_color = self.path_color

                # EAST wall condition
                if self.mat_walls[row][col][Direction.EAST.value] == 1:
                    adjusted_pos = current_pos - 1
                    self.maze_board.children[adjusted_pos].background_color = self.wall_color
                else:
                    adjusted_pos = current_pos - 1
                    self.maze_board.children[adjusted_pos].background_color = self.path_color

                # SOUTH wall condition
                if self.mat_walls[row][col][Direction.SOUTH.value] == 1:
                    adjusted_pos = current_pos - self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].background_color = self.wall_color
                else:
                    adjusted_pos = current_pos - self.MAZE_BOARD_COLS
                    self.maze_board.children[adjusted_pos].background_color = self.path_color

                # WEST wall condition
                if self.mat_walls[row][col][Direction.WEST.value] == 1:
                    adjusted_pos = current_pos + 1
                    self.maze_board.children[adjusted_pos].background_color = self.wall_color
                else:
                    adjusted_pos = current_pos + 1
                    self.maze_board.children[adjusted_pos].background_color = self.path_color

    def _get_child_index(self, row, col):
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
        real_pos = self.MAZE_BOARD_CHILDREN_SIZE - pos - 1
        return real_pos

    def _get_walk_length(self, dt):
        '''
        This function serves the purpose of getting the walk length from
        one square to the next. It is a callback because the GridLayout
        must be set up first before being able to properly calculate
        :param dt:
        :return:
        '''

        # Grab the two indices based on matrix rows and columns
        initial_index = self._get_child_index(self.INITIAL_ROW, self.INITIAL_COL)
        end_index = self._get_child_index(self.INITIAL_ROW + 1, self.INITIAL_COL)

        # Get the two y coordinates for those indices
        y1 = self.maze_board.children[initial_index].pos[1]
        y2 = self.maze_board.children[end_index].pos[1]

        # Calculate the walk_length
        self.walk_length = y1 - y2
        print(self.walk_length)

    def _place_character(self, dt):
        '''
        This callback serves the purpose of calculating the character's position
        and then placing the character there.
        :param dt:
        :return:
        '''

        # Get the index for initial position of where the position is
        # supposed to be
        index = self._get_child_index(self.INITIAL_ROW, self.INITIAL_COL)

        # Get the x,y size of the gridlayout square
        square_size = self.maze_board.children[index].size
        square_x = square_size[0] / 2
        square_y = square_size[1] / 2

        # Get the x,y size of character (represented as an image)
        char_size = self.character.size
        char_x = char_size[0] / 2
        char_y = char_size[1] / 2

        # Get the x,y position of the initial square
        initial_pos = self.maze_board.children[index].pos
        initial_x = initial_pos[0]
        initial_y = initial_pos[1]

        # Calculate the x,y position to place the character
        x = initial_x + square_x - char_x
        y = initial_y + square_y - char_y

        # Place character
        self.character.pos = [x, y]


class MazeApp(App):

    def build(self):
        root = RootWidgit()
        Clock.schedule_once(root._get_walk_length, 1)
        Clock.schedule_once(root._place_character, 1)
        return root

if __name__ == "__main__":
    MazeApp().run()