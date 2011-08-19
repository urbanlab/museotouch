from museolib.backend import Backend, BackendItem
import json

class BackendJSON(Backend):

    def load_items(self):
        filename = self.options.get('filename', None)
        with open(filename, 'r') as fd:
            data = json.loads(fd.read())
        assert(filename is not None)
        for item in data['items']:
            yield BackendItem(item)
