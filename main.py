from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
import util
import time

from kivy.config import Config
Config.set('graphics', 'width', '1250')
Config.set('graphics', 'height', '600')

class RootWidgit(FloatLayout):

    def __init__(self):
        super(RootWidgit, self).__init__()

        self.mat_walls, self.ROWS, self.COLS = util.build_matrix_walls()

    def testing(self):

        grid1 = self.ids.maze1
        grid1.rows = 3
        grid1.add_widget(Label(text='a'))
        grid1.add_widget(Label(text='b'))
        grid1.add_widget(Label(text='c'))
        grid1.add_widget(Label(text='d'))
        grid1.add_widget(Label(text='d'))
        grid1.add_widget(Label(text='d'))
        grid1.add_widget(Label(text='d'))

class MazeApp(App):

    def build(self):
        return RootWidgit()

if __name__ == "__main__":
    MazeApp().run()