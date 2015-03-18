from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.slider import SizeSlider
from museolib.widgets.basket import Basket
from kivy.utils import platform

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    try :
        from museolib.gesture_board import GestureBoard
        root = GestureBoard()
    except:
        root = FloatLayout()
        class Valid():
            pass
    background = Image(source='widgets/background.png', size=(1920,1080))
    root.add_widget(background)

    # -------------------------------------------------------------------------
    # Add a date slider to our root widget.
    app.date_slider = slider = CircularSlider(
            pos_hint={'right': 1, 'center_y': 0.5},
            size_hint=(None, None),
            size=(250, 500))
    root.add_widget(slider)

    # -------------------------------------------------------------------------
    # Size slider
    app.size_slider = slider = SizeSlider(
	    size=(500, 150), size_hint=(None, None))
    scatter = size_slider_scatter = Scatter(size=app.size_slider.size,
            auto_bring_to_front=False,
	        pos_hint={'top': 0.98, 'center_x': .5},
            size_hint=(None, None), rotation=-180,
            do_translate=False, do_rotate=False, do_scale=False)
    scatter.add_widget(app.size_slider)
    root.add_widget(scatter)

    # -------------------------------------------------------------------------
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            pos_hint={'center_x': 0.5, 'y': 0},
            size_hint=(None, None),
            size=(500, 200),
            sources=sources,
            suffix='_active')
    root.add_widget(imagemap)

    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(500, 250),
            size_hint=(None, None))
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
        ordering_origin.y = instance.y + 20
        ordering_origin.x = instance.right + 20
    imagemap.bind(pos=set_ordering_origin_pos)

    # -------------------------------------------------------------------------
    # Create a button to order by datation
    ordering_datation = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_datation.bind(on_release=app.do_ordering_datation)
    root.add_widget(ordering_datation)

    def set_ordering_datation_pos(instance, value):
        ordering_datation.y = instance.top + 20
        ordering_datation.right = instance.right - 20
    app.date_slider.bind(pos=set_ordering_datation_pos)

    # -------------------------------------------------------------------------
    # Create a button to order by size
    ordering_size = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_size.bind(on_release=app.do_ordering_size)
    root.add_widget(ordering_size)

    def set_ordering_size_pos(instance, value):
        ordering_size.y = instance.top - 35
        ordering_size.right = instance.x - 70
    size_slider_scatter.bind(pos=set_ordering_size_pos)

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

