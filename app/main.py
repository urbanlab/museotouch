import kivy
kivy.require('1.0.7-dev')

from os.path import join, dirname
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from museolib.widgets.circularslider import CircularSlider
from museolib.backend.backendxml import BackendXML
from kivy.logger import Logger


class MuseotouchApp(App):

    def update_date_range(self, instance, value):
        print 'range is', value
        ma, mb = value
        count = self.db.length
        item_min = int(ma * count)
        item_max = max(1, int(mb * count))

        items = self.db.items[item_min:item_max]
        print 'selected', len(items)
        item1 = items[0]
        item2 = items[-1]
        print 'minimum date is', item1.date
        print 'maximum date is', item2.date


    def build(self):

        curdir = dirname(__file__)
        self.db = db = BackendXML(filename=join(
            curdir, 'data', 'xml', 'objects.xml'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))

        root = FloatLayout()
        slider = CircularSlider(pos_hint={'right': 1, 'center_y': 0.5})
        root.add_widget(slider)
        slider.bind(value_range=self.update_date_range)


        return root

if __name__ in ('__main__', '__android__'):
    MuseotouchApp().run()
