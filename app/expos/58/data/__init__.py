from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.slider import SizeSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.basket import Basket
from kivy.utils import platform

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    # -------------------------------------------------------------------------
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            pos_hint={'right': 1, 'y': 0},
            size_hint=(None, None),
            size=(840, 175),
            sources=sources,
            suffix='_active')
    s = Scatter(rotation=90,pos_hint=app.imagemap.pos_hint,size=app.imagemap.size,size_hint=(None,None))
    s.add_widget(app.imagemap)
    root.add_widget(s)

    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(500, 250),
            size_hint=(None, None),color_file='widgets/test.png',color_file_selected='widgets/test_down.png')
    scatter = keywords_scatter = Scatter(size=app.keywords.size,
            auto_bring_to_front=False,
            pos_hint={'x': 0, 'center_y': 0.5},
            size_hint=(None, None), rotation=-90,
            do_translate=False, do_rotate=False, do_scale=False)
    scatter.add_widget(app.keywords)
    root.add_widget(scatter)

    # -------------------------------------------------------------------------
    # Create a button to replace randomly elements on screen
    # This button is on the bottom/left part of the screen
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_origin = Button(
        background_normal='widgets/corner_bottomleft.png',
        background_down='widgets/corner_bottomleft_down.png',
        **kwargs)
    ordering_origin.bind(on_release=app.do_reset_item_position)
    root.add_widget(ordering_origin)

    # -------------------------------------------------------------------------
    # Create a button to order by continent
    # This button must be placed to the right of continent
    kwargs = {'size_hint': (None, None), 'size': (40, 40),
            'border': (0, 0, 0, 0)}
    ordering_origin = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_origin.bind(on_release=app.do_ordering_origin)
    root.add_widget(ordering_origin)

    def set_ordering_origin_pos(instance, value):
        ordering_origin.y = instance.width +20
        ordering_origin.x = instance.x + 50
    s.bind(pos=set_ordering_origin_pos)

    # -------------------------------------------------------------------------
    # Create a button to order by keywords
    ordering_keywords = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    #ordering_keywords.bind(on_release=app.do_ordering_keywords)
    root.add_widget(ordering_keywords)

    def set_ordering_keywords_pos(instance, value):
        ordering_keywords.x = 20
        ordering_keywords.top = instance.y - 40
    keywords_scatter.bind(pos=set_ordering_keywords_pos)

    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1, 'top': 1},'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0), 'color' : (0,0,0,1), 'bold' : True}
    #active to False disables the basket
    #email_send to True activates sending the url of the basket by email
    #url_send to True activates sending the url of the basket to a specific url 
    app.basket = basket = Basket(
        active = False,
        background_normal='widgets/corner_topright.png',
        background_down='widgets/corner_topright_down.png',
        email_send = True,
        url_send = False,
        url_send_url = 'http://urltest.lapin.be?url=',
        app = app, 
        **kwargs)
    if basket.active :
        #do not offer a basket on tablets, only on tables
        if platform() not in ('android'):  
            root.add_widget(basket)

    # -------------------------------------------------------------------------

    return root

