# -*- coding: utf-8 -*-

import kivy
kivy.require('1.0.8-dev')

from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')

from random import random, randint
from os.path import join, dirname, exists, basename
from os import mkdir
from zipfile import ZipFile
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.resources import resource_add_path, resource_remove_path
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.utils import format_bytes_to_human

import museolib
from museolib.utils import format_date
from museolib.widgets.imageitem import ImageItem
from museolib.widgets.exposelector import ExpoSelector
#from museolib.backend.backendxml import BackendXML
from museolib.backend.backendjson import BackendJSON
from museolib.backend.backendweb import BackendWeb
import json
import imp

try:
    mode = 'mobile'
    import android
except ImportError:
    mode = 'table'

def delayed_work(func, items, delay=0):
    if not items:
        return
    def _delayed_work(*l):
        item = items.pop()
        if func(item) is False or not len(items):
            return False
        Clock.schedule_once(_delayed_work, delay)
    Clock.schedule_once(_delayed_work, delay)

class MuseotouchApp(App):

    @property
    def mode(self):
        return mode

    def do_reset_item_position(self, *largs):
        self.images_pos = {}
        root = self.root_images
        for i, item in enumerate(reversed(root.children)):
            x = randint(root.x + 200, root.right - 200)
            y = randint(root.y + 300, root.top - 100)
            rotation = randint(0, 360)
            item.flip_front = True
            (Animation(d=0.1 + i / 30.) + Animation(scale=0.30, center=(x, y),
                    rotation=rotation, t='out_quad', d=.25)).start(item)

    def do_ordering_origin(self, *largs):
        children = self.root_images.children
        origs = list(set([x.item.origin_key for x in children]))

        m = 300
        x = 150
        y = self.root_images.height / 2 - 75

        for i, item in enumerate(reversed(children)):
            ix = x + origs.index(item.item.origin_key) * m
            iy = y
            item.flip_front=True
            (Animation(d=0.05 + i / 30.) + Animation(scale=0.30, pos=(ix, iy),
                    rotation=0 + random() * 20 - 10, t='out_quad',
                    d=.20)).start(item)

    def do_ordering_datation(self, *largs):
        children = self.root_images.children[:]
        children.sort(key=lambda x: x.item.date)

        # remove and readd all children
        self.root_images.clear_widgets()
        for item in reversed(children):
            self.root_images.add_widget(item)

        cx, cy = self.root_images.center

        # seperate the table in 2
        imgs = 512 * 0.3
        width = self.root_images.width - 300
        height = self.root_images.height - 300
        x = 50
        y = self.root_images.top - imgs - 50
        dx = 1
        dy = -1

        mx = 1 + width // imgs
        my = 1 + height // imgs

        for i, item in enumerate(children):
            mi = i % (mx * my)
            ix = x + (mi % mx) * imgs * dx
            iy = y + (mi // mx) * imgs * dy
            item.flip_front=True
            (Animation(d=0.1 + i / 30.) + Animation(scale=0.30, pos=(ix, iy),
                    rotation=0., t='out_quad',
                    d=.25)).start(item)

        return

    def show_object(self, defs):
        source = defs['source']
        if source not in self.images_displayed:
            return
        current_images = [x.source for x in self.root_images.children]
        if source in current_images:
            return

        images_pos = self.images_pos
        if source in images_pos:
            p = images_pos[source]
            defs.pop('center', None)
            defs['center'] = p['center']
            defs['rotation'] = p['rotation']

        center = defs.pop('center')
        rotation = defs.pop('rotation')
        item = ImageItem(**defs)
        self.root_images.add_widget(item, -1)
        item.rotation = rotation
        item.center = center
        images_pos[source] = {
            'center': item.center,
            'rotation': item.rotation}

    def show_objects(self, objects):
        images = [x.source for x in self.root_images.children]
        root = self.root

        images_to_add = []
        images_displayed = []
        for item in objects:
            # is the current filename is already showed ?
            filename = item.filename
            if filename in images:
                images.remove(filename)
                continue

            x = randint(root.x + 200, root.right - 200)
            y = randint(root.y + 300, root.top - 100)
            angle = randint(0, 360)

            image = dict(source=filename, rotation=angle + 90,
                    center=(x, y), item=item, app=self)
            images_to_add.append(image)
            images_displayed.append(filename)

        self.images_displayed = images_displayed
        delayed_work(self.show_object, images_to_add)

        # remove all the previous images
        for child in self.root_images.children[:]:
            for filename in images:
                if filename == child.source:
                    self.images_pos[filename] = {
                        'center': child.center,
                        'rotation': child.rotation }
                    self.root_images.remove_widget(child)

    def update_objects_from_filter(self, *largs):
        '''Update the objects displayed from filters (date range, origin...)
        '''
        # start from all items
        items = self.db.items

        # update date range from slider value
        if self.date_slider:
            ma, mb = self.date_slider.value_range
            count = len(items)
            item_min = int(ma * count)
            item_max = max(item_min + 1, int(mb * count))

            # adjust item selection
            items = items[item_min:item_max]
            if len(items) == 0:
                self.show_objects(items)
                return
            item1 = items[0]
            item2 = items[-1]

            # set the text inside the slider
            self.date_slider.text_min = format_date(item1.date)
            self.date_slider.text_max = format_date(item2.date)

        # filter from origin
        if self.imagemap:
            origin_ids = self.imagemap.active_ids
            items = [x for x in items if x.origin_key in origin_ids]

        # show only the first 10 objects
        self.show_objects(items)

    def build_config(self, config):
        config.setdefaults('museotouch', {
            'url_api': 'http://museotouch.erasme.org/prive/api/',
            'url_data': 'http://museotouch.erasme.org/prive/uploads/',
            'expo': '',
        })

    def build_settings(self, settings):
        jsondata = '''[
            {
                "type": "numeric",
                "title": "Exposition",
                "desc": "Identifiant de l'exposition par defaut",
                "section": "museotouch",
                "key": "expo"
            }, {
                "type": "string",
                "title": "URL API",
                "desc": "Url vers l'API du backend web",
                "section": "museotouch",
                "key": "url_api"
            }, {
                "type": "string",
                "title": "URL Data",
                "desc": "Url vers les datas (scenarios et objets)",
                "section": "museotouch",
                "key": "url_data"
            }]'''
        settings.add_json_panel('Museotouch', self.config, data=jsondata)

    def build(self):
        config = self.config

        #: imagemap widget. If set, it will be used to filter items from
        #: origin_key
        self.imagemap = None

        #: date_slider widget. If set, it will be used to filter items from
        #: a the date range.
        self.date_slider = None

        # set the image type from mode
        self.imgtype = 'dds'
        if mode == 'table':
            # full resolution
            self.imgdir = 'dds'
        else:
            # reduced resolution
            self.imgdir = 'dds512'


        # list of removed objects
        self.images_displayed = []
        self.images_pos = {}

        # add data directory as a resource path
        self.data_dir = data_dir = join(dirname(museolib.__file__), 'data')
        resource_add_path(data_dir)

        # add kv file
        Builder.load_file(join(data_dir, 'global.kv'))

        # create trigger for updating objects
        self.trigger_objects_filtering = Clock.create_trigger(
            self.update_objects_from_filter, 0)

        # web backend
        self.backend = BackendWeb(
                url=config.get('museotouch', 'url_api'),
                data_url=config.get('museotouch', 'url_data'))

        # if we are on android, always start on selector
        # otherwise, check configuration
        if mode == 'table':
            self.build_for_table()
        else:
            self.build_selector()


    def build_for_table(self):
        # check which exposition we must use from the configuration
        expo = str(self.config.getint('museotouch', 'expo'))
        if expo is None or int(expo) <= 0:
            # no exposition set in the configuration file.
            # show the selector
            return self.build_selector()
        self.show_expo(expo)
        return FloatLayout()

    def build_selector(self, *l):
        return ExpoSelector(app=self)

    def build_app(self):
        try:
            self._build_app()
        except Exception, e:
            self.error(e)

    def _build_app(self):
        # Import the module
        modexpo = imp.load_source('__expo__', join(
            self.expo_data_dir, '__init__.py'))

        # link with the db. later, we need to change it to real one.
        Builder.load_file(join(self.expo_data_dir, 'museotouch.kv'))
        self.db = db = BackendJSON(filename=join(
            self.expo_dir, 'objects.json'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))

        # resolving filename for all item
        items = db.items[:]
        imgtype = self.imgtype
        for item in items[:]:
            if imgtype == 'raw':
                directory, ext = 'raw', 'png'
            else:
                directory, ext = self.imgdir, imgtype
            filename = join(self.expo_img_dir,  directory, '%d.%s' % (item.id, ext))
            if not exists(filename):
                Logger.error('Museolib: Unable to found image %s' % filename)
                items.remove(item)
                continue
            item.filename = filename

        db.items = items
        Logger.info('Museotouch: %d items usable' % len(db.items))

        # construct the app.
        self.root = root = modexpo.build(self)

        # add root layer for putting image
        self.root_images = FloatLayout()
        root.add_widget(self.root_images)

        # update the initial slider values to show date.
        if self.date_slider:
            self.date_slider.bind(value_range=self.trigger_objects_filtering)

        if self.imagemap:
            self.imagemap.bind(active_ids=self.trigger_objects_filtering)

        self.trigger_objects_filtering()


        parent = self.root.parent
        if parent:
            parent.remove_widget(self.root)
        else:
            from kivy.core.window import Window
            parent = Window
        self.root = root
        parent.add_widget(self.root)
        return root

    def show_expo(self, expo_id, popup=None):
        # check if expo is available on the disk
        self.expo_dir = self.get_expo_dir(expo_id)
        self.expo_data_dir = join(self.expo_dir, 'data')
        self.expo_img_dir = join(self.expo_dir, 'images')
        resource_add_path(self.expo_data_dir)

        # be able to run offline too.
        force_sync = True
        if force_sync:
            # create popup
            if popup is None:
                popup = Popup(title='Chargement...', size_hint=(None, None),
                        size=(300, 300), auto_dismiss=False)
                popup.open()
            # synchronize it !
            self.sync_expo(expo_id, popup)
        else:
            self.build_app()


    #
    # Synchronisation of an exhibition
    # this part is seperated in multiple step:
    # 1. create directory layout for an exhibition if not exists
    # 2. update the objects list of an exhibition
    # 3. fetch missing objects
    #

    def get_expo_dir(self, expo_id=None):
        if expo_id is None:
            return join(dirname(__file__), 'expos')
        return join(dirname(__file__), 'expos', expo_id)

    def sync_expo(self, expo_id, popup=None):
        # adjust the popup 
        popup.title = 'Synchronisation en cours...'
        popup.content = Image(source='loader.gif', anim_delay=.1)
        Animation(size=(300, 200), d=.2, t='out_quad').start(popup)
        self._sync_popup = popup

        # prepare popup for synchronisation
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(halign='center'))
        layout.add_widget(Label(halign='center'))
        layout.add_widget(ProgressBar())
        self._sync_popup.content = layout

        self._sync_popup_text(u'Téléchargement de la description')

        # create layout for exhibition
        for directory in (
                self.expo_dir,
                self.expo_data_dir,
                self.expo_img_dir,
                join(self.expo_img_dir, self.imgdir)):
            try:
                mkdir(directory)
            except OSError:
                pass

        # get the initial json
        self.backend.set_expo(expo_id)

        # get the initial zipfile
        self.backend.get_expos(
                uid=expo_id,
                on_success=self._sync_expo_1,
                on_error=self._sync_error_but_continue,
                on_progress=self._sync_progress)

    def _sync_popup_text(self, text):
        self._sync_popup.content.children[-1].text = text

    def _sync_expo_1(self, req, result):
        # check result files to found a zip files
        self._expo_files = files = [x['fichier'] for x in result['data']]
        zipfiles = [x for x in files if x.rsplit('.', 1)[-1] == 'zip']
        if len(zipfiles) != 1:
            self.error(u'Aucun fichier de données attaché '
                    u'à cette exposition (zip not found)')
            return

        # write the part of the json corresponding to that expo in the dir
        expojson = join(self.expo_dir, 'expo.json')
        with open(expojson, 'w') as fd:
            json.dump([result], fd)

        # if we already downloaded the data, we might have a checksum if
        # everything is ok.
        zipchecksum = join(self.expo_dir, 'data.checksum')
        checksum = ''
        if exists(zipchecksum):
            with open(zipchecksum, 'r') as fd:
                checksum = fd.read()

        if checksum == zipfiles[0]:
            Logger.info('Museolib: expo data dir already downloaded, continue.')
            # avoid downloading the zip, already got it.
            self._sync_expo_3()
            return

        # download the zip
        self._sync_popup_text(u'Téléchargement des données')
        self.backend.get_file(
            zipfiles[0],
            on_success=self._sync_expo_2,
            on_error=self._sync_error_but_continue,
            on_progress=self._sync_progress)

    def _sync_expo_2(self, req, result):
        # write result to data.zip
        zipfilename = join(self.expo_dir, 'data.zip')
        with open(zipfilename, 'w') as fd:
            fd.write(result)

        # uncompress in current directory
        zp = ZipFile(zipfilename)
        zp.extractall(self.expo_data_dir)

        # all ok, write original filename
        zipchecksum = join(self.expo_dir, 'data.checksum')
        with open(zipchecksum, 'w') as fd:
            fd.write(req.url)

        self._sync_expo_3()

    def _sync_expo_3(self):
        # try to found at least one image
        images = [x for x in self._expo_files if \
            x.rsplit('.', 1)[-1].lower() in ('png', 'jpg')]

        if not images:
            self._sync_expo_5()
            return

        # if we already downloaded the data, we might have a checksum if
        # everything is ok.
        thumbchecksum = join(self.expo_dir, 'thumbnail.checksum')
        checksum = ''
        if exists(thumbchecksum):
            with open(thumbchecksum, 'r') as fd:
                checksum = fd.read()

        if checksum == images[0]:
            Logger.info('Museolib: expo thumbnail already downloaded, continue.')
            # avoid downloading the zip, already got it.
            self._sync_expo_5()
            return

        # download the first one as a thumbnail
        self._sync_popup_text(u'Téléchargement de la miniature')
        self.backend.get_file(
            images[0],
            on_success=self._sync_expo_4,
            on_error=self._sync_error_but_continue,
            on_progress=self._sync_progress)

    def _sync_expo_4(self, req, result):
        ext = req.url.rsplit('.', 1)[-1]
        thumbnailfn = join(self.expo_dir, 'thumbnail.%s' % ext)
        with open(thumbnailfn, 'w') as fd:
            fd.write(result)

        # all ok, write original filename
        thumbchecksum = join(self.expo_dir, 'thumbnail.checksum')
        with open(thumbchecksum, 'w') as fd:
            fd.write(req.url)

        self._sync_expo_5()

    def _sync_expo_5(self):
        # get objects now.
        self._sync_popup_text(u'Téléchargement des objets')
        self.backend.get_objects(
                on_success=self._sync_expo_6,
                on_error=self._sync_error_but_continue,
                on_progress=self._sync_progress)

    def _sync_expo_6(self, req, result):
        filename = join(self.expo_dir, 'objects.json')
        with open(filename, 'wb') as fd:
            json.dump(result, fd)

        # on the result, remove all the object already synced
        items = result['items'][:]
        for item in result['items']:
            fichiers = item['data']
            if not fichiers:
                items.remove(item)
                continue
            for fichier in fichiers:
                fichier = fichier['fichier']
                if not self._sync_is_filename_of_item(item, fichier):
                    continue
                item['__item_filename__'] = fichier
                filename, ext = self._sync_convert_filename(fichier)
                local_filename = self._sync_get_local_filename(filename)
                if not exists(local_filename):
                    continue
            items.remove(item)

        self._sync_result = items
        self._sync_index = 0
        self._sync_missing = []

        if len(items):

            self._sync_download()

        else:
            # no item to synchronize, all done !
            self._sync_popup.dismiss()
            self.build_app()

    def _sync_get_local_filename(self, fn):
        if type(fn) in (list, tuple):
            fn = fn[0]
        return join(self.expo_img_dir, self.imgdir, fn)

    def _sync_is_filename_of_item(self, item, fichier):
        uid = fichier.split('/')[-1].rsplit('.', 1)[0]
        return str(uid) == str(item['id'])

    def _sync_convert_filename(self, filename):
        # from the original filename given by json
        # convert to the filename we want.
        filename = basename(filename)
        if self.imgtype != 'raw':
            filename = filename.rsplit('.', 1)[0] + '.' + self.imgtype
        # get ext
        ext = filename.rsplit('.', 1)[-1]
        return filename, ext

    def _sync_download(self):
        uid = self._sync_result[self._sync_index]['id']
        filename, ext = self._sync_convert_filename(
            self._sync_result[self._sync_index]['__item_filename__'])

        text = 'Synchronisation de %d/%d' % (
                self._sync_index + 1, len(self._sync_result))
        if len(self._sync_missing):
            text += '\n(%d non disponible)' % len(self._sync_missing)
        self._sync_popup.content.children[-1].text = text
        self._sync_popup.content.children[-2].text = filename

        # check if the file already exist on the disk
        filename = self._sync_get_local_filename(filename)
        if exists(filename):
            # speedup a little bit. but we can't use always -1.
            Clock.schedule_once(self._sync_download_next,
                    -1 if self._sync_index % 10 < 8 else 0)
        else:
            self.backend.download_object(uid, self.imgdir, self.imgtype,
                self._sync_download_ok, self._sync_error, self._sync_progress)

    def _sync_download_ok(self, req, result):
        if req.resp_status < 200 or req.resp_status >= 300:
            # look like invalid ? ok.
            self._sync_missing.append(self._sync_index)
        else:
            # save on disk
            filename, ext = self._sync_convert_filename(req.url)
            filename = self._sync_get_local_filename(filename)
            with open(filename, 'wb') as fd:
                fd.write(result)
        Clock.schedule_once(self._sync_download_next)

    def _sync_download_next(self, *largs):
        self._sync_index += 1
        if self._sync_index >= len(self._sync_result):
            self._sync_end()
            return
        self._sync_download()

    def _sync_end(self):
        self._sync_popup.dismiss()
        self.build_app()

    def _sync_progress(self, req, current, total):
        if total == -1:
            total = req.chunk_size * 10
            current %= req.chunk_size * 10
            total_str = None
        else:
            total_str = format_bytes_to_human(total)
        print '*progress*', req.url, current, total, req.chunk_size
        self._sync_popup.content.children[0].max = total
        self._sync_popup.content.children[0].value = current
        text = self._sync_popup.content.children[-2].text
        filename = text.split(' ')[0]
        text = ''
        if filename:
            text = '%s - ' % filename
        text = '%s' % format_bytes_to_human(current)
        if total_str is not None:
            text += '/%s' % total_str
        self._sync_popup.content.children[-2].text = text

    def _sync_error(self, req, result):
        self.error('Erreur lors de la synchro')

    def _sync_error_but_continue(self, req, result):
        self._sync_popup.dismiss()
        self.build_app()

    def error(self, error):
        content = BoxLayout(orientation='vertical')
        label = Label(text=error, valign='middle')
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        btn = Button(text='Fermer', size_hint_y=None, height=50)
        content.add_widget(btn)
        btn.bind(on_release=self.reset)
        popup = Popup(title='Erreur', content=content, auto_dismiss=False,
                size_hint=(.5, .5))
        popup.open()

    def reset(self, *l):
        # reset the whole app, restart from scratch.
        from kivy.core.window import Window
        for child in Window.children[:]:
            Window.remove_widget(child)

        # remove everything from the current expo
        if hasattr(self, 'expo_data_dir'):
            resource_remove_path(self.expo_data_dir)
            Builder.unload_file(join(self.expo_data_dir, 'museotouch.kv'))
            self.expo_dir = self.expo_data_dir = self.expo_img_dir = None

        # restart with selector.
        Window.add_widget(self.build_selector())
        

if __name__ in ('__main__', '__android__'):

    MuseotouchApp().run()
