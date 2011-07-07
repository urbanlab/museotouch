import kivy
kivy.require('1.0.7-dev')

from glob import glob
from os.path import join, dirname, exists
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger
from kivy.resources import resource_add_path
from kivy.lang import Builder
from museolib.utils import format_date
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.imageitem import ImageItem
from museolib.backend.backendxml import BackendXML

class MuseotouchApp(App):

    def show_objects(self, objects):
        self.root_images.clear_widgets()
        data_dir = self.data_dir
        #directory = ext = 'dxt'
        #directory, ext = 'original', 'png'
        directory = ext = 'dds'
        for item in objects:
            filename = join(data_dir, 'images', directory, '%d.%s' % (item.id, ext))
            if not exists(filename):
                Logger.error('Museolib: Unable to found image %s' % filename)
                continue
            image = ImageItem(source=filename)
            self.root_images.add_widget(image)

    def update_date_range(self, instance, value):
        # update date range from slider value
        ma, mb = value
        count = self.db.length
        item_min = int(ma * count)
        item_max = max(item_min + 1, int(mb * count))

        # adjust item selection
        items = self.db.items[item_min:item_max]
        item1 = items[0]
        item2 = items[-1]

        # set the text inside the slider
        instance.text_min = format_date(item1.date)
        instance.text_max = format_date(item2.date)

        # show only the first 10 objects
        self.show_objects(items)

    def build(self):
        # add data directory as a resource path
        self.data_dir = data_dir = join(dirname(__file__), 'data')
        resource_add_path(data_dir)

        # add kv file
        Builder.load_file(join(data_dir, 'museotouch.kv'))

        # link with the db. later, we need to change it to real one.
        self.db = db = BackendXML(filename=join(
            data_dir, 'xml', 'objects.xml'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))

        # construct the app.
        # at one moment, this could be moved to a "generic" app.xml file
        # that can be used to load another scenario
        self.root = root = FloatLayout()
        slider = CircularSlider(
                pos_hint={'right': 1, 'center_y': 0.5},
                size_hint=(None, None),
                size=(250, 500))
        root.add_widget(slider)

        # search image for map (exclude _bleu) files
        sources = glob(join(data_dir, 'widgets', 'map', '*.png'))
        sources = [x for x in sources if '_bleu' not in x]
        imagemap = ImageMap(
                pos_hint={'center_x': 0.5, 'y': 0},
                size_hint=(None, None),
                size=(500, 268),
                sources=sources,
                suffix='_bleu')
        root.add_widget(imagemap)

        # add root layer for putting image
        self.root_images = FloatLayout()
        self.root.add_widget(self.root_images)

        # update the initial slider values to show date.
        slider.bind(value_range=self.update_date_range)
        self.update_date_range(slider, slider.value_range)

        return root

if __name__ in ('__main__', '__android__'):
    MuseotouchApp().run()
