import kivy
kivy.require('1.0.7-dev')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from museolib.widgets.circularslider import CircularSlider


class MuseotouchApp(App):

    def build(self):
        root = FloatLayout()
        slider = CircularSlider(pos_hint={'right': 1, 'center_y': '0.5'})
        root.add_widget(slider)
        return root

if __name__ in ('__main__', '__android__'):
    MuseotouchApp().run()
