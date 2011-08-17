from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.animation import Animation

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
        content = Label(text='Chargement...')
        self.popup(content=content, title='Liste des expositions')

    def on_success(self, req, result):
        layout = ExpoPopupChoice()
        for expo in result:
            item = Builder.template('ExpoItem', selector=self, **expo)
            layout.add_expo(item)
        self.popup(content=layout, title='Liste des expositions',
                size=(600, 400))
    def build_selector(self):
        return ExpoSelector(app=self)


    def on_error(self, req, result):
        content = Label(text='Erreur lors du chargement\n' + str(result))
        p = self.popup(content=content, title='Erreur')
        p.allow_dismiss = True
        p.bind(on_dismiss=self.load)

    def popup(self, content, title, **kwargs):
        if not self._popup:
            self._popup = popup = Popup(
                    allow_dismiss=False,
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
        self.app.show_expo(expo, self._popup)
