__all__ = ('Keywords', )

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, \
        NumericProperty, StringProperty


class Keyword(Label):

    selected = BooleanProperty(False)

    controler = ObjectProperty(None)

    group = ObjectProperty(None)

    text_id = StringProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.selected = not self.selected
            return True

    def on_selected(self, instance, value):
        keywords = self.controler.selected_keywords
        key = (self.group, self.text_id)
        if value:
            if not key in keywords:
                keywords.append(key)
                self.group.count_selected += 1
        else:
            if key in keywords:
                keywords.remove(key)
                self.group.count_selected -= 1


class KeywordsGroup(GridLayout):

    title = StringProperty('')

    accitem = ObjectProperty(None)

    count_selected = NumericProperty(0)

    def on_count_selected(self, instance, value):
        text = '%s' % self.title
        if value > 0:
            text += ' (%d)' % value
        self.accitem.title = text


class Keywords(Accordion):

    keywords = ListProperty([])

    selected_keywords = ListProperty([])

    title_template = StringProperty(None)

    def __init__(self, **kwargs):
        super(Keywords, self).__init__(**kwargs)

    def on_keywords(self, instance, value):
        self.clear_widgets()

        accitem = None
        accgroup = None
        for item in value:
            # create new accordion
            k = {}
            if self.title_template:
                k['title_template'] = self.title_template
            accitem = AccordionItem(title=item['group'], **k)
            self.add_widget(accitem)
            # create new group
            accgroup = KeywordsGroup(title=item['group'], accitem=accitem)
            accitem.add_widget(accgroup)
            for child in item['children']:
                keyword = Keyword(text=child['name'], text_id=child['id'],
                        controler=self, group=accgroup)
                accgroup.add_widget(keyword)

