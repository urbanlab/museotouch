#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from museolib.widgets.tutorials.tutoitem import TutoItem

class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Essayez de doubler la taille\n de cette fiche"
		self.item = TutoItem(img_path)
		self.item.do_translation = False
		self.item.do_rotation = False
		self.item.remove_widget(self.item.children[0])
		self.item.bind(scale=self.get_scale)
		self.add_widget(self.item)
		self.item.anim_item(self.pos)
		with self.item.canvas.before:
			Color(0.1,0.1,0.1,1)
			Rectangle(size=self.item.size)
			self.canvas_label=Label(text="Bravo !",font_size=50,pos=(self.item.width*0.4,self.item.height*0.4))
	def get_scale(self,instance,scale):
		if scale > 2:
			op = 0
		elif scale < 2:
			op = 1
		Animation(opacity=op,d=0.2).start(self.item.l)