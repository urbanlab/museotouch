#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from museolib.widgets.tutorials.tutoitem import TutoItem

class TutoWidget(Widget):
	text = StringProperty('')
	def __init__(self,img_path):
		super(TutoWidget,self).__init__()
		self.text = "Essayez de réduire la taille\n de cette fiche de moitié"
		item = TutoItem(img_path)
		item.do_translation = False
		item.do_rotation = False
		item.remove_widget(item.children[0])
		item.bind(scale=self.get_scale)
		self.add_widget(item)
		item.anim_item(self.pos)
	def get_scale(self,instance,scale):
		if scale < 0.5:
			self.parent.parent.text="Bravo !"
		elif scale >0.5:
			self.parent.parent.text = "Essayez de réduire la taille\n de cette fiche de moitié"



