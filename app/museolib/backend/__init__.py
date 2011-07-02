
class BackendItem(dict):
    @property
    def date(self):
        return int(self['date_crea'])

class Backend(object):
    def __init__(self, **options):
        self.items = []
        self.options = options

        for item in self.load_items():
            self.add_item(item)
        self.items = sorted(self.items, key=lambda x: x.date)

    def add_item(self, item):
        assert(isinstance(item, BackendItem))
        self.items.append(item)

    @property
    def length(self):
        return len(self.items)
