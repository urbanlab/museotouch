#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
from kivy.graphics import Ellipse,Color
from museolib.widgets.tutorials.tutoitem import TutoItem
from random import randint

class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Déplacez la fiche sur le point rouge"
		self.item = TutoItem(img_path)
		self.item.remove_widget(self.item.children[0])
		self.item.do_scale=False
		self.add_widget(self.item)
		self.item.anim_item(self.pos)
		self.dot = RedDot()
		self.add_widget(self.dot)
		self.item.bind(pos=self.check_collision)

	def check_collision(self,instance,pos):
		if self.item.collide_widget(self.dot):
			self.dot.pos=self.dot.random_pos()

class RedDot(Scatter):
	def __init__(self):
		super(RedDot,self).__init__()
		self.pos=self.random_pos()
		self.size_hint=(None,None)
		with self.canvas.before:
			Color(1,0,0,1)
			Ellipse(size=(100,100))

	def random_pos(self):
		return (randint(0,Window.width*0.8),randint(0,Window.height*0.8))