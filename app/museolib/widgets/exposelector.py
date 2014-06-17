from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.logger import Logger
from os import listdir
from os.path import isdir, join, exists
from json import load
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
import random, os, time, locale
from os.path import dirname,abspath, join, isfile

from kivy.clock import Clock

class ExpoPopupChoice(ScrollView):

    def add_expo(self, widget):
        self.list_expos.add_widget(widget)

Factory.register('ExpoPopupChoice', cls=ExpoPopupChoice)

class ExpoItem(ButtonBehavior, Widget):
    expo = ObjectProperty(None)
    selector = ObjectProperty(None)

    color = (1,1,1,1)

    def __init__(self, **kwargs):
        yellow = (0.894, 0.886, 0.133,1)
        cobalt = (0.172, 0.2, 0.219,1)
        violet = (0.223, 0.015, 0.270,1)
        blue = (0, 0.376, 0.666,1)

        colors = [yellow, cobalt, violet, blue]
        random.shuffle(colors)

        rd = random.randint(0,3)
        self.color = colors[rd]

        super(ExpoItem, self).__init__(**kwargs)





    def launch_expo(self, dt):
        self.selector.select_expo(self.expo)

    def on_press(self):    
        img = self.ids['main_img']
        Animation.stop_all(img)
        anim = Animation(color=self.color, d=.2)
        anim.start(img)
        anim.on_complete = self.launch_expo

    def on_release(self):
        img = self.ids['main_img']
        Animation.cancel_all(img)
        img.color = (1,1,1,1)

class ExpoSelector(FloatLayout):

    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._popup = None
        super(ExpoSelector, self).__init__(**kwargs)
        self.req = self.app.backend.get_expos(on_success=self.on_success,
                on_error=self.on_error)
        # self.load()
        # self.load_offline(None)

    def load(self, *largs):
        content = Image(source='loader.gif', anim_delay=.1)
        self.popup(content=content, title='Liste des expositions')

    def load_offline(self, *l):
        self.show_expos()

    def on_success(self, req, result):
        self.show_expos(result)

    def show_expos(self, online=None):
        # get offline expo
        offline = self.get_offline_expos()
        if online is not None and type(offline) in (list, tuple):
            # mix with online expo
            result = self.mix_expos(offline, online)
        else:
            result = offline
        # show them.
        layout = ExpoPopupChoice()
        layout.list_expos.bind(minimum_height=layout.list_expos.setter('height'))

        # Alphabetical sort, case insensitive, and with accents
        result = sorted(result, key=lambda x: x['name'].lower(), cmp=locale.strcoll)
                
        for expo in result:
            # convert to string key, python 2.6.
            expo = dict([(str(x), y) for x, y in expo.iteritems()])
            zipfiles = [x['fichier'] for x in expo['data'] if
                    x['fichier'].rsplit('.', 1)[-1] == 'zip']
            data = [x['fichier'] for x in expo['data'] if
                    x['fichier'].rsplit('.', 1)[-1].lower() in ('jpg', 'png')]
            
            expo_dir = self.app.get_expo_dir(expo['id'])
            jpg = join(expo_dir, 'thumbnail.jpg')
            png = join(expo_dir, 'thumbnail.png')
            no_img = abspath(join(dirname(__file__), os.pardir, 'data/quit.png'))

            expo['no_img'] = False
            if isfile(jpg):
                expo['data'] = jpg
            elif isfile(png):
                expo['data'] = png
            else:
                expo['data'] = no_img
                expo['no_img'] = True
            expo['__zipfiles__'] = zipfiles
            # item = Builder.template('ExpoItem', selector=self, **expo)
            item = ExpoItem(selector=self, expo=expo)
            layout.add_expo(item)
        self.popup(content=layout, title='Liste des expositions')

    def get_offline_expos(self):
        # minimal files to check
        files = (
            'data', 'data.zip', 'data.checksum', 'expo.json', 'images',
            'thumbnail.checksum', 'thumbnail.jpg')
        expos_dir = self.app.get_expo_dir()
        result = []
        for item in listdir(expos_dir):
            Logger.debug('Museotouch: checking if %r is valid' % item)
            try:
                int_item = int(item)
            except:
                Logger.debug('Museotouch: skip, unable to convert to int')
                continue
            if str(int_item) != item:
                Logger.debug('Museotouch: skip, item is not a number') 
                continue
            d = join(expos_dir, item)
            if not isdir(d):
                Logger.debug('Museotouch: skip, item is not a directory') 
                continue
            ok = True
            for fn in files:
                dfn = join(d, fn)
                if not exists(dfn):
                    Logger.debug('Museotouch: skip, missing %r' % fn)
                    ok = False
                    break
            if not ok:
                continue
            try:
                jsonfn = join(d, 'expo.json')
                with open(jsonfn, 'r') as fd:
                    json = load(fd)[0]
                result.append(json)
                Logger.info('Museotouch: add expo "%s"' % json['name'])
            except:
                Logger.exception('Museotouch: skip, unable to load json')
        return result

    def mix_expos(self, offline, online):
        result = {}
        for item in offline + online:
            result[item['id']] = item
        return result.values()

    def build_selector(self):
        return ExpoSelector(app=self)

    def on_error(self, req, result):
        # content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        # content.add_widget(Label(text=
        #     'Erreur lors du chargement des expositions\n'
        #     'disponible en ligne.\n\n' +
        #     str(result)))
        # btn = Button(text='Continuer', size_hint_y=.25)
        # btn.bind(on_release=self.load_offline)
        # content.add_widget(btn)
        # self.popup(content=content, title='Erreur')
        print 'error'
        self.load_offline(None)

    def popup(self, content, title, **kwargs):
        if not self._popup:
            self._popup = popup = ModalView(
                    auto_dismiss=False,
                    size_hint=(None, None),
                    size=(400, 400))
            popup.open()

        else:
            popup = self._popup

        kwargs.setdefault('size', (Window.width, Window.height))
        Animation(t='out_quad', d=.2, **kwargs).start(popup)
        popup.content = content
        popup.add_widget(content)
        # popup.title = title
        return popup

    def select_expo(self, expo):
        for child in Window.children[:]:
            Window.remove_widget(child)
        self.app.show_expo(expo['id'])