from museolib.utils import convert_to_key
error_log = []
class BackendItem(dict):
    @property
    def date(self):
        if 'date_crea' in self['fields']:
            try :
                return int(self['fields']['date_crea'])
            except:
                return self.error_logger('Date')

    @property
    def id(self):
        return int(self['itemId'])

    @property
    def origin(self):
        if 'orig_geo' !='' or orig_geo != None:
            if 'orig_geo' in self['fields']:
                return self['fields']['orig_geo']
        else:
            return self.error_logger('Origine geographique')

    @property
    def origin_ex(self):
        if 'orig_geo_prec' in self['fields']:
            return self['fields']['orig_geo_prec']

    @property
    def title(self):
        return self['name']

    # @property
    # def description(self):
    #     return self['cartel']

    @property
    def origin_key(self):
        return convert_to_key(self.origin)

    @property
    def medias(self):
        ret = []
        for x in self['fields']['data']:
            name = x.rsplit('/')[-1].rsplit('.')[0]
            if name == str(self.id):
                continue
            ret.append(x)
        return ret

    # @property
    # def taille(self):
    #     try:
    #         return int(self['fields']['taille'])
    #     except:
    #         return self.error_logger('Taille')

    def __getattr__(self, nom):
        """ Si l'attribut n'est pas dans ceux ci dessus, c'est un item du JSON : """
        if nom in self:  # renvoie None sinon
            return self[nom]
        elif nom in self['fields']:
            return self['fields'][nom]
        else:
            if nom == 'description':
                import pdb; pdb.set_trace()
            raise AttributeError(nom)

    def __setattr__(self, nom, val):
        self[nom] = val
    def error_logger(self,prop):
        # print 'Champ %s mal rempli pour la fiche : %s'%(prop,self.title)
        if self.title not in error_log:
            error_log.append(self.title)
        return 'Champ non ou mal rempli dans le back-office'

class Backend(object):
    def __init__(self, **options):
        self.items = []
        self.options = options

        for item in self.load_items():
            self.add_item(item)
        self.items = sorted(self.items, key=lambda x: x.date)
    def get_errors(self):
        return error_log
    def add_item(self, item):
        assert(isinstance(item, BackendItem))
        self.items.append(item)

    @property
    def length(self):
        return len(self.items)

    # database request
    def get_expos(self, on_success=None, on_error=None):
        pass
