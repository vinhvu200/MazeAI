def get_matrix_wall(maze_file, rows, cols):
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

    return mat_walls

def get_end_points(maze_file):

    # Gather how many end points
    line = maze_file.readline()
    end_points = int(line)

    end_rows = []
    end_cols = []
    end_rewards = []

    # iterate through all end points to get
    # end rows, cols, and rewards.
    # Index of all three list will tell you about the end point
    while end_points != 0:
        line = maze_file.readline()
        line_by_space = line.split(' ')
        end_rows.append(int(line_by_space[0]))
        end_cols.append(int(line_by_space[1]))
        end_rewards.append(float(line_by_space[2].rstrip()))
        end_points -= 1

    return end_rows, end_cols, end_rewards


def parse_maze_txt_file(maze_file):
    # Open maze file
    maze_file = open(maze_file, 'r')

    # Read and split lines by space
    line = maze_file.readline()
    line_by_space = line.split(' ')

    # First two values indicate rows and cols respectively
    rows = int(line_by_space[0])
    cols = int(line_by_space[1])

    # Read and split lines by space
    line = maze_file.readline()
    line_by_space = line.split(' ')

    # Initial rows and cols
    initial_row = int(line_by_space[0])
    initial_col = int(line_by_space[1])

    # Get the ending rows, cols, and rewards
    end_rows, end_cols, end_rewards = get_end_points(maze_file)

    # Get the 3D wall matrix
    mat_walls = get_matrix_wall(maze_file, rows, cols)

    # return matrix, rows, cols
    return mat_walls, rows, cols, initial_row, initial_col, end_rows, \
                end_cols, end_rewards


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)