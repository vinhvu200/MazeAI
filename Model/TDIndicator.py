from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse


class TDIndicator(Widget):

    def __init__(self, **kwargs):
        super(TDIndicator, self).__init__(**kwargs)
        self.color = [0, 1, 0, 0.65]
        self.strength = 0

    def draw(self):
        '''
        This function determines how big the indicator circle will be
        according to its strength and then draws the circle to be in
        the middle of the TDSquare
        :return:
        '''

        # Get the adjusted distance between parent x,y and child x,y with
        # the child size be affected by the strength as well
        adjust_dist_x = self.parent.size[0] - self.size[0] * self.strength
        adjust_dist_y = self.parent.size[1] - self.size[1] * self.strength

        # Divide those distance by two to have the proper distance to adjust
        adjust_dist_x /= 2
        adjust_dist_y /= 2

        # Add the adjusted distance to the parent position
        pos_x = self.parent.pos[0] + adjust_dist_x
        pos_y = self.parent.pos[1] + adjust_dist_y

        # Store the position as a list
        pos = [pos_x, pos_y]

        # The indicator size is based on the strength set
        size_x = self.size[0] * self.strength
        size_y = self.size[1] * self.strength
        size = [size_x, size_y]

        # Draw out the appropriate circle for the indicator
        with self.canvas:
            Color(0, 1, 0, 0.65)
            Ellipse(pos=pos, size=size)

    def set_strength(self, highest_val):
        '''
        Set the strength variable based on the best choice available
        from TDSquare
        :param highest_val: Float
        :return:
        '''

        # Check the highest value decision of that square
        # in order to determine the strength of the indicator
        if highest_val < 0.1:
            self.strength = 0
        elif highest_val < 0.2:
            self.strength = 0.1
        elif highest_val < 0.3:
            self.strength = 0.2
        elif highest_val < 0.4:
            self.strength = 0.3
        elif highest_val < 0.5:
            self.strength = 0.4
        elif highest_val < 0.6:
            self.strength = 0.5
        elif highest_val < 0.7:
            self.strength = 0.6
        elif highest_val < 0.8:
            self.strength = 0.7
        elif highest_val < 0.9:
            self.strength = 0.8
        elif highest_val < 1:
            self.strength = 0.9
        else:
            self.strength = 1