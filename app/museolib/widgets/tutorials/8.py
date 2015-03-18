#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget

class TutoWidget(Widget):
	def __init__(self,img_path=None):
		super(TutoWidget,self).__init__()
		self.text = "Utilisez ce widget des deux manières"