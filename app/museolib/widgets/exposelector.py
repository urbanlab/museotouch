from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.logger import Logger
from os import listdir
from os.path import isdir, join, exists
from json import load
from kivy.uix.button import Button

class ExpoPopupChoice(BoxLayout):
    def add_expo(self, widget):
        self.list_expos.add_widget(widget)

Factory.register('ExpoPopupChoice', cls=ExpoPopupChoice)

class ExpoSelector(FloatLayout):

    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._popup = None
        super(ExpoSelector, self).__init__(**kwargs)
        self.req = self.app.backend.get_expos(on_success=self.on_success,
                on_error=self.on_error)
        self.load()

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
        for expo in result:
            # convert to string key, python 2.6.
            expo = dict([(str(x), y) for x, y in expo.iteritems()])
            zipfiles = [x['fichier'] for x in expo['data'] if
                    x['fichier'].rsplit('.', 1)[-1] == 'zip']
            data = [x['fichier'] for x in expo['data'] if
                    x['fichier'].rsplit('.', 1)[-1].lower() in ('jpg', 'png')]
            expo['data'] = data
            expo['__zipfiles__'] = zipfiles
            item = Builder.template('ExpoItem', selector=self, **expo)
            layout.add_expo(item)
        self.popup(content=layout, title='Liste des expositions',
                size=(1000, 800))

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
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text=
            'Erreur lors du chargement des expositions\n'
            'disponible en ligne.\n\n' +
            str(result)))
        btn = Button(text='Continuer', size_hint_y=.25)
        btn.bind(on_release=self.load_offline)
        content.add_widget(btn)
        self.popup(content=content, title='Erreur')

    def popup(self, content, title, **kwargs):
        if not self._popup:
            self._popup = popup = Popup(
                    auto_dismiss=False,
                    size_hint=(None, None),
                    size=(400, 400))
            popup.open()
        else:
            popup = self._popup

        kwargs.setdefault('size', (400, 400))
        Animation(t='out_quad', d=.2, **kwargs).start(popup)
        popup.content = content
        popup.title = title
        return popup

    def select_expo(self, expo):
        self.app.show_expo(expo['id'], self._popup)
