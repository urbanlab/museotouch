from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.basket import Basket
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
    BooleanProperty, ListProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.loader import Loader
from kivy.animation import Animation
import random
from pdb import set_trace as rrr

from museolib.widgets.imageitem import ImageItem

class ScrollViewItem(Image):
    texture = ObjectProperty(None)
    id = ObjectProperty(None)
    name = ObjectProperty(None)
    app = ObjectProperty(None)
    
    source = StringProperty(None)
    itemWidth = NumericProperty(None)
    totalHeight = NumericProperty(None)
    animOrange = Animation(color = [0.90,0.29,0.157,1], duration=0.1)   
    animWhite = Animation(color = [1,1,1,1], duration=0.1)
    
    isOrange = False

    def __init__(self, **kwargs):
        super(ScrollViewItem, self).__init__(**kwargs)
        self.image = Image(source = self.source, keep_data=True)
        xOrigin = self.image.texture.width/2 - self.itemWidth/2
        self.texture = self.image.texture.get_region(xOrigin, 0, self.itemWidth, self.totalHeight)
        self.imgItem = None

    
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        self.animOrange.bind(on_complete = self.isOrangeAnimationFinished)
        self.animWhite.stop(self)
        self.animOrange.start(self)        
        return True
 
    def on_touch_up(self,touch):
        if touch.grab_current is self:
            self.animOrange.stop(self)
        if (self.isOrange == True): 
            self.show_object()
        self.animWhite.bind(on_complete = self.isWhiteAnimationFinished)
        
        self.animWhite.start(self)      
        touch.ungrab(self)
        return True

    def isOrangeAnimationFinished(self, animation, widget):
        self.isOrange = True

    def isWhiteAnimationFinished(self, animation, widget):
        self.isOrange = False
    
    def updateSize(self, width, height):
        xOrigin = self.image.texture.width /2 - width/2
        self.texture = self.image.texture.get_region(xOrigin, 0, width, height)

    def show_object(self):
        
        #source = u'expos/4/images/dds/42.dds'
        #if source not in self.images_displayed:
        #    return
        #current_images = [x.source for x in self.root_images.children]
        #if source in current_images:
        #    return

        #images_pos = self.images_pos
        #if source in images_pos:
        #    p = images_pos[source]
        #    defs.pop('center', None)
        #    defs['center'] = p['center']
        #    defs['rotation'] = p['rotation']
        if self.imgItem is None:
            center = self.center #defs.pop('center')
            rotation = random.randint(0,359) #defs.pop('rotation')
            item = ImageItem(source=self.image.source, square=True, item=self.db_item, app=self.app)
            #import pdb; pdb.set_trace()
            self.parent.parent.parent.parent.add_widget(item, index=0)
            # scrollviewwidget>gridlayout>scrollview>FloatLayout (global)
            item.rotation = rotation
            item.center = center
            item.barre = self
            self.imgItem = item
        #images_pos[source] = {
        #    'center': item.center,
        #    'rotation': item.rotation}
