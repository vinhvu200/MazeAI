from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import mainthread

from Model.BorderLabel import BorderLabel
from Model.Direction import Direction

from kivy.config import Config
Config.set('graphics', 'width', '1250')
Config.set('graphics', 'height', '600')


class RootWidgit(FloatLayout):

    maze1 = 'maze1.txt'

    def __init__(self):
        super(RootWidgit, self).__init__()

        # Get the maze_board and value_board GridLayout from .kv file
        self.maze_board = self.ids.maze_board
        self.value_board = self.ids.value_board

        # Generate the 3D matrix containing the walls along with ROWS
        # and COLS of the board
        self.mat_walls, self.ROWS, self.COLS = self._build_matrix_walls(self.maze1)

        # Readjust rows and columns to fit walls in between for the board rows
        self.BOARD_ROWS = self.ROWS * 2 + 1
        self.BOARD_COLS = self.COLS * 2 + 1

        # Initialize the 2D maze matrix where 1 will indicate where the user is
        self.maze_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]
        self.maze_board_mat[0][2] = 1

        # Initialize the 2D value matrix to perform reinforcement learning on
        self.value_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]

        # Populate boards with the current matrices
        self._populate_board()

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
        self.maze_board.cols = self.BOARD_COLS
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
                                background_color=[0, 0, 1, 1])
                
                # Disable button after creation because background_colors and such
                # would not save otherwise
                button.disabled=True

                # Add button to our value_board gridlayout
                self.value_board.add_widget(button)


        # populate maze_board GridLayout
        for x in xrange(self.BOARD_ROWS):

            # Creates the actual vertical path
            if x % 2 == 1:
                # Handles horizontal wall widgits as well as the actual path
                for y in xrange(self.BOARD_COLS):

                    # Creates actual path
                    if y % 2 == 1:
                        self.maze_board.add_widget(Label(text=str(self.maze_board_mat[x/2][y/2])))
                    # Creates wall
                    else:
                        self.maze_board.add_widget(BorderLabel(size_hint=[0.1, 1]))
            # create the vertical walls
            else:
                for y in xrange(self.maze_board.cols):
                    self.maze_board.add_widget(BorderLabel(size_hint=[0.1, 0.1]))

    @mainthread
    def _populate_walls(self):

        label = self.maze_board.children[9]

        print(type(label))
        label.canvas.before.clear()
        with label.canvas.before:
            Color(1, 0, 0, 1)
            Rectangle(pos=label.pos, size=label.size)

        #with self.canvas.before:
        #    Color(1, 1, 1, 0.25)
        #    Rectangle(pos=self.pos, size=self.size)

        print(label.pos)
        print(label.size)

        for x in xrange(self.ROWS):
            for y in xrange(self.COLS):
                if self.mat_walls[x][y][Direction.NORTH.value] == 1:
                    pass
                if self.mat_walls[x][y][Direction.EAST.value] == 1:
                    pass
                if self.mat_walls[x][y][Direction.SOUTH.value] == 1:
                    pass
                if self.mat_walls[x][y][Direction.WEST.value] == 1:
                    pass

class MazeApp(App):

    def build(self):
        return RootWidgit()

if __name__ == "__main__":
    MazeApp().run()