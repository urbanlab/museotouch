import kivy
kivy.require('1.0.7-dev')

import random
from glob import glob
from os.path import join, dirname, exists
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger
from kivy.resources import resource_add_path
from kivy.lang import Builder
from kivy.clock import Clock
from museolib.utils import format_date
from museolib.widgets.circularslider import CircularSlider
from museolib.widgets.imagemap import ImageMap
from museolib.widgets.imageitem import ImageItem
from museolib.backend.backendxml import BackendXML

class MuseotouchApp(App):

    def get_filenames_from_objects(self, objects):
        data_dir = self.data_dir
        directory = ext = 'dds'
        for item in objects:
            filename = join(data_dir, 'images', directory, '%d.%s' % (item.id, ext))
            if not exists(filename):
                Logger.error('Museolib: Unable to found image %s' % filename)
                continue
            yield filename, item

    def show_objects(self, objects):
        images_displayed = [x.source for x in self.root_images.children]

        filenames = list(self.get_filenames_from_objects(objects))
        root = self.root
        add = self.root_images.add_widget
        randint = random.randint
        for filename, item in filenames:

            # is the current filename is already showed ?
            if filename in images_displayed:
                images_displayed.remove(filename)
                continue

            x = randint(root.x + 200, root.right - 200)
            y = randint(root.y + 300, root.top - 100)
            angle = randint(0, 360)

            image = ImageItem(source=filename, rotation=angle + 90, center=(x, y))
            add(image)

        # remove all the previous images
        for child in self.root_images.children[:]:
            for filename in images_displayed:
                if filename == child.source:
                    self.root_images.remove_widget(child)

    def update_objects_from_filter(self, *largs):
        '''Update the objects displayed from filters (date range, origin...)
        '''
        # update date range from slider value
        ma, mb = self.slider.value_range
        count = self.db.length
        item_min = int(ma * count)
        item_max = max(item_min + 1, int(mb * count))

        # adjust item selection
        items = self.db.items[item_min:item_max]
        item1 = items[0]
        item2 = items[-1]

        # set the text inside the slider
        self.slider.text_min = format_date(item1.date)
        self.slider.text_max = format_date(item2.date)

        # filter from origin
        origin_ids = self.imagemap.active_ids
        items = [x for x in items if x.origin_key in origin_ids]

        # show only the first 10 objects
        self.show_objects(items)

    def build(self):
        # add data directory as a resource path
        self.data_dir = data_dir = join(dirname(__file__), 'data')
        resource_add_path(data_dir)

        # add kv file
        Builder.load_file(join(data_dir, 'museotouch.kv'))

        # create trigger for updating objects
        self.trigger_objects_filtering = Clock.create_trigger(
            self.update_objects_from_filter, 0)

        # link with the db. later, we need to change it to real one.
        self.db = db = BackendXML(filename=join(
            data_dir, 'xml', 'objects.xml'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))

        # construct the app.
        # at one moment, this could be moved to a "generic" app.xml file
        # that can be used to load another scenario
        self.root = root = FloatLayout()
        self.slider = slider = CircularSlider(
                pos_hint={'right': 1, 'center_y': 0.5},
                size_hint=(None, None),
                size=(250, 500))
        root.add_widget(slider)

        # search image for map (exclude _active) files
        sources = glob(join(data_dir, 'widgets', 'map', '*.png'))
        sources = [x for x in sources if '_active' not in x]
        self.imagemap = imagemap = ImageMap(
                pos_hint={'center_x': 0.5, 'y': 0},
                size_hint=(None, None),
                size=(500, 268),
                sources=sources,
                suffix='_active')
        root.add_widget(imagemap)

        # add root layer for putting image
        self.root_images = FloatLayout()
        self.root.add_widget(self.root_images)

        # update the initial slider values to show date.
        slider.bind(value_range=self.trigger_objects_filtering)
        imagemap.bind(active_ids=self.trigger_objects_filtering)
        self.trigger_objects_filtering()

        return root


if __name__ in ('__main__', '__android__'):
    MuseotouchApp().run()
