from museolib.backend import Backend, BackendItem
import json

class BackendJSON(Backend):

    def load_items(self):
        filename = self.options.get('filename', None)        
        with open(filename, 'r') as fd:
            data = json.loads(fd.read())[0]

        self.keywords = data['keywords']
        assert(filename is not None)
        for item in data['items']:
            yield BackendItem(item)
