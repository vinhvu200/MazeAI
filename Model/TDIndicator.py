from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color


class TDIndicator(Widget):

    def __init__(self, **kwargs):
        super(TDIndicator, self).__init__(**kwargs)
        #self.color = Color(0, 1, 0, 0.65)
        self.color = Color(0, 1, 0)
        #self.rgb_color = [0, 1, 0, 0.65]
        self.strength = 0.0

    def draw(self):
        '''
        This function determines how big the indicator circle will be
        according to its strength and then draws the circle to be in
        the middle of the TDSquare
        :return:
        '''

        self.canvas.clear()
        start_opacity = 0.2
        count = 3

        self._draw(self.parent.size, self.parent.pos, self.strength,
                   start_opacity, count)

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
        elif highest_val < 0.11:
            self.strength = 0.15
        elif highest_val < 0.33:
            self.strength = 0.25
        elif highest_val < 0.44:
            self.strength = 0.35
        elif highest_val < 0.55:
            self.strength = 0.45
        elif highest_val < 0.66:
            self.strength = 0.55
        elif highest_val < 0.77:
            self.strength = 0.65
        elif highest_val < 0.88:
            self.strength = 0.75
        else:
            self.strength = 0.85

    def _draw(self, parent_size, parent_pos, strength, opacity, count):

        if count == 0:
            return

        if strength < 0:
            strength = 0

        # Get the adjusted distance between parent x,y and child x,y with
        # the child size be affected by the strength as well
        adjust_dist_x = parent_size[0] - self.size[0] * strength
        adjust_dist_y = parent_size[1] - self.size[1] * strength

        # Divide those distance by two to have the proper distance to adjust
        adjust_dist_x /= 2
        adjust_dist_y /= 2

        # Add the adjusted distance to the parent position
        pos_x = parent_pos[0] + adjust_dist_x
        pos_y = parent_pos[1] + adjust_dist_y

        # Store position as a list
        pos = [pos_x, pos_y]

        # The indicator size is based on the strength set
        size_x = self.size[0] * strength
        size_y = self.size[1] * strength
        size = [size_x, size_y]

        # Create the ring Instruction Group
        ring = InstructionGroup()
        # ring.add(Color(0, 1, 0, opacity))

        color = Color(self.color.r, self.color.g,
                       self.color.b, opacity)
        ring.add(color)
        ring.add(Ellipse(pos=pos, size=size))
        self.canvas.add(ring)

        # Create new values to recurse
        self._draw(size, pos, strength - 0.2, opacity + 0.2, count - 1)