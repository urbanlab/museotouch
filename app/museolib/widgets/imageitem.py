from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty, ListProperty
from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from os.path import splitext, join, isfile
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

    def on_index(self, instance, value):
        if self.media:
            if isinstance(self.media, Video):
                self.media.play = False
            self.media = None
        value = value % len(self.item.medias)
        media = self.item.medias[value]
        name, ext = splitext(media)
        ext = ext[1:].lower()

        # convert media url to local media path (all medias are already downloaded)
        from museolib.utils import no_url
        media = join(self.parent.parent.parent.parent.app.expo_dir, 'otherfiles', no_url(media))
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
                w = AsyncImage(source=media)
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
    
    def __init__(self, *args, **kwargs):

        square = False
        if 'square' in kwargs and kwargs['square'] == True:
            square = True
            del kwargs['square']
        super(ImageItem, self).__init__(**kwargs)
        self.on_start()
        if square:
            # Rognage => maximum square :
            my_ceil = lambda n: 0 if n < 0 else n
            L,H = self.img_square.texture.size
            x = my_ceil(L-H)/2
            y = my_ceil(H-L)/2
            w = min(L,H)
            h = min(L,H)
            #import pdb; pdb.set_trace()
            self.img_square.texture = self.img_square.texture.get_region(x, y, w, h)

    def on_start(self):
        print 'start'

    def on_touch_down(self, touch):
        ret = super(ImageItem, self).on_touch_down(touch)
        if not ret:
            return
        if self.counter == 0:
            Animation(alpha_button=1., t='out_quad', d=0.3).start(self)
        if is_android and touch.is_double_tap:
            self.flip()
        uid = '%s_counter' % self.uid
        touch.ud[uid] = True
        self.counter += 1
        #remember init pos in case of a drag to basket
        self.last_touch_down_pos = touch.pos

        #### MOMENTUM ####
        # Animation.stop_all(self, 'pos')
        # if not hasattr(self, 'isMoving'):
        #     self.isMoving = False
        # self.isMoving = False
        #### MOMENTUM ####
        return True
    
    def on_touch_move(self, touch):
        ret = super(ImageItem,self).on_touch_move(touch)

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
        ret = super(ImageItem, self).on_touch_up(touch)

        ##### MOMENTUM ######
        # print touch.px, touch.py, touch.x, touch.y, touch.time_end - touch.time_start, touch.time_update

        # lastPos = (touch.px, touch.py)
        # currentPos = (touch.x, touch.y)
        # deltaV = Vector(currentPos) - Vector(lastPos)
        # nextPos = Vector(self.pos) + (deltaV * 5)
        # distance = Vector(lastPos).distance(currentPos)

        # if distance > 0:
        #     length = time.time() - touch.time_update
        #     if length > 0:
        #         velocity = distance / length
        #         duration = 1000/velocity
        #         if not self.isMoving:
        #             def reset_on_moving(arg):
        #                 self.isMoving = False
        #             anim = Animation(pos = nextPos, duration= duration, t = 'out_cubic')
        #             anim.on_complete = reset_on_moving
        #             anim.start(self)
        #             self.isMoving = True

        ##### MOMENTUM ######

        # whatever is happening, if this touch was a touch used for counter,
        # remove it.
        uid = '%s_counter' % self.uid
        if uid in touch.ud:
            del touch.ud[uid]
            self.counter = max(0, self.counter - 1)
            if self.counter == 0:
                Animation(alpha_button=0., t='out_quad', d=0.3).start(self)

        return ret

    def flip(self):
        self.flip_front = not self.flip_front
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
                scale = max(1., self.scale)
                k['scale'] = scale
        if is_android:
            k['rotation'] = 0.
        Animation(flip_alpha=alpha,
            t='out_quad', d=0.3, **k).start(self)

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
        x, y = value
        x = max(parent.x, x)
        y = max(parent.y, y)
        x = min(parent.right, x)
        y = min(parent.top, y)
        self.center = x, y

    def on_parent(self, instance, value):
        if value is None and self.content:
            self.content.stop()
