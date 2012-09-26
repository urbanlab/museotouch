from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.factory import Factory

from pdb import set_trace as rrr
from datetime import datetime, timedelta, time
from time import strptime

class MySlider(FloatLayout):
    value_min = NumericProperty(0.0)
    value_max = NumericProperty(1.0)
    value_range = ReferenceListProperty(value_min, value_max)
    rognage = NumericProperty(0.0)
    decalage = NumericProperty(0.0)

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
        value = (touch.x - self.decalage - self.x) / self.width
        value = min(1.0, max(0.0, value))
        value_center = (self.value_min + self.value_max) / 2.
        name = 'value_min' if value < value_center else 'value_max'
        setattr(self, name, value)


class CalendarSlider(FloatLayout):
    slider_h = ObjectProperty(None)
    slider_d = ObjectProperty(None)

    days_min = ObjectProperty(datetime(2000,1,1))
    days_max = ObjectProperty(datetime(2000,1,1))
    hours_min = ObjectProperty(datetime(2000,1,1))
    hours_max = ObjectProperty(datetime(2000,1,1))
    update = ReferenceListProperty(days_min, days_max, hours_min, hours_max)

    def __init__(self, **kwargs):
        super(CalendarSlider, self).__init__(**kwargs)

        if 'pos_type' in kwargs:
            self.pos_type = kwargs['pos_type']
        else:
            self.pos_type = 'horizontal'

        if 'display' in kwargs:
            if 'hours' not in kwargs['display']:
                self.remove_widget(self.slider_h)
                self.hours = False
            else:
                self.hours = True
            if 'days' not in kwargs['display']:
                self.remove_widget(self.slider_d)
                self.days = False
            else:
                self.days = True
        
        self.slider_h.bind(
            value_min=self.up_min_hours,
            value_max=self.up_max_hours)
        self.slider_d.bind(
            value_min=self.up_min_days,
            value_max=self.up_max_days)
        #self.bind(update=self.foo)

    def foo(self, *args):
        print '* calendar widget has been updated'

    def accepts(self, strdate):
        if len(strdate) == 0:
            return True
        if len(strdate) <= 4: # juste une annee
            date = datetime(year=int(strdate), month=7, day=1)
        else:
            date = datetime(*strptime(strdate, "%d/%m/%Y %H:%M:%S")[:6])

        if self.days_min.date() <= date.date() <= self.days_max.date():
            if self.hours_min.date() < self.hours_max.date():  # chevauchement sur 2 jours
                if self.hours_min.time() <= date.time() <= time(23, 59, 59) or time(0, 0, 0) <= date.time() <= self.hours_max.time():
                    return True 
            elif self.hours_min.time() <= date.time() <= self.hours_max.time():
                return True
        return False

    def up_min_hours(self, *args):
        d = self.hours_end - self.hours_begin
        s = d.seconds * self.slider_h.value_min
        d = self.hours_begin + timedelta(seconds=s)
        #print d.time()
        if d.time() != self.hours_min.time():
            self.hours_min = d

    def up_min_days(self, *args):
        d = self.days_end - self.days_begin
        s = (d.days * 86400 + d.seconds) * self.slider_d.value_min
        d = self.days_begin + timedelta(seconds=s)
        #print d.date()
        if d.date() != self.days_min.date():
            self.days_min = d

    def up_max_hours(self, *args):
        d = self.hours_end - self.hours_begin
        s = d.seconds * self.slider_h.value_max
        d = self.hours_begin + timedelta(seconds=s)
        #print d.time()
        if d.time() != self.hours_max.time():
            self.hours_max = d

    def up_max_days(self, *args):
        d = self.days_end - self.days_begin
        s = (d.days * 86400 + d.seconds) * self.slider_d.value_max
        d = self.days_begin + timedelta(seconds=s)
        #print d.date()
        if d.date() != self.days_max.date():
            self.days_max = d

    def adjust_slider(self, slider, rognage=0.0, decalage=0.0):
        if slider == 'hours':
            slider = self.slider_h
        elif slider == 'days':
            slider = self.slider_d
        # adjustment must me in ['rognage', 'decalage']
        slider.rognage, slider.decalage = rognage, decalage

    def __setattr__(self, attr, value):
        if attr == 'days_begin': self.days_min = value
        if attr == 'days_end': self.days_max = value
        if attr == 'hours_begin': self.hours_min = value
        if attr == 'hours_end': self.hours_max = value
        super(CalendarSlider, self).__setattr__(attr, value)

Factory.register('MySlider', cls=MySlider)

class SizeSliderApp(App):
    def build(self):
        print 'build slider app'
        mul = CalendarSlider(pos_hint={'top': 0.75}, display=['hours', 'days'])
        mul.days_begin = datetime(2012, 8, 15, 0, 0, 0)
        mul.days_end = datetime(2012, 8, 18, 23, 59, 59)
        mul.hours_begin = datetime(2000, 1, 1, 13, 30, 0)
        mul.hours_end = datetime(2000, 1, 2, 5, 0, 0)
        mul.adjust_slider('hours', 196, 8) # rognage de 196 pixels, decalage vers la droite de 8
        mul.adjust_slider('days', 460, -21)

        return mul

if __name__ == '__main__':
    Factory.register('MySlider', cls=MySlider)
    SizeSliderApp().run()

