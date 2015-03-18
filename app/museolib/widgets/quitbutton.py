
from kivy.uix.image import Image
from kivy.properties import StringProperty

class QuitButton(Image):
	state = StringProperty('normal')
	def on_touch_down(self, touch):
		if not self.collide_point(*touch.pos):
			return False
		self.state = "down"

	def on_touch_up(self, touch):
		if not self.collide_point(*touch.pos):
			return False
		self.state = 'normal'
		self.do_action()

	def do_action():
		pass