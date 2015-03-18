from kivy.uix.dropdown import DropDown
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.properties import ListProperty,ObjectProperty,StringProperty

class CustomDropDown(Scatter):
	menu = ObjectProperty(DropDown(max_height=100,auto_width=False,width=200))
	button_text = StringProperty()
	def __init__(self, **kwargs):
		super(CustomDropDown, self).__init__(**kwargs)

	def populate_drop_down(self,batch_list=[]):
		self.menu.clear_widgets()
		batch_list.append('Tous les lots')
		for index in batch_list:
			btn = Button(text=index.capitalize(), size_hint_y=None, height=25)
			btn.bind(on_release=self.on_list_select)
			self.menu.add_widget(btn)

	def on_list_select(self,btn):
		self.menu.select(btn.text)
		self.button_text=btn.text