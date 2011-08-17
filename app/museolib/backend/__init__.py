from museolib.utils import convert_to_key

class BackendItem(dict):
    @property
    def date(self):
        return int(self['date_crea'])

    @property
    def id(self):
        return int(self['id'])

    @property
    def origin(self):
        return self['orig_geo']

    @property
    def origin_key(self):
        return convert_to_key(self.origin)

    @property
    def title(self):
        return self['nom']

    @property
    def description(self):
        return self['cartel']

    @property
    def datation(self):
        return self['datation']

    @property
    def date_crea(self):
        return self['date_crea']

    @property
    def origin_ex(self):
        return self['orig_geo_prec']

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

    # database request
    def get_expos(self, on_success=None, on_error=None):
        pass
