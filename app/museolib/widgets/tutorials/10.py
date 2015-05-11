#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from museolib.widgets.tutorials.tutoitem import TutoItem


class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = ""
		self.item = TutoItem('validation.png')
		self.item.pos=(Window.width*0.7,Window.height*0.2)
		self.item.rotation=0
		self.item.opacity=1
		self.item.remove_widget(self.item.children[0])
		with self.item.canvas.before:
			Color(0.1,0.1,0.1,1)
			Rectangle(size=self.item.size)
			self.canvas_label=Label(text="Touchez moi !",font_size=50,pos=(self.item.width*0.4,self.item.height*0.4))
		self.add_widget(self.item)
		self.item.bind(contacts=self.update_text)

	def update_text(self,instance,pos):
		self.canvas_label.text=str(self.item.contacts)
