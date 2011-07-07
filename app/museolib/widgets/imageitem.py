from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

class ImageItem(Scatter):
    
    source = StringProperty(None)
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._trigger_container = Clock.create_trigger(
                self._update_container, 0)
        super(ImageItem, self).__init__(**kwargs)
        self._trigger_container()

    def _update_container(self, dt):
        assert(self.container is not None)
        self.container.clear_widgets()
        source = self.source
        if source is None:
            return
        image = Image(source=source)
        self.container.add_widget(image)

