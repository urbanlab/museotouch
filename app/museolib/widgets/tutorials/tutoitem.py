#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import NumericProperty,ListProperty
from kivy.animation import Animation
from kivy.core.window import Window
class TutoItem(Scatter):
	contacts=NumericProperty(0)
	color=ListProperty([0,0,1])
	def __init__(self,img):
		super(TutoItem,self).__init__()
		self.size_hint=(None,None)
		self.l = Image(source=img,size_hint=(None,None),size=(512,512))
		self.b = Button(pos=(512 - 70, 512 - 70),size=(64, 64),background_down='museolib/data/next_down.png',background_normal='museolib/data/next.png',opacity=0)
		self.b.bind(on_release=self.flip)
		self.size=self.l.size
		self.add_widget(self.l)
		self.add_widget(self.b)
		self.flipped=False
		self.contacts=0
		self.item={}
	def anim_item(self, pos,rot = 20):
		self.pos=(Window.width,0)
		self.rotation=359
		anim=Animation(opacity=1,pos=(Window.width*0.65,Window.height*0.1),rotation=rot,d=0.5)
		anim.start(self)

	def on_touch_down(self, touch): 
		ret = super(TutoItem, self).on_touch_down(touch)
		if not ret:
		    return
		self.contacts+=1
		Animation(opacity=1., t='out_quad', d=0.3).start(self.b)
		return True

	def on_touch_up(self, touch): 
		if not touch.grab_current == self:
			return False
		ret = super(TutoItem, self).on_touch_up(touch)
		self.contacts-=1
		Animation(opacity=0, t='out_quad', d=0.3).start(self.b)
		self.check_valid(touch.pos)

	def flip(self,arg):
		if self.flipped == False:
			Animation(size=(self.width*0.2,self.height*0.2),pos=(self.l.x,self.height-(self.l.height*0.2)),d=0.5).start(self.l)
			self.flipped=True
		else:
			Animation(size=(self.width,self.height),pos=(0,0),d=0.5).start(self.l)
			self.flipped=False
		Animation(opacity=0, t='out_quad', d=0.3).start(self.b)	
	def on_scale(self,instance,scale):
		return scale
	def check_valid(self,touch):
		if self.parent :
			try:
				wid = self.parent.board.children[0]
				if wid.collide_point(*touch):
					Animation(color=(0,0,1,0.9),d=0.3).start(wid)
					nbr_valid = len(wid.ids['my_layout'].children)
					available_pos = self.check_availability(wid)
					if available_pos != None :
						temp = self
						temp.do_scale=False
						temp.do_translation = False
						temp.do_rotation=False
						temp.pos=(0,0)
						self.parent.remove_widget(self)
						wid.ids['my_layout'].add_widget(temp)
						anim=Animation(pos=wid.children_pos[str(available_pos)]['pos'], rotation=0,d=0.2,scale=wid.width*0.00190)
						anim.start(self)
			except:
				pass
	def check_availability(self,validation_widget):
		for pos in range(0,4):
			if validation_widget.children_pos[str(pos)]['available'] == True:
				validation_widget.children_pos[str(pos)]['available'] = False
				return pos
		return None