from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from museolib.widgets.tutorial import Tutorial
from os import listdir
from os.path import join
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

class SplashScreen(FloatLayout):
	vid=ObjectProperty(None)
	# splashObject=ObjectProperty(None)
	def __init__(self,splash_dir,selector_reference,interval):
		super(SplashScreen,self).__init__(valid=False)
		# keeping expo selector reference to unbind its "on_touch_down" and "on_touch_up" functions
		# in order to avoid two concurrent clocks to be launched at the same time.
		self.selector_reference=selector_reference
		Window.unbind(on_touch_down=selector_reference.on_touch_down)
		Window.unbind(on_touch_up=selector_reference.on_touch_up)
		# images directory
		self.splash_dir=splash_dir
		self.opacity=1
		# Index of the image to display
		self.img_index=0
		# Image names list
		self.files_list=self.get_files_list()
		self.files_list.sort()
		# Interval between images
		self.interval = interval
		# Launch Timer
		if self.files_list !=[]:
			self.step(self.interval)
	def step(self,interval):
		if interval!=0:
			Clock.schedule_interval(self.show_images,interval)
	def stop(self):
		Clock.unschedule(self.show_images)
	def quit(self):
		self.stop()
		# Unload kivy definition for the fake validation widget
		for f in Builder.files :
			if "valid.kv" in f:
				Builder.unload_file(f)
				break
		# Remove fake validation widget if exists
		for child in self.children:
			if isinstance(child, Tutorial):
				try :
					board = child.children[0].children[0].board
				except:
					pass
		print Window.children
		# Stop video if active
		if self.vid:
			self.vid.play=False
		# Reactivate and show hidden widgets
		for child in Window.children:
			child.opacity=1
			child.disabled=False
		Window.remove_widget(self)
		# Rebind previous functions to be able to launch a new splashscreen
		Window.bind(on_touch_down=self.selector_reference.on_touch_down)
		Window.bind(on_touch_up=self.selector_reference.on_touch_up)
	def previous(self):
		self.show_images(direction='r')
	def next(self):
		self.show_images(direction='l')
	def get_files_list(self):
		files_list=[]
		for f in listdir(self.splash_dir):
		#list all image and video files in the directory
			if f.endswith(('.jpg','.png','.avi','.mp4')):
				files_list.append(f)
		return files_list
	def show_images(self,arg=None,direction='l'):
		# eye candy
		if self.vid:
			self.vid.opacity=0
			self.vid.play=False
			self.vid.position=0
		self.ids.img.opacity=0

		if direction=='l':
			self.img_index+=1
			self.start_pos=(Window.width,0)
		else:
			self.img_index-=1
			self.start_pos=(-Window.width,0)

		if self.img_index > len(self.files_list)-1:
			self.img_index=0
		# if image is the last one of the list, go back to the first
		elif self.img_index < 0 :
			self.img_index=len(self.files_list)-1
		# remove last tuto widget
		for child in self.children:
			if isinstance(child,Tutorial):
				self.remove_widget(child)
		# determinate the type of content (image, video, tutorial)
		if self.files_list[self.img_index].endswith(('.avi','.mp4')):
			self.show_video(join(self.splash_dir,self.files_list[self.img_index]))
			self.slide_animation(self.vid,self.start_pos)
		else:
			if 'tuto' in self.files_list[self.img_index]:
				obj = Tutorial(join(self.splash_dir,self.files_list[self.img_index]))
				self.add_widget(obj)
			else:
				self.ids.img.source=join(self.splash_dir,self.files_list[self.img_index])
				obj = self.ids.img
			self.slide_animation(obj,self.start_pos)
	def slide_animation(self,obj,start_pos):
		Animation.cancel_all(self.ids.img)
		if self.vid:
			Animation.cancel_all(self.vid)
		obj.pos=start_pos
		anim=Animation(opacity=1,pos=(0,0),d=1)
		anim.start(obj)
	def show_video(self,video):
		if not self.vid:
			self.vid = Video(source=video,play=True,size_hint=(None,None),size=self.size)
			self.add_widget(self.vid)
		else:
			self.ids.img.opacity=0
			self.vid.opacity=1
			self.vid.play=True
		# When video playback is finished (eos chages to True) trigger on_touch_up to launch a new timer
		self.vid.bind(eos=self.video_eos_callback)
		self.stop()

	def on_touch_down(self,touch):
		super(SplashScreen,self).on_touch_down(touch)
		self.stop()
	def on_touch_up(self,touch):
		super(SplashScreen,self).on_touch_up(touch)
		self.step(self.interval)
	def video_eos_callback(self,instance,eos):
		self.step(self.interval)