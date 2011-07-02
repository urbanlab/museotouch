import kivy
kivy.require('1.0.7-dev')

from os.path import join, dirname
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger
from kivy.resources import resource_add_path
from museolib.utils import format_date
from museolib.widgets.circularslider import CircularSlider
from museolib.backend.backendxml import BackendXML


class MuseotouchApp(App):

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


    def build(self):
        # add data directory as a resource path
        curdir = dirname(__file__)
        resource_add_path(join(curdir, 'data'))

        # link with the db. later, we need to change it to real one.
        self.db = db = BackendXML(filename=join(
            curdir, 'data', 'xml', 'objects.xml'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))

        # construct the app.
        root = FloatLayout()
        slider = CircularSlider(
                pos_hint={'right': 1, 'center_y': 0.5},
                size_hint=(None, None),
                size=(250, 500))
        root.add_widget(slider)

        # update the initial slider values to show date.
        slider.bind(value_range=self.update_date_range)
        self.update_date_range(slider, slider.value_range)

        return root

if __name__ in ('__main__', '__android__'):
    MuseotouchApp().run()
