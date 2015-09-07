from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ReferenceListProperty, NumericProperty,StringProperty


class SizeSlider(FloatLayout):
    value_min = NumericProperty(0.0)
    value_max = NumericProperty(1.0)
    value_range = ReferenceListProperty(value_min, value_max)
    conditional_value = NumericProperty(1.0)
    name = StringProperty('sizeslider')
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        self.update_from_touch(touch)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            touch.ungrab(self)
            return True

    def update_from_touch(self, touch):
        value = (touch.x - self.x) / self.width
        # if value <= self.conditional_value:
        value = min(1.0, max(0.0, value))
        value_center = (self.value_min + self.value_max) / 2.
        name = 'value_min' if value < value_center else 'value_max'
        # if self.conditional_value < 1.0:
        #     name='value_max'
        setattr(self, name, value)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(SizeSlider(
        size_hint=(None, None),
        pos_hint={'right': 1, 'center_y': 0.5},
        size=(300, 600)
    ))

