
from kivy.uix.image import Image
from kivy.properties import StringProperty


class QuitButton(Image):
	state = StringProperty('normal')
	def on_touch_down(self, touch):
		if not self.collide_point(*touch.pos):
			return False
		delay = touch.time_update - touch.time_start
		if delay < 0.2:
			self.state = "down"
		else:
			self.state = 'normal'

	def on_touch_up(self, touch):
		if not self.collide_point(*touch.pos):
			return False
		self.state = 'normal'
		delay = touch.time_update - touch.time_start
		if delay > 0.2:
			self.do_action()

	def do_action():
		pass