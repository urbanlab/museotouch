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
            size_hint=(None, None),
            size=(385, 1000),
            sources=sources,
            suffix='_active')
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=False,
            size=imagemap.size,
            size_hint=(None, None), rotation=0, scale=1,
            pos_hint={'right': 1, 'center_y': .5},
            do_translation=False, do_rotation=False, do_scale=False)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)

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
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_origin = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_origin.bind(on_release=app.do_ordering_origin)
    root.add_widget(ordering_origin)

    def set_ordering_origin_pos(instance, value):
        ordering_origin.right = instance.right - 20
        ordering_origin.y = instance.top - 1020
    scatter_imagemap.bind(pos=set_ordering_origin_pos)

    # -------------------------------------------------------------------------
    # Create a button to order by keyword group
    kwargs = {'size_hint': (None, None), 'size': (64, 64),
            'border': (0, 0, 0, 0)}
    ordering_keywords = Button(
            background_normal='widgets/circle_filter.png',
            background_down='widgets/circle_filter_down.png',
            **kwargs)
    ordering_keywords.bind(on_release=app.do_ordering_keywords)
    root.add_widget(ordering_keywords)

    def set_ordering_keywords_pos(instance, value):
        ordering_keywords.x = instance.x
        ordering_keywords.y = instance.top - 845
    scatter_keywords.bind(pos=set_ordering_keywords_pos)

    # -------------------------------------------------------------------------
    # Create a basket widget
    # This button is on the bottom/left part of the screen
    kwargs = {'pos_hint':{'right': 1, 'top': 1},'size_hint': (None, None), 'size': (128, 128),
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

