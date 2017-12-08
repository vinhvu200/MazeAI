from kivy.uix.button import Button
from kivy.graphics import Color


class TDSquare(Button):

    def __init__(self, **kwargs):
        '''
        NOTE: Children[0] is a Kivy Image
              Children[1] is a TDIndicator Model
        :param kwargs:
        '''

        super(TDSquare, self).__init__(**kwargs)

        # Background images to show the most likely direction
        arrow_north = 'Images/arrow_north.png'
        arrow_east = 'Images/arrow_east.png'
        arrow_south = 'Images/arrow_south.png'
        arrow_west = 'Images/arrow_west.png'
        self.background_images = [arrow_north, arrow_east, arrow_south, arrow_west]

        # Set up for button
        self.background_disabled_normal = ''
        self.disabled_color = [1, 1, 1, 1]
        self.background_normal = ''
        self.background_color = [0.862, 0.862, 0.862, 1]

        # direction_values go [NORTH, EAST, SOUTH, WEST]
        self.direction_values = [0, 0, 0, 0]

        # Eligibility_trace go [NORTH, EAST, SOUTH, WEST]
        self.eligibility_trace = [0, 0, 0, 0]

        # Set reward and text
        self.reward = 0

        # Set default rgb color
        self.colour = Color(1, 1, 1)


        # self.text = 'N: {}\n' \
        #             'E: {}\n' \
        #             'S: {}\n' \
        #             'W: {}'.format(str(round(self.direction_values[0], 2)),
        #                            str(round(self.direction_values[1], 2)),
        #                            str(round(self.direction_values[2], 2)),
        #                            str(round(self.direction_values[3], 2)))

    def update(self):
        '''
        This function updates the Button image with the reward,
        and direction values
        :return: None
        '''
        # self.disabled_color = [1, 0, 0, 1]
        # self.text = 'N: {}\n' \
        #             'E: {}\n' \
        #             'S: {}\n' \
        #             'W: {}'.format(str(round(self.direction_values[0], 2)),
        #                            str(round(self.direction_values[1], 2)),
        #                            str(round(self.direction_values[2], 2)),
        #                            str(round(self.direction_values[3], 2)))

        if len(self.children) > 0:
            if self.children[0].opacity == 0:
                self.children[0].opacity = 1

            max_val = max(self.direction_values)
            max_index = self.direction_values.index(max_val)

            self.children[0].source = self.background_images[max_index]
            self.children[1].set_strength(max_val * 4)
            self.children[1].color = self.colour

            if self.colour.rgb != [1.0, 1.0, 1.0]:
                self.children[1].draw()

    def set_TDIndicator_color(self, color):
        self.colour = color

    def set_reward(self, reward):
        '''
        Sets the reward. Want to call update after it is set.
        :param reward: integer or float
        :return: None
        '''
        self.reward = reward

    def reset_eligibility_trace(self):
        self.eligibility_trace = [0, 0, 0, 0]