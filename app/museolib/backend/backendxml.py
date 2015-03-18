from museolib.backend import Backend, BackendItem
from xml.dom import minidom

class BackendXML(Backend):

    def load_items(self):
        filename = self.options.get('filename', None)
        assert(filename is not None)
        xmldoc = minidom.parse(filename)
        for item in xmldoc.getElementsByTagName('objet'):
            result = dict()
            for key in ('id', 'nom', 'date_crea', 'date_acqui', 'datation',
                    'orig_geo', 'orig_geo_prec', 'taille', 'cartel'):
                result[key] = item.getElementsByTagName(key)[0].firstChild.data
            yield BackendItem(result)
