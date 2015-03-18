#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from museolib.widgets.tutorials.tutoitem import TutoItem

class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Faites effectuer un demi-tour\n à cette fiche"
		self.item = TutoItem(img_path)
		self.item.remove_widget(self.item.children[0])
		self.item.do_scale = False
		self.item.do_translation = False
		self.item.bind(rotation=self.get_rotation)
		self.add_widget(self.item)
		self.item.anim_item(self.pos,rot=359)
	def get_rotation(self,instance,rotation):
		if self.item.rotation > 170 and self.item.rotation < 190 :
			self.parent.parent.text="Bravo !"