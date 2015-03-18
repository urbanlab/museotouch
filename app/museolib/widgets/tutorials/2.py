#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior

class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Essayez de lancer une exposition"
		self.add_widget(FakeExpoSelector())

class FakeExpoSelector(BoxLayout):
	def __init__(self):
		super(FakeExpoSelector,self).__init__()
		self.orientation='horizontal'
		self.pos=(Window.width*0.6,Window.height*0.2)
		self.add_widget(FakeExpoItem(img='tuto_assets/expo1.jpg',color = (0.894, 0.886, 0.133,1),text='BRA'))
		self.add_widget(FakeExpoItem(img='tuto_assets/expo2.jpg',color = (0, 0.376, 0.666,1),text='VO !'))


class FakeExpoItem(ButtonBehavior,Scatter):
	def __init__(self,img,color,text):
		super(FakeExpoItem,self).__init__()
		self.do_scale=False
		self.do_rotation=False
		self.do_translation=False
		self.size_hint=(None,None)
		self.size=(310,310)
		self.l=Label(text=text,font_size=70,size=self.size,pos=self.pos)
		self.add_widget(self.l)
		self.image = Image(source=img,size=self.size)
		self.add_widget(self.image)
		self.color= color
		self.complete=False
		with self.canvas.before:
			Color(0, 0.376, 0.666,1)
			Rectangle(pos=self.pos,size=self.size)
	def on_press(self):    
		Animation.stop_all(self.image)
		anim = Animation(opacity=0, t='out_quad', d=0.5)
		anim.start(self.image)
		anim.on_complete = self.completed
	def on_release(self):
		if self.complete==False:
			Animation.cancel_all(self.image)
			Animation(opacity=1, t='out_quad', d=0.1).start(self.image)
	def completed(self,instance):
		if self.complete == False:
			self.complete=True
