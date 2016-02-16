from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.properties import ListProperty,StringProperty
from kivy.core.window import Window
from kivy.graphics import Rectangle,Color
from random import randint
from functools import partial

class TimeLine(Scatter):
	color = ListProperty([0,0,1,0.9])
	order_field=StringProperty('taille')
	def __init__(self,**kwargs):
		super(TimeLine,self).__init__(**kwargs)
		# self.item_components={}
		self.app = App.get_running_app()
		self.size_hint=(None,None)
		self.label = Label(text="Replacez les fiches dans l'ordre",font_size=20)
		self.add_widget(self.label)
		self.close_btn=Button(background_normal='quit.png',background_down='quit_down.png',size=(64,64))
		self.add_widget(self.close_btn)
		self.add_btn=Button(background_normal='add.png',background_down='add_down.png',size=(32,32))
		self.add_widget(self.add_btn)
		self.check_btn=Button(background_normal='check.png',background_down='check_down.png',size=(32,32))
		self.add_widget(self.check_btn)
		self.last_component_pos=(self.x+40,self.y+20)
		self.components=0
		self.do_scale=False

		with self.canvas.before:
			Color(0.5, 0.5, 0.5, 0.1)
			self.rect = Rectangle(size=self.size)
		self.add_components(3)
		# Buttons bindings
		self.close_btn.bind(on_release=self.close)
		self.add_btn.bind(on_release=partial(self.add_components,1))
		self.check_btn.bind(on_release=self.check)


	def add_components(self,number,instance=None):
		for num in range(0,number) :
			component = TimelineComponent()
			component.pos = (self.last_component_pos[0]-200,self.last_component_pos[1])
			Animation(pos=self.last_component_pos,d=0.2).start(component)
			self.add_widget(component)
			if self.components != 0:
				with self.canvas :
					Color(rgba=self.color)
					Rectangle(pos=(self.last_component_pos[0]-100,component.height*0.35),source='right_arrow.png')
			self.last_component_pos=(self.last_component_pos[0]+component.width + 100,self.last_component_pos[1])
			self.components+=1
			component.label.text=str(self.components)
			component.label.size=component.label.texture_size
			component.label.texture_update()
			component.label.pos=(-component.label.texture_size[0]*0.8,component.height*0.9)
			self.rect.size =self.size=[self.components*(component.width+100),component.height+60]
			self.label.pos=(self.width*0.45,self.height*0.75)
			self.label.text = "Replacez les fiches dans l'ordre ( Nombre actuel de fiches : %s )"%self.components
			self.close_btn.pos=(self.width-self.close_btn.width+5,self.height-self.close_btn.height+5)
			self.add_btn.pos=(self.width-self.add_btn.width-10,(self.height-self.add_btn.height)*0.5)
			self.check_btn.pos=(self.width-self.add_btn.width-10,10)

	def close(self,instance):
		item_list = [child for child in self.children if isinstance(child,TimelineComponent) and child.has_image]
		if item_list == [] and self.parent != None:
			self.clear_widgets()
			self.canvas.clear()
			self.components = 0
			self.parent.exists=False
			self.parent.remove_widget(self)
			self=None
			return
		for i in item_list:
			self.remove_item(i.layout.children[0])


	def check(self,instance):
		for child in self.children:
			if isinstance(child, TimelineComponent) and child.has_image==True:
				if str(child.layout.children[0].item['fields'][self.order_field]) == str(child.label.text) :
					child.color = (0,1,0,0.9)
				else :
					child.color = (1,0,0,0.9)
				child.anim_color(child.color)

	def remove_item(self,i):
		temp = i
		temp.do_scale=True
		temp.do_translation = True
		temp.do_rotation=True
		temp.pos=i.parent.parent.to_window(i.parent.parent.x,i.parent.parent.y)
		i.parent.parent.has_image=False
		i.parent.parent.anim_color()
		i.parent.remove_widget(i)
		for wid in self.parent.children :
			if isinstance(wid,FloatLayout):
				wid.add_widget(temp,0)
				break
		anim=Animation(pos=(randint(int(0.5*Window.width-300),int(0.5*Window.width+100)),randint(int(0.5*Window.height-300),int(0.5*Window.height+100))),rotation=randint(0,360),d=0.2,scale=0.5)
		anim.start(temp)
		try :
			self.app.db.items.append(i.item)
			self.app.valid_order_list.remove(i.item.id)
		except:
			pass

class TimelineComponent(Scatter):
	color = ListProperty([0,0,1,0.9])
	def __init__(self,**kwargs):
		super(TimelineComponent,self).__init__(**kwargs)
		self.size_hint=(None,None)
		self.size=(200,200)
		self.layout = FloatLayout(pos=self.pos,size=self.size)
		self.layout.size_hint=(None,None)
		self.add_widget(self.layout)
		self.do_scale=False
		self.do_rotation=False
		self.do_translation=False
		self.label = Label(text="",font_size=40)
		self.add_widget(self.label)
		self.has_image=False
		with self.layout.canvas:
			Color(rgba=self.color)
			self.rect=Rectangle(size=self.size,source="validation.png")
	def on_touch_down(self,touch):
		super(TimelineComponent,self).on_touch_down(touch)
		if self.collide_point(*touch.pos):
			if touch.is_double_tap and self.has_image==True:
				self.parent.remove_item(self.layout.children[0])
	def anim_color(self,color=(0,0,1,0.9)):
		Animation(rgba=color,d=0.3).start(self.layout.canvas.children[0])

