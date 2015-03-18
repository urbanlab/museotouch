#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from museolib.widgets.tutorials.tutoitem import TutoItem

class TutoWidget(Widget):
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Essayez de retourner cette fiche"
		self.item = TutoItem(img_path)
		self.add_widget(self.item)
		self.item.anim_item(self.pos)
		with self.item.canvas.before:
			Color(0.1,0.1,0.1,1)
			Rectangle(size=self.item.size)
			self.canvas_label=Label(text="Bravo !",font_size=50,pos=(self.item.width*0.4,self.item.height*0.4))