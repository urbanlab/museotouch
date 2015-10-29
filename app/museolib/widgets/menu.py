#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.app import App
from museolib.widgets.splashscreen import SplashScreen
from os.path import join

class Menu(FloatLayout):
	def __init__(self):
		super(Menu,self).__init__()
		self.app = App.get_running_app()
		self.button = Button(background_normal="menu.png",background_down="menu_down.png",size_hint=(None,None),\
						size=(Window.width*0.032,Window.width*0.032),pos_hint={'top':1,'right':1},on_press=self.show_menu,on_release=self.clear_menu)
		self.add_widget(self.button)
		self.menu_items={'help':[[Window.width*0.064,0],'help.png','help_down.png',self.help],\
						'credits':[[Window.width*0.048,Window.width*0.048],'credits.png','credits_down.png',self.credits],\
						'exit':[[0,Window.width*0.064],'quit.png','quit_down.png',self.exit]}
	
	def show_menu(self,instance):
		# ensures that the menu is always on top
		parent = self.parent
		self.parent.remove_widget(self)
		parent.add_widget(self)
		self.parent.menu=self
		#---------------------------------------
		for item in self.menu_items.values():
			b = Button(background_normal=item[1],size_hint=(None,None),\
						background_down=item[2],size=(Window.width*0.032,Window.width*0.032),pos=self.button.pos,on_release=item[3])
			b.opacity=0
			self.add_widget(b)
			Animation(pos=[self.button.x-item[0][0],self.button.y-item[0][1]],opacity=1,d=0.5,t='out_bounce').start(b)
	def clear_menu(self,instance):
		for child in self.children[:-1]:
			Animation(pos=self.button.pos,d=0.3,t='out_quad').start(child)
			self.remove_widget(child)
	def help(self,instance):
		self.selector.screen_saver(None)

	def credits(self,instance):
		print "credits"

	def exit(self,instance):
		try:
			self.app.reset(go_to_menu=True)
		except:
			pass


