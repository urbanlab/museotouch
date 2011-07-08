from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty
from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout

class ImageItemContent(FloatLayout):
    item = ObjectProperty(None)
    flip_alpha = NumericProperty(1.)

class ImageItem(Scatter):
    
    #: Backend item reference
    item = ObjectProperty(None)

    #: Image filename to use
    source = StringProperty(None)

    #: Element that will contain the content/description
    container = ObjectProperty(None)

    #: Element created the first time the widget is flipped
    content = ObjectProperty(None)

    #: Border that can be used to draw outline 
    border = NumericProperty(5)

    #: For animation
    flip_alpha = NumericProperty(1.)
    flip_front = BooleanProperty(True)

    def on_touch_down(self, touch):
        ret  = super(ImageItem, self).on_touch_down(touch)
        if not ret:
            return
        if touch.is_double_tap:
            self.flip()
        return True

    def flip(self):
        self.flip_front = not self.flip_front
        # first time ? create content

    def on_flip_front(self, instance, value):
        # do animation ?
        alpha = 1. if value else 0.
        Animation(flip_alpha=alpha, t='out_quad', d=0.3).start(self)

    def ensure_content(self):
        if self.content is not None:
            return
        self.content = ImageItemContent(item=self.item,
                flip_alpha=self.flip_alpha)

    def on_flip_alpha(self, instance, value):
        content = self.content
        if content is None and value != 1:
            self.ensure_content()
            content = self.content

        if value == 1 and content is not None:
            self.container.remove_widget(content)
        elif content not in self.container.children:
            self.container.add_widget(content)
        content.flip_alpha = value
