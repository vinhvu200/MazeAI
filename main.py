import random
import util
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics import Color
from Model.Enum.Direction import Direction
from Model.Enum.Speed import Speed
from Model.Enum.State import State
from Model.Path import Path
from Model.Sprite import Sprite
from Model.TDIndicator import TDIndicator
from Model.TDSquare import TDSquare

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '500')
from kivy.core.window import Window


class RootWidgit(FloatLayout):

    maze1 = 'Maze/maze1.txt'
    maze2 = 'Maze/maze2.txt'

    ROWS = 0
    COLS = 0
    END_ROWS = []
    END_COLS = []

    END_COLOURS = [Color(0, 1, 0),
                  Color(1, 1, 0),
                  Color(0, 0, 1),
                  Color(1, 1, 0)]

    character = None
    td_children_flag = False
    mat_walls = [[[]]]

    # Maze Board GridLayout Parameters
    maze_board_mat = [[]]
    MAZE_BOARD_ROWS = 0
    MAZE_BOARD_COLS = 0
    maze_board_children_size = 0

    # RL parameters
    episodes = 0
    epsilon = 0.0
    discount = 0.9
    _lambda = 0.9
    learning_rate = 0.6
    move_cost = 0.05

    def __init__(self, **kwargs):
        super(RootWidgit, self).__init__(**kwargs)

        # Get the maze_board and value_board GridLayout from .kv file
        self.maze_board = self.ids.maze_board
        self.value_board = self.ids.value_board

        # Get Buttons from .kv file
        self.learn_toggle_button = self.ids.learn_toggle_button
        self.reset_button = self.ids.reset_button
        self.speed_button = self.ids.speed_button
        self.maze_one_button = self.ids.maze_one_button
        self.maze_two_button = self.ids.maze_two_button
        self.epsilon_increase_button = self.ids.epsilon_increase_button
        self.epsilon_decrease_button = self.ids.epsilon_decrease_button
        self.learning_rate_increase_button = self.ids.learning_rate_increase_button
        self.learning_rate_decrease_button = self.ids.learning_rate_decrease_button
        self.lambda_increase_button = self.ids.lambda_increase_button
        self.lambda_decrease_button = self.ids.lambda_decrease_button
        self.discount_increase_button = self.ids.discount_increase_button
        self.discount_decrease_button = self.ids.discount_decrease_button

        # Get Labels from .kv file
        self.episode_label = self.ids.episode_label
        self.epsilon_label = self.ids.epsilon_label
        self.learning_rate_label = self.ids.learning_rate_label
        self.lambda_label = self.ids.lambda_label
        self.discount_label = self.ids.discount_label

        # Set progress label text
        self.episode_label.text = str(self.episodes)
        self.epsilon_label.text = str(self.epsilon)
        self.learning_rate_label.text = str(self.learning_rate)
        self.lambda_label.text = str(self._lambda)
        self.discount_label.text = str(self.discount)
        self.current_maze = self.maze1

        # Pass in the maze .txt file to set up
        self._setup_maze(self.current_maze)

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
        if self.td_children_flag is False:
            self._add_TDSquare_children()
        self.td_children_flag = True

        # Set up the keyboard and bind it
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Bind Buttons from .kv file
        self.learn_toggle_button.bind(on_press=self._learn_toggle)
        self.reset_button.bind(on_press=self._reset)
        self.speed_button.bind(on_press=self._toggle_speed)
        self.maze_one_button.bind(on_press=self._set_maze_one)
        self.maze_two_button.bind(on_press=self._set_maze_two)
        self.epsilon_increase_button.bind(on_press=self._increase_epsilon)
        self.epsilon_decrease_button.bind(on_press=self._decrease_epsilon)
        self.learning_rate_increase_button.bind(on_press=self._increase_learning_rate)
        self.learning_rate_decrease_button.bind(on_press=self._decrease_learning_rate)
        self.lambda_increase_button.bind(on_press=self._increase_lambda)
        self.lambda_decrease_button.bind(on_press=self._decrease_lambda)
        self.discount_increase_button.bind(on_press=self._increase_discount)
        self.discount_decrease_button.bind(on_press=self._decrease_discount)

    def learn_q(self, dt):
        '''
        - This function should be continuously call for the character to slowly learn the maze.
        It is scheduled again in self._end_animation binding.
        - If the character made it to the end, shuffle it around to another square
        :param dt:
        :return: None
        '''

        # Termination state: When character made it to the end.
        # Randomly place character onto new square, increment episodes
        # and increment epsilon
        if self._check_termination_square(self.character.current_row,
                                          self.character.current_col) is True:
            self._reset_character()

        # Otherwise, have it learn the maze
        else:
            # Get child_index to obtain the td_square from the value_board
            current_td_square = self._get_td_square(self.character.current_row,
                                                    self.character.current_col)

            # action_index is the index to be used while
            # best_action_index is the "best" move possible
            action_index, best_action_index = self._determine_action(current_td_square)

            # SPECIAL CASE
            # If character is in the initial position, it cannot move upward
            # otherwise it will cause an error
            if self.character.current_row == self.INITIAL_ROW and \
                self.character.current_col == self.INITIAL_COL and \
                action_index == Direction.NORTH.value:

                while action_index == Direction.NORTH.value:
                    action_index = random.randint(0, 3)

            # Choose appropriate animation based on index
            # IMPORTANT: After this is called, the character will
            # have updated its rows and columns
            valid_flag = self._animate(action_index)

            # Get the new updated td_square
            new_td_square = self._get_td_square(self.character.current_row,
                                                self.character.current_col)

            # Calculate updates for the current_td_square
            self._calculate_update_q(current_td_square, new_td_square, action_index, valid_flag)

            # Update the image and color
            self._color_trace()

    def learn_q_lambda(self, dt):
        '''
        Have character learn through Q-learn-lambda with
        backward view eligibility trace
        :param dt:
        :return:
        '''

        # Termination state: When character made it to the end.
        # Randomly place character onto new square, increment episodes
        # and increment epsilon
        if self._check_termination_square(self.character.current_row,
                                          self.character.current_col) is True:
            self._reset_character()

        else:
            # Get child_index to obtain the td_square from the value_board
            current_td_square = self._get_td_square(self.character.current_row,
                                                    self.character.current_col)

            # action_index is the index to be used while
            # best_action_index is the "best" move possible
            action_index, best_action_index = self._determine_action(current_td_square)

            # SPECIAL CASE
            # If character is in the initial position, it cannot move upward
            # otherwise it will cause an error
            if self.character.current_row == self.INITIAL_ROW and \
                            self.character.current_col == self.INITIAL_COL and \
                            action_index == Direction.NORTH.value:

                while action_index == Direction.NORTH.value:
                    action_index = random.randint(0, 3)

            # Choose appropriate animation based on index
            # IMPORTANT: After this is called, the character will
            # have already updated its rows and columns
            valid_flag = self._animate(action_index)

            # Get the new updated td_square
            new_td_square = self._get_td_square(self.character.current_row,
                                                self.character.current_col)

            # Calculate the q_value (valid_flag determines whether
            # the AI hit the wall or not)
            q_val = self._calculate_q_val(current_td_square, new_td_square, action_index, valid_flag)

            # Increase eligibility trace
            current_td_square.eligibility_trace[action_index] += 1

            # Update values in accordance to Q-lambda
            self._calculate_update_q_lambda(q_val, action_index, best_action_index)

            # Update the image and color
            self._color_trace()

    def _add_TDSquare_children(self):
        '''
        This function adds an Image widget to each button to represent arrows of
        where the AI will move to if they land on that square. It also adds an
        indicator to show how strong the decision is. It constantly changes
        as it is being updated.
        :return:
        '''

        # Add image to each of the td_squares of the value_board
        for td_square in self.value_board.children:

            # Create td_indicator to be added into children of value_board
            td_indicator = TDIndicator(x=td_square.x, y=td_square.y,
                                       size=td_square.size)

            # The image source will show arrow of where it will move next
            image = Image(x=td_square.x, y=td_square.y,
                          size=td_square.size, opacity=0)

            # Add the two widgets
            td_square.add_widget(td_indicator)
            td_square.add_widget(image)

        # Remove td_indicator and images if it is a termination square
        for x in xrange(len(self.END_REWARDS)):

            # Clear all its children
            td_square = self._get_td_square(self.END_ROWS[x],
                                            self.END_COLS[x])
            td_square.clear_widgets()

            # Set the text color and size
            td_square.disabled_color = [0, 0, 0, 1]
            td_square.halign = 'center'
            td_square.font_size = '25sp'

            # Change background of td_square based on whether it is
            # positive or negative
            if self.END_REWARDS[x] > 0:
                td_square.text = '+{}'.format(self.END_REWARDS[x])
                td_square.background_color = [0, 1, 0, .75]
                end_colour = self.END_COLOURS[x].rgb
                end_colour.append(0.75)
                td_square.background_color = end_colour
            else:
                td_square.text = '{}'.format(self.END_REWARDS[x])
                td_square.background_color = [1, 0, 0, .75]

    def _assign_rewards(self):
        '''
        - This function assigns rewards and colors of the termination square
        - Assign a high negative Q-value NORTH of the entrance so that the
            AI won't move off the map
        :return:
        '''

        for x in range(len(self.END_REWARDS)):

            # Assign reward and color to termination square
            td_square = self._get_td_square(self.END_ROWS[x], self.END_COLS[x])
            td_square.reward = self.END_REWARDS[x]

            if td_square.reward > 0:
                td_square.colour = self.END_COLOURS[x]

        # Change value direction of value of initial square
        # to negative so that it can't move up
        td_square = self._get_td_square(self.INITIAL_ROW, self.INITIAL_COL)
        td_square.direction_values[Direction.NORTH.value] = -100

        for row in range(self.ROWS):
            for col in range(self.COLS):
                valid_flag_north = self._valid_move(row, col, Direction.NORTH)
                valid_flag_east = self._valid_move(row, col, Direction.EAST)
                valid_flag_south = self._valid_move(row, col, Direction.SOUTH)
                valid_flag_west = self._valid_move(row, col, Direction.WEST)

                td_square = self._get_td_square(row, col)

                if valid_flag_north is False:
                    td_square.direction_values[Direction.NORTH.value] = -100

                if valid_flag_east is False:
                    td_square.direction_values[Direction.EAST.value] = -100

                if valid_flag_south is False:
                    td_square.direction_values[Direction.SOUTH.value] = -100

                if valid_flag_west is False:
                    td_square.direction_values[Direction.WEST.value] = -100

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

    def _calculate_q_val(self, current_td_square, new_td_square, action_index, valid_flag):
        '''
        This function calculates the Q_value.

        :param current_td_square: TDSquare
        :param new_td_square:  TDSquare
        :param action_index: integer, chosen action
        :param valid_flag: boolean, determines whether AI hit a wall or not
        :return:
        '''

        # Current td_square value of the "best" move grabbed from the current_max_index
        current_val = current_td_square.direction_values[action_index]

        # new td_square reward
        reward = new_td_square.reward

        # Find the max_value of the direction_values and its index of new_td_square
        new_max_val = max(new_td_square.direction_values)

        # Equation
        q_val = self.learning_rate * (reward + self.discount*new_max_val - current_val - self.move_cost)

        return q_val

    def _calculate_update_q(self, current_td_square, new_td_square, index, valid_flag):
        '''
        - Using Q-learning, the character updates its current td_square direction_values
        accordingly so that the next move can be chosen.
        - Valid flag used to increase penalty when bumping walls
        :param current_td_square: TDSquare
        :param new_td_square: TDSquare
        :param current_max_index: integer
        :return:
        '''

        # Current td_square value of the "best" move grabbed from the current_max_index
        current_val = current_td_square.direction_values[index]

        # new td_square reward
        reward = new_td_square.reward

        # Find the max_value of the direction_values and its index of new_td_square
        new_max_val = max(new_td_square.direction_values)

        # Q-learning equation
        current_td_square.direction_values[index] += \
            self.learning_rate * (reward + self.discount * new_max_val - current_val - self.move_cost)

    def _calculate_update_q_lambda(self, q_val, action_index, best_index):
        '''
        This function upates all the td_square in the value_board following
        Q-lambda learning.
        :param q_val: float
        :param action_index: int
        :param best_index: int
        :return:
        '''

        # Check all td_squares in value board
        for td_square in self.value_board.children:

            # Look at each direction of the td_square
            for direction in Direction:

                # Grab the eligibility trace for specific direction
                elig_trace_val = td_square.eligibility_trace[direction.value]

                # adjust_q_val accordingly and add to the direction q_val
                adjust_q_val = self.learning_rate * q_val * elig_trace_val
                td_square.direction_values[direction.value] += adjust_q_val

                # If selected action is "best" action, then decay it
                if action_index == best_index:
                    adjust_elig_trace = self.discount * self._lambda * elig_trace_val
                    td_square.eligibility_trace[direction.value] = adjust_elig_trace

                # If selected action is not "best" action, set it to 0
                else:
                    td_square.eligibility_trace[direction.value] = 0


    def _change_position(self, row, col, current_direction):
        '''
        This function changes the row or column based on the direction
        it is trying to go.
        :param row: int
        :param col: int
        :param current_direction_index: Direction (enum)
        :return: row, col (int, int)
        '''

        if current_direction is Direction.NORTH:
            return row-1, col

        if current_direction is Direction.EAST:
            return row, col+1

        if current_direction is Direction.SOUTH:
            return row+1, col

        if current_direction is Direction.WEST:
            return row, col-1

        return row, col

    def _check_termination_square(self, row, col):
        '''
        Check the row and column passed in to see if it lands on
        a terminating square
        :param row: int
        :param col: int
        :return:
        '''

        for x in xrange(len(self.END_ROWS)):

            if row == self.END_ROWS[x] and col == self.END_COLS[x]:
                    return True

        return False

    def _color_trace(self):
        '''
        This function iterates through all the td_squares
        and set its color based on where the arrows will
        take it.
        :return:
        '''

        for row in range(self.ROWS):
            for col in range(self.COLS):

                # Trace each td_square to find the termination color
                color = self._trace(row, col)

                # Get and set color of current td_square
                td_square = self._get_td_square(row, col)
                td_square.colour = color
                td_square.set_TDIndicator_color(color)

                # Update the td_square to show the changes
                td_square.update()

    def _decrease_discount(self, dt):
        if self.discount > 0.11:
            self.discount -= 0.1
        else:
            self.discount = 0.0
        self.discount_label.text = str(self.discount)

    def _decrease_epsilon(self, dt):
        if self.epsilon > 0.051:
            self.epsilon -= 0.05
        else:
            self.epsilon = 0.0
        self.epsilon_label.text = str(self.epsilon)

    def _decrease_lambda(self, dt):
        if self._lambda > 0.11:
            self._lambda -= 0.1
        else:
            self._lambda = 0.0
        self.lambda_label.text = str(self._lambda)

    def _decrease_learning_rate(self, dt):
        if self.learning_rate > 0.11:
            self.learning_rate -= 0.1
        else:
            self.learning_rate = 0.0
        self.learning_rate_label.text = str(self.learning_rate)

    def _determine_action(self, current_td_square):
        '''
        This function uses epsilon greedy to choose its next move.
        The action_index is the move chosen while best_action_index
        is the "best" move at the moment
        :param current_td_square: the td_square the character is currently on
        :return:
        '''

        # Generate random number to determine epsilon greedy
        rand_num = random.uniform(0, 1)

        # Case where we take random move
        if rand_num < self.epsilon:
            action_index = random.randint(0, 3)
        # Case where we take "best" move
        else:
            max_val = max(current_td_square.direction_values)
            action_index = current_td_square.direction_values.index(max_val)

        # Max_index holds the "best" move
        max_val = max(current_td_square.direction_values)
        best_action_index = current_td_square.direction_values.index(max_val)

        # return indices
        return action_index, best_action_index

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

        # Continue learning if character's state is LEARNING
        if self.character.state is State.LEARNING:
            self.learn_q_lambda(None)

    def _get_best_direction(self, row, col):
        '''
        This function gets the best direction_index and returns it.
        Best direction_index is the one with highest Q-value
        :param row:
        :param col:
        :return:
        '''

        td_square = self._get_td_square(row, col)
        max_val = max(td_square.direction_values)
        index  = td_square.direction_values.index(max_val)

        if index == Direction.NORTH.value:
            return Direction.NORTH
        if index == Direction.EAST.value:
            return Direction.EAST
        if index == Direction.SOUTH.value:
            return Direction.SOUTH
        if index == Direction.WEST.value:
            return Direction.WEST

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

    def _get_td_square(self, row, col):
        '''
        Given a row and column, this will return the correct
        td_square from value board to be used
        :param row: int
        :param col: int
        :return: TDSquare
        '''

        child_index = self._get_child_index_value_board(row, col)
        return self.value_board.children[child_index]

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

    def _handle_keyboard_action(self, keycode):
        '''
        This function handles certain keys that user may press
        :param keycode:
        :return:
        '''

        # Make sure the actions are only completed if desired keys
        # are pressed
        animate_flag = False

        # This boolean checks if the AI bumped into a wall or not
        valid_move = False

        # The decision the AI will make
        action_index = 0

        # Conditions to determine which direction to move character
        # Three options for validity of move: True, False, None
        # True: There are no walls; therefore, you can walk through
        # False: There is a wall; animate "bumping" into wall
        # None: Character is now out of bound
        # NORTH CONDITION
        if keycode[1] == 'w':

            if self.character.current_row == self.INITIAL_ROW and \
                            self.character.current_col == self.INITIAL_COL:
                return False, False, False

            animate_flag = True
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.NORTH)
            action_index = Direction.NORTH.value
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.NORTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.NORTH)
        # WEST
        elif keycode[1] == 'a':
            animate_flag = True
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.WEST)
            action_index = Direction.WEST.value
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.WEST)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.WEST)
        # SOUTH
        elif keycode[1] == 's':
            animate_flag = True
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.SOUTH)
            action_index = Direction.SOUTH.value
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.SOUTH)
            if valid_move is False:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.SOUTH)
        # EAST
        elif keycode[1] == 'd':
            animate_flag = True
            valid_move = self._valid_move(self.character.current_row, self.character.current_col,
                                          Direction.EAST)
            action_index = Direction.EAST.value
            if valid_move:
                # Get animation for walking
                self.animate = self.character.get_walk_animation(Direction.EAST)
            else:
                # Get animation for wall_bump
                self.animate = self.character.get_bump_wall_animation(Direction.EAST)

        return animate_flag, valid_move, action_index

    def _increase_discount(self, dt):
        if self.discount < 0.99:
            self.discount += 0.1
        self.discount_label.text = str(self.discount)

    def _increase_epsilon(self, dt):
        if self.epsilon < 0.99:
            self.epsilon += 0.05
        self.epsilon_label.text = str(self.epsilon)

    def _increase_lambda(self, dt):
        if self._lambda < 0.99:
            self._lambda += 0.1
        self.lambda_label.text = str(self._lambda)

    def _increase_learning_rate(self, dt):
        if self.learning_rate < 0.99:
            self.learning_rate += 0.1
        self.learning_rate_label.text = str(self.learning_rate)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _learn_toggle(self, dt):
        '''
        This callback is toggles between having the AI learn
        and stopping it so that the user can manually move
        :param dt:
        :return:
        '''

        if self.character.state == State.LEARNING:

            # Change states and bg color
            self.character.state = State.MANUAL
            self.learn_toggle_button.background_color = [1, 1, 1, 1]

        elif self.character.state == State.MANUAL:

            # Change states and bg color
            self.character.state = State.LEARNING
            self.learn_toggle_button.background_color = [0, 0, 1, 1]

            # Start Learning
            self.learn_q_lambda(None)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        This function serves the purpose of handling keyboard events
        to move the character based on the keys: w, a, s, d.
        '''

        # AI's current row/col before moving
        curr_row = self.character.current_row
        curr_col = self.character.current_col

        # If AI is learning, make sure it won't be interrupted
        if self.character.state is State.LEARNING:
            return True

        # handles keyboard action and receive variables to update keyboard
        animate_flag, valid_move, action_index = self._handle_keyboard_action(keycode)

        # Only complete these commands if any of the desired keys are pressed
        if animate_flag is True:
            
            # Bind the animation
            self.animate.bind(on_complete=self._end_animation)

            # Start animation
            self.animate.start(self.character)

            # Unbind keyboard to stop action in middle of animation
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)

            # Update the value_board accordingly
            self._update_value_board(valid_move, curr_row, curr_col, action_index)

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def _opposite_directions(self, direction_1, direction_2):
        '''
        Function takes two direction index and tells you if
        they are opposite of each other
        :param direction_1: Direction (enum)
        :param direction_2: Direction (enum)
        :return: boolean
        '''

        if direction_1 is Direction.NORTH and \
           direction_2 is Direction.SOUTH:
            return True

        if direction_1 is Direction.EAST and \
           direction_2 is Direction.WEST:
            return True

        if direction_1 is Direction.SOUTH and \
           direction_2 is Direction.NORTH:
            return True

        if direction_1 is Direction.WEST and \
           direction_2 is Direction.EAST:
            return True

        return False

    def _place_character(self):
        '''
        This callback serves the purpose of calculating the character's position
        and then placing the character there.
        :param dt:
        :return:
        '''

        # Get index of character
        row = self.character.current_row
        col = self.character.current_col
        index = self._get_child_index_maze_board(row, col)

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

        # Set maze_board's children size back to 0
        self.maze_board_children_size = 0

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

    def _reset(self, dt):
        '''
        This callback resets the current maze to its initial position

        :param dt:
        :return: None
        '''

        # Reset episodes
        self.episodes = 0
        self.episode_label.text = str(self.episodes)

        # Unbind keyboard
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)

        # Unbind Buttons from .kv file
        self.learn_toggle_button.unbind(on_press=self._learn_toggle)
        self.reset_button.unbind(on_press=self._reset)
        self.speed_button.unbind(on_press=self._toggle_speed)
        self.maze_one_button.unbind(on_press=self._set_maze_one)
        self.maze_two_button.unbind(on_press=self._set_maze_two)

        # Set Default colors for buttons
        self.learn_toggle_button.background_color = [1, 1, 1, 1]

        # Set default speed
        self.speed_button.text = 'Speed: 1'

        # Tells the callback_setup that the children widgets
        # have not been added yet (These child widgets are
        # the arrow Images)
        self.td_children_flag = False

        # Clear the GridLayout of its childrens
        self.value_board.clear_widgets()
        self.maze_board.clear_widgets()

        # Remove character
        self.remove_widget(self.character)

        # Recreate character with the saved states
        self.character = Sprite(current_row=self.INITIAL_ROW,
                                current_col=self.INITIAL_COL)

        # Set up maze
        self._setup_maze(self.current_maze)

    def _reset_character(self):
        '''
        This function places the character in a completely new area
        to continue learning the maze
        :return:
        '''

        # Reset eligibility trace
        for td_square in self.value_board.children:
            td_square.reset_eligibility_trace()

        # Increment episodes
        self.episodes += 1

        # Display updates
        self.episode_label.text = str(self.episodes)

        # Save current state
        state = self.character.state
        speed = self.character.speed

        # Remove character
        self.remove_widget(self.character)

        # if self.current_maze is self.maze2:
        #     row = self.INITIAL_ROW
        #     col = self.INITIAL_COL
        # else:
        #     # Generate new placement for character
        #     row = random.randint(0, self.ROWS - 1)
        #     col = random.randint(0, self.COLS - 1)
        #
        #     # Generate new placement for character
        #     while self._check_termination_square(row, col) is True:
        #         row = random.randint(0, self.ROWS - 1)
        #         col = random.randint(0, self.COLS - 1)

        row = self.INITIAL_ROW
        col = self.INITIAL_COL

        self.character = Sprite(current_row=row,
                                current_col=col,
                                speed=speed,
                                state=state)

        # Set up callback and start continue learning
        self.callback_setup(None)

        # If the AI is learning, let it continue learning
        if self.character.state is State.LEARNING:
            self.learn_q_lambda(None)

    def _set_maze_one(self, dt):
        self.current_maze = self.maze1
        self._reset(None)

    def _set_maze_two(self, dt):
        self.current_maze = self.maze2
        self._reset(None)

    def _setup_maze(self, maze):
        '''
        This function sets up the maze according to the .txt file
        passed in.

        :param maze: .txt file defining the maze
        :return:
        '''

        # Parse out the maze .txt file to get relevant information
        self.mat_walls, self.ROWS, self.COLS, self.INITIAL_ROW, self.INITIAL_COL, \
            self.END_ROWS, self.END_COLS, self.END_REWARDS = util.parse_maze_txt_file(maze)

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

        # Assign rewards to the appropriate td_squares
        self._assign_rewards()

        if self.character is None:
            self.character = Sprite(current_row=self.INITIAL_ROW,
                                    current_col=self.INITIAL_COL)

        # Do the callback setup in 1 second, when the boards have finished
        Clock.schedule_once(self.callback_setup, 1)

    def _toggle_speed(self, dt):
        '''
        Toggle speed in order
        NORMAL -> FAST -> HYPER -> NORMAL...
        :param dt:
        :return:
        '''

        if self.character.speed is Speed.NORMAL:
            # self.speed_button.text = 'Speed:\nFast'
            self.speed_button.text = 'Speed: 2'
            self.character.set_speed_fast()
            self.character.speed = Speed.FAST

        elif self.character.speed is Speed.FAST:
            # self.speed_button.text = 'Speed:\nHyper'
            self.speed_button.text = 'Speed: 3'
            self.character.set_speed_hyper()
            self.character.speed = Speed.HYPER

        elif self.character.speed is Speed.HYPER:
            # self.speed_button.text = 'Speed:\nNormal'
            self.speed_button.text = 'Speed: 1'
            self.character.set_speed_normal()
            self.character.speed = Speed.NORMAL

    def _trace(self, originial_row, original_col):
        '''
        - Given a row and column, this function finds associates it
        to the correct td_square and then follows it until it
        finds a terminating square. It then returns the terminating
        square's color.
        - If it does not find a terminating square, it will return
        the default white color
        :param originial_row:
        :param original_col:
        :return: Color(rgb)
        '''

        # Keep track of the original row and col
        row = originial_row
        col = original_col

        # Find the best direction
        current_direction = self._get_best_direction(row, col)

        # Check if the current square is a terminating square
        termination_flag = self._check_termination_square(row, col)

        # Check if the direction it is moving in is valid
        valid_move_flag = self._valid_move(row, col, current_direction)

        # Update the row and col while keeping track of last_direction
        # Continue following same steps as above
        # BREAK CONDITIONS:
        #   - if the move from current square is invalid
        #   - if it is on a termination flag
        #   - if the current_direction and last_direction are opposite
        while valid_move_flag is True and termination_flag is False:

            row, col = self._change_position(row, col, current_direction)
            last_direction = current_direction

            current_direction = self._get_best_direction(row, col)
            termination_flag = self._check_termination_square(row, col)
            valid_move_flag = self._valid_move(row, col, current_direction)

            if self._opposite_directions(current_direction, last_direction):
                break

        # Default white color
        color = Color(1, 1, 1)

        # Get the termination square_color if it lands on it
        if termination_flag is True:
            td_square = self._get_td_square(row, col)
            color = td_square.colour

        # return color
        return color

    def _update_value_board(self, valid_flag, current_row, current_col, action_index):
        '''
        This function updates the value board when the AI is being moved
        manually according to Q-lambda

        :param valid_flag: boolean
        :param current_row: int, AI's row he just moved from
        :param current_col: int, AI's col he just moved from
        :param action_index: int, which direction he will move in
        :return:
        '''

        # Get current td_square
        current_td_square = self._get_td_square(current_row, current_col)

        # Get new td_square
        new_td_square = self._get_td_square(self.character.current_row,
                                            self.character.current_col)

        # Get the best action index for that square
        _, best_action_index = self._determine_action(current_td_square)

        # Calculate the q_value (valid_flag determines whether
        # the AI hit the wall or not)
        q_val = self._calculate_q_val(current_td_square, new_td_square, action_index, valid_flag)

        # Increase eligibility trace
        current_td_square.eligibility_trace[action_index] += 1

        # Update values in accordance to Q-lambda
        self._calculate_update_q_lambda(q_val, action_index, action_index)

        # Trace correct color and then update
        self._color_trace()

        # If character is in a terminating square, then reset its position
        if self._check_termination_square(self.character.current_row,
                                          self.character.current_col) is True:
            self._reset_character()

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
        return root


if __name__ == "__main__":
    MazeApp().run()