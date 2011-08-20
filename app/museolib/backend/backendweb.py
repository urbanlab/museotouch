from museolib.backend import Backend, BackendItem
from kivy.network.urlrequest import UrlRequest
from functools import partial
from urllib import unquote_plus

class BackendWeb(Backend):

    def __init__(self, **kwargs):
        super(BackendWeb, self).__init__(**kwargs)
        self.expo = None
        self.url = kwargs.get('url')
        self.data_url = kwargs.get('data_url')

    def set_expo(self, uid):
        self.expo = uid

    def build_url(self, path):
        return self.url + path

    def build_data_url(self, path):
        return self.data_url + path

    def unquote_json(self, on_success, req, json):
        on_success(req, self._unquote(json))

    def _unquote(self, json):
        unquote = self._unquote
        tp = type(json)
        if tp in (list, tuple):
            return tp([unquote(x) for x in json])
        elif tp is dict:
            return dict((x, unquote(y)) for x, y in json.iteritems())
        elif tp in (str, unicode):
            json = unquote_plus(json)
            try:
                json = json.encode('latin1')
                json = json.decode('utf8')
            except:
                pass
        return json

    def load_items(self, on_success=None, on_error=None):
        return []

    #
    # Public
    #

    def get_expos(self, on_success=None, on_error=None):
        url = self.build_url('')
        on_success = partial(self.unquote_json, on_success)
        self.req = UrlRequest(url, on_success, on_error)

    def get_objects(self, on_success=None, on_error=None):
        assert(self.expo is not None)
        url = self.build_url('?act=expo&id=%s' % self.expo)
        on_success = partial(self.unquote_json, on_success)
        self.req = UrlRequest(url, on_success, on_error)

    def download_object(self, uid, ext, is_raw, on_success=None, on_error=None,
            on_progress=None):
        # 2 cases to handle
        # raw images are in objets/raw/*.png
        # compressed images are dispatched in multiple folder like
        # - objets/compressed/dds/*.dds
        # - ...
        raw = 'raw' if is_raw else 'compressed'
        subfolder = '%s/' % ext if not is_raw else ''
        url = self.build_data_url('objets/%s/%s%s.%s' % (
            raw, subfolder, uid, ext
        ))
        self.req = UrlRequest(url, on_success, on_error, on_progress,
                chunk_size=32768)

