from kivy.uix.image import Image

class Sprite(Image):

    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.size_hint = [None, None]