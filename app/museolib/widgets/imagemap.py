from os import sep
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, BooleanProperty, StringProperty
from kivy.resources import resource_find
from kivy.core.image import Image as CoreImage


class ImageMapItem(Image):

    active = BooleanProperty(False)
    source_active = StringProperty(None)
    source_original = StringProperty(None)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return self.toggle_active(touch)

    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        else:
            filename = resource_find(self.source)
            image = CoreImage(filename, keep_data=True)
            texture = image.texture
            self.texture = texture
            self._coreimage = image

    def toggle_active(self, touch):
        x, y = touch.pos
        x -= self.x
        y -= self.y
        x = int(x)
        y = int(y)
        y = self.parent.height - y # Because texture is flipped vertically in kivy 1.5.0
        coreimage = self._coreimage
        try:
            color = coreimage.read_pixel(x, y)
        except IndexError:
            return False
        if color[-1] == 0:
            return False
        if self.parent.show_one_cat_only:
            for child in self.parent.children:
                if not child == self:
                    if child.active == True:
                        child.active = False
                        child.source = child.source_original
        self.active = not self.active
        self.source = self.source_active if self.active \
                else self.source_original
        return True

class ImageMap(FloatLayout):

    suffix = StringProperty('')
    sources = ListProperty([])
    active_ids = ListProperty([])
    show_one_cat_only = BooleanProperty(False)

    def __init__(self, **kwargs):
        self._update_images = Clock.create_trigger(self.update_images, -1)
        super(ImageMap, self).__init__(**kwargs)
        self.bind(suffix=self._update_images,
                sources=self._update_images)
        self._update_images()

    def update_images(self, dt):
        for child in self.children[:]:
            child.unbind(active=self.on_child_active)
            self.remove_widget(child)

        for filename in self.sources:
            parts = filename.rsplit('.', 1)
            if len(parts) != 2:
                continue
            filename_suffix = '%s%s.%s' % (parts[0], self.suffix, parts[1])
            image = ImageMapItem(source=filename,
                    pos_hint={'x': 0, 'y': 0},
                    source_original=filename,
                    source_active=filename_suffix)
            image.bind(active=self.on_child_active)
            self.add_widget(image)

    def get_filename_id(self, filename):
        return filename.rsplit(sep, 1)[-1].rsplit('.', 1)[0]

    def on_child_active(self, instance, value):
        get_id = self.get_filename_id
        self.active_ids = [get_id(x.source_original) for x \
                in self.children if x.active]
        #print 'Image map "orig" changed to', self.active_ids
