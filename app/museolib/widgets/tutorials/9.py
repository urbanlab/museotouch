#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from kivy.core.window import Window
from museolib.gesture_board import GestureBoard
from kivy.graphics import Color,Rectangle
from museolib.widgets.tutorials.tutoitem import TutoItem
from kivy.lang import Builder
from kivy.animation import Animation
from random import randint,random
class TutoWidget(Widget):
	def __init__(self,img_path=None):
		super(TutoWidget,self).__init__()
		self.load_kv()
		self.text = "Tracez un carré ci-dessous"
		self.add_board()
		self.colors={'1':(1,random(),random(),0.8),'2':(random(),1,random(),0.8),'3':(random(),random(),1,0.8)}
		self.add_items(6)
	def load_kv(self):
		self.loaded = False
		for f in Builder.files:
			if 'valid.kv' in f:
				self.loaded=True
				break
			else :
				self.loaded=False
		if self.loaded == False:
			Builder.load_file('tuto_assets/valid.kv')
	def add_board(self):
		w = Widget(pos=(Window.width*0.45,0),size=(Window.width*0.5,Window.height*0.9))
		self.board = GestureBoard()
		self.board.pos=w.pos
		self.board.size=w.size
		self.board.bind(exists=self.update_text)
		w.add_widget(self.board)
		self.add_widget(w)
	def add_items(self,number):
		for item in range(0,number):
			rand = randint(1,3)
			t=TutoItem('tuto_assets/texture.png')
			t.l.opacity=0
			t.remove_widget(t.children[0])
			t.size=(256,256)
			t.size_hint=(None,None)
			Animation(pos=(randint(0,Window.width*0.5),randint(0,int(Window.height*0.8))),rotation=randint(0,360),d=0.2).start(t)
			with t.canvas.before:
				c=Color()
				c.rgba=self.colors[str(rand)]
				Rectangle(size=t.size)
			t.item['taille']=rand
			self.add_widget(t)
	def update_text(self,instance,exists):
		self.parent.parent.text='Bravo !\nMaintenant, rassemblez quelques carrés\nde la même couleur puis essayez de valider'



