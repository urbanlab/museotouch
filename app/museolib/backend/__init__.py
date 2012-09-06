from museolib.utils import convert_to_key

class BackendItem(dict):
    @property
    def date(self):
        if 'date_crea' in self:
            return int(self['date_crea'])

    @property
    def id(self):
        return int(self['id'])

    @property
    def origin(self):
        if 'orig_geo' in self:
            return self['orig_geo']

    @property
    def origin_ex(self):
        if 'orig_geo_prec' in self:
            return self['orig_geo_prec']

    @property
    def title(self):
        return self['nom']

    # @property
    # def description(self):
    #     return self['cartel']

    @property
    def origin_key(self):
        return convert_to_key(self.origin)

    @property
    def medias(self):
        ret = []
        for x in self['data']:
            name = x['fichier'].rsplit('/')[-1].rsplit('.')[0]
            if name == str(self.id):
                continue
            ret.append(x['fichier'])
        return ret

    @property
    def taille(self):
        try:
            return int(self['taille'])
        except:
            return 0

    def __getattr__(self, nom):
        """ Si l'attribut n'est pas dans ceux ci dessus, c'est un item du JSON : """
        if nom in self:  # renvoie None sinon
            return self[nom]
        else:
            if nom == 'description':
                import pdb; pdb.set_trace()
            raise AttributeError(nom)

    def __setattr__(self, nom, val):
        self[nom] = val

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
