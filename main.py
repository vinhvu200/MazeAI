from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label

from Model.BorderLabel import BorderLabel

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
        self.BOARD_ROWS = self.ROWS * 2 - 1
        self.BOARD_COLS = self.COLS * 2 - 1

        # Initialize the 2D maze matrix where 1 will indicate where the user is
        self.maze_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]
        self.maze_board_mat[0][2] = 1

        # Initialize the 2D value matrix to perform reinforcement learning on
        self.value_board_mat = [[0 for _ in xrange(self.COLS)] for _ in xrange(self.ROWS)]

        self._populate_board()

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

        self.maze_board.cols = self.BOARD_COLS
        self.value_board.cols = self.COLS

        # populate value_board GridLayout
        for x in xrange(self.ROWS):
            for y in xrange(self.COLS):
                self.value_board.add_widget(Label(text=str(self.value_board_mat[x][y])))

        # populate maze_board GridLayout
        for x in xrange(self.BOARD_ROWS):

            if x % 2 == 0:
                # Handles horizontal wall widgits as well as the actual path
                for y in xrange(self.BOARD_COLS):

                    # Creates actual path
                    if y % 2 == 0:
                        self.maze_board.add_widget(Label(text='a'))
                    # Creates wall
                    else:
                        self.maze_board.add_widget(BorderLabel(size_hint=[0.1, 1]))
            else:
                for y in xrange(self.maze_board.cols):
                    self.maze_board.add_widget(BorderLabel(size_hint=[0.1, 0.1]))


class MazeApp(App):

    def build(self):
        return RootWidgit()

if __name__ == "__main__":
    MazeApp().run()