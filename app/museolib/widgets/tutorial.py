from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty,ListProperty,ObjectProperty
class Tutorial(BoxLayout):
	img_path = StringProperty(None)
	img_size = ListProperty([Window.width/2,Window.height])
	text = StringProperty('A vous de jouer !')
	tuto = ObjectProperty(None)
	def __init__(self,image,**kwargs):
		super(Tutorial,self).__init__()
		self.img_path = image
		self.number = image.split('-')[1].split('.')[0]
		self.tuto = self.get_tuto_widget()
		self.ids.tuto_container.add_widget(self.tuto)
		self.text=self.tuto.text
	def get_tuto_widget(self):
		tuto = __import__("museolib.widgets.tutorials.%s" % self.number, fromlist=["museolib.widgets.tutorials"])
		return tuto.TutoWidget(img_path=self.img_path)
