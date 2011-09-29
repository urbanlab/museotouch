from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.keywords import Keywords
from museolib.widgets.slider import SizeSlider

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
            size=(600, 800),
            sources=sources,
            suffix='_active')
    scatter = scatter_imagemap = Scatter(
            auto_bring_to_front=False,
            size=(600, 800),
            size_hint=(None, None), rotation=90, scale=.5,
            pos_hint={'center_x': 0.5, 'y': 0},
            do_translate=False, do_rotate=False, do_scale=False)
    scatter.add_widget(app.imagemap)
    root.add_widget(scatter)

    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(500, 250),
            size_hint=(None, None),
            title_template='KeywordItemTitle')
    scatter = Scatter(size=app.keywords.size,
            auto_bring_to_front=False,
            pos_hint={'x': 0, 'center_y': 0.5},
            size_hint=(None, None), rotation=-90,
            do_translate=False, do_rotate=False, do_scale=False)
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
    scatter_imagemap.bind(pos=set_ordering_origin_pos)

    return root

