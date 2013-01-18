from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, \
        StringProperty, ListProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.vector import Vector

from kivy.uix.scatter import Scatter
import math

class Keyword(Scatter):
    selected = BooleanProperty(False)

    group = ObjectProperty(None)

    text = StringProperty(None)

    id = StringProperty(None)

    total = NumericProperty(0)

    rank = NumericProperty(0)

    controler = ObjectProperty(None)

    def __init__(self, **kwargs): 
        super(Keyword, self).__init__(**kwargs)
        self.key_label.bind(texture_size=self.setup_size)
        self.controler.bind(global_angle = self.update_position)

    def setup_size(self, instance, size):
        self.size = size
        self.update_position(None, 0)

    def update_position(self, instance, global_angle):
        # self.size = size
        step = (2*math.pi) / self.total
        angle = self.rank * step + math.radians(global_angle)

        self.center_x = (self.parent.parent.outer_radius/2 - self.height) * -math.cos(angle) + self.parent.width/2
        self.center_y = (self.parent.parent.outer_radius/2 - self.height) * math.sin(angle)  + self.parent.height/2
        self.rotation = math.degrees(-angle) + 90


class CircularKeywordPicker(FloatLayout):
    # value_min = NumericProperty(0.0)
    # value_max = NumericProperty(1.0)
    inner_radius = NumericProperty(320)
    outer_radius = NumericProperty(400)
    # angle_min = NumericProperty(0.)
    # angle_max = NumericProperty(180.)
    # value_range = ReferenceListProperty(value_min, value_max)
    # text_min = StringProperty('')
    # text_max = StringProperty('')

    keywords = ListProperty([])
    alphabetical_sort = BooleanProperty(True)

    global_angle = NumericProperty(0)

    def __init__(self, **kwargs):   
        super(CircularKeywordPicker, self).__init__(**kwargs)

    def on_keywords(self, instance, value):
        self.clear_widgets()
        for item in value:
            if item['group'].find('filtre') == -1:

                self.group = group = Scatter(size_hint=(None,None), size = self.size, do_translation=False, do_scale=False)
                group.size= (self.outer_radius, self.outer_radius)
                group.pos_hint={'center_x':0.5, 'center_y':0.5}

                from kivy.graphics import Color, Rectangle

                self.add_widget(group)

                children = item['children']
                if self.alphabetical_sort:
                    children.sort(key=lambda x: x['name'])
                total = len(children)
                rank = 0
                for child in children:
                    key = Keyword(text = child['name'], id = child['id'], total=total, rank = rank, controler = self)
                    rank = rank + 1
                    # self.labels_container.add_widget(key)
                    # self.add_widget(key)
                    group.add_widget(key)


    def on_global_angle(self, instance, value):
        if abs(self.global_angle) >= 359:
            self.global_angle = 0

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        # self.update_from_touch(touch)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            # self.update_from_touch(touch)
            touch.ungrab(self)
            return True

    def update_from_touch(	self, touch):
        delta = 0
        if abs(touch.dy) >= abs(touch.dx) :
            delta = touch.dy
        else:
            delta = touch.dx 

        if delta > 0:
            self.global_angle = self.global_angle + 2
        else:
            self.global_angle = self.global_angle - 2

        # x, y = touch.pos

        # # convert angle to value between 0-1
        # angle = Vector(x - self.right, y - self.center_y).angle((1, 0))
        # value = None
        # if 90 <= angle <= 180:
        #     value = 0.5 + (1 - ((angle - 90) / 90.)) * 0.5
        # elif -180 <= angle <= -90:
        #     value = ((angle + 90) / 90.) * -0.5
        # else:
        #     return

        # # detect which name to use
        # value_center = (self.value_min + self.value_max) / 2.
        # name = 'value_min' if value < value_center else 'value_max'

        # # calculate distance from the right/center
        # dist = Vector(x, y).distance(Vector(self.right, self.center_y))

        # # factor
        # inner_radius = self.inner_radius
        # factor_distance = 50.
        # factor = 1. + max((dist - inner_radius) / factor_distance, 0)

        # # get the diff
        # if 'value' in touch.ud:
        #     name = touch.ud.name
        #     oldvalue = touch.ud.value
        #     diff = (value - oldvalue) / factor
        #     touch.ud.value = value
        #     oldvalue = touch.ud.initvalue
        #     touch.ud.initvalue = value = oldvalue + diff
        # else:
        #     touch.ud.initvalue = value
        #     touch.ud.value = value
        #     touch.ud.name = name

        # # set the value !
        # value = max(min(value, 1), 0)
        # if name == 'value_min':
        #     if value > self.value_max:
        #         return
        # elif value < self.value_min:
        #     return
        # setattr(self, name, value)

if __name__ == '__main__':
    from kivy.base import runTouchApp
    runTouchApp(CircularKeywordPicker(
        size_hint=(None, None),
        pos_hint={'right': 1, 'center_y': 0.5},
        size=(300, 600)
    ))

