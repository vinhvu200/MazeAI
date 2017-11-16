from kivy.uix.button import Button


class TDSquare(Button):

    def __init__(self, **kwargs):

        super(TDSquare, self).__init__(**kwargs)

        # Set up for button
        self.background_disabled_normal = ''
        self.disabled_color = [1, 1, 1, 1]
        self.background_normal = ''
        self.background_color = [0, 0, 1, 0.65]

        # Directions go [NORTH, EAST, SOUTH, WEST]
        self.directions = [0, 0, 0, 0]

        # Set reward and text
        self.reward = 0
        self.text = 'R: {}\n' \
                    'N: {} - E: {}\n' \
                    'S: {} - W: {}'.format(str(self.reward), str(self.directions[0]),
                                   str(self.directions[1]), str(self.directions[2]),
                                   str(self.directions[3]))

    def update(self):
        '''
        This function updates the Button text with the reward,
        and direction values
        :return: None
        '''
        self.text = 'R: {}\n' \
                    'N: {} - E: {}\n' \
                    'S: {} - W: {}'.format(str(self.reward), str(self.directions[0]),
                                           str(self.directions[1]), str(self.directions[2]),
                                           str(self.directions[3]))

    def set_reward(self, reward):
        '''
        Sets the reward. Want to call update after it is set.
        :param reward: integer or float
        :return: None
        '''
        self.reward = reward
