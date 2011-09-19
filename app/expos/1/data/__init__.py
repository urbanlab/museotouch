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
    # Size slider
    app.size_slider = slider = SizeSlider(
	    size=(420, 30), size_hint=(None, None))
    scatter = Scatter(size=app.size_slider.size,
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
            size=(500, 268),
            sources=sources,
            suffix='_active')
    root.add_widget(imagemap)

    # -------------------------------------------------------------------------
    # Create a widget for keywords
    # Here we are using a scatter between to be able to rotate the widget
    app.keywords = Keywords(
            size=(500, 250),
            size_hint=(None, None))
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
    ordering_origin = Button(
            background_normal='widgets/filter_reload.png',
            background_down='widgets/filter_reload_down.png',
            **kwargs)
    ordering_origin.bind(on_release=app.do_reset_item_position)
    toolbar_layout.add_widget(ordering_origin)

    # -------------------------------------------------------------------------
    # Create a button to order by continent
    ordering_origin = Button(
            background_normal='widgets/filter_origin.png',
            background_down='widgets/filter_origin_down.png',
            **kwargs)
    ordering_origin.bind(on_release=app.do_ordering_origin)
    toolbar_layout.add_widget(ordering_origin)

    return root

