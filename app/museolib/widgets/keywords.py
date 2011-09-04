from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, BooleanProperty

class Keyword(Label):

    selected = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.selected = not self.selected
            return True

class KeywordsGroup(GridLayout):
    pass

class Keywords(Accordion):
    keywords = ListProperty([])

    def __init__(self, **kwargs):
        super(Keywords, self).__init__(**kwargs)

    def on_keywords(self, instance, value):
        self.clear_widgets()

        accitem = None
        accgroup = None
        for item in value:
            if 'name' in item:
                # create new accordion
                accitem = AccordionItem(title=item['name'])
                self.add_widget(accitem)
                # create new group
                accgroup = KeywordsGroup()
                accitem.add_widget(accgroup)
            elif 'keywords' in item:
                for key in item['keywords']:
                    keyword = Keyword(text=key)
                    accgroup.add_widget(keyword)

