from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, \
        StringProperty, ListProperty, BooleanProperty, ObjectProperty, NumericProperty
from kivy.vector import Vector

from kivy.uix.scatter import Scatter
import math
from kivy.animation import Animation

class Keyword(Scatter):
    selected = BooleanProperty(False)

    group = ObjectProperty(None)

    text = StringProperty(None)

    id = StringProperty(None)

    total = NumericProperty(0)

    rank = NumericProperty(0)

    controler = ObjectProperty(None)

    delta = NumericProperty(1.0)

    def __init__(self, **kwargs): 
        super(Keyword, self).__init__(**kwargs)
        self.key_label.bind(texture_size=self.setup_size)
        self.controler.bind(global_angle = self.update_position)

    def setup_size(self, instance, size):
        self.size = size
        self.update_position(None, 0)
        # self.key_label.text = str(self.rank)

    def update_position(self, instance, global_angle):
        step = (2*math.pi) / self.total
        angle = self.rank * step + math.radians(global_angle)

        self.center_x = (self.parent.outer_radius/2 - self.height) * -math.cos(angle) + self.parent.width/2
        self.center_y = (self.parent.outer_radius/2 - self.height) * math.sin(angle)  + self.parent.height/2
        self.rotation = math.degrees(-angle) + 90

        min_angle = 60
        max_angle = 120
        gap = (max_angle - min_angle)/2
        
        if min_angle + 20 < self.rotation < max_angle - 20:
            self.controler.current_rank = self.rank

        if min_angle < self.rotation < max_angle:
            self.delta =  round(abs(self.rotation - 90) / gap, 1)
        else:
            self.delta = 1.0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True
        return super(Keyword, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and self.collide_point(*touch.pos) and not self.rotation == 90:
            # print self.total, self.rank, self.total - self.rank
            a = math.degrees((2*math.pi / self.total) * (self.total - self.rank)) ##### BUG : self.total - self.rank
            if abs(a) > 180:
                sign = math.copysign(1, a) * -1
                a = (360 - abs(a)) * sign
            # print self.controler.global_angle, a
            # print (abs(self.controler.global_angle) + abs(a)) /2 
            self.controler.go_to_angle(a)
            touch.ungrab(self)
            return True

class CircularKeywordPicker(FloatLayout):
    inner_radius = NumericProperty(320)
    outer_radius = NumericProperty(400)
    # value_range = ReferenceListProperty(value_min, value_max)

    keywords = ListProperty([])
    alphabetical_sort = BooleanProperty(True)

    global_angle = NumericProperty(0)
    current_rank = NumericProperty(0)
    total = NumericProperty(0)

    active_ids = ObjectProperty([])

    def __init__(self, **kwargs):   
        super(CircularKeywordPicker, self).__init__(**kwargs)

    def on_keywords(self, instance, value):
        self.clear_widgets()
        for item in value:
            if item['group'].find('filtre') == -1:
                children = item['children']
                if self.alphabetical_sort:
                    children.sort(key=lambda x: x['name'])
                self.total = len(children)
                rank = 0
                for child in children:
                    key = Keyword(text = child['name'], id = child['id'], total=self.total, rank = rank, controler = self)
                    rank = rank + 1
                    self.add_widget(key)

    def on_global_angle(self, instance, value):
        if abs(self.global_angle) > 360: # bug aussi la : revoir comment faire plus d'un seul tour
            # print 'global angle reset ', self.global_angle
            if math.copysign(1,self.global_angle) > 0:
                self.global_angle = self.global_angle - 360
            else:
                self.global_angle = self.global_angle + 360
            # print 'new global angle ', self.global_angle

    def in_circle(self, x, y):
        dist = (self.outer_radius/2 - x) ** 2 + (self.outer_radius/2 - y) ** 2
        dist2 = (self.inner_radius/2 - (x - (self.outer_radius - self.inner_radius)/2)) ** 2 + (self.inner_radius/2 - (y - (self.outer_radius - self.inner_radius)/2)) ** 2
        
        in_outer_radius = dist < ((self.outer_radius/2) ** 2)
        in_inner_radius =  dist2 < ((self.inner_radius/2) ** 2)

        if in_outer_radius and not in_inner_radius:
            return True
        else:
            return False

    def on_touch_down(self, touch):
        ret = super(CircularKeywordPicker, self).on_touch_down(touch)
        if not self.collide_point(*touch.pos):
            return

        if self.in_circle(touch.x, touch.y):
            touch.grab(self)
            return True
        return ret

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.update_from_touch(touch)
            # return True

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            if touch.dy != 0:
                self.correct_position()
                touch.ungrab(self)
            return True

    def filter_items(self, *largs):
        current_child = self.children[self.total - self.current_rank -1]
        self.active_ids = current_child.id

    def go_to_angle(self, a, d = .5):
        Animation.stop_all(self)
        anim = Animation(global_angle = a, duration= d, t='linear')
        anim.on_complete = self.filter_items
        anim.start(self)


    previous_rank = NumericProperty(0)
    def correct_position(self):
        a = math.degrees((2*math.pi / self.total) * (self.total - self.current_rank))
        self.go_to_angle(a = a, d = .2)
        self.previous_rank = self.current_rank


    def update_from_touch(self, touch):
        delta = 0
        if abs(touch.dy) >= abs(touch.dx) :
            delta = touch.dy

        a  = Vector(touch.px - 150, touch.py -150 ).angle((touch.x-150, touch.y-150))
        # self.global_angle = math.degrees(Vector(touch.ox, touch.oy).angle(Vector(touch.x, touch.y)))
        self.global_angle =  a + self.global_angle

        # print touch.ox-150, touch.oy-150, touch.x-150, touch.y-150
        # print self.global_angle
        # if touch.x < self.width/2 :
        #     self.global_angle = self.global_angle + (touch.dx + touch.dy)/2
        # else:    
        #     self.global_angle = self.global_angle - (touch.dx + touch.dy)/2
            # if delta > 0:
            #     self.global_angle = self.global_angle + delta
            # else:
            #     self.global_angle = self.global_angle - delta




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

