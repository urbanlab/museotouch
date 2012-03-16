from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.basket import Basket
from kivy.utils import platform

title_font_size = 25
title_color = (0.8862745098039215, 0.19215686274509805, 0.15294117647058825,1)#(1,0,0,1)#(197/255.,176/255.,210/255.) 
title_font = 'widgets/PetitaBold.ttf'
title_bold = True


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
            pos = (400,230),
            #pos_hint={'y': 0.01, 'center_x': .5},
            size_hint=(None, None), rotation=-90, scale=0.9,
            do_translate=False, do_rotate=False, do_scale=False)
    scatter.add_widget(app.date_slider)
    root.add_widget(scatter)

    # -------------------------------------------------------------------------
    # Create an image map widget
    # search image for map (exclude _active) files
    sources = glob(join(app.expo_data_dir, 'widgets', 'map', '*.png'))
    sources = [x for x in sources if '_active' not in x]
    app.imagemap = imagemap = ImageMap(
            size_hint=(None, None),
            size=(700, 893),
            sources=sources,
            suffix='_active')
    #root.add_widget(imagemap)
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=False,
            size_hint=(None, None),
            size=imagemap.size,
            #pos_hint={'x': 0.61, 'center_y': .55},
            #pos_hint={'y': 0.61},
            pos = (1040,70),
            rotation=0, 
            scale=0.5,
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)
    

    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(450, 650),
            size_hint=(None, None),
            orientation='vertical',
            title_template='KeywordItemTitle')
    scatter = scatter_keywords = Scatter(
            size=app.keywords.size,
            auto_bring_to_front=False,
            #pos_hint={'x': 0.01, 'center_y': 0.5},
            size_hint=(None, None),
            pos = (0,-200),
            rotation=0, 
            scale=0.9,
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.keywords)
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
    # Create a button to order by map
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_origin = o = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            pos = (1040,10),
            **kwargs)
    ordering_origin.bind(on_release=app.do_ordering_origin)
    root.add_widget(ordering_origin)

    #Function disabled since ordering button pos is fixed
    def set_ordering_origin_pos(instance, value):
        #ordering_origin.right = instance.right + 100
        ordering_origin.x = instance.x - 20
        ordering_origin.y = instance.top - 500
    #scatter_imagemap.bind(pos=set_ordering_origin_pos) 

    #Place the title next to it
    title_map = Label(
            text='Departement',
            font_name=title_font,
            font_size=title_font_size,
            color=title_color,
            bold=title_bold,
            size_hint=(None, None),
            size = (350,40),
            pos = (o.x + 40, o.y + 14)
            )
    root.add_widget(title_map)

    # -------------------------------------------------------------------------
    # Create a button to order by keyword group
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_keywords = o = Button(
            pos = (10,10),
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_keywords.bind(on_release=app.do_ordering_keywords)
    root.add_widget(ordering_keywords)

    #Function disabled since ordering button pos is fixed
    def set_ordering_keywords_pos(instance, value):
        ordering_keywords.x = instance.x
        ordering_keywords.y = instance.y - 50
    #scatter_keywords.bind(pos=set_ordering_keywords_pos)

    #Place the title next to it
    title_map = Label(
            text='Types de cartes',
            font_name=title_font,
            font_size=title_font_size,
            color=title_color,
            bold=title_bold,
            size_hint=(None, None),
            size = (300,40),
            pos = (o.x + 80, o.y + 14)
            )
    root.add_widget(title_map)

    # -------------------------------------------------------------------------
    # Create a button to order by datation
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_datation = o = Button(
            pos = (422,10),
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_datation.bind(on_release=app.do_ordering_datation)
    root.add_widget(ordering_datation)

    def set_ordering_datation_pos(instance, value):
        ordering_datation.y = instance.x - 20
        ordering_datation.x = instance.y
    #app.date_slider.bind(pos=set_ordering_datation_pos)

    #Place the title next to it
    title_map = Label(
            text='Date',
            font_name=title_font,
            font_size=title_font_size,
            color=title_color,
            bold=title_bold,
            size_hint=(None, None),
            size = (220,40),
            pos = (o.x + 20, o.y + 14)
            )
    root.add_widget(title_map)

    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1, 'top': 1},'size_hint': (None, None), 'size': (100, 100),
            'border': (0, 0, 0, 0), 'color' : (0,0,0,1), 'bold' : True}
    #active to False disables the basket
    #email_send to True activates sending the url of the basket by email
    #url_send to True activates sending the url of the basket to a specific url 
    app.basket = basket = Basket(
        active = True,
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

