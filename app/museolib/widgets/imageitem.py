from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty
from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.label import Label
from os.path import splitext, join, isfile, basename
from kivy.core.window import Window
from kivy.clock import Clock
from museolib.widgets.validation import Valid as Valid
from pdb import set_trace as rrr

from kivy.vector import Vector
import time

try:
    import android
    is_android = True
except ImportError:
    is_android = False

class ItemMediaBrowser(FloatLayout):
    item = ObjectProperty(None)
    index = NumericProperty(-1)
    content = ObjectProperty(None)
    media = ObjectProperty(None, allownone=True)
    medias_sorted = BooleanProperty(False)

    def on_index(self, instance, value):
        if self.medias_sorted ==False :
            medialist = self.item.medias
            medialist.sort()
        if self.media:
            if isinstance(self.media, Video):
                self.media.play = False
            self.media = None
        value = value % len(medialist)
        media = medialist[value]
        name, ext = splitext(media)
        ext = ext[1:].lower()

        # convert media url to local media path (all medias are already downloaded)
        # from museolib.utils import no_url
        
        media = join(self.parent.parent.parent.parent.app.expo_dir, 'otherfiles', basename(media))
        
        if not isfile(media):
            print " ### Oops, this media is not downloaded !"
        try:
            if ext in ('mp3', 'ogg', 'flac', 'wav'):
                w = Label(text="It's a song : " + media)
                if not isfile(media):
                    w = Label(text="Song not downloaded.")
            elif ext in ('avi', 'mkv', 'mp4', 'ogv', 'mpg', 'mpeg', 'dv'):
                w = Video(source=media, play=True)
            else:                
                w = Image(source=media)
        except:
            w = Label(text='Unable to read that media')
        self.content.clear_widgets()
        self.content.add_widget(w)
        self.media = w

    def stop(self):
        if self.media:
            if isinstance(self.media, Video):
                self.media.play = False
            self.media = None

class ImageItemContent(FloatLayout):
    item = ObjectProperty(None)
    imageitem = ObjectProperty(None)
    flip_alpha = NumericProperty(1.)
    mediacontent = ObjectProperty(None, allownone=True)

    def toggle_media(self):
        '''Toggle display of medias if exist
        '''
        if not self.mediacontent:
            self.mediacontent = ItemMediaBrowser(item=self.item)
            self.add_widget(self.mediacontent)
            self.mediacontent.index = 0
            self.imageitem.color[3] = 0
        else:
            self.remove_widget(self.mediacontent)
            self.mediacontent = None
            self.imageitem.color[3] = 1

    def stop(self):
        if self.mediacontent:
            self.mediacontent.stop()


class ImageItem(Scatter):
    #: Reference of the application
    app = ObjectProperty(None)
    
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

    #: Button animation
    alpha_button = NumericProperty(0.)

    #: Touch counter
    counter = NumericProperty(0)

    #: Basket widget
    basket = ObjectProperty(None)

    #: Last touch_down to date
    last_touch_down_pos = ObjectProperty(None)

    #: Color
    color = ListProperty([1, 1, 1, 1])

    #: If we want a square img
    img_square = ObjectProperty(None)

    #: Boolean to activate physics or not
    physics = BooleanProperty(True)
    
    def __init__(self, *args, **kwargs):
        self.vector=(0,0)
        self.previous_position=(0,0)
        self.current_position=(0,0)
        self.start=0
        self.stop=0
        square = False
        if 'square' in kwargs and kwargs['square'] == True:
            square = True
            del kwargs['square']
        super(ImageItem, self).__init__(**kwargs)
        self.on_start()
        if square:
            self.squarize_img()    
    
    def on_start(self):
        #Replace this function in init.py to personnalize dynamically an image item 
        pass

    def squarize_img(self):
        # Rognage => maximum square :
        my_ceil = lambda n: 0 if n < 0 else n
        L,H = self.img_square.texture.size
        x = my_ceil(L-H)/2
        y = my_ceil(H-L)/2
        w = min(L,H)
        h = min(L,H)
        self.img_square.texture = self.img_square.texture.get_region(x, y, w, h)

    def on_touch_down(self, touch): 
        ret = super(ImageItem, self).on_touch_down(touch)
        if not ret:
            return
        self.physics = self.app.config.getboolean('museotouch','physics')
        # if self.counter == 0:
        Animation(alpha_button=1., t='out_quad', d=0.3).start(self)
        if is_android and touch.is_double_tap:
            self.flip()
        uid = '%s_counter' % self.uid
        touch.ud[uid] = True
        self.counter += 1
        touch.ud['counter'] = self.counter
        #remember init pos in case of a drag to basket
        self.last_touch_down_pos = touch.pos

        if self.collide_point(*touch.pos) and self.physics==True:
            self.start=time.time()
            self.vector=Vector(0,0)
            Clock.unschedule(self.move)
        return True
    
    def on_touch_move(self, touch):
        ret = super(ImageItem,self).on_touch_move(touch)
        Clock.unschedule(self.move)
        if self.collide_point(*touch.pos) and self.physics == True:
            self.previous_position = self.current_position
            self.current_position = self.pos
            current_vector = Vector(self.current_position)-Vector(self.previous_position)
            if current_vector != Vector(0,0) and current_vector.length()<100:
                self.vector=current_vector*2
        #check if the item collides with the basket
        #get basket center point
        if self.basket == None : 
            self.basket = self.app.basket 
        basket = self.basket 
        if basket.active : 
            x,y = basket.center
            #check if collides with the basket
#            if self.collide_point(x,y) : 
            if self.collide_widget(basket):
                #add itself to the basket
                item = self.item
                item_id = int(item['id'])
                if not basket.already_in( item_id) : 
                    basket.add_item( item_id, item, self )
                #send back to init position
                pos = self.last_touch_down_pos
                #avoid a bug when touching the keyboard
                if pos is not None :
                    pos = pos
                else :
                    pos = (100,100)  
                anim = Animation(center = pos, duration = .5, t='out_quad' )
                anim.start(self)       
        return ret

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        ret = super(ImageItem, self).on_touch_up(touch)

        if self.collide_point(*touch.pos) and self.physics == True:
            self.stop=time.time()
            if self.stop-self.start >0.05:
                Clock.schedule_interval(self.move,1./60.)

        # whatever is happening, if this touch was a touch used for counter,
        # remove it.
        uid = '%s_counter' % self.uid
        if uid in touch.ud:
            del touch.ud[uid]
            self.counter = max(0, self.counter - 1)
            # if self.counter == 0:
            Animation(alpha_button=0., t='out_quad', d=0.3).start(self)
            self.check_valid(touch.pos)
        return ret

    def flip(self):
        self.flip_front = not self.flip_front
        Animation(alpha_button=0., t='out_quad', d=0.3).start(self)
        # first time ? create content

    def on_flip_front(self, instance, value):
        self.color[3] = 1
        # do animation ?
        alpha = 1. if value else 0.
        k = {}
        if self.app.mode == 'mobile':
            k['rotation'] = 0
            if not self.flip_front:
                scale = max(1., self.scale)
            else:
                scale = min(.30, self.scale)
            k['scale'] = scale
        else:
            if not self.flip_front:
                if not isinstance(self.parent.parent,Valid):
                    scale = max(1., self.scale)
                    k['scale'] = scale
        if is_android:
            k['rotation'] = 0.
        Animation(flip_alpha=alpha,
            t='out_quad', d=0.3, **k).start(self)
        self.image_opacity("up")

    def image_opacity(self,go_up_down):
        try :
            self.ids['img_front']
            if go_up_down=="down":
                Animation(opacity=0.2).start(self.ids.img_front)
            else :
                Animation(opacity=1).start(self.ids.img_front)
        except:
            pass

    def ensure_content(self):

        if self.content is not None:
            return
        self.content = ImageItemContent(item=self.item,
                flip_alpha=self.flip_alpha, imageitem=self)

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

    def on_btn_close(self, *largs):
        # called when close button have been released
        if self.alpha_button < 0.8:
            return
        self.parent.remove_widget(self)

    def on_btn_moreinfo(self, *largs):
        # called when moreinfo button have been released
        if self.alpha_button < 0.8:
            return
        self.flip()

    def collide_point(self, x, y):
        # custom collision. some button are outside widget, so check if
        # collision can happen on them too.
        x, y = self.to_local(x, y)
        ret = 0 <= x <= self.width and 0 <= y <= self.height
        if ret:
            return ret
        for child in self.children:
            ret = child.collide_point(x, y)
            if ret:
                return ret
        return False

    def on_center(self, instance, value):
        parent = self.parent
        if not parent:
            return
        # causing problems when the item scale was too important
        # x, y = value
        # x = max(parent.x, x)
        # y = max(parent.y, y)
        # x = min(parent.right, x)
        # y = min(parent.top, y)
        # self.center = x, y

    def on_parent(self, instance, value):
        if value is None and self.content:
            self.content.stop()

    def move(self,arg):
        self.pos = Vector(self.pos) + self.vector*0.5
        self.vector*=0.95
        if abs(self.vector[0]+self.vector[1])<0.001:
            Clock.unschedule(self.move)
    def on_pos(self,instance,position):
        self.check_boundaries()
    def check_valid(self,touch):
        if self.parent :
            for wid in self.parent.parent.children :
                if isinstance(wid,Valid) and wid.collide_point(*touch):
                    Animation(color=(0,0,1,0.9),d=0.3).start(wid)
                    nbr_valid = len(wid.ids['my_layout'].children)
                    if nbr_valid <=3:
                        temp = self
                        temp.do_scale=False
                        temp.do_translation = False
                        temp.do_rotation=False
                        temp.vector=Vector(0,0)
                        temp.pos=(0,0)
                        self.parent.remove_widget(self)
                        wid.ids['my_layout'].add_widget(temp)
                        anim=Animation(pos=wid.children_pos[str(nbr_valid)], rotation=0,d=0.2,scale=wid.width*0.00095)
                        anim.start(self)

    def check_boundaries(self):
        #change direction
        if self.x+(self.width*self.scale)>Window.width or self.x < 0 :
            self.vector=Vector(-self.vector[0],self.vector[1])*0.05
        if self.y+(self.height*self.scale)>Window.height or self.y < 0 :
            self.vector=Vector(self.vector[0],-self.vector[1])*0.05
        #prevent from going off the screen
        if self.scale <1 :
            if self.x < 0:
                self.x=0
            if self.y < 0:
                self.y=0
            if self.x + (self.width*self.scale) > Window.width:
                self.x = Window.width -(self.width*self.scale)
            if self.y + (self.height*self.scale) > Window.height:
                self.y = Window.height -(self.height*self.scale)