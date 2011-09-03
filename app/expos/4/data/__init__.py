from os.path import join
from glob import glob
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap

def build(app):
    # Here, you must return a root widget that will be used for app
    # You also have app instance in parameter.

    # -------------------------------------------------------------------------
    # Our root widget
    root = FloatLayout()

    # -------------------------------------------------------------------------
    # Add a date slider to our root widget.
    app.date_slider = slider = CircularSlider(
            pos_hint={'right': 1, 'center_y': 0.5},
            size_hint=(None, None),
            size=(250, 500))
    root.add_widget(slider)

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
    # Create a button to order by continent
    ordering_origin = Button(text='Continent', size_hint=(None, None),
            size=(80, 50), pos=(0, 30))
    ordering_origin.bind(on_release=app.do_ordering_origin)
    root.add_widget(ordering_origin)

    # -------------------------------------------------------------------------
    # Create a button to order by datation
    ordering_datation = Button(text='Datation', size_hint=(None, None),
            size=(80, 50), pos=(110, 30))
    ordering_datation.bind(on_release=app.do_ordering_datation)
    root.add_widget(ordering_datation)

    return root

