from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import mainthread

from Model.BorderLabel import BorderLabel
from Model.Direction import Direction

from kivy.config import Config
Config.set('graphics', 'width', '1300')
Config.set('graphics', 'height', '600')


class RootWidgit(FloatLayout):

    maze1 = 'maze1.txt'
    wall_color = [.627, .321, .094, 1]
    path_color = [0, 0, 1, 1]

    def __init__(self):
        super(RootWidgit, self).__init__()

        # Get the maze_board and value_board GridLayout from .kv file
        self.maze_board = self.ids.maze_board
        self.value_board = self.ids.value_board

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

        # Populate boards with the current matrices and
        # return maze_board_children_size
        self.MAZE_BOARD_CHILDREN_SIZE = self._populate_board()

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

    def _populate_board(self):
        '''
        This function serves the purpose of populating the GridLayouts set up in
        the .kv file.
        - The value_board GridLayout is straight forward since it just takes
        the values from the matrix and plugs it in.
        - The maze_board is a bit different because we have to adjust it to
        add walls in-between

        :return: None
        '''

        # setting columns for the GridLayout
        self.maze_board.cols = self.MAZE_BOARD_COLS
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
                button.disabled=True

                # Add button to our value_board gridlayout
                self.value_board.add_widget(button)

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

                    # Add to board
                    self.maze_board.add_widget(button)

        maze_board_children_size = 0
        for _ in self.maze_board.children:
            maze_board_children_size += 1

        return maze_board_children_size

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

class MazeApp(App):

    def build(self):
        return RootWidgit()

if __name__ == "__main__":
    MazeApp().run()