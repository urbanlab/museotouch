from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, \
        BooleanProperty
from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout

try:
    import android
    is_android = True
except ImportError:
    is_android = False


class ImageItemContent(FloatLayout):
    item = ObjectProperty(None)
    flip_alpha = NumericProperty(1.)

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
            if self.collide_point(x,y) : 
                #add itself to the basket
                item_id = int(self.item['id'])
                if not basket.already_in( item_id) : 
                    basket.add_item( item_id )
                    #send back to init position
                    pos = self.last_touch_down_pos
                    anim = Animation(center = pos, duration = .5, t='out_quad' )
                    anim.start(self)
            
        return ret

    def on_touch_up(self, touch):
        ret = super(ImageItem, self).on_touch_up(touch)

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
