#!/usr/bin/env python
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line
from kivy.gesture import Gesture, GestureDatabase
from kivy.vector import Vector
from kivy.properties import NumericProperty,BooleanProperty
from museolib.my_gestures import gestures
from museolib.widgets.validation import Valid
from museolib.widgets.timeline import TimeLine

def simplegesture(name, point_list):
    """
    A simple helper function
    """
    g = Gesture()
    g.add_stroke(point_list)
    g.normalize()
    g.name = name
    return g
class GestureBoard(FloatLayout):
    """
    Our application main widget, derived from touchtracer example, use data
    constructed from touches to match symboles loaded from my_gestures.

    """
    edge_size = NumericProperty(0)
    exists=BooleanProperty(False)
    def __init__(self, *args, **kwargs):
        super(GestureBoard, self).__init__()
        self.gdb = GestureDatabase()
        self.first_touch=[]
        # add pre-recorded gestures to database
        for gest in gestures:
            self.gdb.add_gesture(gest)
    def on_touch_down(self, touch):
        super(GestureBoard,self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            if App.get_running_app().config.getboolean('museotouch','validation') == True:
                self.first_touch=touch.pos  
                # start collecting points in touch.ud
                # create a line to display the points
                userdata = touch.ud
                userdata['line'] = Line(points=(touch.x, touch.y))
                return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            super(GestureBoard,self).on_touch_move(touch)
            # store points of the touch movement
            try:
                touch.ud['line'].points += [touch.x, touch.y]
                return True
            except (KeyError) as e:
                pass

    def on_touch_up(self, touch):
        super(GestureBoard,self).on_touch_up(touch)
        # touch is over, display informations, and check if it matches some
        # known gesture.
        try :
            g = simplegesture(
                    '',
                    list(zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))
                    )
            # Next line prints the string corresponding to the gesture made
            # print self.gdb.gesture_to_str(g)
            self.edge_size = (self.stroke_length(list(zip(touch.ud['line'].points[::2], touch.ud['line'].points[1::2]))))/4 
            if self.edge_size < 150:
                self.edge_size=150
            if self.edge_size > 400:
                self.edge_size = 400               
        # gestures to my_gestures.py
        except :
            return

        # use database to find the more alike gesture, if any
        g2 = self.gdb.find(g, minscore=0.9)
        if g2:
            for index,gest in enumerate(gestures) :
                if (g2[1] == gest):
                    widget_type="validation"
                    if index in [0,1]:
                        gest_pos=[touch.x,touch.y-self.edge_size]
                    elif index in [2,3]:
                        gest_pos=[touch.x-self.edge_size,touch.y-self.edge_size]
                    elif index in [4,5]:
                        gest_pos=[touch.x-self.edge_size,touch.y]
                    elif index in [6,7]:
                        gest_pos=[touch.x,touch.y]
                    elif index in [7,8]:
                        gest_pos=[touch.x,touch.y]
                        widget_type="timeline"
                    self.create_and_add_widget(widget_type,gest_pos)
                    break
    def create_and_add_widget(self,widget_type,gest_pos):
        if widget_type =="validation":
            widget = Valid(pos=(0,0),size=[self.edge_size,self.edge_size],rotation=180,scale_min=0.5)
            anim=Animation(pos=gest_pos,d=.3,rotation=0,transition='out_sine')
        elif widget_type =="timeline" and self.exists == False:
            self.exists=True
            widget = TimeLine()
            widget.pos=(0,self.first_touch[1]-widget.height*0.5)
            anim=Animation(pos=(self.first_touch[0],self.first_touch[1]-widget.height*0.5),d=.3,transition='out_sine')
            pass
        else:
            return
        self.add_widget(widget)
        anim.start(widget)            
    def stroke_length(self,l):
        distance = 0
        for index, point in enumerate(l) :
            if index < len(l)-1:
                distance += Vector(point).distance(l[index+1])
        return distance