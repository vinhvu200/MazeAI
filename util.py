from enum import Enum

def build_matrix_walls():
    '''
    This function serves the purpose of generating a 3D matrix
    which tells where the walls are indicated for each square on
    the board. The walls are NORTH, EAST, SOUTH, and WEST respectively.

    EXAMPLE: [1, 0, 0, 1]
    - This tells us there is a wall NORTH and SOUTH of the square

    :return: matrix_walls, rows, cols
    '''

    # Open maze file
    maze_file = open('maze1.txt', 'r')

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
