from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label 
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.imagebuttons import ImageButtons 
from museolib.widgets.keywords import Keywords
from museolib.widgets.basket import Basket
from museolib.widgets.circularslider import CircularSlider
# from museolib.widgets.calendarslider import CalendarSlider 
from kivy.utils import platform
from kivy.animation import Animation


def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()
    
    # -------------------------------------------------------------------------
    # Add a date slider to our root widget.
    app.date_slider = slider = CircularSlider(
           size_hint=(None, None),
           orientation='horizontal',
           size=(250, 500))
    scatter = date_slider_scatter = Scatter(size=app.date_slider.size,
           auto_bring_to_front = False,
           pos_hint={'y': 0.01, 'center_x': .5},
           size_hint=(None, None), rotation=-90, scale=0.9,
           do_translate=False, do_rotate=False, do_scale=False)
    scatter.add_widget(app.date_slider)
    root.add_widget(scatter)
    
    # app.date_slider = slider = CalendarSlider(
    #         size_hint=(None,None),
    #         size = (3000, 100),
            
    #         )
#    scatter = date_slider_scatter = Scatter(size= app.date_slider.size,
#            auto_bring_to_front = False,
#            pos_hint = {'y':0, 'center_x':0.5},
#            size_hint = (None,None),
#            do_translate=False,
#            do_rotate=False,
#            do_scale=False)
#    scatter.add_widget(app.date_slider)
    # root.add_widget(slider)                
    
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'europ_map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            size_hint=(None, None),
            size=(600, 600),
            sources=sources,
            suffix='_active')
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=False,
            size=imagemap.size,
            size_hint=(None, None), rotation=0, scale=1,
            pos_hint={'right': 1.12, 'center_y': .5},
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)
    
#    sources = glob(join(app.expo_data_dir, 'widgets', 'europ_map', '*.png'))
#    sources = [x for x in sources if '_active' not in x]
    
    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(550, 650),
            size_hint=(None, None),
            orientation='vertical',
            title_template='KeywordItemTitle')
    scatter = scatter_keywords = Scatter(size=app.keywords.size,
            auto_bring_to_front=False,
            pos_hint={'x': 0.01, 'center_y': 0.5},
            size_hint=(None, None), rotation=0,
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.keywords)
    root.add_widget(scatter)
    
    #Create an image map widget
    # Mouvements artistiques, boutons du haut
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imageButtons = imageButtons = ImageButtons(
                                                   size_hint=(None, None),
                                                   size=(1128, 150),
                                                   sources=sources,
                                                   suffix='_active')
    scatter = scatter_imageButtons = Scatter(
                                             auto_bring_to_front=False,
                                             size=imageButtons.size,
                                             size_hint=(None, None), rotation=0, scale=1,
                                             pos_hint={'center_x':.5, 'y': .85},
                                             do_translation=False, do_rotation=False, do_scale=False)
    
    scatter.add_widget(app.imageButtons)
    root.add_widget(scatter)

    # -------------------------------------------------------------------------
    # Create a layout for buttons
    toolbar_layout = BoxLayout(size_hint=(None, None),
        pos=(32, 32), spacing=32)
    kwargs = {'size_hint': (None, None), 'size': (64, 64)}
    root.add_widget(toolbar_layout)

    # -------------------------------------------------------------------------
    # Create a button to replace randomly elements on screen
    # This button is on the bottom/left part of the screen
    '''kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_random = Button(
        background_normal='widgets/corner_bottomleft.png',
        background_down='widgets/corner_bottomleft_down.png',
        **kwargs)
    ordering_random.bind(on_release=app.do_reset_item_position)
    root.add_widget(ordering_random)'''

    # -------------------------------------------------------------------------
    # Create a button to order by body part
    kwargs = {'size_hint': (None, None), 'size': (97, 120),
            'border': (0, 0, 0, 0)}
    ordering_origin = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_origin.bind(on_release=app.do_ordering_origin)
    root.add_widget(ordering_origin)

    def set_ordering_origin_pos(instance, value):
        ordering_origin.right = instance.right - 20
        ordering_origin.y = instance.top - 1050
    scatter_imagemap.bind(pos=set_ordering_origin_pos)
#    scatter_imagemap2.bind(pos=set_ordering_origin_pos)

    # -------------------------------------------------------------------------
    # Create a button to order by keyword group
    kwargs = {'size_hint': (None, None), 'size': (97, 120),
            'border': (0, 0, 0, 0)}
    ordering_keywords = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_keywords.bind(on_release=app.do_ordering_keywords)
    root.add_widget(ordering_keywords)

    def set_ordering_keywords_pos(instance, value):
        ordering_keywords.x = instance.x
        ordering_keywords.y = instance.top - 810
    scatter_keywords.bind(pos=set_ordering_keywords_pos)

    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1.34, 'top': 1},'size_hint': (None, None), 'size': (700, 1080),
            'border': (0, 0, 0, 0), 'color' : (0,0,0,1), 'bold' : True}
    #active to False disables the basket
    #email_send to True activates sending the url of the basket by email
    #url_send to True activates sending the url of the basket to a specific url 
    app.basket = basket = Basket(
        active = False,
        background_normal='widgets/partage.png',
        background_down='widgets/partage_active.png',
        email_send = True,
        url_send = False,
        url_send_url = 'http://urltest.lapin.be?url=',
        app = app, 
        **kwargs)
    if basket.active :
        #do not offer a basket on tablets, only on tables
        if platform() not in ('android'):  
            root.add_widget(basket, index=0)
            root.add_widget(basket.itemsLayout, index = 0)
            basket.itemsLayout.pos_hint = {'right':1.1, 'top':0.85}
                
    basket.open = False
    def translateObject(object, xParam):
        anim = Animation(x = object.x + xParam, duration = 0.2)
        anim.start(object)
        
    def translateAllItems(xParam):
        translateObject(app.root_images, xParam)
        for i, item in enumerate(reversed(app.root_images.children)):
#            anim = Animation(x=item.x + xParam, duration = 0.2)
#            anim.start(item)
            translateObject(item, xParam)
                
    def moveAllItems(xParam):
        app.root_images.x = xParam 
        for i, item, in enumerate(reversed(app.root_images.children)):
            item.x = xParam

    def translateBasket(instance):
        if basket.open == True:
            anim = Animation(x=0, duration=0.2)
            anim.start(root)
            
            translateAllItems(640)
            basket.open = False
        else:
            anim = Animation(x=-640, duration=0.2)
            anim.start(root)
            translateAllItems(-640)
#            root.remove_widget(basket)
#            root.add_widget(basket)
            basket.open = True
        
    def grabBasket(self,touch):
        if not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        return True
    
    def moveBasket(self, touch):
        if touch.grab_current is self:
            root.x = touch.x - self.x
#            app.root_images.x = touch.x - app.root_images.x
#            for i, item in enumerate(reversed(app.root_images.children)):
#                item.x = touch.x - self.x
        return True

    def ungrabBasket(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            print root.x
            if basket.open == False:
                if root.x < -200:
                    anim = Animation(x=-640, duration=0.2)
                    anim.start(root)
                    root.remove_widget(basket)
                    root.add_widget(basket)
                    basket.open = True
                else:
                    anim = Animation(x=0, duration=0.3 )
                    anim.start(root)
                    basket.open = False
            else:
                if root.x < -640:
                    anim = Animation(x=-640, duration = 0.2)
                    anim.start(root)
                    basket.open = True
                else:
                    anim = Animation(x=0, duration = 0.2)
                    anim.start(root)
                    basket.open = False
                                     
        return True
            
    basket.bind(on_release=translateBasket)
#    basket.bind(on_touch_move=moveBasket)
#    basket.bind(on_touch_down=grabBasket)
#    basket.bind(on_touch_up=ungrabBasket)
    # -------------------------------------------------------------------------
    return root

