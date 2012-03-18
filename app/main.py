# -*- coding: utf-8 -*-

import kivy
kivy.require('1.0.8-dev')

from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')

from random import random, randint
from os.path import join, dirname, exists, basename
from os import makedirs
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
from kivy.utils import format_bytes_to_human, platform

import museolib
from museolib.utils import format_date
from museolib.widgets.imageitem import ImageItem
from museolib.widgets.exposelector import ExpoSelector
from museolib.backend.backendjson import BackendJSON
from museolib.backend.backendweb import BackendWeb
from json import dump, dumps
from imp import load_source
from math import ceil

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
        if platform() in ('android', 'ios'):
            return 'mobile'
        return 'table'

    def do_reset_item_position(self, *largs):
        self.images_pos = {}
        root = self.root_images     
        for i, item in enumerate(reversed(root.children)):
            x = randint(root.x + 200, root.right - 500)
            y = randint(root.y + 300, root.top - 200)
            rotation = randint(0, 360)
            item.flip_front = True
            (Animation(d=0.1 + i / 30.) + Animation(scale=item.scale_min, center=(x, y),
                    rotation=rotation, t='out_quad', d=.25)).start(item)

    def do_ordering_origin(self, *largs):
        children = self.root_images.children
        origs = list(set([x.item.origin_key for x in children]))
        def index_for_child(groups, child):
            return groups.index(child.item.origin_key)
        self._display_ordering_as_group(children, origs, index_for_child)

    def do_ordering_keywords(self, *largs):
        # ordering only on the current selected group
        if not self.keywords:
            return
        # get current active group
        children = self.root_images.children
        active = [x for x in self.keywords.children if not x.collapse]
        groups = [uid for g, uid in self.keywords.selected_keywords if g.accitem
                in active]
        if not groups:
            return
        def index_for_child(groups, child):
            for index, key in enumerate(groups):
                if key in child.item.keywords:
                    return index
            return -1
        self._display_ordering_as_group(children, groups, index_for_child)

    def do_ordering_size(self, *largs):
        children = self.root_images.children[:]
        children.sort(key=lambda x: x.item.taille)
        self._display_ordering_as_table(children)

    def do_ordering_datation(self, *largs):
        children = self.root_images.children[:]
        children.sort(key=lambda x: x.item.date)
        self._display_ordering_as_table(children)

    def _display_ordering_as_group(self, children, groups, 
            index_for_child):
        # size of image
        imgs = int(512 * .7)

        # size of area for work
        width = self.root_images.width - 800
        height = self.root_images.height - 400

        # images per size
        mx = max(1, width // imgs)
        my = max(1, height // imgs)

        # max
        mmx = min(len(groups), mx)
        mmy = int(min(ceil(len(groups) / float(mx)), my))

        x = self.root_images.center_x - (mmx * imgs) / 2
        y = self.root_images.center_y - (mmy * imgs) / 2 + imgs
        m = imgs

        # direction
        dx = 1
        dy = -1

        for i, item in enumerate(reversed(children)):
            mi = index_for_child(groups, item)
            ix = x + (mi % mx) * m * dx
            iy = y + (mi // mx) * m * dy
            '''
            ix = x + groups.index(keyfn(item)) * m
            iy = y
            '''
            item.flip_front=True
            (Animation(d=0.05 + i / 30.) + Animation(scale=item.scale_min, pos=(ix, iy),
                    rotation=0 + random() * 20 - 10, t='out_quad',
                    d=.20)).start(item)

    def _display_ordering_as_table(self, children):
        # remove and readd all children
        self.root_images.clear_widgets()
        for item in reversed(children):
            self.root_images.add_widget(item)

        cx, cy = self.root_images.center

        # size of image
        imgs = int(512 * .5)

        # size of area for work
        width = self.root_images.width - 600
        height = self.root_images.height - 400

        # images per size
        mx = 1 + width // imgs
        my = 1 + height // imgs

        # initial position
        x = self.root_images.center_x - (mx * imgs) / 2
        y = self.root_images.center_y + (my * imgs) / 2 - imgs

        # XXX make it configurable, this is to prevent overlap with map widget
        y += 80

        # direction
        dx = 1
        dy = -1

        for i, item in enumerate(children):
            mi = i % (mx * my)
            ix = x + (mi % mx) * imgs * dx
            iy = y + (mi // mx) * imgs * dy
            item.flip_front=True
            (Animation(d=0.1 + i / 30.) + Animation(scale=item.scale_min, pos=(ix, iy),
                    rotation=0., t='out_quad',
                    d=.25)).start(item)

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
            y = randint(root.y + 400, root.top - 100)
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

        # filter on size
        if self.size_slider:
            # reorder item by taille
            items.sort(key=lambda x: x.taille)
            ma, mb = self.size_slider.value_range
            count = len(items)
            item_min = int(ma * count)
            item_max = max(item_min + 1, int(mb * count))

            # adjust item selection
            items = items[item_min:item_max]
            if len(items) == 0:
                self.show_objects(items)
                return

        # filter from origin
        if self.imagemap:
            origin_ids = self.imagemap.active_ids

            # special case. If we got some keywords, but no origin, don't use
            # it.
            if self.keywords and self.keywords.selected_keywords and not origin_ids:
                pass
            else:
                items = [x for x in items if x.origin_key in origin_ids]

        # filter with keywords
        # AND between group
        # OR inside group
        if self.keywords and self.keywords.selected_keywords:
            selected_keywords = self.keywords.selected_keywords
            groups = list(set([x[0] for x in selected_keywords]))
            groups_result = {}
            items_result = []

            # check every group
            for group in groups:
                # check keywords for current group
                keywords = [x[1] for x in selected_keywords if x[0] == group]

                result = []

                # check every items if we got at least one keyword of that group
                for item in items:
                    for key in keywords:
                        # found one group keyword in the item ?
                        if key in item.keywords:
                            result.append(item)
                            if not item in items_result:
                                items_result.append(item)
                            break

                # add the result to the group result
                groups_result[group] = result

            # on all the avialable item, ensure they are all in the selected
            # group
            for item in items_result[:]:
                valid = all([item in x for x in groups_result.itervalues()])
                if not valid:
                    items_result.remove(item)

            # now set the result as the new set of items
            items = items_result


        # show only the first 10 objects
        self.show_objects(items)

    def build_config(self, config):
        config.setdefaults('museotouch', {
            'url': 'http://museotouch.erasme.org/prive/',
            'url_api': 'http://museotouch.erasme.org/prive/api/',
            'url_data': 'http://museotouch.erasme.org/prive/uploads/',
            'expo': '0',
            'email_send' : 'True',
            'url_send_url' : 'http://urltest.lapin.be',
            'url_send' : 'True',
            'url_send_detailed_item' : 'True'
        })
        if platform() not in ('ios', 'android'):
            config.setdefaults('rfid', {
                'uid_restart': '',
                'uid_mainscreen': '',
                'uid_settings': '',
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
        if platform() not in ('ios', 'android'):
            jsondata = '''[
                {
                    "type": "string",
                    "title": "Redémarrage",
                    "desc": "RFID pour le redémarrage de l'application",
                    "section": "rfid",
                    "key": "uid_restart"
                }, {
                    "type": "string",
                    "title": "Ecran principal",
                    "desc": "Retour vers l'écran principal",
                    "section": "rfid",
                    "key": "uid_mainscreen"
                }, {
                    "type": "string",
                    "title": "Configuration",
                    "desc": "Affichage de l'écran de configuration",
                    "section": "rfid",
                    "key": "uid_settings"
                }]'''
            settings.add_json_panel('Rfid', self.config, data=jsondata)

    def build(self):
        config = self.config

        #: imagemap widget. If set, it will be used to filter items from
        #: origin_key
        self.imagemap = None

        #: date_slider widget. If set, it will be used to filter items from
        #: a the date range.
        self.date_slider = None

        #: keywords widget. If set, it will be used to show keywords
        self.keywords = None

        #: size slider. If set, it will be used to show all size
        self.size_slider = None

        # set the image type from mode
        self.imgtype = 'dds'
        self.imgdir = 'dds'

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

        # rfid daemon
        self.rfid_daemon = None
        if platform() not in ('ios', 'android'):
            try:
                from museolib.rfid import RfidDaemon
                self.rfid_daemon = RfidDaemon()
                self.rfid_daemon.bind(on_uid=self.on_rfid_uid)
                self.rfid_daemon.start()
            except Exception:
                Logger.critical('Unable to import RfidDaemon, pynfc missing ?')
                Logger.exception('')

        # if we are on android, always start on selector
        # otherwise, check configuration
        if self.mode == 'table':
            self.build_for_table()
        else:
            self.build_selector()

    def on_stop(self):
        if self.rfid_daemon:
            self.rfid_daemon.stop()
        super(MuseotouchApp, self).on_stop()

    def on_rfid_uid(self, instance, uid):
        Logger.debug('App: Got RFID %r' % uid)
        token = self.config.get
        if uid in token('rfid', 'uid_restart').lower().split(','):
            Logger.info('App: Rfid ask to restart the app !')
            self.stop()
        elif uid in token('rfid', 'uid_mainscreen').lower().split(','):
            Logger.info('App: Rfid ask to return on main screen')
            self.close_settings()
        elif uid in token('rfid', 'uid_settings').lower().split(','):
            Logger.info('App: Rfid ask to open settings')
            self.open_settings()
        else:
            # TODO: check on webserver if some scenario need to be done
            pass

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
        modexpo = load_source('__expo__', join(
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

        # update keywords
        if self.keywords:
            self.keywords.keywords = db.keywords
            self.keywords.bind(selected_keywords=self.trigger_objects_filtering)

        # update size slider
        if self.size_slider:
            self.size_slider.bind(value_range=self.trigger_objects_filtering)

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
        if self.mode == 'mobile':
            root_expo = '/sdcard/museotouch/expos'
        else:
            root_expo = join(dirname(__file__), 'expos')
        try:
            makedirs(root_expo)
        except OSError, e:
            print 'ERROR WHILE CREATING INITIAL LAYOUT?'
            print e
        if expo_id is None:
            return root_expo
        return join(root_expo, expo_id)

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
                makedirs(directory)
            except OSError:
                pass

        # get the initial json
        self.backend.set_expo(expo_id)

        # get the initial zipfile
        Logger.info('Museotouch: Synchronization starting')
        self.backend.get_expos(
                uid=expo_id,
                on_success=self._sync_expo_1,
                on_error=self._sync_error_but_continue,
                on_progress=self._sync_progress)

    def _sync_popup_text(self, text):
        self._sync_popup.content.children[-1].text = text

    def _sync_expo_1(self, req, result):
        Logger.info('Museotouch: Synchronization part 1')
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
            dump([result], fd)

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
        Logger.info('Museotouch: Synchronization part 2')
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
        Logger.info('Museotouch: Synchronization part 3')
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
        Logger.info('Museotouch: Synchronization part 4')
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
        Logger.info('Museotouch: Synchronization part 5')
        # get objects now.
        self._sync_popup_text(u'Téléchargement des objets')
        self.backend.get_objects(
                on_success=self._sync_expo_6,
                on_error=self._sync_error_but_continue,
                on_progress=self._sync_progress)

    def _sync_expo_6(self, req, result):
        Logger.info('Museotouch: Synchronization part 6')
        filename = join(self.expo_dir, u'objects.json')
        with open(filename, 'wb') as fd:
            s = dumps(result)
            fd.write(s)

        # on the result, remove all the object already synced
        items = result['items'][:]
        for item in result['items']:
            fichiers = item['data']
            if not fichiers:
                print '===> remove item %r, no data attached' % item['nom']
                items.remove(item)
                continue
            need_sync = True
            print 'check', item['id']
            for fichier in fichiers:
                fichier = fichier['fichier']
                if not self._sync_is_filename_of_item(item, fichier):
                    print '1'
                    continue
                item['__item_filename__'] = fichier
                filename, ext = self._sync_convert_filename(fichier)
                local_filename = self._sync_get_local_filename(filename)
                if not exists(local_filename):
                    print '2'
                    continue
                # now, ensure the md5 is the same
                md5_local_filename = '%s.md5sum' % local_filename
                md5 = item['fichier_md5'].strip()

                # if we don't have md5 sum attached, forget about it.
                if not exists(md5_local_filename):
                    if not md5:
                        need_sync = False
                    print '3', need_sync, repr(md5)
                    continue
                # ok, is the md5 is the same ?
                with open(md5_local_filename, 'r') as fd:
                    md5_local = fd.read()
                # different md5, redownload.
                if md5 != md5_local:
                    print '4', repr(md5)
                    continue
                need_sync = False
            if not need_sync:
                items.remove(item)

        Logger.info('Museotouch: %d need to be synced' % len(items))

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
        '''
        if exists(filename):
            # speedup a little bit. but we can't use always -1.
            Clock.schedule_once(self._sync_download_next,
                    -1 if self._sync_index % 10 < 8 else 0)
        else:
        '''
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

            # write md5 attached to item if exist
            item_md5 = self._sync_result[self._sync_index]['fichier_md5'].strip()
            if item_md5:
                md5_filename = '%s.md5sum' % filename
                with open(md5_filename, 'wb') as fd:
                    fd.write(item_md5)

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
        #print '*progress*', req.url, current, total, req.chunk_size
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
        if type(error) not in (str, unicode):
            error = str(error)
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
