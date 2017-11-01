from enum import Enum

def build_matrix_walls():
    maze_file = open('maze1.txt', 'r')
    line = maze_file.readline()
    line_by_space = line.split(' ')

    rows = line_by_space[0]
    cols = line_by_space[1]
    print(rows)
    print(cols)

    for x in range(int(rows)):
        for y in range(int(cols)):

            line = maze_file.readline()
            if line == '\n':
                line = maze_file.readline()

            # split line by space
            line_by_space = line.split(' ')

            direction = list()
            direction.append(int(line_by_space[0]))
            direction.append(int(line_by_space[1]))
            direction.append(int(line_by_space[2]))
            direction.append(int(line_by_space[3].rstrip()))

            print('{} {} - {}'.format(x, y, direction))
