import unicodedata
import configparser
from kivy.network.urlrequest import UrlRequest
import json

def format_date(dt):
    '''Format the integer date to text for slider
    '''
    if dt < 0:
        return '%d AV JC' % dt
    return str(dt)

def remove_accents(str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(str))
    return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

hexa_table = list(range(ord('a'), ord('z')+1)) + list(range(ord('A'), ord('Z')+1)) + list(range(ord('0'), ord('9') + 1)) + [ord('_'), ord('-')]
ascii_table = map(chr, hexa_table)

def convert_to_key(name):
    name = remove_accents(name.lower())
    name = u''.join([x if x in ascii_table else '_' for x in name])
    return name

def no_url(f):
    return f[7:].replace('/', '_')

class send_mail:  # s'utilise comme une fonction

    def __init__(self, items, email_to, email_from=''):
        items = [items] if not isinstance(items, list) else items  # ensure it's a list
        self.ids_items = ','.join([str(item.id) for item in items])
        self.email_to, self.email_from = email_to, email_from

        self.api = {
            'new' : '?act=cart',
            'add': ['?act=acart&item=','&cart='],
            'mail': ['?act=scart&id=','&mail=', '&from='],
        }
        conf = ConfigParser()
        conf.read('museotouch.ini')
        self.url = conf.get('museotouch', 'url_api')
        self.id_basket = None

        self._do()

    def _do(self):
        # new basket
        url_new = self.url + self.api['new']
        self.rep = UrlRequest(url_new, self.add_items, self.on_error)

    def add_items(self, req, resp):
        self.id_basket = resp['id']
        url_add = self.url + self.api['add'][0] + self.ids_items + self.api['add'][1] + self.id_basket
        self.rep = UrlRequest(url_add, self.send_email, self.on_error)

    def send_email(self, req, resp):
        url_mail = self.url + self.api['mail'][0] + self.id_basket + self.api['mail'][1] + self.email_to + self.api['mail'][2] + self.email_from
        self.rep = UrlRequest(url_mail, self.on_success, self.on_error)

    def on_success(self, *args, **kwargs):
        print('<success SendMail>')

    def on_error(self, *args, **kwargs):
        print('<error SendMail>')



