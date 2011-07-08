from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, \
        StringProperty
from kivy.vector import Vector


class CircularSlider(FloatLayout):
    value_min = NumericProperty(0.0)
    value_max = NumericProperty(1.0)
    inner_radius = NumericProperty(210)
    outer_radius = NumericProperty(230)
    angle_min = NumericProperty(0.)
    angle_max = NumericProperty(180.)
    value_range = ReferenceListProperty(value_min, value_max)
    text_min = StringProperty('')
    text_max = StringProperty('')

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
        x, y = touch.pos

        # convert angle to value between 0-1
        angle = Vector(x - self.right, y - self.center_y).angle((1, 0))
        value = None
        if 90 <= angle <= 180:
            value = 0.5 + (1 - ((angle - 90) / 90.)) * 0.5
        elif -180 <= angle <= -90:
            value = ((angle + 90) / 90.) * -0.5
        else:
            return

        # detect which name to use
        value_center = (self.value_min + self.value_max) / 2.
        name = 'value_min' if value < value_center else 'value_max'

        # calculate distance from the right/center
        dist = Vector(x, y).distance(Vector(self.right, self.center_y))

        # factor
        inner_radius = self.inner_radius
        factor_distance = 50.
        factor = 1. + max((dist - inner_radius) / factor_distance, 0)

        # get the diff
        if 'value' in touch.ud:
            name = touch.ud.name
            oldvalue = touch.ud.value
            diff = (value - oldvalue) / factor
            touch.ud.value = value
            oldvalue = touch.ud.initvalue
            touch.ud.initvalue = value = oldvalue + diff
        else:
            touch.ud.initvalue = value
            touch.ud.value = value
            touch.ud.name = name

        # set the value !
        value = max(min(value, 1), 0)
        if name == 'value_min':
            if value > self.value_max:
                return
        elif value < self.value_min:
            return
        setattr(self, name, value)



if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(CircularSlider(
        size_hint=(None, None),
        pos_hint={'right': 1, 'center_y': 0.5},
        size=(300, 600)
    ))

