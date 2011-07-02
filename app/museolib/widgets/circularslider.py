from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.lang import Builder

Builder.load_string('''
#:import math math
<CircularSlider>:
    angle_min: self.value_min * 180
    angle_max: self.value_max * 180
    x_min: math.sin(math.radians(self.angle_min)) * self.outer_radius
    y_min: -math.cos(math.radians(self.angle_min)) * self.outer_radius
    x_max: math.sin(math.radians(self.angle_max)) * self.outer_radius
    y_max: -math.cos(math.radians(self.angle_max)) * self.outer_radius

    canvas:
        Color:
            rgb: 0.5490, 1, 1
        Ellipse:
            pos: self.right - self.outer_radius, self.center_y - self.outer_radius
            size: self.outer_radius * 2, self.outer_radius * 2
            angle_start: (root.angle_min + 180) % 360
            angle_end: (root.angle_max + 180) % 360
        Color:
            rgb: 0.5333, 0.5411, 0.5450
        Ellipse:
            pos: self.right - self.inner_radius, self.center_y - self.inner_radius
            size: self.inner_radius * 2, self.inner_radius * 2
        Color:
            rgb: 0, 0, 0
        Ellipse:
            pos: self.right - self.inner_radius + 50, self.center_y - self.inner_radius + 50
            size: (self.inner_radius - 50) * 2, (self.inner_radius - 50) * 2
        Color:
            rgb: 1, 1, 1
        Line:
            points: (self.right, self.center_y, self.right - self.x_min, self.center_y + self.y_min)
        Color:
            rgb: 1, 0, 0
        Line:
            points: (self.right, self.center_y, self.right - self.x_max, self.center_y + self.y_max)
    AnchorLayout:
        BoxLayout:
            size_hint: None, None
            size: (100, 100)
            orientation: 'vertical'
            Label:
                text: '%d' % root.angle_min
            Label:
                text: '%d' % root.angle_max
''')


class CircularSlider(Widget):
    value_min = NumericProperty(0.1)
    value_max = NumericProperty(0.9)
    inner_radius = NumericProperty(200)
    outer_radius = NumericProperty(220)
    angle_min = NumericProperty(0.)
    angle_max = NumericProperty(180.)
    x_min = NumericProperty(0)
    y_min = NumericProperty(0)
    x_max = NumericProperty(0)
    y_max = NumericProperty(0)
    value_range = ReferenceListProperty(value_min, value_max)

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

